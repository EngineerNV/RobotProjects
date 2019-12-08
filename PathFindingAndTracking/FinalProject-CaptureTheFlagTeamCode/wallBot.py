#!/usr/bin/env python
from bail import *

'''

The robot running this script has a lateral wall fixed to itself (right side).
The robot will go forward x units until it hits hits an obstacle, then reverse
    for the same approximate distance
'''

ser = serial.Serial("/dev/serial0", 115200)

# modify/disable sensor values to account for length of flag protruding from the front
robotControl.changeSensorThreshold(ser, 650, 400, 550)
# robotControl.changeSensorThreshold(ser, 9000, 9000, 9000)

# determined PWM values to modify each wheel's rotation amount
l = 131
r = 158
robotControl.changePWMvalues(ser, l, r)

# this robot is a defender with ID = 3
bail = Bail("defender", 3)

# give a couple seconds for the robot to get ready as well as let the square-driving robot to get around the goal
time.sleep(2)
# begin pacing
while 1:

    # check if we need to move out of the way
    bail.bail_out()

    for i in range(3):
        robotControl.moveRobotXY(ser, 18, 0)
        out = robotControl.readResponse(ser)[0]
        print("forward", l, r, out.rightWheelDist, out.leftWheelDist)

        time.sleep(0.5)

    for i in range(3):
        robotControl.moveRobotBackX(ser, 18)
        out = robotControl.readResponse(ser)[0]
        print("backward", out.rightWheelDist, out.leftWheelDist)

        time.sleep(0.5)

    # if out.rightWheelDist > out.leftWheelDist:
    #     r += 1
    # elif out.rightWheelDist < out.leftWheelDist:
    #     l += 1





