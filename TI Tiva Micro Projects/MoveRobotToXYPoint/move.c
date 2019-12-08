/*
 * move.c
 *
 *  Created on: Apr 10, 2018
 *      Author: Nick
 */
#include "move.h"


#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include "inc/tm4c123gh6pm.h"


//#include "driverlib/gpio.c"
#include "driverlib/gpio.h"
#include "driverlib/pin_map.h"
#include "driverlib/uart.h"

#include <math.h>

//#include "driverlib/sysctl.c"
#include "driverlib/sysctl.h"


#include "inc/hw_types.h"
#include "inc/hw_memmap.h"

//#include "driverlib/interrupt.c"
#include "driverlib/interrupt.h"

//#include "driverlib/pwm.c"
#include "driverlib/pwm.h"


//gpio port B base
#define GPIO_PORT_B ((volatile uint32_t *)0x40059000)
//gpio port F base
#define GPIO_PORT_F ((volatile uint32_t *)0x4005D000)

//offsets for the GPIO
#define GPIO_DATA   (0x3FC >> 2)
#define GPIO_DIR   (0x400 >> 2)
#define GPIO_DEN   (0x51C >> 2)

//general base for the GPIO
#define GPIO_BASE   ((volatile uint32_t *)0x400FE000)

//offsets used for general base
#define hp_offset   (0x06C >> 2) //high performance bus controll
#define rcgc_offset    (0x608 >> 2)

#define af_offset (0x420 >>2) //gpioafcl

#define pctl_offset (0x52C >> 2) //gpiopctl register

#define LEFT_BUMP 1
#define RIGHT_BUMP 2
#define FRONT_BUMP 3

//#include "lab7_def.h"

extern double left_wheel_edge_count;
extern double right_wheel_edge_count;
extern int bump_flag;
extern int toggle;
void moveInit(void)
{
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOC);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOD);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOE);

    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOA))
    {
    }
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOC))
    {
    }
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOD))
    {
    }

    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOE))
    {
    }


    //interrupt inputs

    GPIOPinTypeGPIOInput(GPIO_PORTA_BASE, //this is for the interrupt from the bumper sensor
            GPIO_PIN_5);

    GPIOPinTypeGPIOInput(GPIO_PORTC_BASE,
        GPIO_PIN_5);
    GPIOPinTypeGPIOInput(GPIO_PORTD_BASE,
            GPIO_PIN_2);

    //epins for infaraed Zack stuff
    //GPIOPinTypeGPIOInput(GPIO_PORTE_BASE,
                //(GPIO_PIN_2 | GPIO_PIN_3 | GPIO_PIN_1 ));

    GPIOPinTypeADC(GPIO_PORTE_BASE, (GPIO_PIN_2 | GPIO_PIN_3 | GPIO_PIN_1));



    // left Wheel Movement pins
    GPIOPinTypeGPIOOutput(GPIO_PORTA_BASE, GPIO_PIN_2 | GPIO_PIN_3);
    GPIOPinWrite(GPIO_PORTA_BASE,
            (GPIO_PIN_2 | GPIO_PIN_3),
            (GPIO_PIN_2 | GPIO_PIN_3 ));

    //activating port B
    GPIO_BASE[rcgc_offset] |= (1<<1);
    GPIO_BASE[rcgc_offset] |= (1<<1);
    //activating port F
    GPIO_BASE[rcgc_offset] |= (1<<5);
    GPIO_BASE[rcgc_offset] |= (1<<5);
    //activating the high performance HP setting for port B
    GPIO_BASE[hp_offset] |= (1<<1);
    GPIO_BASE[hp_offset] |= (1<<5);

    GPIO_PORT_B[GPIO_DIR] |= (1<<6) | (1<<7) | (1<<2) | (1<<3) | (1<<4);
    GPIO_PORT_B[GPIO_DEN] |= (1<<6) | (1<<7) | (1<<2) | (1<<3) | (1<<4);

    //port f is used to activate LEDS
    GPIO_PORT_F[GPIO_DIR] |= (1<<2);//blue led
    GPIO_PORT_F[GPIO_DEN] |= (1<<2);

    //gpio data Port B
    GPIO_PORT_B[GPIO_DATA] |= (1<<2); //output pin for right side of manual IN2
    GPIO_PORT_B[GPIO_DATA] |= (1<<3);//ouptut pin for left side of manual IN1
    GPIO_PORT_B[GPIO_DATA] |= (1<<4); // standby pin, keep high
    GPIO_PORT_B[GPIO_DATA] |= (1<<6); //PWM 0 pin
    GPIO_PORT_B[GPIO_DATA] |= (1<<7); // PWM 1 pin

    //Activating alternative functions for pins
    GPIO_PORT_B[af_offset] |= (1<<6);
    GPIO_PORT_B[af_offset] |= (1<<7);
    GPIO_PORT_B[pctl_offset] |=(0x4 << 28);
    GPIO_PORT_B[pctl_offset] |= (0x4 << 24);

    // Enable the PWM0 peripheral
    //
    SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);
    // Wait for the PWM0 module to be ready.
    //
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_PWM0))
    {

    }
    //
    // Configure the PWM generator for count down mode with immediate updates
    // to the parameters.
    //
    PWMGenConfigure(PWM0_BASE, PWM_GEN_0,
    PWM_GEN_MODE_DOWN | PWM_GEN_MODE_NO_SYNC);
    //
    // Set the period. For a 50 KHz frequency, the period = 1/50,000, or 20
    // microseconds. For a 20 MHz clock, this translates to 400 clock ticks.
    // Use this value to set the period.
    //
    //Clock actually runs at 16Mhz   16Mhz/50000 = 320
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_0, 320);
    //
    // Set the pulse width of PWM0 for a 50% duty cycle.
    //
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_0, 160); // pin pb6 left wheel
    //
    // Set the pulse width of PWM1 for a 50% duty cycle.
    //
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, 152); //pin pb7 right wheel
    //
    // Start the timers in generator 0.
    //
    PWMGenEnable(PWM0_BASE, PWM_GEN_0);
    //
    // Enable the outputs.
    //
    PWMOutputState(PWM0_BASE, (PWM_OUT_0_BIT | PWM_OUT_1_BIT), true);
    return 0;
}

