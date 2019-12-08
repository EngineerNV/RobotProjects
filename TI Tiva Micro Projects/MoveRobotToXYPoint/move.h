/*
 * move.h
 *
 *  Created on: Apr 10, 2018
 *      Author: Nick
 */

#ifndef MOVE_H_
#define MOVE_H_

void moveInit(void);
//movement functions
void moveStop(void);
void moveForward(void);
void moveBackwards(void);
void left_wheel_moveBackwards(void);
void right_wheel_moveBackwards(void);
void left_wheel_moveForward(void);
void right_wheel_moveForward(void);
void move2point(double x, double y);
//turning declarations
void turn_right(double d);
void turn_left(double d);
void turn_bot(double x, double y);
void moveForward_x(double d);

void bump_response(int bump_flag);
void front_response(void);

#endif /* MOVE_H_ */
