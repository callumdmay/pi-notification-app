#!/usr/bin/env python
# vim: set fileencoding=utf-8
# vim: tabstop=4 shiftwidth=4 softtabstop=4
""" Web service for ambient light measurement """

# core python libraries
###########################################################
from multiprocessing import Process, Pipe, current_process
import threading
import os
import stat
import logging
import logging.handlers
import time
import pickle
import datetime
import threading
from optparse import OptionParser
import platform
import random
import json
import atexit


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
from PIL import Image
if 'Windows' not in platform.platform():
	import picamera
	from picamera import PiCamera
# internal libraries and modules
###########################################################
from config import Configuration

#
# Classes
#
class Camera(PiCamera):
	"""picamera subclassed to add some extra functionality"""
	def __init__(self, config = None):
		"""add a config constructor"""
		PiCamera.__init__(self)
		if config:
			self.config(config)

	def config(self,config):
		"""configure the camera with parameters passed in a dict"""
		for parameter, value in config.__dict__.iteritems():
			# print parameter, value
			setattr(self, parameter, value)


class PythonObjectEncoder(json.JSONEncoder):
	"""a subclass workaround for unsupported JSON objects.  provides readable text"""
	def default(self, obj):
		logger.info("PythonObjectEncoder reports: {} is type {}".format(str(obj), type(obj)))
		if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
			return json.JSONEncoder.default(self, obj)
		return ({'_python_object': str(type(obj)) + ":" + str(obj)})

#
# Constants, Global variables and instances
#
App_Name = "Light Monitor"
logger = object()
options = object()
Config = object()

# folder and file locations
ScriptFolderPath = os.path.dirname(os.path.realpath(__file__))
ScriptFilePath = os.path.realpath(__file__)
ImageFolderPath = os.path.join(ScriptFolderPath, 'static', 'images')
LastImagePath = os.path.join(ImageFolderPath, 'last.jpg')

# Flask
#app = Flask(__name__)
#api = Api(app)
CALLBACK_PORT = 5000  # Flask listening port

# configuration filepaths
ConfigFilePath = os.path.join(ScriptFolderPath, 'lightmonitor.cfg')
Default_Config_FilePath = os.path.join(ScriptFolderPath, 'default.cfg')

# logging
if 'Windows' in platform.platform():
	Logfolderpath = ScriptFolderPath
else:
	Logfolderpath = "/log/"
Logfilename = 'lightmonitorR.log'

# Misc
CONFIG_INTERVAL = 300  # interval in seconds between config checks


######################################################################################################################



# def web_listen(pipe, options):
# 	# thread to listen for incoming web requests
# 	if 'Windows' in platform.platform():
# 		logger = set_up_logging(options)
# 	else:
# 		logger = logging.getLogger()
# 	logger.info('webservice starting up on process {}'.format(current_process().pid))
# 	web_incoming, web_response = pipe
# 	##      app.run(host='0.0.0.0', port=CALLBACK_PORT, threaded=True, debug=False)
# 	app.run(host='0.0.0.0', port=CALLBACK_PORT, debug=False)


