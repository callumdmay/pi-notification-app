#!/usr/bin/env python
# vim: set fileencoding=utf-8
# vim: tabstop=4 shiftwidth=4 softtabstop=4
""" Web service for ambient light measurement """

# core python libraries
###########################################################
from multiprocessing import Process, Pipe, current_process
import os
import stat
import logging
import logging.handlers
import time
import ConfigParser
import sys
import datetime
import threading
import thread
from optparse import OptionParser
import platform
import random
import json

'''
import os
import sys	#Nathan
import stat
import requests
import traceback
import argparse

from threading import Timer

import Queue
import pickle

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
import ftplib
import smtplib
import paramiko
'''

# peripheral libraries
###########################################################
from flask import Flask
from flask import render_template
from flask.ext.restful import reqparse, abort, Api, Resource
from flask import Response
from flask import request
from flask import jsonify

# internal libraries and modules
###########################################################
from config import Configuration

#
# Classes
#



#
# Constants, Global variables and instances
#
App_Name = "Light Monitor"

# folder and file locations
ScriptFolderPath = os.path.dirname(os.path.realpath(__file__))
ScriptFolderName = os.path.realpath(__file__)

# Flask
app = Flask(__name__)
api = Api(app)
CALLBACK_PORT = 5000  # Flask listening port

# configuration
Config = object()
ConfigFilePath = os.path.join(ScriptFolderPath, 'lightmonitor.cfg')
Default_Config_FilePath = os.path.join(ScriptFolderPath, 'default.cfg')

# logging
if 'Windows' in platform.platform():
	Logfolderpath = ScriptFolderPath
else:
	Logfolderpath = "/log/"
Logfilename = 'lightmonitorR.log'

# Misc
t0 = 0  # timer
MONITOR_INTERVAL = 300  # interval in seconds between RTU check-ins


######################################################################################################################


def abort_if_od_id_isnt_valid(od_id):
	# only allow OD1 or OD2
	if od_id != 1 and od_id != 2:
		abort(404, message="On Demand {0} doesn't exist.".format(od_id))


def web_listen(pipe):
	# thread to listen for incoming web requests
	# logger.info('weblistener starting up on process {}'.format(current_process().pid))
	web_incoming, web_response = pipe
	##      app.run(host='0.0.0.0', port=CALLBACK_PORT, threaded=True, debug=False)
	app.run(host='0.0.0.0', port=CALLBACK_PORT, debug=False)


class Camera(Resource):
	def get(self, od_id):
		abort_if_od_id_isnt_valid(od_id)
		response = ("no response from coprocessor after 5 seconds", 500)  # default - no response - internal error 500
		logger.debug("web OD request.")
		# if od_id is valid just put it into the web_listener pipe and wait for a response
		web_incoming.send((od_id, time.time()))  # send the request and timestamp it
		time.sleep(0.1)

		if web_incoming.poll(5):  # wait for five seconds to respond and if response, populate the response information
			response = web_incoming.recv()
		else:
			logger.error("main routine did not respond to incoming web OD request")

		return response [0], response [1]


# setup routings here
api.add_resource(Camera, '/OD<int:od_id>')


@app.route("/")
def hello():
	return "Hello World!"


@app.route("/light")
def light_level():
	camera_ready = random.choice((True, False, True, True, True))
	if camera_ready:
		return "Light level = {}".format(random.randrange(0, 255))
	else:
		return "Camera not ready or not responding"


@app.route("/light_level", methods=['GET', 'POST'])
def get_data():
	if request.method == 'GET':
		camera_ready = random.choice((True, False, True, True, True))
		#camera_ready = True
		if camera_ready:
			data = {"level": random.randrange(0, 255), "histogram": random.randrange(0, 255)}
			js = json.dumps(data)
			resp = Response(js, status=200, mimetype='application/json')
			resp.headers ['Link'] = 'http://evildad.com'
			return resp
		else:
			message = {
				'status': 404,
				'message': 'Camera not responding or not available'.format(request.json),
			}
			resp = jsonify(message)
			resp.status_code = 404
			return resp
	if request.method == 'POST':
		if 'backlight_level' in request.json:
			pass  # TODO set the actual backlight level
			backlight_set = random.choice((True, False, False, False, True))
			if backlight_set:
				return 'backlight level set to {}! \n'.format(request.json ['backlight_level'])
			else:
				system_error_message = "stop bugging me!"
				message = {
					'status': 404,
					'message': 'Backlight level set failed.  Information from system: {}'.format(system_error_message),
				}
				resp = jsonify(message)
				resp.status_code = 404
				return resp
		else:
			message = {
				'status': 404,
				'message': 'No backlight level request found in {}'.format(request.json),
			}
			resp = jsonify(message)
			resp.status_code = 404
			return resp


