#!/usr/bin/env bash
#turn the backlight on
echo 0 > /sys/class/backlight/rpi_backlight/bl_power
#set the backlight to brightness $1
echo $1 > /sys/class/backlight/rpi_backlight/brightness


