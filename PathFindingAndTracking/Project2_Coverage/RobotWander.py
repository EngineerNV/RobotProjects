# Author: Courtney Banh
import math
import PWMrobotControl
import serial
import time
from map_class import map_class

OBSTACLE_DISTANCE = 900 # in ADC increments
MOVEMENT_DISTANCE = 30

# Open Serial Port
ser = serial.Serial("/dev/serial0",115200)

# Change the sensor threshold
##PWMrobotControl.changeSensorThreshold(ser, OBSTACLE_DISTANCE, OBSTACLE_DISTANCE, OBSTACLE_DISTANCE)
##time.sleep(1)

while True:
    # Get sensor values
    PWMrobotControl.getSensors(ser)
    result, msgType = PWMrobotControl.readResponse(ser)
    print("Result: " + str(result))
    time.sleep(1)
        
    while result[1] > OBSTACLE_DISTANCE: # while obstacle is in front
        # Turn robot right  
        PWMrobotControl.rotateRobot(ser,3*(math.pi/2))
        temp_result = PWMrobotControl.readResponse(ser)
        time.sleep(1)
        # Check sensor values
        PWMrobotControl.getSensors(ser)
        result, msgType = PWMrobotControl.readResponse(ser)
        print("Result: " + str(result))
        time.sleep(1)

    # Move robot forward
    PWMrobotControl.moveRobotXY(ser, MOVEMENT_DISTANCE, 0) # Move forward
    temp_result = PWMrobotControl.readResponse(ser)
    time.sleep(1)
    
    print("Obstacle flag: " + str(temp_result[1]))
    
    if temp_result[1] == 1:
        print("obstacle detected - stopped movement - need to turn")
        PWMrobotControl.rotateRobot(ser,19*(math.pi/18))
        temp_result = PWMrobotControl.readResponse(ser)
        time.sleep(1)