void bump_response(int bump_type)
{
    double d = .29*right_wheel_edge_count; //go back the distance we just traveled
    //reset edges for next movement
    left_wheel_edge_count=0;
    right_wheel_edge_count=0;

    if(bump_type == LEFT_BUMP)
    {
    // left wheel move forward
        left_wheel_moveForward();
        //right wheel move backward
        right_wheel_moveBackwards();
        //continue to turn until we reach the distance giving us the angle - .29 cm a tick
        while( (.29*left_wheel_edge_count) < d );

    }
    else if(bump_type == RIGHT_BUMP)
    {
        left_wheel_moveBackwards();
                //right wheel move backward
        right_wheel_moveForward();
                //continue to turn until we reach the distance giving us the angle - .29 cm a tick
        while( (.29*left_wheel_edge_count) < d );
    }
    else if(bump_type == FRONT_BUMP)
    {
        moveBackwards();
        while( (.29*left_wheel_edge_count) < d );
    }


    moveStop();
    //reset edges for next movement
    left_wheel_edge_count=0;
    right_wheel_edge_count=0;

    //bump_flag = 0;
}


void front_response(void) // is activated when we have Left and Right = 1 or F = 1
{
    double d = 7.62; //3 inch movement
    //reset edges for next movement
    left_wheel_edge_count=0;
    right_wheel_edge_count=0;
    moveBackwards();
    while( (.29*left_wheel_edge_count) < d );
    moveStop();
    //reset edges for next movement
    left_wheel_edge_count=0;
    right_wheel_edge_count=0;
    turn_bot(-.6,1);
}


void moveForward_x(double d) // give distance in cms
{
    // left wheel move forward
    left_wheel_moveForward();
    //right wheel move backward
    right_wheel_moveForward();
    //continue to turn until we reach the distance giving us the angle - .29 cm a tick
    while( (.29*right_wheel_edge_count) < d && bump_flag ==0 );
    moveStop();

    if(bump_flag)
        bump_response(FRONT_BUMP);

    //reset edges for next movement
    left_wheel_edge_count=0;
    right_wheel_edge_count=0;
}

