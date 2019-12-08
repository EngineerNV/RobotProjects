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

print(ser)

# 14 September 2018 - Project 0
# Write a program to have the robot drive in a square.

robotControl.moveRobotXY(40,0,ser)
robotControl.rotateRobot(ser,(math.pi))
time.sleep(.5)

robotControl.moveRobotXY(40,0,ser)
robotControl.rotateRobot(ser,(math.pi))
time.sleep(.5)

robotControl.moveRobotXY(40,0,ser)
robotControl.rotateRobot(ser,(math.pi))
time.sleep(.5)

robotControl.moveRobotXY(40,0,ser)
robotControl.rotateRobot(ser,(math.pi))
time.sleep(.5)

# Move robot to X,Y where X is positive
#robotControl.moveRobotXY(10,0,ser)

# Move robot until obstacle seen
#robotControl.moveRobotObs(ser)

# Rotate robot by angleToTurn (0 to 2pi)
#result = robotControl.rotateRobot(ser,math.pi)

# Move robot backward by X
#result = robotControl.moveRobotBackX(ser, 12)

# Read result
# Returns named tuple in the order (obsFlag, v, w, time)
#result = robotControl.readResponse(ser)
#time.sleep(.5)
#print(result.obsFlag, result.rightWheelDist, result.leftWheelDist, result.time)

# Send and read one ir command so that msgType has a value
#robotControl.getSensors(ser)
#result, msgType = robotControl.readResponse(ser)
#time.sleep(.5)
#print(result)
  
# Close Serial Port
ser.close()

print("Done")

