Created by Nicholas Vaughn and Courtney Banh 


Project 2 Coverage

In order to run this program you have to have python 3 installed 

Here is the command to run it 

python3 RobotCoverage.py 

RobotCoverage.py is the high level file that incoprates the exploring alg with the tracking 

PWMrobotControl is the most recent motion control code to communicate with the microcontroller

It is used in the RobotCoverage.py

The robotTrack.py contains all the modules used for tracking. 
Their are three methods inside it, detectGoal() returns boolean if goal is sensed, trackingAlg() performs tracking
and returs a list of moves it performed while tracking an object, and reverseMoves(moveList[]) which takes in a list of moves
and has the robot reverse them to go back to its original exploring position 

The trackingAlg() uses the old robotControl.py file to perform microcontroller communication.