#Created by Nicholas Vaughn and Auong Something 
#This code was made to perform a wall following 
#Alg for Offense Capture the flag using a Finite State Machine
#The robot should always start with a corner on its left side 
# import the necessary packages
import sys
#Custom Files 
from actions import *
#Variable Declarations 
#    Directions 
NORTH,EAST,SOUTH,WEST = 1,2,3,4
dir = NORTH 
#    States 
CHECK_MV, L_TURN_MV, TURN_180, MV_FWD_AF_180, R_TURN, MV_FWD_AF_L = 1,2,3,4,5,6
STATE = CHECK_MV# we assume that we start with the conditions meeting the criteria for CHECK_MV
haveGoal = False # this will switch behavior for exploring and returning home
# have goal only changes the behavior of checking states

#Running the Script 
#initializing FSM 
while 1:
     if STATE == CHECK_MV: 
        print('In CHECK_MV')
        #state check
        [L,F,R] = getSensors()
        if L==1 and F == 0:#we are in this state currently
            pass
        elif L==1 and F==1 and R==1:
            STATE=TURN_180
            continue
        elif L==1 and F==1 and R==0:
            STATE=R_TURN
            continue
        elif L==0:
            STATE=L_TURN_MV
            continue
        else: # error condition
            print('WARNING MISSING A STATE CHECK_MV')
            sys.exit()
        #executing the state    
        if haveGoal == False:
            moveFWD()
            [goalChase,goalCaught,turn_list]=check_goal_180() # need to figure out how to use his check code 
            # this could be a value or a list depending on what Jason has  
            # goal Caught means we blacked out chasing the Goal and we have it.
            
            if goalCaught:    # checking CHECK_180 result
                haveGoal = True
                reverseTurnList(turn_list)
                continue
            elif goalChase:
                reverseTurnList(turn_list)
                continue
                
            #turnR()
            #for x in range(0,3):
            #    obs_flag = moveFWD()
            #    [goalChase,goalCaught,turn_list]=check_goal_180()
            #    if obs_flag or goalChase: # if we cant moveFWD or we chased goal stop
            #        break
            
            if goalCaught:    # checking CHECK_180 result
                haveGoal = True
                reverseTurnList(turn_list)
                continue
            elif goalChase:
                
                reverseTurnList(turn_list)
                continue
            #Going back to the wall 
            #turnBack() #180 turn
            #for x in range(0,3):
               # moveFWD()
            #turnR()
            #print('here')
            moveFWD()
        else: # if we have the goal we should just move forward and check to try to get back 
            print('In Check_MV looking for end')
            check_end()
            moveFWD()
            moveFWD()
     elif STATE == L_TURN_MV: # needs to check state after execution
        print('In L_TURN_MV STATE')
        turnL()
        moveFWD()
        #input("L_TURN_MV State Paused")
        #state check
        [L,F,R] = getSensors()
        if L==1 and F == 0:
            STATE = CHECK_MV
        elif L==0 and F==0:
            STATE = MV_FWD_AF_L
        elif F==1 and R==1:
            STATE = TURN_180
        elif F==1 and R==0:
            STATE = R_TURN
        else:
            print('WARNING MISSING A STATE IN L_TURN_MV')
            sys.exit()
     elif STATE == TURN_180:    
        print('In TURN_180')
        turnBack()
        [L,F,R] = getSensors()  
        #input("TURN_180 paused")
        #state check
        if L==1 and F==1 and R==1:
            pass #stay in this state
        elif L==1 and F==1 and R==0:
            STATE = R_TURN
        elif F==0:
            STATE = MV_FWD_AF_180
        elif F==1 and L==0:
            STATE = L_TURN_MV
        else:
            print('WARNING MISSING A STATE IN TURN_180')
            sys.exit()    
     elif STATE == MV_FWD_AF_180:    
        print('In MV_FWD_AF_180')
        moveFWD()
        [L,F,R]=getSensors()
        #input("MV_FWD_AF_180 State paused")
        #state check 
        if L==1 and F==1 and R==1:
            STATE = TURN_180
        elif L==1 and F==1 and R==0:
            STATE = R_TURN
        elif L==1 and F==0:
            STATE = CHECK_MV
        elif L==0:
            STATE = L_TURN_MV
        else:
            print('WARNING MISSING A STATE IN MV_FWD_AF_180')
            sys.exit()
     elif STATE == MV_FWD_AF_L:
        print('In MV_FWD_AF_L')
        moveFWD()
        [L,F,R]=getSensors()
        #input("MV_FWD_AF_L State paused")
        #state check 
        if L==0 and F==0:
            pass
        elif F==1 and R==1:
            STATE=TURN_180
        elif F==1 and R==0:
            STATE=R_TURN
        elif L==1 and F==0:
            STATE=CHECK_MV
        else:
            print('WARNING MISSING A STATE IN MV_FWD_AF_L')
            sys.exit()
     elif STATE == R_TURN:
        print('In R_TURN')
        turnR()
        [L,F,R]=getSensors()
        #input("R_TURN State paused")
        #state Check 
        if L==1 and F==1 and R==1:
            STATE=TURN_180
        elif L==1 and F==1 and R==0:
            STATE=R_TURN
        elif L==1 and F==0:
            STATE=CHECK_MV
        elif L==0:
            STATE=L_TURN_MV
        else:
            print('WARNING MISSING A STATE IN R_TURN')
            sys.exit()
