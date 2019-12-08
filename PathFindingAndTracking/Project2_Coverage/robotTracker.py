
#Test function Nicholas Vaughn
# import the necessary packages
from collections import deque
import numpy as np
import argparse
import cv2
import imutils
import time
import math
import robotControl
import serial

from picamera.array import PiRGBArray
from picamera import PiCamera

# Initial HSV values for testing
##HLo = 80
##SLo = 90
##VLo = 80
##
##HUp = 250
##SUp = 255
##VUp = 255
##
##def nothing(x):
##        pass

# Create window for HSV sliders
##cv2.namedWindow('image')
##
##cv2.createTrackbar('HLo', 'image', 80, 255, nothing)
##cv2.createTrackbar('HUp', 'image', 250, 255, nothing)
##cv2.createTrackbar('SLo', 'image', 90, 255, nothing)
##cv2.createTrackbar('SUp', 'image', 255, 255, nothing)
##cv2.createTrackbar('VLo', 'image', 80, 255, nothing)
##cv2.createTrackbar('VUp', 'image', 255, 255, nothing)

moveList = []

# Open Serial Port
ser = serial.Serial("/dev/serial0",115200)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 600)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 600))

# allow the camera to warmup
time.sleep(0.1)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
        help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
        help="max buffer size")
args = vars(ap.parse_args())



pts = deque(maxlen=args["buffer"])

# Initialize frame count
frame_count = 0
FRAME_MAX = 6
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
        
        # Testing with sliders for HSV
##        hlo = cv2.getTrackbarPos('HLo', 'image')
##        slo = cv2.getTrackbarPos('SLo', 'image')
##        vlo = cv2.getTrackbarPos('VLo', 'image')
##        hup = cv2.getTrackbarPos('HUp', 'image')
##        sup = cv2.getTrackbarPos('SUp', 'image')
##        vup = cv2.getTrackbarPos('VUp', 'image')
##	
##        threshLower = np.array([hlo,slo,vlo])
##        threshUpper = np.array([hup,sup,vup])
        
        # Tested constraints for HSV threshold - use these when done testing
        # Constraining using blue paper circle
        # Threshold values for testing in CSB
##        threshLower = (99,119,140)
##        threshUpper = (176,233,231)
        # Threshold values for testing in Baun
        threshLower = (80,90,80)
        threshUpper = (250,255,255)
        

        # construct a mask for the color "blue", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, threshLower, threshUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cv2.imshow("mask",mask)
# find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
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
                                robotControl.rotateRobot(ser,(math.pi/24))
                                #time.sleep(.5)
                        elif center[0] > X_MAX:
                                # Turn robot right
                                print("TURN RIGHT")
								moveList.append('R')
                                #time.sleep(.5)
                                robotControl.rotateRobot(ser,25*(math.pi/24))
                                #time.sleep(.5)
                        elif radius < RADIUS_MAX:
                                # Move robot forward
                                print("MOVE FORWARD")
								moveList.append('F')
                                robotControl.moveRobotXY(5, 0, ser)
                        
                        # draw the circle and centroid on the frame,
                        # then update the list of tracked points
                        cv2.circle(image, (int(x), int(y)), int(radius),
                                (0, 255, 255), 2)
                        cv2.circle(image, center, 5, (0, 0, 255), -1)

        # update the points queue
##        pts.appendleft(center)
##        # loop over the set of tracked points
##        for i in range(1, len(pts)):
##                # if either of the tracked points are None, ignore
##                # them
##                if pts[i - 1] is None or pts[i] is None:
##                        continue
##
##                # otherwise, compute the thickness of the line and
##                # draw the connecting lines
##                thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
##                cv2.line(image, pts[i - 1], pts[i], (0, 0, 255), thickness)

        # Reset frame count
        if frame_count == FRAME_MAX:
                frame_count = 0

        # show the frame
        cv2.rectangle(image,(X_MIN,Y_MIN),(X_MAX,Y_MAX),(0,255,0),2)
        cv2.imshow("Frame",image )
        key = cv2.waitKey(1) & 0xFF
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
                break
ser.close()
cv2.destroyAllWindows()
    