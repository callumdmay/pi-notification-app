#
# first we monitor the host serial , if available the rtu port as well as looking for pictures
#
old_host_bytes = 0
old_rtu_bytes = 0
new_rtu_bytes = 0

waiting_for_host = True
logger.debug("{0:.3f}     waiting for host".format(time.time() - t0))
announce_waiting = False

while waiting_for_host:
	if announce_waiting:
		logger.debug(
			"{0:.3f}     waiting for host.  Active threads {1}".format(time.time() - t0, threading.enumerate()))
		announce_waiting = False
	old_host_bytes = hostSer.inWaiting()  # we loop until old = new after a defined interval

	if True:
		if not rtuSer.isOpen():
			rtuSer.open()
			logger.error("RtuSer reopened")
		try:
			old_rtu_bytes = rtuSer.inWaiting()
		except Exception as e:
			logger.error('Unexpected OLD-rtubytes serial read error: {} '.format(sys.exc_info() [0]))

	# wait to check the serial port again by either checking the watchdog or sleeping
	if time.time() >= next_watchdog_check:
		watchdog.ping(wdog)
		next_watchdog_check = time.time() + watchdog_check_interval
	else:
		time.sleep(0.1)

	# now check both ports again
	new_host_bytes = hostSer.inWaiting()
	if True:
		# if the rtu is not occupied with another thread, initialize the serial port and count bytes
		if not rtuSer.isOpen():
			rtuSer.open()
			logger.error("RtuSer reopened")
		try:
			new_rtu_bytes = rtuSer.inWaiting()
		except:
			logger.error('Unexpected NEW-rtubytes serial read error: {} '.format(sys.exc_info() [0]))

	# if there are rtu bytes send
	if new_rtu_bytes == old_rtu_bytes and new_rtu_bytes > 0:
		hostSer.write(rtuSer.read(new_rtu_bytes))
	elif new_rtu_bytes == 0:
		# nothing to send, no other activity, so check for pictures and also check for web requests
		if not fetching_pic:
			# we're not currently getting a pic, so check the rtu for pics and also the web interface
			result = read_holding_registers(client, rtuNum, RTU_REG_STATUS, 1)
			# logger.info('result: {}'.format(result))
			if len(result) != 1:
				# RTU status error - log, count etc.
				RTU_status_errors += 1
				if RTU_status_errors < RTU_status_error_limit:
					logger.error('RTU read status register consecutive failure #{}'.format(RTU_status_errors))
				else:
					logger.critical(
						'RTU read status register consecutive failure #{}'.format(RTU_status_errors))
			else:
				# good read.  reset error counter and process the status
				if RTU_status_errors != 0:
					logger.info(
						'RTU read status register consecutive failures ended at {}'.format(RTU_status_errors))
				RTU_status_errors = 0
				if result [0] & AnyAvail:
					logger.info(
						"{0:.3f} image(s) detected. Setting fetching_pic to True".format(time.time() - t0))
					fetching_pic = True
					starting_fetch = True
					announce_waiting = True

			# now check the web listener
			t = web_response.poll(0.1)
			# logger.debug("web incoming poll: {}".format(t))
			if t:  # wait for 100 mS to respond
				# TODO eventually this will comprise a full parser, but for now check the timestamp and pass the parameter along to OD pic
				t = web_response.recv()  # a tuple containing the web request with timestamp
				if (time.time() - t [1]) > 5:  # if the request is more than 5 seconds old it is stale
					logger.error("stale OD request from web.  Request was {}".format(t))
				else:
					logger.info("OD request from web.  Request was {}".format(t))
					# first check rtu status.  if the alarm bit for this camera is set, take action (currently, just flag it)
					rtu_status = check_rtu_status(client, slaveUnit)
					if len(rtu_status) != 0:
						if rtu_status [0] & t [0] << 1:
							logger.error('RTU camera alarm on {}.  Will try anyway'.format(t [0]))
							web_message = (
								"Coldsnap camera alarm detected but will try anyway.  It may be a few minutes for the image to return.  Time: {:%Y-%m-%d %H:%M:%S}".format(
									datetime.datetime.now()), 201)
						else:
							web_message = (
								"Coldsnap alarm detected but will try anyway.  It may be a few minutes for the image to return.  Time: {:%Y-%m-%d %H:%M:%S}".format(
									datetime.datetime.now()), 201)
					else:
						web_message = (
							"Image request sent to Coldsnap.  It may be a few minutes for the image to return.  Time: {:%Y-%m-%d %H:%M:%S}".format(
								datetime.datetime.now()), 201)
					take_od_image(t [0], client)
					web_response.send(web_message)
					announce_waiting = True
			# now service Modbus request queues
			if workQueue.qsize() > 0:
				logger.debug('workQueue items found')
				try:
					queue_request = workQueue.get(block=True, timeout=5)
				except Queue.Empty as e:
					logger.error("weird, workQueue was empty or timed out?")
				else:
					logger.debug('workQueue item received: {}'.format(queue_request))
					# logger.info('workQueue item received'.format(queue_request))
					queue_result = queue_request
					if (queue_request ["start_time"] - time.time()) > 5:
						# the request is old
						logger.error("workQueue was too old :{}".format(queue_request))
					else:
						# perform the request and return the result
						result = queue_request ["function"](*queue_request ["parameters"])
						queue_request ["end_time"] = time.time()
						queue_request ["results"] = result
						try:
							rtu_check_Queue.put(queue_request, block=True, timeout=5)
						except Queue.Empty as e:
							logger.error("rtu_check_Queue was empty?")
						except Queue.Full as e:
							logger.error("rtu_check_Queue was full or timed out?")
						else:
							logger.debug('workQueue result sent'.format(queue_request))
					# request done
					workQueue.task_done()
		# end if not fetching_pic:
		else:
			# fetching pic
			if starting_fetch:
				# new pic
				starting_fetch = False
				photo_start_time = datetime.datetime.now()
				photo = getpics(client, offset=0, maxreads=4)
			else:
				# pic in process
				photo = getpics(client, offset=photo.offset, maxreads=4, photo=photo)
			if photo.error:
				# photo error - try again, right back at the status port
				logger.error("Error fetching image - starting again")
				starting_fetch = True
				fetching_pic = False
			elif photo.complete:
				# we have a photo!  Store it
				logger.info(
					'photo retrieved in {} and stored as {}'.format(datetime.datetime.now() - photo_start_time,
																	photo.filename))
				f = open(os.path.join(photo.filepath, photo.filename), 'wb')
				photo_data = ''.join(photo.image)
				f.write(photo_data)
				f.close()

				# get this photo to be uploaded
				if not image_upload_Queue.full():
					try:
						image_upload_Queue.put(photo, block=True, timeout=1)
					except:
						logger.error(
							"error putting photo into image_upload_Queue: {}".format(sys.exc_info() [0]))

					else:
						logger.debug('Photo successfully enqueued for upload')
				else:
					logger.critical('image_upload_Queue is full!  Will pickle the image file and continue')
				# and pickle it
				picklefile = photo.filename.split('.') [0] + '.pkl'
				if not os.path.exists(pickle_folder_path):
					try:
						os.makedirs(pickle_folder_path)
						os.chmod(pickle_folder_path, stat.S_IRWXU + stat.S_IRGRP + stat.S_IROTH)
					except OSError as exception:
						logger.critical('Failed to create pickle_folder_path directory  Error = {0}'.format(
							exception.errno))

				output = open(os.path.join(pickle_folder_path, picklefile), 'wb')
				# FIXME this should be reversed
				pickle.dump(photo, output, 0)
				# pickle.dump(photo, output, -1)
				output.close()
				logger.debug('photo pickled as {}'.format(output.name))

				# wrap up
				del photo
				fetching_pic = False

			# now service Modbus request queues
			if workQueue.qsize() > 0:
				logger.debug('workQueue items found')
				try:
					queue_request = workQueue.get(block=True, timeout=5)
				except Queue.Empty as e:
					logger.error("weird, workQueue was empty or timed out?")
				else:
					logger.debug('workQueue item received: {}'.format(queue_request))
					# logger.info('workQueue item received'.format(queue_request))
					queue_result = queue_request
					if (queue_request ["start_time"] - time.time()) > 5:
						# the request is old
						logger.error("workQueue was too old :{}".format(queue_request))
					else:
						# perform the request and return the result
						result = queue_request ["function"](*queue_request ["parameters"])
						queue_request ["end_time"] = time.time()
						queue_request ["results"] = result
						try:
							rtu_check_Queue.put(queue_request, block=True, timeout=5)
						except Queue.Empty as e:
							logger.error("rtu_check_Queue was empty?")
						except Queue.Full as e:
							logger.error("rtu_check_Queue was full or timed out?")
						else:
							logger.debug('workQueue result sent'.format(queue_request))
					# request done
					workQueue.task_done()
			t = web_response.poll(0.1)
			# logger.debug("web incoming poll: {}".format(t))
			if t:  # wait for 100 mS to respond
				# TODO eventually this will comprise a full parser, but for now check the timestamp and pass the parameter along to OD pic
				t = web_response.recv()  # a tuple containing the web request with timestamp
				if (time.time() - t [1]) > 5:  # if the request is more than 5 seconds old it is stale
					logger.error("stale OD request from web.  Request was {}".format(t))
				else:
					logger.info("OD request from web.  Request was {}".format(t))
					# first check rtu status.  if the alarm bit for this camera is set, take action (currently, just flag it)
					rtu_status = check_rtu_status(client, slaveUnit)
					if len(rtu_status) != 0:
						if rtu_status [0] & t [0] << 1:
							logger.error('RTU camera alarm on {}.  Will try anyway'.format(t [0]))
							web_message = (
								"Coldsnap camera alarm detected but will try anyway.  It may be a few minutes for the image to return.  Time: {:%Y-%m-%d %H:%M:%S}".format(
									datetime.datetime.now()), 201)
						else:
							web_message = (
								"Coldsnap alarm detected but will try anyway.  It may be a few minutes for the image to return.  Time: {:%Y-%m-%d %H:%M:%S}".format(
									datetime.datetime.now()), 201)
					else:
						web_message = (
							"Image request sent to Coldsnap.  It may be a few minutes for the image to return.  Time: {:%Y-%m-%d %H:%M:%S}".format(
								datetime.datetime.now()), 201)
					take_od_image(t [0], client)
					web_response.send(web_message)
					announce_waiting = True

	# if there are host bytes set the flag to drop out of the loop
	if new_host_bytes == old_host_bytes and new_host_bytes > 0:
		waiting_for_host = False

