from serial_pi import sendCommand

def comm(command, arg = 0):
	#x = 0	#base case for commands that don't have an argument
	num = 3	#base number for the serial read (confirmation)
	if command == 'stop' :
		data = sendCommand(0x0,arg,num)
	elif command == 'mf' :
		#if arg == 0 :
			#arg = input("\nInput distance to travel: ")
		data = sendCommand(0x1,arg,num)
	elif command == 'tl' :
		#if arg == 0 :
			#arg = input("\nInput angle to turn to: ")
		data = sendCommand(0x2,arg,num)
	elif command == 'tr' :
		#if arg == 0 :
			#arg = input("\nInput angle to turn to: ")
		data = sendCommand(0x3,arg,num)
	elif command == 'oaof' :
		#if arg == 0 :
			#arg = input("\nInput 1 for on or 0 for off: ")
		data = sendCommand(0x4,arg,num)
	elif command == 'gsd' :
		num = 14
		data = sendCommand(0x5,arg,num)
	else :
		print('Command not found! Enter one of the following:')
		print('stop : ends all operations')
		print('mf : Move Forward to the input distance (cm)')
		print('tl : Turn Left to the input angle (deg)')
		print('tr : Turn Right to the input angle (deg)')
		print('oaof : Obstacle Avoidance On/oFf sends the input on (1) or off (2)')
		print('gsd : Get Sensor Data sends a request for current IR distances')
	return data;