# ECPE 255
# 28 September 2018
# Courtney Banh, Nick Vaughn

# Import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from sys import exit
import argparse
import imutils
import time
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
from makeROI import makingRec

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
# --tracker : The OpenCV object tracker to use.
# By default, it is set to kcf (Kernelized Correlation Filters).
# For a full list of possible tracker code strings refer to the next code block.
ap.add_argument("-t", "--tracker", type=str, default="kcf",
	help="OpenCV object tracker type")
args = vars(ap.parse_args())

# Extract the OpenCV version info
(major, minor) = cv2.__version__.split(".")[:2]
 
# If we are using OpenCV 3.2 OR BEFORE, we can use a special factory
# function to create our object tracker
if int(major) == 3 and int(minor) < 3:
	tracker = cv2.Tracker_create(args["tracker"].upper())
 
# Otherwise, for OpenCV 3.3 OR NEWER, we need to explicity call the
# approrpiate object tracker constructor:
else:
	# Initialize a dictionary that maps strings to their corresponding
	# OpenCV object tracker implementations
	OPENCV_OBJECT_TRACKERS = {
		"csrt": cv2.TrackerCSRT_create,
		"kcf": cv2.TrackerKCF_create,
		"boosting": cv2.TrackerBoosting_create,
		"mil": cv2.TrackerMIL_create,
		"tld": cv2.TrackerTLD_create,
		"medianflow": cv2.TrackerMedianFlow_create,
		"mosse": cv2.TrackerMOSSE_create
	}
 
	# Grab the appropriate object tracker using our dictionary of
	# OpenCV object tracker objects
	tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
 
# Initialize the bounding box coordinates of the object we are going
# to track
initBB = None

# Initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)

# Allow the camera to warmup
time.sleep(0.1)

# Grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array

# display the image on screen and wait for a keypress
cv2.imshow("Image", image)
cv2.waitKey(0)

# Use makeROI.py module to get BB of object
if makingRec(image) is not None:
        [xmin, ymin, w, h] = makingRec(image)
else:
        print("[INFO] No object identified for tracking, ending script")
        exit()

# Grab the reference to the camera for video stream
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
print("[INFO] starting video stream...")
	
# Capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# Grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
	
	# TODO: Track object in frame
 
	# Show the frame
	cv2.imshow("Frame", image)
	key = cv2.waitKey(1) & 0xFF
 
	# Clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# If the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
 
# Initialize the FPS throughput estimator
fps = None

