import math

class Map:
	def __init__(self,row,col):
		self.row = row 
		self.col = col
		self.grid = [[0 for x in range(col)] for y in range(row)] # each grid square will update the HIMM value, but is intialized to 0
		self.visited = [[0 for x in range(col)] for y in range(row)] # this keep booleans of whether we have visited a space before
		self.position = [7,11]
		self.visited[7][11] = 1  
		self.angle =  180 # will only use 90 degree turns to travel to each coordinate
	def print_map(self):
		print('_____Map Positions____')
		for r in range(self.row-1,-1,-1):
			
				# if self.position[0] == r and self.position[1]:
					# print(' p ')
				# else:
			print(self.grid[r])
	def been_here_before(self,row,col):
		return self.visited[row][col]
	def update_position(self,row,col,angle): #this will update our current position, not needed but makes for faster coding
		self.position[0] = row 
		self.position[1] = col
		self.visited[row][col]
		self.angle = angle
	def set_grid(self,row,col,val): # this will set the value at a grid square 
		self.grid[row][col] = val
	def check_grid(self,row,col): # this will give us a value from a grid square 
		return self.grid[row][col]