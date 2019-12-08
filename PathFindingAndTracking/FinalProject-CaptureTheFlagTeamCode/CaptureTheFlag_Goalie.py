import cv2
import io
import sys
import math
#import robotControl
import robotControl
import serial
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import picamera
import random
import goalie_bail as bail

width = 640
height = 480
camera = PiCamera()
camera.resolution = (width,height)
#camera.framerate = 32
#camera.rotation = 180
rawCapture = PiRGBArray(camera, size=(640,480))
time.sleep(0.1)
im_cen_x = int(math.floor(width/2))
im_cen_y = int(math.floor(height/2))
im_cen = (im_cen_x,im_cen_y)
stream = io.BytesIO()
found = False
fails = 0
turn_angles = [math.pi/2, math.pi/4, 0, math.pi + math.pi/4, math.pi + math.pi/2]
#camera.start_preview()
#time.sleep(0.2)
#camera.stop_preview()

#Color definitions:
#Our Object
lower_red = [0, 104, 104]#[4, 150, 101]
upper_red =[180, 172, 203] #[17, 220, 222]
red_nood = [(lower_red,upper_red)]
#Our Goal
lower_goal = [43, 83, 0]
upper_goal = [69, 255, 255]
blue_goal = [(lower_goal,upper_goal)]
#Blue Object
lower_blue = [85, 100, 61]#[76, 29, 47]#[63, 189, 88]
upper_blue = [97, 211, 156] #[93, 201, 179]#[83, 209, 180]
blue_nood = [(lower_blue,upper_blue)]

#Purple Object
lower_purp = [107, 87, 95]#[100, 51, 66]#[0, 0, 70]
upper_purp = [127, 145, 199] #[132, 255, 182]#[180, 41, 158]
purp_nood = [(lower_purp,upper_purp)]

###################################################################
##GLOBAL CHANGES: CHANGE GLOBAL TO WHICH COLOR YOU ARE GUARDING####
###################################################################
global search_for
search_for = blue_nood

ser = serial.Serial("/dev/serial0",115200)
bail = bail.Bail("attacker")


def see_obj():
	trackfail = False
	##    camera.start_preview()
	##    time.sleep(0.2)
	with picamera.array.PiRGBArray(camera) as stream:
		camera.capture(stream, format='bgr')
		image = stream.array
##    camera.stop_preview()
	image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
##    cv2.imwrite("/home/pi/Desktop/Frame.jpg", image)
	# Define an initial bounding box
	for (lower,upper) in search_for:
		lower = np.array(lower, dtype = "uint8")
		upper = np.array(upper, dtype = "uint8")
		mask = cv2.inRange(image, lower, upper)
		output = cv2.bitwise_and(image, image, mask = mask)    
	rawCapture.truncate()
	#Object in center of vision
	print("Frame: " + str(image[im_cen_y,im_cen_x,2]))
	print("Output: " + str(output[im_cen_y,im_cen_x,2]))
	nest_break = False
	gotEm = False
	for i in range(0,width,10):
		for j in range(int(height*0.25),int(height),10):
			if output[j,i,2] > 0:
				print("found while turning")
				print("i = " + str(i))
				print("j = " + str(j))
				gotEm = True
				fails = 0
				nest_break = True
				break
		if nest_break == True:
			break
	if gotEm == True:
		#tracking(False) #i don't think we need to track track. just need to see if it is in the frame
		trackfail = True
	print("Definitely back to main")
	if trackfail == True:
		return True
	else:
		return False

def lost_it():
	robotControl.moveRobotXY(55, 0, ser) #straight movement
	time.sleep(.5)
	robotControl.rotateRobot(ser,math.pi+math.pi/2)#corner turn
	time.sleep(.5)
	robotControl.moveRobotXY(20, 0, ser) #straight movement
	time.sleep(.5)
	robotControl.rotateRobot(ser,math.pi+math.pi/2)#corner turn
	time.sleep(.5)

def robot_run():
	#basically want to circle while keeping noodle at edge of sensors
	#option1: make a square around the noodle. at every corner, turn towards the
	#		  middle to make sure that the noodle is still there. If yes, then
	#		  keep drawing the square. If no, then...
	#ROBOT PLACEMENT: Start robot at bottom right corner so that 
	#the noodle is on the left side of the robot
	#initial check
	robotControl.rotateRobot(ser,math.pi+math.pi/4) #turn to look at center
	noodle_here = False
	is_taken = False
	time.sleep(1)
	noodle_here = see_obj()
	time.sleep(.5)
	if not noodle_here:
		print("Opsie, they took It T-T")
		is_taken = True
		bail.bail_out()
		time.sleep(.5)
		print("Goalie finished screaming and feels a little better")
		#robotControl.moveRobotXY(55, 0, ser)
		#time.sleep(1)
	elif noodle_here:
		print("Cool beans, It is still here")
	robotControl.rotateRobot(ser,math.pi/4)#turn back to normal course
	time.sleep(.5)
	while not is_taken:
		robotControl.moveRobotXY(35, 0, ser) #straight movement
		time.sleep(1)
		robotControl.rotateRobot(ser,math.pi+math.pi/2)#corner turn
		time.sleep(1)
		robotControl.rotateRobot(ser,math.pi+math.pi/4) #turn to look at center
		time.sleep(1)
		#at this point, check if noodle is still in the middle. if it is, run off in the distance;
		#else if it is still there then continue to patrol
		noodle_here = see_obj()
		if not noodle_here:
			print("Opsie, they took It T-T")
			is_taken = True
			bail.bail_out()
			print("Goalie finished screaming and feels a little better")
			#robotControl.moveRobotXY(50, 0, ser)
			#time.sleep(1)
		elif noodle_here:
			print("Cool beans, It is still here")
		
		robotControl.rotateRobot(ser,math.pi/4)#turn back to normal course
		time.sleep(1)
	while is_taken:
		lost_it()
	

def main():
	robotControl.changeSensorThreshold(ser, 7000, 7000, 7000) #i think it's left, middle, right. 1500 for each is most sensitive, the higher the number, the less sensitive it becomes
	robot_run()
	# Close Serial Port
	ser.close()
	
main()
	
