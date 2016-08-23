#!/usr/bin/env bash
echo "setting backlight to level $1"
echo $1 > /sys/class/backlight/rpi_backlight/brightness

