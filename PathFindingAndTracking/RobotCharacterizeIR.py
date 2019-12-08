#******************************************************
 # Robotics Interface code
 # 
 # Connects the raspberry pi to a microcontroller via
 # the serial port.  Defines a set of functions for
 # controlling the robot movement, measuring sensors,
 # and configuring parameters
 #
 # Author: Elizabeth Basha
 # Date: Fall 2018
 #*****************************************************
#! /usr/bin/env python

import math
import robotControl
import serial
import time

print("Starting")

# Open Serial Port
ser = serial.Serial("/dev/serial0",115200)

# 17 September 2018 - Project 0
# Characterize your IR sensors. Measure different
# distances multiple times; determine the relationship
# between ADC and distance as well as the variance in
# your sensor measurements.

#filename = input("Enter filename for output: ")
#f = open(filename,"w+")

for i in range(10):
    robotControl.getSensors(ser)
    result, msgType = robotControl.readResponse(ser)
    time.sleep(1)
    #f.write(str(result[0]) + " " + str(result[1]) + " " + str(result[2]) + "\n")  # Write to file

#f.close()
  
# Close Serial Port
ser.close()

print("Done")

