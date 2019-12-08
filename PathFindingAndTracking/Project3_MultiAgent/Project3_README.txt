Created by Nicholas Vaughn and Courtney Banh 


Project 3: Multi-Agent and Communications

In order to run this program you have to have Python 3 installed. 

Here is the command to run it:

python3 robotCommProtocol.py 

robotCommProtocol.py fully contains the communication protocol for Simon Says.

PWMrobotControl.py is the most recent motion control code to communicate with the microcontroller.

It is used in robotCommProtocol.py.

robotCommProtocol.py contains all the code for playing a game of Simon Says. 
There are three methods inside it: simon(), player(), and performCommand(). simon() and player() 
perform their respective parts of the finite state machine representing the communication 
protocol. performCommand() interprets the received message and executes the correct task.