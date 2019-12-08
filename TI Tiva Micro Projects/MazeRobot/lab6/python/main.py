#main
#Zack & Nick
from command import comm

def main():
	command = ''
	while command != 'q':	#exit the loop by typing 'q'
		command = input("\nEnter bot command: ")
		if command != 'q' :
			comm(command)
	return
	
if __name__ == "__main__":
   main()
