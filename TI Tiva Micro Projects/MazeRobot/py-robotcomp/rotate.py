from command import comm
import math

def rotateR90():
	track_width = 9.4	#cm
	d_angle = 90
	dist = (d_angle/360) * (track_width * math.pi)
	dist = dist * 100	#multiplied to retain two decimal points, will be divided on the Tiva side
	dist = int(dist)
	return comm('tr', dist)
	
def rotateL90():
	track_width = 9.4	#cm
	d_angle = 90
	dist = (d_angle/360) * (track_width * math.pi)
	dist = dist * 100	#multiplied to retain two decimal points, will be divided on the Tiva side
	dist = int(dist)
	return comm('tl', dist)

def rotate180():
	track_width = 9.4	#cm
	d_angle = 200
	dist = (d_angle/360) * (track_width * math.pi)
	dist = dist * 100	#multiplied to retain two decimal points, will be divided on the Tiva side
	dist = int(dist)
	return comm('tl', dist)