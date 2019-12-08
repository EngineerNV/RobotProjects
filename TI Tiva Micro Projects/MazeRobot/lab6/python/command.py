from serial_pi import sendCommand

def comm(command):
	x = 0	#base case for commands that don't have an argument
	num = 3	#base number for the serial read (confirmation)
	if command == 'stop' :
		sendCommand(0x0,x,num)
	elif command == 'mf' :
		dist = input("\nInput distance to travel: ")
		sendCommand(0x1,dist,num)
	elif command == 'tl' :
		angle = input("\nInput angle to turn to: ")
		sendCommand(0x2,angle,num)
	elif command == 'tr' :
		angle = input("\nInput angle to turn to: ")
		sendCommand(0x3,angle,num)
	elif command == 'oaof' :
		onoff = input("\nInput 1 for on or 0 for off: ")
		sendCommand(0x4,onoff,num)
	elif command == 'gsd' :
		num = 5
		sendCommand(0x5,x,num)
	else :
		print('Command not found! Enter one of the following:')
		print('stop : ends all operations')
		print('mf : Move Forward to the input distance (cm)')
		print('tl : Turn Left to the input angle (deg)')
		print('tr : Turn Right to the input angle (deg)')
		print('oaof : Obstacle Avoidance On/oFf sends the input on (1) or off (2)')
		print('gsd : Get Sensor Data sends a request for current IR distances')
	return;