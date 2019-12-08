

/**
 * main.c
 */

#include "inc/tm4c123gh6pm.h"

#include <stdio.h>
#include "driverlib/gpio.c"
#include "driverlib/gpio.h"
#include "driverlib/pin_map.h"
#include "driverlib/uart.h"
#include <stdint.h>

#include <math.h>

#include "driverlib/sysctl.c"
#include "driverlib/sysctl.h"


#include "inc/hw_types.h"
#include "inc/hw_memmap.h"

#include "driverlib/interrupt.c"
#include "driverlib/interrupt.h"

#include "driverlib/pwm.c"
#include "driverlib/pwm.h"

#include "driverlib/adc.c"
#include "driverlib/adc.h"

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

void gpio_start_interrupt(void);
void moveInit(void);
void gpioPort_aInt(void);
void gpioPort_cInt(void);
void gpioPort_dInt(void);
double wheel_speed(int left_right);

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
//void turn_LR(int right_left); // right == 1, left == 0

uint32_t irPull(int i); //1 for front, 3 for right , 2 for left
void irInit(void);

void bump_response(void);
void front_response(void);

//counters for wheel edges
double left_wheel_edge_count=0;
double right_wheel_edge_count=0;

//toggle for led
int toggle =0;
int bump_flag = 0;
//interrupt debounce timers
uint32_t timeA = 0;
uint32_t timeB = 0;


#define START_CMD_BYTE 0xaa
#define STOP_CMD_BYTE 0x55
#define ACK_BYTE 0xFF
#define MAX_CMD_SIZE    5  //this can be adjusted depending on command

void init_UART(void);
void tx_UART(char array[]);
void rx_UART(char array[]);
void UART_response(void);

uint8_t obst_flag = 1;

//identity Bytes
#define STOP_ID_BYTE    0x00
#define MOVE_FORWARD_BYTE 0X01
#define TURNS_LEFT_BYTE 0x02
#define TURNS_RIGHT_BYTE 0x03
#define OBST_AVOID_BYTE    0x04
#define GET_SENSOR_BYTE   0x05


uint32_t right = 0;
uint32_t left = 0;
uint32_t front = 0;

int main(void)
{
    init_UART();
    int thresh = 2047; // this is half of the 12 bit adc value
    IntMasterDisable();
    SysTickPeriodSet(16777216);   //sets the maximum period for the debounce reference clock
    SysTickEnable();    // starts the debounce reference clock
    moveInit(); // this initializes all the gpio ports
    gpio_start_interrupt(); // this initialized the gpio interrupt
    irInit();


    bump_flag = 0;


    while(1){
        if(obst_flag){
            if( irPull(1) >= thresh)
                front = 1;
            else
                front = 0;
            if(irPull(3) >= thresh)
                right = 1;
            else
                right = 0;
            if(irPull(2) >= thresh)
                left = 1;
            else
                left = 0;
        }
        UART_response();
    }
    return 0;
}


void init_UART(){
    SysCtlClockSet( SYSCTL_USE_OSC | SYSCTL_OSC_MAIN | SYSCTL_XTAL_16MHZ | SYSCTL_SYSDIV_1 );
    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART1);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);

    GPIOPinConfigure(GPIO_PB0_U1RX);
    GPIOPinConfigure(GPIO_PB1_U1TX);
    GPIOPinTypeUART(GPIO_PORTB_BASE, (GPIO_PIN_0 | GPIO_PIN_1));

    UARTConfigSetExpClk(UART1_BASE, SysCtlClockGet(), 9600,
         UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE |
         UART_CONFIG_PAR_NONE);

    UARTEnable(UART1_BASE);
    return 0;
}
//page 557 we want nonblocking code



void tx_UART(char array[]){
    int i = 0;
    while(array[i] != STOP_CMD_BYTE){
        UARTCharPut(UART1_BASE,array[i]);
        i++;
    }
    UARTCharPut(UART1_BASE,array[i]); //sending stop byte
}

