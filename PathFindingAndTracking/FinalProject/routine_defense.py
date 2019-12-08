
#Test function Nicholas Vaughn
# import the necessary packages
from collections import deque
import numpy as np
import argparse
import cv2
import imutils
import time
import math
import PWMrobotControl
import serial
from picamera.array import PiRGBArray
from picamera import PiCamera


# Open Serial Port
ser = serial.Serial("/dev/serial0",115200)

# Initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 600)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 600))

# allow the camera to warmup
time.sleep(0.1)


#boolean function
def detectGoal():
    print("Check for goal!")
    # Initialize frame count
    frame_count = 0
    FRAME_MAX = 5
    RADIUS_MAX = 120
    ##X_MIN = 163
    ##X_MAX = 476
    ##Y_MIN = 150
    ##Y_MAX = 450
    X_MIN = 256
    X_MAX = 384
    Y_MIN = 240
    Y_MAX = 360

    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame_count = frame_count + 1
            # grab the raw NumPy array representing the image, then initialize the timestamp
            # and occupied/unoccupied text
    # resize the frame, blur it, and convert it to the HSV
            # color space
        image = frame.array
        frame_im = imutils.resize(image, width=600)
        blurred = cv2.GaussianBlur(frame_im, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        threshLower = (8,0,8)
        threshUpper = (115,68,98)

            # construct a mask for the color "purple", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
        mask = cv2.inRange(hsv, threshLower, threshUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
##        cv2.imshow("mask",mask)
            
    # find contours in the mask and initialize the current
            # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        center = None

        # only proceed if at least one contour was found else we exit 
        if len(cnts) > 0:
##            ser.close()
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            
            rawCapture.truncate(0)
            return 1
        elif frame_count == FRAME_MAX:
##            ser.close()
            # show the frame
##            cv2.rectangle(image,(X_MIN,Y_MIN),(X_MAX,Y_MAX),(0,255,0),2)
##            cv2.imshow("Frame",image )
                        
            rawCapture.truncate(0)
            return 0
##        if frame_count == FRAME_MAX:
##            frame_count = 0

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

#def aggressive_defense(ser):

#def find_noodle(ser): 
	#if noodle is in center of view
	# go back to routine_defense
	
	#else if noodle is not in center of view but still in view,
	# recenter and then go back to routine_defense
	
	#else if noodle is not in view,
	# move on to aggressive_defense
	
def routine_defense(ser):
    dist = 100
    if detectGoal() == 1:
        time.sleep(2)
        print("Turn left")
        PWMrobotControl.rotateRobot(ser,(math.pi/2))
        time.sleep(1.5)
        print("Move forward dist/2")
        PWMrobotControl.moveRobotXY(ser, int(dist/2), 0)
        time.sleep(2)
        print("Turn 180 degrees")
        PWMrobotControl.rotateRobot(ser,(math.pi))
        time.sleep(1)
        for i in range(5):
            print("Move forward n")
            PWMrobotControl.moveRobotXY(ser,dist,0)
            time.sleep(4)
            print("Rotate 180 degrees")
            PWMrobotControl.rotateRobot(ser,(math.pi))
            time.sleep(1)
            print("Move backwards n")
            PWMrobotControl.moveRobotXY(ser, dist, 0)
            time.sleep(4)
            print("Rotate 180 degrees")
            PWMrobotControl.rotateRobot(ser,(math.pi))
            time.sleep(1.5)
            #go half distance forward to the center and face the noodle
        print("Move forward dist/2")
        PWMrobotControl.moveRobotXY(ser, int(dist/2), 0)
        time.sleep(2)
        print("Turn 90 degrees left")
        PWMrobotControl.rotateRobot(ser,(math.pi/2))
        time.sleep(1.5)
##        while (True):			#routine defense
##            for i in range(5):
##                print("Move forward n")
##                PWMrobotControl.moveRobotXY(ser,dist,0)
##                time.sleep(4)
##                print("Rotate 180 degrees")
##                PWMrobotControl.rotateRobot(ser,(math.pi))
##                time.sleep(1)
##                print("Move backwards n")
##                PWMrobotControl.moveRobotXY(ser, dist, 0)
##                time.sleep(4)
##                print("Rotate 180 degrees")
##                PWMrobotControl.rotateRobot(ser,(math.pi))
##                time.sleep(1)
##                #go half distance forward to the center and face the noodle
##            print("Move forward dist/2")
##            PWMrobotControl.moveRobotXY(ser, int(dist/2), 0)
##            time.sleep(2)
##            print("Turn 90 degrees left")
##            PWMrobotControl.rotateRobot(ser,(math.pi/2))
##            time.sleep(1)

            #find the noodle after routine check
        if not find_noodle(ser):
            aggressive_defense(ser)
                
def main():
    time.sleep(2)
    PWMrobotControl.changePWMvalues(ser, 150, 166)
    PWMrobotControl.moveRobotXY(ser,100,0)
    #routine_defense(ser)
				
		
		
if __name__ == "__main__":
    main()

	