def set_up_logging(loglvl, console_logging_enabled):
	# set up logging
	logger = logging.getLogger('')
	logger.setLevel(loglvl)
	# modules

	# add a rotating loghandler.  it will log to DEBUG or INFO
	# if the directory doesn't exist, create it
	if not os.path.exists(Logfolderpath):
		try:
			os.makedirs(Logfolderpath)
			os.chmod(Logfolderpath, stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH)
		except OSError as exception:
			logger.critical('Failed to create Log folder root directory  Error = {0}'.format(exception.errno))

	Rotations = 20
	rotatelogh = logging.handlers.RotatingFileHandler(Logfolderpath + '/' + Logfilename, mode='a', maxBytes=1000000,
													  backupCount=Rotations, encoding=None, delay=0)
	rotatelogh.setLevel(logging.DEBUG if loglvl == logging.DEBUG else logging.INFO)

	formatter = logging.Formatter('%(asctime)s\t%(threadName)s\t%(funcName)s:%(lineno)d\t%(levelname)s\t%(message)s')
	# tell the handler to use this format and add to root handler
	rotatelogh.setFormatter(formatter)
	logger.addHandler(rotatelogh)

	# now add a console logger if  enabled
	if console_logging_enabled:
		# define a Handler which writes INFO messages or higher to the sys.stderr
		console = logging.StreamHandler()
		console.setLevel(loglvl)
		# set a format which is simpler for console use
		if options.service:
			formatter = logging.Formatter('%(lineno)-5d %(levelname)-8s %(message)s')
		else:
			formatter = logging.Formatter('%(asctime)s %(funcName)-16s:%(lineno)-5d %(levelname)-8s %(message)s')
		# tell the handler to use this format
		console.setFormatter(formatter)
		# add the handler to the root logger
		logger.addHandler(console)

	## logger.addHandler(t)

	##        # set up  filters
	##        console.addFilter(NomodbusFilter())
	##        logger.addFilter(NomodbusFilter())
	else:
		# logging disabled so add log it
		logger.info("Console logging disabled")

	# modules
	t = logging.getLogger('requests.packages.urllib3.connectionpool')
	t.setLevel(logging.WARNING)

	return logger


def build_parse_options():
	# parse the command line
	parser = OptionParser()

	# logging
	parser.add_option("--noconsolelog", action='store_false', dest="console_logging_enabled", default=True,
					  help="Turn console logging OFF (default = on)")  # log flag
	parser.add_option("-I", '--info', dest='loglvl', action='store_const', const=logging.INFO, default=logging.INFO,
					  help="Log Info and higher i.e. no DEBUG (this is the default)")
	parser.add_option("-W", '--warning', dest='loglvl', action='store_const', const=logging.WARNING,
					  default=logging.INFO,
					  help="Log Warning and higher.  Default = INFO")
	parser.add_option("-D", '--debug', dest='loglvl', action='store_const', const=logging.DEBUG, default=logging.INFO,
					  help="Log Debug and higher i.e. EVERYTHING.  Default = INFO")
	parser.add_option("-C", '--critical', dest='loglvl', action='store_const', const=logging.CRITICAL,
					  default=logging.INFO,
					  help="Log Critical and higher.  Default = INFO")

	# test related parameters
	parser.add_option("-t", '--test', action="store_true", dest='TestMode', default=False,
					  help='TestMode. A flag to enable the system can behave differently for test purposes')
	parser.add_option("--loop", type="int", dest="loop", default=1,
					  help="Repeat or loop the test this quantity (default = 1)")
	parser.add_option("-d", "--delay", type="float", dest="delay", default=5,
					  help="Delay between tests in minutes.  default = 5 minutes")
	parser.add_option("-R", "--run_constantly", action='store_true', dest="run_constantly", default=False,
					  help="Monitor constantly i.e. loop tests forever (default = False, only test for --loop loops")
	parser.add_option('--noservice', action="store_false", dest='service', default=True,
					  help='Run as an app, not service. Default = no, run as service')
	parser.add_option('--systemconfig', action="store_true", dest='system_config', default=False,
					  help='Use Coldsnap system configuration. Default = no, use command line parameters')

	# test targets and options
	parser.add_option("--ping-target", type="str", dest="ping_target", default="8.8.8.8",
					  help="Network target to ping (default = 8.8.8.8 - google).  Try goaglo.com for a forced failure")
	parser.add_option("--no-ping", action='store_false', dest="ping_enabled", default=True,
					  help="do *NOT* ping (default = *DO* ping)")
	parser.add_option("--no-modem", action='store_false', dest="modem_enabled", default=True,
					  help="do *NOT* check the modem (default = *DO* check modem)")

	(options, args) = parser.parse_args()

	return (options)


if __name__ == '__main__':
	""" main loop """

	global options, Config, logger

	# set up options and read off command line
	options = build_parse_options()

	# set up logging
	logger = set_up_logging(options.loglvl, options.console_logging_enabled)

	#
	#       configuration
	#

	# config main, then modules.  initialize config error to False
	Config = Configuration(Default_Config_FilePath)
	logger.debug("Loading system config file from file: " + ConfigFilePath)

	Config.load(ConfigFilePath)

	# # now exit the application if there have been any errors
	# if Config.configError:
	# 	logger.critical(
	# 		"Configuration errors encountered.  It's not safe to continue.  Please check the logs and all the config files, both input and written by the system")
	# 	sys.exit(1)
	#
	# test mode modifications
	#
	if options.TestMode:
		pass

	logger.info('{2} app starting up,  filename: {0} modified {1}'.format(ScriptFolderName, time.ctime(
		os.path.getmtime(ScriptFolderName)), App_Name))
	logger.info('Options:{0}'.format(options))  # record the options as set
	logger.info('logging level: {0} ({1})'.format(options.loglvl, logging.getLevelName(options.loglvl)))

	#
	# set up hardware
	#


	#
	#       Threads and processes
	#

	# set up multiprocessing for web listener
	web_incoming, web_response = Pipe()
	if Config.Web.enabled:
		web_listener = Process(target=web_listen, args=((web_incoming, web_response),), name='WebListn')
		web_listener.start()
		logger.debug('web_listener process started.  main process is {}'.format(current_process().pid))
	else:
		logger.info('Web Listener *not started* since it was not enabled')

	# other threads

	#
	# ##########################     main loop
	#
	random.seed()

	while True:
		pass

	# end while True
