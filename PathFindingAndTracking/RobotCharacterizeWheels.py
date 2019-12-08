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
# Characterize your wheels.  Measure the variance in
# moving straight and rotation.

filename = input("Enter filename for output for moving straight: ")
f = open(filename,"w+")

for i in range(10):
    robotControl.moveRobotXY(20,0,ser)
    result = robotControl.readResponse(ser)
    time.sleep(1)
    f.write(str(result.obsFlag) + " " + str(result.rightWheelDist) + " " + str(result.leftWheelDist) + " " + str(result.time) + "\n")  # Write to file

f.close()

filename = input("Enter filename for output for rotating: ")
f = open(filename,"w+")

for i in range(10):
    robotControl.rotateRobot(ser,(math.pi))
    result = robotControl.readResponse(ser)
    time.sleep(1)
    f.write(str(result.obsFlag) + " " + str(result.rightWheelDist) + " " + str(result.leftWheelDist) + " " + str(result.time) + "\n")  # Write to file

f.close()
  
# Close Serial Port
ser.close()

print("Done")