def measure_light(image):
	""""take an image and return an integer estimating its overall brightness"""
	im = Image.open(image, 'r')
	list_of_bins = im.histogram()
	logger.info("Image : {}".format(str(image), list_of_bins))
	logger.debug("Image {} histogram results: {}".format(str(image), list_of_bins))
	# iter_list = iter(list_of_bins)
	# R_offset = 0
	# G_offset = 256
	# B_offset = 512
	colours = "red", "green", "blue"
	colour_totals = dict.fromkeys((key for key in colours),0)
	colour_intensities = colour_totals.copy()
	colour_brightness = colour_totals.copy()
	colour_darkness = dict.fromkeys((key for key in colours),255)
	colour_lightness = colour_totals.copy()
	total_pixels = colour_totals.copy()
	overall_average = 0
	for brightness in range(0,255):
		# colour_totals["red"] += list_of_bins[brightness] * brightness
		# colour_totals ["green"] += list_of_bins[brightness+256] * brightness
		# colour_totals ["blue"] += list_of_bins[brightness+512] * brightness
		for i,key in enumerate(colours):
			total_pixels[key] += list_of_bins[(i)*256 + brightness]
			colour_totals [key] += list_of_bins[(i)*256 + brightness] * brightness
			# if there are pixels at this brightness, see if they are the lightest or darkest
			if list_of_bins[(i)*256 + brightness] > 0:
				if colour_darkness[key] > brightness:
					colour_darkness[key] = brightness
				if colour_brightness[key] < brightness:
					colour_brightness[key] = brightness
	for key in colour_totals:
		colour_intensities[key] = float(colour_totals[key])/float(total_pixels[key])
		overall_average += float(colour_intensities[key])/3.0
		colour_lightness[key] = sum([colour_brightness[key], colour_darkness[key]])/len([colour_brightness[key], colour_lightness[key]])

	logger.info("Measure light results.  Colour totals - {}".format(colour_totals))
	logger.info("Measure light results.  Total pixels - {}".format(total_pixels))
	logger.info("Measure light results.  Colour lightness - {}".format(colour_lightness))
	logger.info("Measure light results.  Colour brightness - {}".format(colour_brightness))
	logger.info("Measure light results.  Colour intensity - {}".format(colour_intensities))
	logger.info("Measure light results.  Overall intensity - {:.1f}".format(overall_average))

	return{"rgb lightness":colour_lightness, "rgb brightness": colour_brightness, "rgb intensity": colour_intensities, "overall intensity": overall_average}


def take_picture(image_filename):
	"""
	take a picture and put it in filename.  set up camera according Config
	return a dict of camera params.  The calling routine is to manage PiCamera exceptions
	"""
	if Config.Camera_Light_Measurement.mode == "fixed":
		cam = Camera(Config.Camera_fixed)
	else:
		cam = PiCamera()
	filename = os.path.join(ScriptFolderPath, 'static', 'images', image_filename)
	logger.info("taking picture - {}".format(filename))
	with cam:
		cam.start_preview()
		time.sleep(2)
		cam.capture(filename)
		for prop in dir(cam):
			try:
				if prop.startswith("_") or "method" in str(getattr(cam, prop)):
					continue
				print('Attribute|{}|Value |{}'.format(prop, str(getattr(cam, prop))))
			except Exception as e:
				print('Attribute|{}|Error, |{}'.format(prop, e))
		# capture some key camera params in a dict
		camera_params = dict(measure_mode=Config.Camera_Light_Measurement.mode, awb_gains=cam.awb_gains,
							 awb_mode=cam.awb_mode, iso=cam.iso,
							 meter_mode=cam.meter_mode, exposure_speed=cam.exposure_speed,
							 resolution=cam.resolution, analog_gain=cam.analog_gain)
	return camera_params


def print_camera_defaults():
	"""dump the camera object attributes to stdout"""
	cam = picamera.PiCamera()
	for prop in dir(cam):
		try:
			print('Attribute|{}|Value |{}'.format(prop, str(getattr(cam, prop))))
		except Exception as e:
			print('Attribute|{}|Error, |{}'.format(prop, e))