# host packet timed out = complete so send it if the serial port is available

logging.debug("host poll ready. check to see if RTU port is available")
t0 = time.time()
packet = hostSer.read(new_host_bytes)
try:  # getting occasional port not open errors here - debug and remove
	rtuSer.write(packet)
except:
	logging.debug("Unexpected rtuSer.write error: {}".format(sys.exc_info() [0]))
	logging.debug("Port info : {0} / {1}".format(rtuSer.port, rtuSer.getSettingsDict()))
	pass

msg = ''
for i in range(len(packet)):
	msg += "{:02x}".format(ord(packet [i])) + " "
logger.info("{0:.3f} host pkt sent: {1}".format(time.time() - t0, msg))

# now wait for the guardtime loop to end

start_time = time.time()  # record the starting time
end_time = start_time
old_rtu_bytes = 0
while end_time - start_time < (HostGuardTime / 1000) * 2:  # break loop if guardtimeout or rtu response received
	if not rtuSer.isOpen():
		rtuSer.open()
		logger.error("RtuSer reopened")
	try:
		old_rtu_bytes = rtuSer.inWaiting()  # we loop until old = new after a defined interval
	except:
		logger.error("error while trying to read RTU response into OLDrtubytes: {}".format(sys.exc_info() [0]))
		# logger.error( "Threads: {0}".format(threading.enumerate()))
		# logger.error(traceback.format_exc())
		# logger.error("rtuSer: {}".format(repr(rtuSer)))
		# rtuSer is unexpectedly closed.  Open it and let's see what happens
		if not rtuSer.isOpen():
			rtuSer.open()
			logger.error("rtuSer was closed.  Have tried opening.  result: {}".format(rtuSer.isOpen()))
			if rtuSer.isOpen():  # try again
				old_rtu_bytes = rtuSer.inWaiting()  # we loop until old = new after a defined interval

	logger.debug("{0:.3f} oldrtubytes: {1}  loop length {2:.4f}".format(time.time() - t0, old_rtu_bytes,
																		end_time - start_time))
	time.sleep(0.1)

	# now check port again
	try:
		new_rtu_bytes = rtuSer.inWaiting()
	except:
		logger.error("error while trying to read RTU response into NEWrtubytes: {}".format(sys.exc_info() [0]))
		logger.error("Threads: {0}".format(threading.enumerate()))
		logger.error(traceback.format_exc())
		logger.error("rtuSer: {}".format(repr(rtuSer)))
		if not rtuSer.isOpen():  # rtuSer is unexpectedly closed.  Open it and let's see what happens
			rtuSer.open()
			logger.error("rtuSer was closed.  Have tried opening.  result: {}".format(rtuSer.isOpen()))
			if rtuSer.isOpen():  # try again
				new_rtu_bytes = rtuSer.inWaiting()  # we loop until old = new after a defined interval

	logger.debug("{0:.3f} newrtubytes: {1}".format(time.time() - t0, new_rtu_bytes))
	if (new_rtu_bytes == old_rtu_bytes) and (new_rtu_bytes > 0):
		logger.debug(
			"{0:.3f} newrtubytes == oldrtubytes.  transiting rtu packet and exitting guardtime loop".format(
				time.time() - t0))
		packet = rtuSer.read(new_rtu_bytes)
		msg = "{0:.3f}".format(time.time() - t0)
		msg += " rtu pkt rec'd:"
		for i in range(len(packet)):
			msg += " {:02x}".format(ord(packet [i]))
		hostSer.write(packet)
		logger.info(msg)
		break
	else:
		end_time = time.time()  # advance the timer
		t = web_response.poll(0.1)  # check for web response
		if t:  # we have a web request that we can't respond to
			# TODO eventually this will comprise a full parser, but for now check the timestamp and pass the parameter along to OD pic
			t = web_response.recv()  # a tuple containing the web request with timestamp
			logger.error("OD request from web but system is waiting on RTU response to host.")
			web_response.send((
				"Coldsnap cannot respond to request since it's responding to a host poll. Time: {:%Y-%m-%d %H:%M:%S}".format(
					datetime.datetime.now()), 500))
			announce_waiting = True

else:
	# we timed out of this loop
	logger.error("{0:.3f} hostguard timeout:  loop length {1}".format(time.time() - t0, old_rtu_bytes,
																	  end_time - start_time))
