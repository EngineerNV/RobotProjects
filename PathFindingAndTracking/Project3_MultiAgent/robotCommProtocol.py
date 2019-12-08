# Project 3: Multi-Agent & Communications
# Courtney Banh, Nick Vaughn
import serial
import time
import random
import sys
from math import pi
from math import radians
from random import randint
import PWMrobotControl

robotSer = serial.Serial("/dev/serial0",115200)
xbeeSer = serial.Serial('/dev/ttyUSB0',57600, timeout = 3)  # open Zigbee serial port
print(xbeeSer.name)  # check which port was really used
##while(True):
####    data = bytearray([int(0xDA),int(0x6),int(0x1),20,int(0xDB)])
####    xbeeSer.write(data)
##
##    reply = xbeeSer.read(5)
##    print(reply)
##    if reply[0] == 218 and reply[4] == 219:
##        print("PACKET RECEIVED")
##        performCommand(reply)
##    #ser.write(b'robotics is cool\n')
##    time.sleep(1)

MY_ID = 6

# Initialize robot ID list
robotID = [2,3,4,5,7,8,9,10,11]
##robotID = [11]


### ROBOT IS SIMON ###
def simon():
    # Send random command
##    command = int(1)
    command = randint(1, 3)
    if command == 1: # Move
        parameter = random.choice([10, 20, 30, 40])
    elif command == 2 or command == 3: # Rotate
        parameter = random.choice([45, 90, 135, 180])
##    elif command == 2: # Rotate right
##        parameter = random.choice([pi/4, pi/2, 3*pi/2, pi])
##    elif command == 3: # Rotate left
##        parameter = random.choice([pi/4, pi/2, 3*pi/2, pi]) + pi
    else:
        print("ERROR: Invalid command")
    packet = bytearray([int(0xDA), MY_ID, int(command), int(parameter), int(0xDB)])
##    performCommand(packet)
    print("Command: " + str(command) + ", parameter: " + str(parameter))
    xbeeSer.write(packet)
    print("Command sent")
    time.sleep(10)
    
    simonFound = False
    while not simonFound:
        # Select random ID from robot ID list
        try:
            randomID = random.choice(robotID)
        except:
            sys.exit("All robots have been removed from list - No more players in the game")
        simonPacket = bytearray([int(0xDA), MY_ID, int(0x4), int(randomID), int(0xDB)])
        print("New Simon: " + str(randomID))
    
        # Wait to receive ack, try 3 times with timeout
        for i in range(3):
            xbeeSer.write(simonPacket)
##            time.sleep(5)
            start = time.time()
            while int(time.time() - start) < 2: 
                continue    
            reply = xbeeSer.read(5)
            if len(reply) == 5:
                print(reply)
                if reply[0] == 218 and reply[4] == 219:
                    if reply[2] == 5 and reply[3] == MY_ID:
                        print("PACKET RECEIVED BY ROBOT " + str(randomID))
                        simonFound = True
                        break
        
        # If ack not received, remove ID from list
        if not simonFound:            
            robotID.remove(randomID)
            print("Robot " + str(randomID) + " removed from ID list")

    # Else ack received from player with ID(i), call Player function
##    player()



### ROBOT IS PLAYER ###
def player():
    # Wait to receive command, read command
    commandReceived = False
    while not commandReceived:
        packet = xbeeSer.read(5)
        if len(packet) == 5:
            print(packet)
            if packet[0] == 218 and packet[4] == 219:
                print("PACKET RECEIVED FROM SIMON")
                commandReceived = True
    
    if packet[2] == 1 or packet[2] == 2 or packet[2] == 3:
        performCommand(packet)  

    # If Simon ID not in ID list, appent ID to list
    if packet[1] not in robotID:
        print("Robot " + str(packet[1]) + " added to ID list")
        robotID.append(packet[1])

    # If message ID(i) received, call Simon function
    if packet[2] == 4 and packet[3] == MY_ID:
        print("Chosen to be the new Simon!")
        # Send confirmation
        packet = bytearray([int(0xDA), MY_ID, int(0x5), packet[1], int(0xDB)])
        xbeeSer.write(packet)
        time.sleep(1)
        
        return True  # call simon()
    else:
        return False  # continue being player



def performCommand(packet):
    if packet[2] == 1:
        # Move
        print("MOVE COMMAND RECEIVED")
        PWMrobotControl.moveRobotXY(robotSer, packet[3], 0)
        result = PWMrobotControl.readResponse(robotSer)
        time.sleep(1)
        if result[1] == 1:  # Obstacle flag
            PWMrobotControl.rotateRobot(robotSer, pi)
            result = PWMrobotControl.readResponse(robotSer)
            time.sleep(1)
    elif packet[2] == 2:
        # Rotate right
        print("ROTATE RIGHT COMMAND RECEIVED")
        theta = radians(packet[3])
        PWMrobotControl.rotateRobot(robotSer, theta)
        result = PWMrobotControl.readResponse(robotSer)
        time.sleep(1)
    elif packet[2] == 3:
        # Rotate left
        print("ROTATE LEFT COMMAND RECEIVED")
        theta = radians(packet[3]) + pi
        PWMrobotControl.rotateRobot(robotSer, theta)
        result = PWMrobotControl.readResponse(robotSer)
        time.sleep(1)
    else:
        print("ERROR: Unable to perform command")



### MAIN ###
# If init ID call Simon function
# Else call Player function
##simon()
while True:
    if player():
        simon()




##while(True):
##data = bytearray([0xDA,0x6,0x1,0x14,0xDB])
##data = bytearray([0xDA,0x6,0x4,0x5,0xDB])
##xbeeSer.write(data)
##
##    reply = xbeeSer.read(5)
##    print(reply)
##    if reply[0] == 218 and reply[4] == 219:
##        print("PACKET RECEIVED")
##        performCommand(reply)
##    #ser.write(b'robotics is cool\n')
##    time.sleep(1)