void rx_UART(char array[] ){
    //clear the array before we give it data
    uint16_t i;
    for(i=0;i<MAX_CMD_SIZE;i++)
        array[i] = 0x00;
    i = 0;
    while(1 ){ // while we still have information inside of the FIFO
        array[i] = UARTCharGet(UART1_BASE);
        if(array[i] == STOP_CMD_BYTE)
            break;
        i++;
    }
    return;
}

void UART_response(){
    char rx_buffer[MAX_CMD_SIZE];
    char tx_buffer[MAX_CMD_SIZE];
    char id_byte;

    uint8_t distance; // used for left, right, and forward movement

    if(UARTCharsAvail(UART1_BASE)) //if we have a command from the pi
    {
        rx_UART(rx_buffer);// grab command
        id_byte = rx_buffer[1]; // 2nd byte has identity of the command

        switch(id_byte)
        {
            case OBST_AVOID_BYTE:
                obst_flag = rx_buffer[2];
                tx_buffer[0] = START_CMD_BYTE;
                tx_buffer[1] = ACK_BYTE;
                tx_buffer[2] = STOP_CMD_BYTE;
                tx_UART(tx_buffer); //send command
                break;
            case STOP_ID_BYTE:
                moveStop();
                //stop byte
                tx_buffer[0] = START_CMD_BYTE;
                tx_buffer[1] = ACK_BYTE;
                tx_buffer[2] = STOP_CMD_BYTE;
                tx_UART(tx_buffer); //send command
                break;
            case TURNS_RIGHT_BYTE:
                distance = rx_buffer[2];
                turn_right(distance);
                tx_buffer[0] = START_CMD_BYTE;
                tx_buffer[1] = ACK_BYTE;
                tx_buffer[2] = STOP_CMD_BYTE;
                tx_UART(tx_buffer); //send command
                break;
            case TURNS_LEFT_BYTE:
                distance = rx_buffer[2];
                turn_left(distance);
                tx_buffer[0] = START_CMD_BYTE;
                tx_buffer[1] = ACK_BYTE;
                tx_buffer[2] = STOP_CMD_BYTE;
                tx_UART(tx_buffer); //send command
                break;
            case MOVE_FORWARD_BYTE:
                distance = rx_buffer[2];
                moveForward_x(distance);
                tx_buffer[0] = START_CMD_BYTE;
                tx_buffer[1] = ACK_BYTE;
                tx_buffer[2] = STOP_CMD_BYTE;
                tx_UART(tx_buffer); //send command
                break;
            case GET_SENSOR_BYTE:
                tx_buffer[0] = START_CMD_BYTE;
                tx_buffer[1] = left;
                tx_buffer[2] = right;
                tx_buffer[3] = front;
                tx_buffer[4] = STOP_CMD_BYTE;
                tx_UART(tx_buffer); //send command
                break;
            default:

                break;
        }
    }
    return;
}

void gpio_start_interrupt(void)
{
    GPIOIntTypeSet(GPIO_PORTA_BASE, GPIO_PIN_5, GPIO_FALLING_EDGE);
    GPIOIntTypeSet(GPIO_PORTC_BASE, GPIO_PIN_5, GPIO_BOTH_EDGES);
    GPIOIntTypeSet(GPIO_PORTD_BASE, GPIO_PIN_2, GPIO_BOTH_EDGES);

    GPIOIntRegister(GPIO_PORTA_BASE, gpioPort_aInt);
    GPIOIntRegister(GPIO_PORTC_BASE, gpioPort_cInt);
    GPIOIntRegister(GPIO_PORTD_BASE, gpioPort_dInt);

    GPIOIntEnable(GPIO_PORTA_BASE, GPIO_INT_PIN_5 );
    GPIOIntEnable(GPIO_PORTC_BASE, GPIO_INT_PIN_5 );
    GPIOIntEnable(GPIO_PORTD_BASE, GPIO_INT_PIN_2 );

    IntMasterEnable();
    return 0;
}

