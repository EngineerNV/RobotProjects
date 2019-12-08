import serial
from time import sleep

def connectXBee ():
	ser = serial.Serial("/dev/ttyUSB0", 57600, timeout = 5)
	print("Connected to device: ", ser.name)
	return ser

# ID 1 can only communicate with ID 3 and ID 2 can only communicate with ID 4.

def sendPacket (ser, ID, flag):
	if (ID == 1):
		othID = 3
	elif (ID == 2):
		othID = 4
	elif (ID == 3):
		othID = 1
	else:
		othID = 2

	print("Sending packet.")
	packet = bytearray(); packet.append(0xDA); packet.append(ID); packet.append(flag); packet.append(othID); packet.append(0xDB)
	ser.write(packet)
	sleep(1)

	breakFlag = 0; tryN = 0
	while True:
		if (tryN >= 3):					# On the third try, remove ID from list and get different Simon.
			print("We're flying solo today, boys.")
			return 1
		
		datRed = []
		data = int.from_bytes(ser.read(1), 'little')
		if (data == 0xDA):
			print("Reading an acknowledge...")
			datRed.append(data)
			while (data != 0xDB):
				data = int.from_bytes(ser.read(1), 'little')
				datRed.append(data)
			# Check if it was from the correct brobot:
			if (datRed[1] == othID and datRed[2] == 0x06):
				print("Robot acknowledges.")
				breakFlag = 1
		if (breakFlag == 1):
			return 0
		else:
			tryN = tryN + 1
			ser.write(packet)

def readPacket (ser, ID):
	if (ID == 1):
		othID = 3
	elif (ID == 2):
		othID = 4
	elif (ID == 3):
		othID = 1
	else:
		othID = 2

	breakFlag = 0
	while True:
		datRed = []
		data = int.from_bytes(ser.read(1), 'little')
		if (data == 0xDA):
			print("Reading a packet...")
			print(data)
			datRed.append(data)
			while (data != 0xDB):
				data = int.from_bytes(ser.read(1), 'little')
				datRed.append(data)
				print(data)
			if (datRed[1] == othID):
				break

	print("Sending acknowledge.")
	sleep(1)
	packet = bytearray(); packet.append(0xDA); packet.append(ID); packet.append(0x6); packet.append(othID); packet.append(0xDB)
	ser.write(packet)
	sleep(1)
	return datRed[2]




