# Created By Nicholas Vaughn
'''''
This was created for actions that the Robot needs to perform
such as movement or checking. This will reduce repeating code 
'''

'''
from collections import deque
import numpy as np
import argparse
import cv2
import imutils
import time
import math
import robotControl
from picamera.array import PiRGBArray
from picamera import PiCamera
'''
#initializing movement files
import robotControl
import serial
import math
import robotConstants
import time
import CaptureTheFlag_Offense as cap
# 0. Open Serial Port
ser = serial.Serial("/dev/serial0",115200)
pi = math.pi

#Constants for conversion
LXD = robotConstants.LX
MXD = robotConstants.MX
RXD = robotConstants.RX

#Adjustments to the robot
robotControl.changeSensorThreshold(ser, 9000, 1500, 9000)
time.sleep(0.5)
robotControl.changePWMvalues(ser, 160, 125)
time.sleep(0.5)

#fill in and take out passes 
import time
def turnL():
	robotControl.rotateRobot(ser, pi/2)
	results, msgType = robotControl.readResponse(ser)
	return results
def turnR():
	robotControl.rotateRobot(ser, (pi+(pi/2)))
	results, msgType = robotControl.readResponse(ser)
	return results
def turnBack():
	robotControl.rotateRobot(ser, pi)
	results, msgType = robotControl.readResponse(ser)
	return results
def moveFWD():
	robotControl.moveRobotXY(10,0,ser)
	results, msgType = robotControl.readResponse(ser)
	return results

def moveBWD():
	robotControl.moveRobotXY(-10,0,ser)
	results, msgType = robotControl.readResponse(ser)
	
def check_goal_180():	
    
    for x in range(0,8): #performing 180 checks
        robotControl.rotateRobot(ser, pi+pi/8)
        results, msgType = robotControl.readResponse(ser)
        tracked = cap.see_obj()
        grabGoal = cap.haveNood()
    	
        if grabGoal or tracked:
           return (grabGoal,tracked)
        time.sleep(.25)
    #checking Goes here
    #add break for when we chase an object 
    turnL()
    turnL()
    return (0,0)
def check_end(): #if we see our end flag we chase it
    for x in range(0,2): #performing 180 checks 
        robotControl.rotateRobot(ser, pi+pi/8)
        results, msgType = robotControl.readResponse(ser)
        tracked = cap.see_obj()
        grabGoal = cap.areWeHome()
        if grabGoal or tracked:
            return (grabGoal,tracked)
    time.sleep(.2)
    robotControl.rotateRobot(ser, pi/4)
    results, msgType = robotControl.readResponse(ser)
    return (0,0)
def getSensors():
    time.sleep(0.5)
    robotControl.getSensors(ser)
    sensors, msgType = robotControl.readResponse(ser)
    #print (sensors)
    #print("We here we here: ")

    if msgType == 3:
        #print(sensors)
        DLS = int(LXD[0]*sensors[0]**5 + LXD[1]*sensors[0]**4 + LXD[2]*sensors[0]**3 + LXD[3]*sensors[0]**2 + LXD[4]*sensors[0] + LXD[5])
        DMS = int(MXD[0]*sensors[1]**5 + MXD[1]*sensors[1]**4 + MXD[2]*sensors[1]**3 + MXD[3]*sensors[1]**2 + MXD[4]*sensors[1] + MXD[5])
        DRS = int(RXD[0]*sensors[2]**5 + RXD[1]*sensors[2]**4 + RXD[2]*sensors[2]**3 + RXD[3]*sensors[2]**2 + RXD[4]*sensors[2] + RXD[5])
        print(DLS,DMS,DRS)
        #convert to bools 
        
        if DLS > 15:
            DLS = 0
        else:
            DLS = 1
        if DMS > 12:
            DMS = 0
        else:
            DMS = 1
        if DRS > 12:
            DRS = 0
        else:
            DRS = 1
        return(DLS,DMS,DRS)
    else:
        L,M,R = range_sensor_values()

def reverseTurnList(t_list):
    pass 		
def sendGoalMsg():
    pass

#robotControl.changePWMvalues(ser,160,125)
#time.sleep(.5)
#robotControl.changeSensorThreshold(ser,0)
#time.sleep(.5)
#while 1:
#	print('180')
# 	res =   turnBack()
#        print('rightWheel:'+str(res.rightWheelDist)+' Left Wheel:' + str(res.leftWheelDist))
#	time.sleep(1)
#	print('Booleans'+str(getSensors()))
	#print('Right')
        #res =   turnR()
        #print('rightWheel:'+str(res.rightWheelDist)+' Left Wheel:' + str(res.leftWheelDist))
        #time.sleep(1)
