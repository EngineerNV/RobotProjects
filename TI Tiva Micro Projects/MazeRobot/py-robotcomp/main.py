#main
#Zack & Nick
from command import comm
import dtc
import rotate
import himm
from map import Map

goal_positions = [[0,16],[0,17],[0,18],[0,19]] 
def main():
	cur_map = Map(35,20)
	command = ''
	command = input("\nPress any button to start magic alg, by Over9000: ")
	while 1:	#exit the loop by typing 'q'
		row =cur_map.position[0]
		col = cur_map.position[1]
		if (goal_positions[0][0] == row and goal_positions[0][1] == col) or (goal_positions[1][0] == row and goal_positions[1][1] == col) or (goal_positions[2][0] == row and goal_positions[2][1] == col) or (goal_positions[3][0] == row and goal_positions[3][1] == col):
			rotate.rotateL90()
			rotate.rotateR90()
			rotate.rotate180()
			break
		cur_map.print_map()
		himm.scan(cur_map)
		himm.scan(cur_map)
		himm.scan(cur_map)
		himm.perform_move(cur_map)
	return
	
if __name__ == "__main__":
   main()
