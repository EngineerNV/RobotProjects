#main
#Zack & Nick
from command import comm
import dtc

def main():
	command = ''
	while command != 'q':	#exit the loop by typing 'q'
		command = input("\nWould you like to run Drive To Coordinate? (y/n): ")
		if command == 'y':
			x = input("Enter x coord: ")
			x = int(x)
			y = input("Enter y coord: ")
			y = int(y)
			dtc.driveToCoord(x,y)		
		#command = input("\nEnter bot command: ")
		#if command != 'q' :
		#	comm(command)
	return
	
if __name__ == "__main__":
   main()
