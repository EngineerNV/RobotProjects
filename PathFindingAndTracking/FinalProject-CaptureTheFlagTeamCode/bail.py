#!/usr/bin/env python
import time
import serial
from struct import unpack
import PWMrobotControl as robotControl
from math import pi

'''

mode = "attacker" or "defender"
my_id = 0 for attacker or omit it in the constructor call below
      = 1, 2, or 3 for defender
      
add somewhere to init the object:
bail = Bail(mode, my_id)

attacker calls this once they have the flag/cylinder
defender calls it whenever they want to check if the attacker wants them to move
    perhaps at the beginning or end of the defender's main loop?
    
bail.bail_out()

'''

# XBee serial-USB port
port = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=None)

# Micro-controller serial port
ser = serial.Serial("/dev/serial0", 115200)

start_byte = 0xDA
stop_byte = 0xDB
bail_byte = 0x56  # 0x56 = int 86

# ids of all robots that aren't attackers
robots_playing = [1, 2, 3]


# attacker(s) broadcasts for everyone to get out of the way
# other robots go to the nearest wall
class Bail(object):

    # default id is 0 for attacker
    def __init__(self, mode, my_id=0):

        # mode is "attacker" or "defender"
        self.mode = mode

        self.my_id = my_id

    def read_and_unpack(self):
        rcv = port.read(3)
        unpacked_data = unpack('BBB', rcv)
        print(unpacked_data)
        start = unpacked_data[0]
        robot_id = unpacked_data[1]
        stop = unpacked_data[2]

        return start, robot_id, stop

    def become_wallflower(self):
        readings = {}
        rotation_counter = 0
        # find nearest wall:
        while rotation_counter <= 6:
            # rotate 45 degrees one direction (right)
            robotControl.rotateRobot(ser, pi + pi / 4)
            _ = robotControl.readResponse(ser)
            rotation_counter += 1
            # get new IR sensor readings
            robotControl.getSensors(ser)
            result, msg_type = robotControl.readResponse(ser)
            readings[rotation_counter] = result

        # max IR values initialized to -1
        max_l = -1
        max_m = -1
        max_r = -1

        # track the rotation count for each max value of each direction
        l_max_count = 0
        m_max_count = 0
        r_max_count = 0

        # track the direction with the absolute max
        max_direction = ""

        # determine which direction had the highest max of all attempts
        # default 0 to go straight until a wall is found
        absolute_max = 0

        # get rotation counter with highest (closest to wall) reading
        for reading_number, reading in readings.items():
            left, middle, right = reading
            max_l = max(max_l, left)
            max_m = max(max_m, middle)
            max_r = max(max_r, right)

            # if new max set, track rotation_count value too
            if max_l == left:
                l_max_count = reading

            if max_m == middle:
                m_max_count = reading

            if max_r == right:
                r_max_count = reading

            absolute_max = max(max_l, max_m, max_r)

            if absolute_max == max_l:
                max_direction = "left"
            elif absolute_max == max_m:
                max_direction = "middle"
            elif absolute_max == max_r:
                max_direction = "right"

        # rotate other direction to face where we saw the max IR reading
        for i in range(absolute_max):
            robotControl.rotateRobot(ser, pi / 4)
            _ = robotControl.readResponse(ser)

        # move one more tick to the respective direction if the max sensor isn't in the middle
        # this is attempting to aim directly at the closest object
        # I.e. turn left/right once more if that's the sensor the max was on
        if max_direction == "left":
            robotControl.rotateRobot(ser, pi / 4)
            _ = robotControl.readResponse(ser)

        elif max_direction == "right":
            robotControl.rotateRobot(ser, pi + pi / 4)
            _ = robotControl.readResponse(ser)

        # go straight until obstacle, should be wall
        robotControl.moveRobotObs(ser)

        print("Defense robot", self.my_id, "is now a wallflower")
        # wait one second forever
        while True:
            time.sleep(1)

    # Attacker:      call this when flag captured
    # everyone else: call this every once in a while (at the beginning of main loop?) to see if they need to move
    def bail_out(self):
        if self.mode == "attacker":

            # track all replied robots to make sure all others acknowledge and move out of the way
            replied_robots = set()

            print("Offense: Requesting other robots to 86 themselves...")

            # Attacker sends 3 bytes: start_byte, bail_byte, stop_byte
            # command to bail is int(86)
            packet = bytearray([int(start_byte), int(bail_byte), int(stop_byte)])
            port.write(packet)

           

            # check if all robots replied to stop short of 10 attempts
            all_replied = False

            # 10 attempts to get responses from all robots = 1 second @ 0.1 sec per attempt
            for i in range(10):
                print(i)
                # begin timer to listen for replies
                broadcast_begin = time.clock()
                # wait 0.1 sec between broadcasts to listen for replies -> save them, build a list of robots that got it
                # they will become the new list of robots
                while broadcast_begin - time.clock() < 0.1:
                    # read packets from xbee
                    print('b4 unpack')
                    start, robot_id, end = self.read_and_unpack()
                    print('whle loop')
                    # only save this ID if getting data in correct format and\
                    # we're looking at a confirmation and\
                    # it was a reply to us
                    if start == start_byte and end == stop_byte:
                        print("Offense: Acknowledgement from robot ID:", robot_id)
                        # save this robot to our list of robots that have replied
                        replied_robots.add(robot_id)
                    # for each robot playing, if they've replied (they're in the list of replies) then we can stop making requests
                    if all(robot in replied_robots for robot in robots_playing):
                        all_replied = True
                        print("Offense: All robots acknowledged!")
                        break

                # everyone says they will bail, stop shouting
                if all_replied:
                    break

        elif self.mode == "defender":

            # read data from xbee
            start, command, end = self.read_and_unpack()
            # only begin if getting data in correct format
            if start == start_byte and end == stop_byte and command == bail_byte:
                print("Defense: Got 86 command from offense. Now becoming wallflower!")
                # post a confirmatory reply that we got the request
                packet = bytearray([int(start_byte), int(self.my_id), int(stop_byte)])
                port.write(packet)

                self.become_wallflower()
