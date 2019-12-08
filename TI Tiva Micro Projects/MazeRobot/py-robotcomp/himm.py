from map import Map
import time 
import rotate
import dtc 
#created by Nicholas Vaughn, file contains functions that implements the main HIMM algorithm with the MAP class
#the MAP class is a container for the values, but this is the actual map building algorithm.

#these lists in list will be used to define the aread of our goal, everytime we update our map, we check to see if our new current position is in the goal,
#if not we continue to move to find it. 

EAST = 0
NORTH = 90
WEST = 180
SOUTH =270
#sensor value constants - putting in the lowest and highest values I see from data to create thresholds. Some of these might not be used
inch1_min = 3468
inch1_max = 3562
inch2_min = 2374
inch2_max = 2397
inch3_min = 1744
inch3_max = 1864
inch4_min = 1366
inch4_max = 1464
inch5_min = 1092
inch5_max = 1305
inch6_min = 950
inch6_max = 1070
inch7_min = 820
inch7_max = 910
inch8_min = 705
inch8_max = 816
inch9_min = 600
inch9_max = 705
inch10_min = 521
inch10_max = 590
inch12_min = 400
inch12_max = 520

def ir_sense(ir_data): # we only care if there is at least 6 inches or 12 inches of free space, so ill return those values, if there are no free spaces, ill return 0  
	# use sensor data to determine distance  
	if ir_data <= inch8_max:
		return 1	
	else:
		return 0

def update_grid_square(dir,free_spaces,row,col,cur_map): #this is only for the update status 
	if dir == NORTH:
		if free_spaces == 1:
			v1 = cur_map.check_grid(row+1,col)
			if v1 >= 0: #we dont decrement when value is -1, we know its a free space for sure
				cur_map.set_grid(row+1,col,v1-1)
		else: #we have no free values
			v1 = cur_map.check_grid(row+1,col)
			if v1 < 15: #we dont decrement when value is -1, we know its a free space for sure
				cur_map.set_grid(row+1,col,v1+3)
	elif dir == EAST:
		if free_spaces == 1:
			v1 = cur_map.check_grid(row,col+1)
			if v1 >= 0: #we dont decrement when value is -1, we know its a free space for sure
				cur_map.set_grid(row,col+1,v1-1)
		else: #we have no free values
			v1 = cur_map.check_grid(row,col+1)
			if v1 < 15: #we dont decrement when value is -1, we know its a free space for sure
				cur_map.set_grid(row,col+1,v1+3)
	elif dir == WEST:
		if free_spaces == 1:
			v1 = cur_map.check_grid(row,col-1)
			if v1 >= 0: #we dont decrement when value is -1, we know its a free space for sure
				cur_map.set_grid(row,col-1,v1-1)
		else: #we have no free values
			v1 = cur_map.check_grid(row,col-1)
			if v1 < 15: #we dont decrement when value is -1, we know its a free space for sure
				cur_map.set_grid(row,col-1,v1+3)
	else:# south
		if free_spaces == 1:
			v1 = cur_map.check_grid(row-1,col)
			if v1 >= 0: #we dont decrement when value is -1, we know its a free space for sure
				cur_map.set_grid(row-1,col,v1-1)
		else: #we have no free values
			v1 = cur_map.check_grid(row-1,col)
			if v1 < 15: #we dont decrement when value is -1, we know its a free space for sure
				cur_map.set_grid(row-1,col,v1+3)

def update_stats(cur_map, left, front, right):
	# angle makes a difference in what values we update, it orients us in the unit square
	cur_row = cur_map.position[0]
	cur_col = cur_map.position[1]
	if cur_map.angle == EAST: #what angle are we facing? 
		update_grid_square(NORTH,left,cur_row,cur_col,cur_map)
		update_grid_square(EAST,front,cur_row,cur_col,cur_map)
		update_grid_square(SOUTH,right,cur_row,cur_col,cur_map)
	elif cur_map.angle == NORTH:
		update_grid_square(WEST,left,cur_row,cur_col,cur_map)
		update_grid_square(NORTH,front,cur_row,cur_col,cur_map)
		update_grid_square(EAST,right,cur_row,cur_col,cur_map)
	elif cur_map.angle == WEST:
		update_grid_square(SOUTH,left,cur_row,cur_col,cur_map)
		update_grid_square(WEST,front,cur_row,cur_col,cur_map)
		update_grid_square(NORTH,right,cur_row,cur_col,cur_map)
	elif cur_map.angle == SOUTH:
		update_grid_square(EAST,left,cur_row,cur_col,cur_map)
		update_grid_square(SOUTH,front,cur_row,cur_col,cur_map)
		update_grid_square(WEST,right,cur_row,cur_col,cur_map)

def scan(cur_map):
	right = 0
	left = 0
	front = 0
	for i in range(5): # going to grab values and get average to help with noise 
		#grabSensor Data command  
		#need to update each value
		data = dtc.getSensorData()
		right = right + data[1]
		front = front + data[2]
		left = left + data[0]
		time.sleep(.1) #this will space out our reads 
	#getting average 
	right = right/5
	left = left/5
	front = front/5
	#getting inches
	l = ir_sense(left)
	r = ir_sense(right)
	f = ir_sense(front)
	update_stats(cur_map,l,f,r)
	