def create_app():
	app = Flask(__name__)

	@app.route("/")
	def hello():
		return "Hello World!"


	@app.route("/light_level")
	def light_level():
		""" measure ambient by taking a pic, analyzing it and returning it as JSON """
		filename = 'last.jpg'
		try:
			camera_params = take_picture(filename)
			light_level = measure_light(os.path.join(ScriptFolderPath, 'static', 'images', filename))
			light_level['camera_info'] = camera_params
		except Exception as e:
			message = {
				'status': 404,
				'message': 'Errors getting light level.  Details: {}'.format(e),
			}
			resp = jsonify(message)
			resp.status_code = 404
			return resp
		js = json.dumps(light_level, cls=PythonObjectEncoder)
		resp = Response(js, status=200, mimetype='application/json')
		resp.headers ['Link'] = 'http://evildad.com'
		return resp


	@app.route("/backlight", methods=['GET', 'POST'])
	def get_set_backlight():
		if request.method == 'GET':
			camera_ready = random.choice((True, False, True, True, True))
			#camera_ready = True
			if camera_ready:
				filename = 'last.jpg'
				try:
					camera_params = take_picture(filename)
					image_to_analyze = os.path.join(ImageFolderPath, filename)
					light_level = measure_light(os.path.join(ScriptFolderPath, 'static', 'images', filename))
					light_level['camera_info'] = camera_params
				except Exception as e:
					return "Sorry, there's something wrong with the camera.  Here's what I have: {}".format(e), 404
				data = {"level": random.randrange(0, 255), "histogram": random.randrange(0, 255)}
				js = json.dumps(light_level, cls=PythonObjectEncoder)
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


	@app.route("/image", methods=['GET'])
	def analyze_image():
		# this is a request to analyze an image.  We need to figure out which and then analyze it.  There can be a request
		# for a specific file or 'check' which means take a picture and then analyze it
		requested_image = request.args.get('image', 'current')
		camera_params = None
		if requested_image == "now":
			filename = 'check.jpg'
			try:
				camera_params = take_picture(filename)
				image_to_analyze = os.path.join(ImageFolderPath, filename)
			except Exception as e:
				return "Sorry, there's something wrong with the camera.  Here's what I have: {}".format(e), 404
		elif requested_image == "current":
			# analyze the last picture taken
			image_to_analyze = LastImagePath
		else:
			# we're looking for an existing image.  make sure it exists
			image_file_path = os.path.join(ImageFolderPath, requested_image)
			if os.path.exists(image_file_path):
				image_to_analyze = image_file_path
			else:
				message = {
					'status': 404,
					'message': "Sorry, can't find the image named {}".format(requested_image),
				}
				resp = jsonify(message)
				resp.status_code = 404
				return "Sorry, can't find the image named {}".format(requested_image), 404
		image_analysis_data = measure_light(image_to_analyze)
		# now populate the graph information.  We are showing lightness, brightness and intensity
		colours = ("red", "blue", "green")
		c_tla = tuple("rgb")
		parameters = ("lightness", "brightness", "intensity")
		values = []
		labels = []
		for parameter in parameters:
			for i, colour in enumerate(colours):
				labels.append(parameter + "-" + c_tla [i])
				values.append(image_analysis_data ["rgb " + parameter] [colour])
		labels.append("overall intensity")
		values.append(image_analysis_data ["overall intensity"])

		# now populate the camera information TODO finish this routine
		if camera_params:
			logger.info('Here is the camera info that should go into the webpage: {}'.format(camera_params))

		image = 'images/' + os.path.basename(image_to_analyze)
		return render_template('image_summary.html', values=values, labels=labels, image=image,
							   file=os.path.basename(image_to_analyze))

	def interrupt():
		global yourThread
		yourThread.cancel()

	def doStuff():
		global Config
		global yourThread
		with dataLock:
			# Do your stuff with commonDataStruct Here
			logger.info('rereading config file looking for changes - thread {}'.format(threading.current_thread().name))
			Config = Configuration(Default_Config_FilePath)
			logger.debug("Loading system config file from file: " + ConfigFilePath)
			Config.load(ConfigFilePath)

		# Set the next thread to happen
		yourThread = threading.Timer(CONFIG_INTERVAL, doStuff, ())
		yourThread.start()

	def doStuffStart():
		# Do initialisation stuff here
		global yourThread
		# Create your thread
		yourThread = threading.Timer(CONFIG_INTERVAL, doStuff, ())
		yourThread.start()

	# Initiate
	doStuffStart()
	# When you kill Flask (SIGTERM), clear the trigger for the next thread
	atexit.register(interrupt)
	return app