void turn_right(double d)
{
    d = d/100;
    // left wheel move forward
    left_wheel_moveForward();
    //right wheel move backward
    right_wheel_moveBackwards();
    //continue to turn until we reach the distance giving us the angle - .29 cm a tick
    while( (.29*right_wheel_edge_count) < d  && bump_flag == 0 );
    moveStop();

    if(bump_flag)
        bump_response(RIGHT_BUMP);

    //reset edges for next movement
    left_wheel_edge_count=0;
    right_wheel_edge_count=0;
}

void turn_left(double d)
{
    d = d/100;
    // right wheel move forward
    right_wheel_moveForward();
    //left wheel move backward
    left_wheel_moveBackwards();
    //continue to turn until we reach the distance giving us the angle - .29 cm a tick
    while( (.29*left_wheel_edge_count) < d && bump_flag == 0 );
    moveStop();

    if(bump_flag)
        bump_response(LEFT_BUMP);

    //reset edges for next movement
    left_wheel_edge_count=0;
    right_wheel_edge_count=0;
}

//circumfrence 18.85 cm
//diameter = 6cm
//l = 9.4/2 = 4.7
double wheel_speed(int left_right)
{
    if(left_right == 0)
    {
        return left_wheel_edge_count;
    }
    else
    {
        return right_wheel_edge_count;
    }
}

void moveForward(void) // this moves both wheels forward
{
    // right wheel move forward
    GPIO_PORT_B[GPIO_DATA] |= (1<<2);
    GPIO_PORT_B[GPIO_DATA] &= ~(1<<3);

    //left wheel move forward
    GPIOPinWrite(GPIO_PORTA_BASE,
            (GPIO_PIN_2 | GPIO_PIN_3),
            ( GPIO_PIN_2 ));
}

void moveStop(void) // this will stop all the wheels
{
    //right wheel stop
    GPIO_PORT_B[GPIO_DATA] |= (1<<2);
    GPIO_PORT_B[GPIO_DATA] |= (1<<3);
    //left wheel stop
    GPIOPinWrite(GPIO_PORTA_BASE,
                (GPIO_PIN_2 | GPIO_PIN_3 |
                GPIO_PIN_4),
                ( GPIO_PIN_2 | GPIO_PIN_3  ));
}

void moveBackwards(void) // this will move both wheels backwards
{
    //right wheel move backwards
    GPIO_PORT_B[GPIO_DATA] &= ~(1<<2);
    GPIO_PORT_B[GPIO_DATA] |= (1<<3);
    //left wheel move backwards
    GPIOPinWrite(GPIO_PORTA_BASE,
                (GPIO_PIN_2 | GPIO_PIN_3 ),
                ( GPIO_PIN_3 ));
}

void left_wheel_moveBackwards(void)
{
    GPIOPinWrite(GPIO_PORTA_BASE,
                    (GPIO_PIN_2 | GPIO_PIN_3 ),
                    ( GPIO_PIN_3 ));
}

void right_wheel_moveBackwards(void)
{
    GPIO_PORT_B[GPIO_DATA] &= ~(1<<2);
    GPIO_PORT_B[GPIO_DATA] |= (1<<3);
}

void left_wheel_moveForward(void)
{
    GPIOPinWrite(GPIO_PORTA_BASE,
      (GPIO_PIN_2 | GPIO_PIN_3),
      ( GPIO_PIN_2 ));
}

void right_wheel_moveForward(void)
{
    GPIO_PORT_B[GPIO_DATA] |= (1<<2);
    GPIO_PORT_B[GPIO_DATA] &= ~(1<<3);
}

void turn_bot(double x, double y) // determines the angle we need to turn and which way to turn
{
    double d;
    double angle = atan2(y,x);

    if(angle < 0)
    {
        d = (angle * 9.4*-1)/3.0;
        turn_right(d);
    }
    else
    {
        d = (angle * 9.4)/3.0;
        turn_left(d);
    }
}
