import cv2
import io
import sys
import math
import robotControl
import serial
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import picamera
import random

# Read video
width = 640
height = 480
camera = PiCamera()
camera.resolution = (width,height)
camera.framerate = 32
##    camera.rotation = 180
rawCapture = PiRGBArray(camera, size=(640,480))
time.sleep(0.1)
    #Lab
##    lower_red = [169, 100, 100]
##    upper_red = [189, 255, 255]
##    red_boundaries = [(lower_red,upper_red)]
    #UKE
##    red_boundaries = [([0,0,15],[90, 90, 255])]
im_cen_x = int(math.floor(width/2))
im_cen_y = int(math.floor(height/2))
im_cen = (im_cen_x,im_cen_y)
stream = io.BytesIO()
found = False
fails = 0
turn_angles = [math.pi/2, math.pi/4, 0, math.pi + math.pi/4, math.pi + math.pi/2]
camera.start_preview()
time.sleep(0.2)
camera.stop_preview()

#Color definitions:
#Our Object
lower_red = [4, 150, 101]
upper_red = [17, 220, 222]
red_nood = [(lower_red,upper_red)]
#Our Goal
lower_goal = [43, 83, 0]
upper_goal = [69, 255, 255]
blue_goal = [(lower_goal,upper_goal)]
#Blue Object
lower_blue = [63, 189, 88]
upper_blue = [83, 209, 180]
blue_nood = [(lower_blue,upper_blue)]

#Purple Object
lower_purp = [0, 0, 70]
upper_purp = [180, 41, 158]
purp_nood = [(lower_purp,upper_purp)]

global search_for
search_for = red_nood
home = 0

ser = serial.Serial("/dev/serial0",115200)

def areWeHome():
    global home
    return home

def haveNood():
    global search_for
    if search_for == blue_goal:
        return True
    else:
        return False

def grabNood():
    global search_for
    print("Turning and Grabbing the payload")
    robotControl.rotateRobot(ser,math.pi)
    result, msgType = robotControl.readResponse(ser)

    time.sleep(0.5)
    robotControl.moveRobotBackX(10, ser)
    result, msgType = robotControl.readResponse(ser)

    print("Going home with the object")

    robotControl.moveRobotXY(20, 0, ser)
    result = robotControl.readResponse(ser)


    search_for = blue_goal

    if search_for == blue_goal:
        print("Now looking for goal")

    return search_for

def tracking(found):
    global search_for, home
    while True:
##        camera.start_preview()
##        time.sleep(0.2)
        with picamera.array.PiRGBArray(camera) as stream:
            camera.capture(stream, format='bgr')
            image = stream.array
##        camera.stop_preview()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        for (lower,upper) in search_for:
            lower = np.array(lower, dtype = "uint8")
            upper = np.array(upper, dtype = "uint8")
            mask = cv2.inRange(image, lower, upper)
            output = cv2.bitwise_and(image, image, mask = mask)    
        rawCapture.truncate()
        #Scan across middle stripe
        nest_break = False
        found = False
        for i in range(0,width,10):
            for j in range(int(height*0.25),int(height),10):
                if output[j,i,2] > 0:
                    print("found while lost")
                    print("i = " + str(i))
                    print("j = " + str(j))
                    fails = 0
                    found = True
                    nest_break = True
                    break
            if nest_break == True:
                break
                
        if found == True:
            #First pixel is top-left corner
            left_edge = i
            top_edge = j
            #Scan right for right edge of cup
            for rightscanner in range(left_edge, width, 10):
                if output[top_edge,rightscanner,2] == 0:
                    right_edge = rightscanner
                    break
            midpoint = int(math.floor((right_edge - left_edge)/2))
            #Scan down from mid-point for bottom edge of cup
            for botscan in range(top_edge, height, 10):
                if output[botscan,midpoint,2] == 0:
                    bot_edge = botscan
                    break
            p0 = left_edge
            p1 = top_edge
            p2 = bot_edge - top_edge
            p3 = right_edge - left_edge
            print("Left: " + str(left_edge))
            print("Right: " + str(right_edge))
            print("Top: " + str(top_edge))
            print("Bottom: " + str(bot_edge))
            bbox = (p0,p1,p3,p2)
            print("bbox = " + str(bbox))
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            print("Ready to start tracking")
            # Initialize tracker with first frame and bounding box
            cv2.putText(image, "*", im_cen, cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,0,0),2)
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            centroid = (int(bbox[0] + bbox[2]/2), int(bbox[1] + bbox[3]/2))
            #If object on right side of image, rotate right
            if centroid[0] > (im_cen_x*1.25):
                print("I'm turning right!")
                robotControl.rotateRobot(ser,math.pi+math.pi/30) #was pi/15
                result = robotControl.readResponse(ser)
            elif centroid[0] < (im_cen_x*0.75):
                print("I'm turning left!")
                robotControl.rotateRobot(ser,math.pi/30)
                result = robotControl.readResponse(ser)
            else:
                robotControl.moveRobotXY(10, 0, ser)
                result = robotControl.readResponse(ser)
                if search_for == red_nood:
                    if output[int(im_cen_y), int(im_cen_x*0.75),2] > 0 and output[int(im_cen_y), int(im_cen_x*1.25),2] > 0:
                        grabNood()
                        print(search_for)
                        return
                else:
                    if output[int(im_cen_y), int(im_cen_x*0.35),2] > 0 and output[int(im_cen_y), int(im_cen_x*1.65),2] > 0:
                        print("I'm home")
                        home = 1
                        return
        else:
            print("back to seeObj")
            return

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27 : break
        
        rawCapture.truncate(0)



