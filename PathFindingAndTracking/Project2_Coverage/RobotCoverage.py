# Author: Courtney Banh
import math
import PWMrobotControl
import serial
import time
import cv2
from map_class import map_class
import robotTrack

# Preassumption: Robot is in corner of room facing empty space
OBSTACLE_DISTANCE = 900 # in ADC increments
MOVEMENT_DISTANCE = 25

# Steps:
# 0. Open Serial Port
ser = serial.Serial("/dev/serial0",115200)

# Change the sensor threshold
##PWMrobotControl.changeSensorThreshold(ser, OBSTACLE_DISTANCE, OBSTACLE_DISTANCE, OBSTACLE_DISTANCE)
##time.sleep(1)

# 1. Initialize empty list "clean_list"
#clean_list = []

# 2. Initialize robot position at (0, 0)
robot_position = (0,0)
robotMap = map_class(99,99)

# 3. Initialize robot direction as north ("1") (N=1, E=2, S=3, W=4)
robot_direction = 1

# 4. Start loop: (Stopping condition: All 4 neighbor cells are in "clean_list")
while not robotMap.isLeftClean() or not robotMap.isRightClean() or not robotMap.isFrontClean() or not robotMap.isBackClean():
    print('inside while loop')
    # a. Update left, right, front, and back cells using robot direction
##    left_cell = (robot_position[0]-1,0)
##    right_cell = (robot_position[0]+1,0)
##    front_cell = (0,robot_position[1]+1)
##    back_cell = (0,robot_position[1]-1)
    
    # Get sensor values
    PWMrobotControl.getSensors(ser)
##    print("after getSensors")
    result, msgType = PWMrobotControl.readResponse(ser)
    print("Result: " + str(result))
    time.sleep(1)
##    total_result = [0,0,0]
##    for i in range(3):
##        robotControl.getSensors(ser)
##        result, msgType = robotControl.readResponse(ser)
##        for j in range(3):
##            total_result[i] = total_result[i] + result[i]
##        print("Result: " + str(result))
##        time.sleep(1)
##        
##    for i in range(3):
##        total_result[i] = total_result[i] / 3
    
    if result[0] > OBSTACLE_DISTANCE:
        robotMap.foundObjLeft()
    
    # b. If no obstacle on the left AND left cell is dirty:
    if result[0] < OBSTACLE_DISTANCE and not robotMap.isLeftClean():
        print('No obstacle on left and left cell is dirty')
        # i. Move robot to left cell
        robotMap.turnLeft() # updating map direction 
        PWMrobotControl.rotateRobot(ser,(math.pi/2)) # Turn left
        temp_result = PWMrobotControl.readResponse(ser)
        time.sleep(1)
        robotMap.moveForward() # change robot map position
        PWMrobotControl.moveRobotXY(ser, MOVEMENT_DISTANCE, 0) # Move forward
        temp_result = PWMrobotControl.readResponse(ser)
        time.sleep(1)
        # ii. Add current cell to "clean_list"
        #clean_list.append(robot_position)
        # iii. Update robot position, direction, neighbors
        ##### TODO #####
        
    # c. If obstacle in front cell:
    elif result[1] > OBSTACLE_DISTANCE:
        print('Obstacle in front cell')
        # i. Loop until no obstacle on the left:
        #while result[0] > OBSTACLE_DISTANCE:
        while result[1] > OBSTACLE_DISTANCE: # while obstacle is in front
            robotMap.foundObjFront()
            # Turn robot right
            robotMap.turnRight() # updating the map direction  
            PWMrobotControl.rotateRobot(ser,14*(math.pi/9))
            temp_result = PWMrobotControl.readResponse(ser)
            time.sleep(1)
            # Update robot direction and neighbors
            ##### TODO #####
            # Check sensor values
            PWMrobotControl.getSensors(ser)
            result, msgType = PWMrobotControl.readResponse(ser)
            print("Result: " + str(result))
            time.sleep(1)
##            total_result = [0,0,0]
##            for i in range(3):
##                robotControl.getSensors(ser)
##                result, msgType = robotControl.readResponse(ser)
##                for j in range(3):
##                    total_result[i] = total_result[i] + result[i]
##                print("Result: " + str(result))
##                time.sleep(1)
##        
##            for i in range(3):
##                total_result[i] = total_result[i] / 3
        # Move robot forward
        robotMap.moveForward() # updating the map
        PWMrobotControl.moveRobotXY(ser, MOVEMENT_DISTANCE, 0) # Move forward
        temp_result = PWMrobotControl.readResponse(ser)
        time.sleep(1)
        # Add cleaned cells to "clean_list"
        #if robot_position not in clean_list:
        #    clean_list.append(robot_position)
        # Update robot position and neighbors
        ##### TODO #####
        # Check sensor values
        PWMrobotControl.getSensors(ser)
        result, msgType = PWMrobotControl.readResponse(ser)
        print("Result: " + str(result))
        time.sleep(1)
##        total_result = [0,0,0]
##        for i in range(3):
##            robotControl.getSensors(ser)
##            result, msgType = robotControl.readResponse(ser)
##            for j in range(3):
##                total_result[i] = total_result[i] + result[i]
##            print("Result: " + str(result))
##            time.sleep(1)
##        
##        for i in range(3):
##            total_result[i] = total_result[i] / 3
            
    # d. If front cell is dirty:
    elif not robotMap.isFrontClean():
        print('Front cell is dirty')
        # i. Move to front cell
        
        PWMrobotControl.moveRobotXY(ser, MOVEMENT_DISTANCE, 0) # Move forward
        temp_result = PWMrobotControl.readResponse(ser)
        time.sleep(1)
        # Check sensor values
        PWMrobotControl.getSensors(ser)
        result, msgType = PWMrobotControl.readResponse(ser)
        print("Result: " + str(result))
        time.sleep(1)
        if temp_result[1] == 0:
            robotMap.moveForward() # updating the map
        elif result[1] < OBSTACLE_DISTANCE:
            PWMrobotControl.rotateRobot(ser,9*(math.pi/8))
            temp_result = PWMrobotControl.readResponse(ser)
            time.sleep(1)
        # ii. Add current cell to "clean_list"
        #clean_list.append(robot_position)
        # iii. Update robot position and neighbors
        ##### TODO #####
    # e. Else:
    else:
        print('Else')
        # i. Turn right
        robotMap.turnRight() # updating the map direction 
        PWMrobotControl.rotateRobot(ser,14*(math.pi/9))
        temp_result = PWMrobotControl.readResponse(ser)
        time.sleep(1)
        # ii. Update robot direction and neighbors
        ##### TODO #####
        
    # Check still frame from camera for object
    if robotTrack.detectGoal() == 1:
        time.sleep(1)
        robotTrack.reverseMoves(robotTrack.trackingAlg())
        cv2.destroyAllWindows()
##        moveList = robotTrack.trackingAlg()
##        robotTrack.reverseMoves(moveList)
    

print('All neighbor cells are clean')