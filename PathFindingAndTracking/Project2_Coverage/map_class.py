# created by NickThePowerful
#this class helps the robot have information about its environment 
import sys 

NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4

class map_class:
	
	
	def __init__(self,h,w):
		
		self.map = [[0 for x in range(w)] for y in range(h)]
		self.pos = (0,0)# position is a tuple for x and y 
		self.dir = NORTH
		self.h = h
		self.w = w
		self.init_map()
		
	def init_map(self): 
		obs = 0 #booleans for explored cells and obstacles
		exp = 0 
		for row in range(0,self.h):
			for col in range(0,self.w):
				self.map[row][col] = (exp,obs)
		self.map[0][0] = (1,0) #putting starting position as explored
		
	def turnRight(self):
		
		
		if self.dir == WEST:
			self.dir = NORTH
		else: 
			self.dir = self.dir + 1 
	
	def turnLeft(self):
		if self.dir == NORTH:
			self.dir = WEST
		else: 
			self.dir = self.dir - 1	
	
	def moveForward(self):
		if self.dir == NORTH:  
			self.pos =  (self.pos[0], self.pos[1]+1)#row+1
			self.map[self.pos[1]][self.pos[0]] = (1,0) # (explored, object)
		elif self.dir == WEST: 
			self.pos =  (self.pos[0] - 1, self.pos[1])#col-1 
			self.map[self.pos[1]][self.pos[0]] = (1,0)
		elif self.dir == EAST: 
			self.pos = (self.pos[0] + 1, self.pos[1])#col +1
			self.map[self.pos[1]][self.pos[0]] = (1,0)
		else: #SOUTH  
			self.pos = (self.pos[0],self.pos[1] -1) #row - 1
			self.map[self.pos[1]][self.pos[0]] = (1,0)
	
	#Updating where found objects are
	def foundObjLeft(self):
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return #dont update map if out of bounds 
			self.map[self.pos[1]][self.pos[0]-1] = (1,1) #col - 1
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return #dont update map if out of bounds
			self.map[self.pos[1]-1][self.pos[0]] = (1,1) # row + 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return #dont update map if out of bounds
			self.map[self.pos[1]+1][self.pos[0]] = (1,1) # row - 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return #dont update map if out of bounds
			self.map[self.pos[1]][self.pos[0]+1] = (1,1) # col - 1
			
	def foundObjRight(self):
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return #dont update map if out of bounds 
			self.map[self.pos[1]][self.pos[0]+1] = (1,1) #col + 1
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return #dont update map if out of bounds
			self.map[self.pos[1]+1][self.pos[0]] = (1,1) # row + 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return #dont update map if out of bounds
			self.map[self.pos[1]-1][self.pos[0]] = (1,1) # row - 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return #dont update map if out of bounds
			self.map[self.pos[1]][self.pos[0]-1] = (1,1) # col - 1
	
	def foundObjFront(self):
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return #dont update map if out of bounds 
			self.map[self.pos[1]+1][self.pos[0]] = (1,1) #row + 1
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return #dont update map if out of bounds
			self.map[self.pos[1]][self.pos[0]-1] = (1,1) # col - 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return #dont update map if out of bounds
			self.map[self.pos[1]][self.pos[0]+1] = (1,1) # col + 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return #dont update map if out of bounds
			self.map[self.pos[1]-1][self.pos[0]] = (1,1) # row - 1
	
	#checking if cells are clean 
	def isLeftClean(self):
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return 1#dont update map if out of bounds 
			return self.map[self.pos[1]][self.pos[0]-1][0] #col - 1
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]-1][self.pos[0]][0] # row - 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]+1][self.pos[0]][0] # row + 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]][self.pos[0]+1][0] # col + 1
			
	def isRightClean(self):
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return 1 #dont update map if out of bounds 
			return self.map[self.pos[1]][self.pos[0]+1][0] #col + 1
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]+1][self.pos[0]][0] # row + 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]-1][self.pos[0]][0] # row - 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]][self.pos[0]-1][0] # col - 1
			
	def isFrontClean(self):
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return 1  
			return self.map[self.pos[1]+1][self.pos[0]][0] # check [row + 1][col] for explored 
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return 1 
			return self.map[self.pos[1]][self.pos[0]-1][0] # col - 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return 1 
			return self.map[self.pos[1]][self.pos[0]+1][0] # col + 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return 1
			return self.map[self.pos[1]-1][self.pos[0]][0] # row - 1
	
	def isBackClean(self):	
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return 1  
			return self.map[self.pos[1]-1][self.pos[0]][0] # check [row - 1][col] for explored 
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return 1 
			return self.map[self.pos[1]][self.pos[0]+1][0] # col + 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return 1 
			return self.map[self.pos[1]][self.pos[0]-1][0] # col - 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return 1
			return self.map[self.pos[1]+1][self.pos[0]][0] # row + 1
	
	
	# checking for objects in map 
	
	def isObjLeft(self):
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return 1#dont update map if out of bounds 
			return self.map[self.pos[1]][self.pos[0]-1][1] #col - 1
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]-1][self.pos[0]][1] # row - 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]+1][self.pos[0]][1] # row + 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]][self.pos[0]+1][1] # col + 1
			
	def isObjRight(self):
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return 1 #dont update map if out of bounds 
			return self.map[self.pos[1]][self.pos[0]+1][1] #col + 1
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]+1][self.pos[0]][1] # row + 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]-1][self.pos[0]][1] # row - 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return 1#dont update map if out of bounds
			return self.map[self.pos[1]][self.pos[0]-1][1] # col - 1
			
	def isObjFront(self):
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return 1  
			return self.map[self.pos[1]+1][self.pos[0]][1] # check [row + 1][col] for explored 
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return 1 
			return self.map[self.pos[1]][self.pos[0]-1][1] # col - 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return 1 
			return self.map[self.pos[1]][self.pos[0]+1][1] # col + 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return 1
			return self.map[self.pos[1]-1][self.pos[0]][1] # row - 1
	
	def isObjBack(self):	
		if self.dir == NORTH:
			if not self.inBounds(self.pos[1]-1,self.pos[0]):
				return 1  
			return self.map[self.pos[1]-1][self.pos[0]][1] # check [row - 1][col] for explored 
		elif self.dir == WEST:
			if not self.inBounds(self.pos[1],self.pos[0]+1):
				return 1 
			return self.map[self.pos[1]][self.pos[0]+1][1] # col + 1
		elif self.dir == EAST:  
			if not self.inBounds(self.pos[1],self.pos[0]-1):
				return 1 
			return self.map[self.pos[1]][self.pos[0]-1][1] # col - 1
		else: #SOUTH 
			if not self.inBounds(self.pos[1]+1,self.pos[0]):
				return 1
			return self.map[self.pos[1]+1][self.pos[0]][1] # row + 1
	
	
	
	def inBounds(self, row,col):
		height = self.h -1 # putting the negative one because we start at 0 
		width = self.w -1
		
		if row > height or row < 0:
			return 0
		if col > width or col < 0:
			return 0
			
		return 1
	
	# check clean cell for all 4 neighbors  
	# obstacle check 
	

	
	def print_map(self):
		for row in range(self.h-1,-1,-1):
			for col in range(0,self.w):
				if row == self.pos[1] and col == self.pos[0]:
					if self.dir == NORTH:
						print("^ ",end="")
					elif self.dir == WEST:
						print("< ",end="")
					elif self.dir == EAST:
						print("> ",end="")
					else: # SOUTH
						print("v ",end="")
				else: # if we are not looking at current position
					cell = self.map[row][col]
					if cell[1] == 1: #obstacle seen 
						print("# ", end="")
					elif cell[0] == 1: # cell been explored
						print("* ", end="")
					else: # cell hasnt been explored
						print("? ", end="")
	
			print("")# endline when we are done printing our a row 
	
	
instant = map_class(15,15)

##instant.moveForward()
##instant.moveForward()
##instant.foundObjRight()
##instant.print_map()	
##print(instant.isObjFront())