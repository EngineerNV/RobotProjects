import math
import PWMrobotControl
import serial
import time
import cv2
import PurpleTrack
import commModule

def main():
    ser = serial.Serial("/dev/serial0",115200)
        
    xBee = commModule.connectXBee()
    time.sleep(2)
    PWMrobotControl.changePWMvalues(ser, 179, 150)
    
##    while (True):
##        PWMrobotControl.moveRobotObs(ser)
    
##    PWMrobotControl.moveRobotXY(ser,100,0)
    
##    PurpleTrack.trackingAlg()
    # Keep doing routine defense as long as the robot detects the noodle when it checks in the center
    while(PurpleTrack.detectGoal()):
        print("tracking Algorithm")
        PurpleTrack.trackingAlg()
        print("routine defense")
        PurpleTrack.routine_defense(ser)
    
    # Send message that noodle has been taken
    print("sending packet that the noodle has been stolen to other defense robot")
    commModule.sendPacket(xBee, 0x2, 0x5)
        
    while (True):
        PurpleTrack.aggressive_defense(ser)
        PurpleTrack.block_thief(ser)

    # Noodle is taken, move to aggressive defense
    #PurpleTrack.aggressiveDefense()
    
if __name__ == "__main__":
    main()