#!/bin/sh
sudo chmod 666 /dev/parport0
sudo rmmod lp
sudo modprobe parport
