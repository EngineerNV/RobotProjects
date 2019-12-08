
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
        # PURPLE
        threshLower = (8,0,8)
        threshUpper = (115,68,98)
        # RED
##        threshLower = (0, 0, 109)
##        threshUpper = (13, 245, 185)

            # construct a mask for the color "blue", then perform
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
##            cv2.circle(image, (int(x), int(y)), int(radius),(0, 255, 255), 2)
##            cv2.circle(image, center, 5, (0, 0, 255), -1)
            
            # show the frame
##            cv2.rectangle(image,(X_MIN,Y_MIN),(X_MAX,Y_MAX),(0,255,0),2)
##            cv2.imshow("Frame",image )
                        
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
        
##    ser.close()
##    camera.close()


#this is the algorithm that will actually run the tracking and return the list of movements 
def trackingAlg(): 
    moveList = []

    # Initialize frame count
##    frame_count = 0
##    FRAME_MAX = 6
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
##        frame_count = frame_count + 1
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        # resize the frame, blur it, and convert it to the HSV
        # color space
        image = frame.array
        frame_im = imutils.resize(image, width=600)
        blurred = cv2.GaussianBlur(frame_im, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        # PURPLE
        threshLower = (8,0,8)
        threshUpper = (115,68,98)
        # RED
##        threshLower = (0, 0, 109)
##        threshUpper = (13, 245, 185)
        
        # construct a mask for the color "blue", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, threshLower, threshUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
##        cv2.imshow("mask",mask)

    # find contours in the mask and initialize the current
            # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:

                    # find the largest contour in the mask, then use
                    # it to compute the minimum enclosing circle and
                    # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            #print("Center: " +str(center) )
                
            # only proceed if the radius meets a minimum size
            if radius > 30:
                # TODO: Add code for rotating robot in if statements
                if center[0] < X_MIN:
                    # Turn robot left
                    print("TURN LEFT")
                    moveList.append('L')
                    #time.sleep(.5)
                    PWMrobotControl.rotateRobot(ser,(math.pi/2))
                    time.sleep(1)
                    PWMrobotControl.moveRobotXY(ser, 10, 0)
                    time.sleep(1)
                    PWMrobotControl.rotateRobot(ser,3*(math.pi/2))
                    #time.sleep(.5)
                elif center[0] > X_MAX:
                    # Turn robot right
                    print("TURN RIGHT")
                    moveList.append('R')
                    #time.sleep(.5)
                    PWMrobotControl.rotateRobot(ser,3*(math.pi/2))
                    time.sleep(1)
                    PWMrobotControl.moveRobotXY(ser, 10, 0)
                    time.sleep(1)
                    PWMrobotControl.rotateRobot(ser, (math.pi/2))
                    #time.sleep(.5)
                else:
                    break
##                elif radius < RADIUS_MAX:
##                    # Move robot forward
##                    print("MOVE FORWARD")
##                    moveList.append('F')
##                    robotControl.moveRobotXY(5, 0, ser)
                temp_result = PWMrobotControl.readResponse(ser)
                time.sleep(1)
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
##                cv2.circle(image, (int(x), int(y)), int(radius),(0, 255, 255), 2)
##                cv2.circle(image, center, 5, (0, 0, 255), -1)
        else:
##            ser.close()
##            camera.close()
            rawCapture.truncate(0)
            return moveList
                    
            # Reset frame count
##        if frame_count == FRAME_MAX:
##            frame_count = 0
        # show the frame
##        cv2.rectangle(image,(X_MIN,Y_MIN),(X_MAX,Y_MAX),(0,255,0),2)
##        cv2.imshow("Frame",image )
        
##        key = cv2.waitKey(1) & 0xFF
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
##        if key == ord("q"):
##            break
    rawCapture.truncate(0)
##    ser.close()
##    camera.close()


#blocks the thief’s path
def block_thief(ser):
    print("Starting to block thief")
    block_movements = []
    while (detectGoal()):
        block_movements = trackingAlg()
        PWMrobotControl.moveRobotBackX(ser, 5)
        time.sleep(0.6)
        PWMrobotControl.moveRobotXY(ser, 5, 0)
        time.sleep(0.6)
    return block_movements


#turn is 0 or pi
def aggressive_defense(ser):
    print("Starting aggressive defense")
    block_movements = []
    # determines the direction the robot turns
    opposite_turn = 0
    turn = 0
    found_in_left = False
    # turn left 45 degrees
    PWMrobotControl.rotateRobot(ser,(math.pi/6))
    left_turn = math.pi/3
    time.sleep(0.8)

    # if the robot detects the noodle, execute block_thief on the left side of map
    if (detectGoal()):
        # turn to be horizontal to the noodle
        PWMrobotControl.rotateRobot(ser,left_turn)
        time.sleep(0.8)
        PWMrobotControl.rotateRobot(ser,(math.pi/25))
        time.sleep(0.3)
        opposite_turn = math.pi
        found_in_left = True
    else:
        PWMrobotControl.rotateRobot(ser,(math.pi/6))
        time.sleep(0.8)
        if (detectGoal()):
            # turn to be horizontal to the noodle
            PWMrobotControl.rotateRobot(ser,math.pi/6)
            time.sleep(0.8)
            PWMrobotControl.rotateRobot(ser,(math.pi/20))
            time.sleep(0.3)
            opposite_turn = math.pi
            found_in_left = True
                
    # if the robot does not detect the noodle, assume it is on the right side of the map
    # and turn 135 degrees right to be horizontal to the noodle, facing right
    if (not found_in_left):
        print("turn right")
        turn = math.pi
        # turn to be horizontal to the noodle
        PWMrobotControl.rotateRobot(ser,(11*math.pi/6))
        time.sleep(1.2)
        
    print("move straight")
    PWMrobotControl.moveRobotXY(ser, 30, 0)
    time.sleep(1.5)
    PWMrobotControl.rotateRobot(ser,(math.pi/2)+opposite_turn)
    time.sleep(0.8)
    PWMrobotControl.rotateRobot(ser,(math.pi/35)+opposite_turn)
    time.sleep(0.5)

    while (not detectGoal()):
        print("Not seeing noodle - Try to find noodle")
        PWMrobotControl.rotateRobot(ser,(math.pi/2)+turn)
        time.sleep(0.8)
        PWMrobotControl.moveRobotXY(ser, 30, 0)
        time.sleep(1)
        PWMrobotControl. rotateRobot(ser,(math.pi/2)+opposite_turn)
        time.sleep(0.8)
    
    print("Found noodle - End aggressive defense")


def routine_defense(ser):
    dist = 50
    half_dist = 25
    full_rotate = math.pi
    partial_rotate = math.pi/30
    half_rotate = math.pi/2
    
##    time.sleep(2)
    print("Turn left")
    PWMrobotControl.rotateRobot(ser,half_rotate)
    time.sleep(0.8)
    print("Move forward dist/2")
##    for i in range(5):
##        PWMrobotControl.moveRobotXY(ser, dist, 0)
##        time.sleep(0.6)
    PWMrobotControl.moveRobotXY(ser, half_dist, 0)
    time.sleep(3.5)
    print("Turn 180 degrees")
    PWMrobotControl.rotateRobot(ser,full_rotate)
    time.sleep(2)
    PWMrobotControl.rotateRobot(ser,partial_rotate)
    time.sleep(0.8)
##    for i in range(2):
    print("Move forward dist")
##    for i in range(10):
##        PWMrobotControl.moveRobotXY(ser, dist, 0)
##        time.sleep(0.6)
    PWMrobotControl.moveRobotXY(ser, dist, 0)
    time.sleep(6.5)
    print("Rotate 180 degrees")
    PWMrobotControl.rotateRobot(ser,full_rotate)
    time.sleep(2)
   # PWMrobotControl.rotateRobot(ser,partial_rotate)
   # time.sleep(0.3)
    print("Move backwards dist")
##    for i in range(10):
##        PWMrobotControl.moveRobotXY(ser, dist, 0)
##        time.sleep(0.6)
    PWMrobotControl.moveRobotXY(ser, dist, 0)
    time.sleep(6.5)
    print("Rotate 180 degrees")
    PWMrobotControl.rotateRobot(ser,full_rotate)
    time.sleep(2)
    PWMrobotControl.rotateRobot(ser,partial_rotate)
    time.sleep(0.8)
    #go half distance forward to the center and face the noodle
    print("Move forward dist/2")
##    for i in range(5):
##        PWMrobotControl.moveRobotXY(ser, dist, 0)
##        time.sleep(0.6)
    PWMrobotControl.moveRobotXY(ser, half_dist, 0)
    time.sleep(3.5)
    print("Turn 90 degrees left")
    PWMrobotControl.rotateRobot(ser,half_rotate)
#    PWMrobotControl.rotateRobot(ser,half_rotate)
    time.sleep(1.5)
    PWMrobotControl.rotateRobot(ser,math.pi/16)
#    PWMrobotControl.rotateRobot(ser,half_rotate)
    time.sleep(0.8)
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

    

##print(detectGoal())
##time.sleep(1)
##reverseMoves(trackingAlg())
##
##ser.close()
##cv2.destroyAllWindows()

