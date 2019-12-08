#driveToCoord & friends
#Zack & Nick

from command import comm
import math
import time

#current pose x,y,theta
x0 = 0
y0 = 0
t0 = 0
IRthreshold = 1500
goal_thresh = .5

def driveToCoord(x,y):
	global x0
	global y0
	global IRthreshold
	global goal_thresh
	dist = 1
	while (x != x0 or y != y0) :
		print('Orienting to Coordinate (' + str(x) + ',' + str(y) + ')...')
		orientToCoord(x,y)
		print('Driving forward...')
		driveForwardTillObj(x,y)
		if (x < (x0 + goal_thresh) and x > (x0 - goal_thresh)) and (y < (y0 + goal_thresh) and y > (y0 - goal_thresh)) :
			print('Coordinate (' + str(x) + ',' + str(y) + ') reached!')
			break
		data = getSensorData()
		if data[2] >= IRthreshold :
			print('Obstacle detected, rotating...')
			rotate90()
		data = getSensorData()
		while (data[0] >= IRthreshold or data[1] >= IRthreshold) :
			print('Avoiding obstacle...')
			driveForward(dist)
			data = getSensorData()
	return
	
def orientToCoord(x,y):
	global x0
	global y0
	global t0
	track_width = 9.4	#cm
	goal_angle = math.atan2(y-y0,x-x0)
	print('Goal angle: ' + str(goal_angle))
	print('current angle: ' + str(t0))
	angle = goal_angle - t0
	print(angle)
	d_angle = math.degrees(angle)
	print(d_angle)
	if angle == 0 :
		print('Facing correct direction')
	elif angle < 0 :
		dist = (-d_angle/360) * (track_width * math.pi)
		print('Turning: ' + str(dist))
		dist = dist * 100	#multiplied to retain two decimal points, will be divided on the Tiva side
		dist = int(dist)
		print('Turning: ' + str(dist))
		bump_check = turnRight(dist)
		if bump_check[1] == 0 :
			rotate90()
	else :
		dist = (d_angle/360) * (track_width * math.pi)
		dist = dist * 100	#multiplied to retain two decimal points, will be divided on the Tiva side
		dist = int(dist)
		print('Turning: ' + str(dist))
		bump_check = turnLeft(dist)
		if bump_check[1] == 0 :
			rotate90()
	t0 = t0 + angle
	return

def driveForwardTillObj(x,y):
	global x0
	global y0
	global t0
	global IRthreshold
	global goal_thresh
	dist = 1
	data = getSensorData()
	while data[2] < IRthreshold:
		driveForward(dist)
		if (x < (x0 + goal_thresh) and x > (x0 - goal_thresh)) and (y < (y0 + goal_thresh) and y > (y0 - goal_thresh)) :
			break
		data = getSensorData()
		#time.sleep(.5)
	return

def rotate90():
	global t0
	global IRthreshold
	track_width = 9.4	#cm
	d_angle = 90
	angle = math.radians(d_angle)
	data = getSensorData()
	L = data[0]
	R = data[1]
	F = data[2]
	if F < IRthreshold :
		return
		#do nothing
	elif L >= IRthreshold :
		dist = (d_angle/360) * (track_width * math.pi)
		dist = dist * 100	#multiplied to retain two decimal points, will be divided on the Tiva side
		dist = int(dist)
		bump_check = turnRight(dist)
		if bump_check[1] == 0 :
			rotate90()
		t0 = t0 - angle
	elif R >= IRthreshold :
		dist = (d_angle/360) * (track_width * math.pi)
		dist = dist * 100	#multiplied to retain two decimal points, will be divided on the Tiva side
		dist = int(dist)
		bump_check = turnLeft(dist)
		if bump_check[1] == 0 :
			rotate90()
		t0 = t0 + angle
	else :
		dist = (d_angle/360) * (track_width * math.pi)
		dist = dist * 100	#multiplied to retain two decimal points, will be divided on the Tiva side
		dist = int(dist)
		bump_check = turnLeft(dist)
		if bump_check[1] == 0 :
			rotate90()
		t0 = t0 + angle
	return

def driveForward(dist):
	global x0
	global y0
	global t0
	bump_check = moveForward(dist)
	if bump_check[1] == 0 :
		rotate90()
	y0 = y0 + dist*math.sin(t0)
	y0 = round(y0,2)
	x0 = x0 + dist*math.cos(t0)
	x0 = round(x0,2)
	print('current position (x,y) = (' + str(x0) + ',' + str(y0) + ')')
	return
	

def getSensorData():
	return comm('gsd')

def turnLeft(angle_dist):
	return comm('tl', angle_dist)

def turnRight(angle_dist):
	return comm('tr', angle_dist)

def moveForward(dist):
	return comm('mf', dist)