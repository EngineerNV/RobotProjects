#created NickThePowerful and sidekick ZackTheSlightlyLessPowerful
import struct 
import serial


def init_serial():
	ser = serial.Serial("/dev/ttyS0")
	ser.baudrate = 9600
	return ser                     #Set baud rate to 9600
def serial_write(data,transmit):
	transmit.write(data)
def serial_read(ser, num): 
	return ser.read(num)
	
def sendCommand(command, arg, num) :
	#recieve = []
	start = 0xAA
	stop = 0x55
	ser = init_serial()
	arg = int(arg) # may not want to always have the arguments be integers
	data = struct.pack('BBiB', start, command, arg, stop )
	serial_write(data,ser)
	recieve = serial_read(ser, num)
	if num == 14:
		data1 = struct.unpack('BBBBBBBBBBBBBB',recieve)
		#print(data1)
		data1 = data1[1:13]
		#print(data1)
		data1 = bytes(data1)
		#print(data1)
		data1 = struct.unpack('iii',data1)
	else:
		data1 = struct.unpack('BBB',recieve)
	print('Returned data: ' + str(data1))
	return data1