def see_obj():
    global search_for
    trackfail = False
    if search_for == red_nood:
        print("Looking for nood")
    elif search_for == blue_goal:
        print("Looking for goal")
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
    if gotEm == True: #Sees object, 
        tracking(False)
        trackfail = True
    print("Definitely back to main")
    if trackfail == True:
        return True
    else:
        return False

if __name__ == '__main__' :
 
 
    # Read video
    width = 640
    height = 480
    camera = PiCamera()
    camera.resolution = (width,height)
    camera.framerate = 32
##    camera.rotation = 180
    rawCapture = PiRGBArray(camera, size=(640,480))
    time.sleep(0.1)
    global search_for



    #Lab
##    lower_red = [169, 100, 100]
##    upper_red = [189, 255, 255]
##    red_boundaries = [(lower_red,upper_red)]
    #UKE
##    red_boundaries = [([0,0,15],[90, 90, 255])]
    im_cen_x = int(math.floor(width/2))
    im_cen_y = int(math.floor(height/2))
    im_cen = (im_cen_x,im_cen_y)
    stream = io.BytesIO()
    found = False
    fails = 0
    turn_angles = [math.pi/2, math.pi/4, 0, math.pi + math.pi/4, math.pi + math.pi/2]
    camera.start_preview()
    time.sleep(0.2)
    camera.stop_preview()
    search_for = red_nood
    #Coverage begins
    while True:
        lost = False
        sensor_dists = [0,0,0,0,0]
        #Start by turning left 90 degrees, then sprinkler effect-ing through a set of angles
        robotControl.rotateRobot(ser,math.pi/2)
        result = robotControl.readResponse(ser)
        see_obj()
        robotControl.getSensors(ser)
        sens, msgType = robotControl.readResponse(ser)
        time.sleep(1)
        sensor_dists[0] = sens[1]
##        print("dists=" + str(sensor_dists))

        #Nick: This is the "exploration" piece
        for i in range(1,5):
            robotControl.rotateRobot(ser, math.pi + math.pi/4)
            blah = robotControl.readResponse(ser)
            lost = see_obj()
            if lost == True:
                break
            robotControl.getSensors(ser)
            sens, msgType = robotControl.readResponse(ser)
            time.sleep(1)
            sensor_dists[i] = sens[1]
        
        if lost == False:
            #turn and face straight again
            robotControl.rotateRobot(ser,math.pi/2)
            result = robotControl.readResponse(ser)
            #index of max sensor distance
            ind = sensor_dists.index(min(sensor_dists))
    ##        print("Longest dist = " + str(min(sensor_dists)) + " index = " + str(ind))
            #Turn to longest sensor distance
    ##        print("Rotating " + str(turn_angles[ind]))
            if turn_angles[ind] != 0:
                robotControl.rotateRobot(ser, turn_angles[ind])
                result = robotControl.readResponse(ser)
            #Move forward
            time.sleep(1)
            robotControl.moveRobotXY(30, 0, ser)
            result = robotControl.readResponse(ser)
            time.sleep(2)



