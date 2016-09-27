#!/bin/sh

#
# Install code_venv
#
# this script will install the python services for the notification app
# assumptions:
# - all python files are copied to the pi and are in APP_PATH
# - the python venv is installed inside APP_PATH
# - CLI_PATH is on $PATH and is chosen by the user. this is where the lightmonitor CLI script is stored
# - folder locations for systemd are standard
# - pi is the user
# 
# exit conditions:
# 0 - all good
# 2 - APP_PATH or some of its contents is missing

# check these locations
APP_PATH='/home/pi/pi-notification-app/lightmonitor/'
VENV_PATH=$APP_PATH'venv/'
PIP_PATH=$APP_PATH'venv/bin/pip'
CLI_PATH='/sbin'

#other useful constants
SERVICE_DEF="lightmonitor.service"
SERVICE_DEF_PATH=APP_PATH'service definitions/lightmonitor.service'
COMMAND_SCRIPT="lightmonitor"
COMMAND_SCRIPT_PATH=APP_PATH'commands/lightmonitor'


# move to app folder for the rest of the routine, but exit if it doesn't exist as all its assumptions are wrong
if [ ! -d $APP_PATH ]; then
	echo "ERROR: $APP_PATH folder missing.  I can't continue until it is installed with all its files.  Exitting ..."
    exit 2
else
	echo "$APP_PATH folder found.  Continuing installation"
fi
cd APP_PATH


# Install python libraries required, in a controlled virtualenv
sudo pip install virtualenv
# Check if virtualenv is installed by checking /home/pi/pi-notification-app/lightmonitor/venv
if [ ! -d "venv" ]; then
	# Install virtualenv
	virtualenv -p /usr/bin/python2.7 $VENV_PATH
fi
${PIP_PATH} install Pillow
${PIP_PATH} install flask
${PIP_PATH} install flask-restful
${PIP_PATH} install picamera

# set up the systemd service
if [ ! -e $SERVICE_DEF_PATH ]; then
	echo "ERROR: $SERVICE_DEF_PATH missing.  I can't continue until it is installed.  Exitting ..."
    exit 2
else
	echo "$SERVICE_DEF_PATH found.  Continuing installation"
fi
sudo cp -p $SERVICE_DEF_PATH /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_DEF
sudo systemctl start $SERVICE_DEF
echo "lightmonitor service is running!"

# set up the CLI command script
if [ ! -e $COMMAND_SCRIPT_PATH ]; then
	echo "ERROR: $COMMAND_SCRIPT_PATH missing.  I can't continue until it is installed.  Exitting ..."
    exit 2
else
	echo "$COMMAND_SCRIPT_PATH found.  Continuing installation"
fi
sudo chown  root.root $COMMAND_SCRIPT_PATH
sudo chmod 755 $COMMAND_SCRIPT_PATH
sudo cp -p $COMMAND_SCRIPT_PATH $CLI_PATH


echo ""
echo "Lightmonitor code, resources and libraries are installed"
echo ""
exit 0