void irInit(void)
{
    // Enable the ADC 0, 2, 1 module for E3, E1, E2.
    //
    SysCtlPeripheralEnable(SYSCTL_PERIPH_ADC0);

    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_ADC0))
    {
    }
    //
    // Wait for the ADC0 module to be ready.
    //

    //
    // Enable the first sample sequencer to capture the value of channel 0 when
    // the processor trigger occurs.


    //AIN1
    ADCSequenceConfigure(ADC0_BASE, 2, ADC_TRIGGER_PROCESSOR, 0);
    ADCSequenceStepConfigure(ADC0_BASE, 2, 0,
         ADC_CTL_CH0);//E3

    ADCSequenceStepConfigure(ADC0_BASE, 2, 1,
         ADC_CTL_CH1); //E2

    ADCSequenceStepConfigure(ADC0_BASE, 2, 2,
            ADC_CTL_IE | ADC_CTL_END | ADC_CTL_CH2); //E1

    ADCSequenceEnable(ADC0_BASE, 2);

}

uint32_t irPull(int i) //1 for front, 3 for right , 2 for left
{
    uint32_t ui32Value[4];

    ADCIntClear(ADC0_BASE, 2);

    ADCProcessorTrigger(ADC0_BASE, 2);
    while(!ADCIntStatus(ADC0_BASE, 2, false))
    {
    }
    ADCSequenceDataGet(ADC0_BASE, 2, ui32Value);

    ADCIntClear(ADC0_BASE, 2);

    if(i == 3) // right E3
    {
        return ui32Value[0];
    }
    else if(i == 1) //front E1
    {
        return ui32Value[2];
    }
    else // left E2
    {
        return ui32Value[1];
    }
}

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

void gpioPort_aInt(void) // bump occured
{
    timeB = SysTickValueGet();
    uint32_t timeC = timeB - timeA;
    bump_flag = 1;
    if(timeC > 16000000)
    {
        if(toggle == 0)
        {
          GPIO_PORT_F[GPIO_DATA] |= (1<<2);
          toggle = 1;

        }
        else
        {
          GPIO_PORT_F[GPIO_DATA] &= ~(1<<2);
          toggle = 0;

        }
    }

    timeA = SysTickValueGet();

    GPIOIntClear(GPIO_PORTA_BASE, GPIO_INT_PIN_5);
    return 0;
}

void gpioPort_cInt(void) //left wheel interrupt
{
    left_wheel_edge_count++;
    GPIOIntClear(GPIO_PORTC_BASE, GPIO_INT_PIN_5);
    return 0;
}

void gpioPort_dInt(void)//right wheel interrupt
{
    right_wheel_edge_count++;
    GPIOIntClear(GPIO_PORTD_BASE, GPIO_INT_PIN_2);
    return 0;
}

void bump_response(void)
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
    bump_flag = 0;
    return 0;
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

    return 0;
}


void moveForward_x(double d) // give distance in cms
{
    // left wheel move forward
    left_wheel_moveForward();
    //right wheel move backward
    right_wheel_moveForward();
    //continue to turn until we reach the distance giving us the angle - .29 cm a tick
    while( (.29*right_wheel_edge_count) < d );
    moveStop();
    //reset edges for next movement
    left_wheel_edge_count=0;
    right_wheel_edge_count=0;
}

void turn_right(double d)
{
    // left wheel move forward
    left_wheel_moveForward();
    //right wheel move backward
    right_wheel_moveBackwards();
    //continue to turn until we reach the distance giving us the angle - .29 cm a tick
    while( (.29*right_wheel_edge_count) < d );
    moveStop();
    //reset edges for next movement
    left_wheel_edge_count=0;
    right_wheel_edge_count=0;
}

void turn_left(double d)
{
    // right wheel move forward
    right_wheel_moveForward();
    //left wheel move backward
    left_wheel_moveBackwards();
    //continue to turn until we reach the distance giving us the angle - .29 cm a tick
    while( (.29*left_wheel_edge_count) < d );
    moveStop();
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
