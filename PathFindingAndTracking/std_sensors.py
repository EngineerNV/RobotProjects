#created by Nick Vaughn
#used to get space seperated data and find std deviation
#each newline is a new line of sensor data from each sensor within each column 
import statistics

file = input("enter file name: ")


f = open(file, "r")
list_middle = []
list_right = []
list_left = []
for line in f:
	fixed_line = line.replace("\n","")
	split_line =  line.split(' ')
	list_left.append(float(split_line[0]))
	list_middle.append(float(split_line[1]))
	list_right.append(float(split_line[2]))
	
ans_left = statistics.variance(list_left)
ans_middle = statistics.variance(list_middle)
ans_right = statistics.variance(list_right)

print("Var Left: " + str(ans_left) + " Var Middle: " + str(ans_middle) + " Var Right: " + str(ans_right))