def perform_move(cur_map):
	cur_row = cur_map.position[0]
	cur_col = cur_map.position[1]
	north_row = cur_row+1
	north_col = cur_col
	west_row = cur_row
	west_col = cur_col-1
	east_row = cur_row
	east_col = cur_col+1
	south_row = cur_row-1
	south_col = cur_col
	l_value = 0
	f_value = 0
	r_value = 0
	if cur_map.angle == EAST: #what angle are we facing? 
		l_value = cur_map.check_grid(north_row,north_col) #North 
		f_value = cur_map.check_grid(east_row,east_col)#East
		r_value = cur_map.check_grid(south_row,south_col)#South
		if f_value <=l_value and f_value <=r_value and f_value<3 and cur_map.been_here_before(east_row,east_col) == 0:
			#Move 8 inches forward
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(EAST,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(east_row,east_col,EAST)
		elif l_value <=f_value and l_value <=r_value and l_value<3 and cur_map.been_here_before(north_row,north_col) == 0:
			# PERFORM NORTH TURN (90 degrees left) and move 8 inches
			rotate.rotateL90()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(NORTH,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(north_row,north_col,NORTH)
		elif r_value <=f_value and r_value <=l_value and r_value<3 and cur_map.been_here_before(south_row,south_col) == 0:
			#Perform SOUTH TURN (90 Degrees Right) and move 8 inches
			rotate.rotateR90()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(SOUTH,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(south_row,south_col,SOUTH)	
		else: # we dont have any good values local min 
			# perform 180 degree turn then go back to to position
			rotate.rotate180()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(WEST,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(west_row,west_col,WEST) 
	elif cur_map.angle == NORTH:
		l_value = cur_map.check_grid(cur_row,cur_col-1)#West 
		f_value = cur_map.check_grid(cur_row+1,cur_col)#North
		r_value = cur_map.check_grid(cur_row,cur_col+1)#East
		if f_value <=l_value and f_value <=r_value and f_value<3 and cur_map.been_here_before(north_row,north_col) == 0:
			#Move 8 inches forward
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(NORTH,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(north_row,north_col,NORTH)
		elif l_value <=f_value and l_value <=r_value and l_value<3 and cur_map.been_here_before(west_row,west_col) == 0:
			# PERFORM WEST TURN (90 degrees left) and move 8 inches
			rotate.rotateL90()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(WEST,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(west_row,west_col,WEST) 
		elif r_value <=f_value and r_value <=l_value and r_value<3 and cur_map.been_here_before(east_row,east_col) == 0:
			#Perform EAST TURN (90 Degrees Right) and move 8 inches
			rotate.rotateR90()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(EAST,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(east_row,east_col,EAST)	
		else: # we dont have any good values local min 
			# perform 180 degree turn, then go there
			rotate.rotate180()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(SOUTH,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(south_row,south_col,SOUTH)
	elif cur_map.angle == WEST:
		l_value = cur_map.check_grid(cur_row-1,cur_col)#South 
		f_value = cur_map.check_grid(cur_row,cur_col-1)#West
		r_value = cur_map.check_grid(cur_row+1,cur_col)#North
		if f_value <=l_value and f_value <=r_value and f_value<3 and cur_map.been_here_before(west_row,west_col) == 0:
			#Move 8 inches forward
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(WEST,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(west_row,west_col,WEST)
		elif l_value <=f_value and l_value <=r_value and l_value<3 and cur_map.been_here_before(south_row,south_col) == 0:
			# PERFORM SOUTH TURN (90 degrees left) and move 8 inches
			rotate.rotateL90()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(SOUTH,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(south_row,south_col,SOUTH)
		elif r_value <=f_value and r_value <=l_value and r_value<3 and cur_map.been_here_before(north_row,north_col) == 0:
			#Perform NORTH TURN (90 Degrees Right) and move 8 inches
			rotate.rotateR90()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(NORTH,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(north_row,north_col,NORTH)	
		else: # we dont have any good values local min 
			# perform 180 degree turn
			rotate.rotate180()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(EAST,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(east_row,east_col,EAST)
	elif cur_map.angle == SOUTH:
		l_value = cur_map.check_grid(cur_row,cur_col+1)#East 
		f_value = cur_map.check_grid(cur_row-1,cur_col)#South
		r_value = cur_map.check_grid(cur_row,cur_col-1)#West
		if f_value <=l_value and f_value <=r_value and f_value<3 and cur_map.been_here_before(south_row,south_col) == 0:
			#Move 8 inches forward
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(SOUTH,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(south_row,south_col,SOUTH)
		elif l_value <=f_value and l_value <=r_value and l_value<3 and cur_map.been_here_before(east_row,east_col) == 0:
			# PERFORM EAST TURN (90 degrees left) and move 8 inches
			rotate.rotateL90()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(EAST,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(east_row,east_col,EAST)
		elif r_value <=f_value and r_value <=l_value and r_value<3 and cur_map.been_here_before(west_row,west_col) == 0:
			#Perform WEST TURN (90 Degrees Right) and move 8 inches
			rotate.rotateR90()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(WEST,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(west_row,west_col,WEST)	
		else: # we dont have any good values local min 
			# perform 180 degree turn
			rotate.rotate180()
			bump = dtc.moveForward(8)
			if bump[1] == 0:
				update_grid_square(NORTH,0,cur_row,cur_col,cur_map)
			else:
				cur_map.update_position(north_row,north_col,NORTH)