def set_up_logging(options):
	# set up logging
	global logger
	logger = logging.getLogger('')
	logger.setLevel(options.loglvl)
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
	rotatelogh.setLevel(logging.DEBUG if options.loglvl == logging.DEBUG else logging.INFO)

	formatter = logging.Formatter('%(asctime)s\t%(threadName)s\t%(funcName)s:%(lineno)d\t%(levelname)s\t%(message)s')
	# tell the handler to use this format and add to root handler
	rotatelogh.setFormatter(formatter)
	logger.addHandler(rotatelogh)

	# now add a console logger if  enabled
	if options.console_logging_enabled:
		# define a Handler which writes INFO messages or higher to the sys.stderr
		console = logging.StreamHandler()
		console.setLevel(options.loglvl)
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

	#global options, Config, logger

	# set up options and read off command line
	options = build_parse_options()

	# set up logging
	logger = set_up_logging(options)

	logger.info('{2} app starting up,  filename: {0} modified {1}'.format(ScriptFilePath, time.ctime(
		os.path.getmtime(ScriptFilePath)), App_Name))
	logger.info('Options:{0}'.format(options))  # record the options as set
	logger.info('logging level: {0} ({1})'.format(options.loglvl, logging.getLevelName(options.loglvl)))

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
		CONFIG_INTERVAL = 10 #shorten config interval for testing

		filename = 'check.jpg'
		logger.info("taking picture - {}".format(filename))
		camera_params = take_picture(filename)
		light_level = measure_light(os.path.join(ScriptFolderPath, 'static', 'images', filename))
		light_level['camera_info'] = camera_params
		logger.info("summary for image - {} - {}".format(filename, light_level))

		# if Config.Camera_Light_Measurement.mode == "fixed":
		# 	cam = Camera(Config.Camera_fixed)
		# else:
		# 	cam = PiCamera()
		#
		# with cam:
		# 	cam.start_preview()
		# 	time.sleep(2)
		# 	cam.capture(filename)
		# 	for prop in dir(cam):
		# 		try:
		# 			if prop.startswith("_") or "method" in str(getattr(cam, prop)):
		# 				continue
		# 			print('Attribute|{}|Value |{}'.format(prop, str(getattr(cam, prop))))
		# 		except Exception as e:
		# 			print('Attribute|{}|Error, |{}'.format(prop, e))
		# 	# capture some key camera params in a dict
		# 	camera_params = dict(measure_mode = Config.Camera_Light_Measurement.mode, awb_gains = cam.awb_gains,
		# 						 awb_mode = cam.awb_mode,iso = cam.iso,
		# 						 meter_mode=cam.meter_mode, exposure_speed=cam.exposure_speed,
		# 						 resolution=cam.resolution, analog_gain=cam.analog_gain)
		# logger.info("analyzing image - {}".format(filename))
		# light_level = measure_light(filename)
		# # add camera params
		# light_level['camera_info'] = camera_params
		# logger.info("summary for image - {} - {}".format(filename, light_level))
		#sys.exit(0)

		# filename = os.path.join(ScriptFolderPath, 'static', 'images', 'test.jpg')
		# logger.info("analyzing image - {}".format(filename))
		# light_level = measure_light(filename)
		# logger.info("summary for image - {} - {}".format(filename, light_level))
		# #sys.exit(0)
		#
		# for i in range(1,10):
		# 	filename =os.path.join(ScriptFolderPath, 'static', 'images', 'image{}.jpg'.format(i))
		# 	logger.info("analyzing image - {}".format(filename))
		# 	light_level = measure_light(filename)
		# 	logger.info("summary for image - image{}.jpg - {}".format(i,light_level))
		# sys.exit(0)


	#
	# set up hardware
	#


	#
	#       Threads and processes
	#

	# lock to control access to variable
	dataLock = threading.Lock()
	# thread handler
	yourThread = threading.Thread()

	app = create_app()
	app.run(host='0.0.0.0', port=CALLBACK_PORT, debug=False)

