/*
 * uart_com.c
 *
 *  Created on: Apr 10, 2018
 *      Author: Nick
 */
#include "uart_com.h"

#include "inc/tm4c123gh6pm.h"

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

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

//#include "driverlib/adc.c"
#include "driverlib/adc.h"

#define START_CMD_BYTE 0xaa
#define STOP_CMD_BYTE 0x55
#define ACK_BYTE 0xFF
#define NACK_BYTE 0x00
#define MAX_CMD_SIZE    15  //this can be adjusted depending on command

//identity Bytes
#define STOP_ID_BYTE    0x00
#define MOVE_FORWARD_BYTE 0X01
#define TURNS_LEFT_BYTE 0x02
#define TURNS_RIGHT_BYTE 0x03
#define OBST_AVOID_BYTE    0x04
#define GET_SENSOR_BYTE   0x05

union integer_data{
    uint32_t u32int;
    uint8_t u8int[4];
};

extern uint8_t obst_flag;
extern int bump_flag;
extern uint32_t left;
extern uint32_t right;
extern uint32_t front;

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

}
//page 557 we want nonblocking code

void tx_UART(char array[],int num){
    int i = 0;
    while(i < num){
        UARTCharPut(UART1_BASE,array[i]);
        i++;
    }
    //UARTCharPut(UART1_BASE,array[i]); //sending stop byte
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
}

void UART_response(){
    char rx_buffer[MAX_CMD_SIZE];
    char tx_buffer[MAX_CMD_SIZE];
    char id_byte;
    union integer_data f_data; // this will store values from left right and front
    union integer_data l_data;
    union integer_data r_data;
    union integer_data d;
    uint8_t distance; // used for left, right, and forward movement
    int dist;
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
                tx_UART(tx_buffer,3); //send command
                break;
            case STOP_ID_BYTE:
                moveStop();
                //stop byte
                tx_buffer[0] = START_CMD_BYTE;
                tx_buffer[1] = ACK_BYTE;
                tx_buffer[2] = STOP_CMD_BYTE;
                tx_UART(tx_buffer,3); //send command
                break;
            case TURNS_RIGHT_BYTE:

                d.u8int[0] = rx_buffer[2];
                d.u8int[1] = rx_buffer[3];
                d.u8int[2] = rx_buffer[4];
                d.u8int[3] = rx_buffer[5];

                //distance = rx_buffer[2];
                dist = (d.u32int >> 16);
                turn_right( dist );
                if(bump_flag)
                {
                    tx_buffer[0] = START_CMD_BYTE;
                    tx_buffer[1] = NACK_BYTE;
                    tx_buffer[2] = STOP_CMD_BYTE;
                }
                else
                {
                    tx_buffer[0] = START_CMD_BYTE;
                    tx_buffer[1] = ACK_BYTE;
                    tx_buffer[2] = STOP_CMD_BYTE;
                }
                bump_flag =0; //just in case of weird error
                tx_UART(tx_buffer,3); //send command
                break;
            case TURNS_LEFT_BYTE:
                d.u8int[0] = rx_buffer[2];
                d.u8int[1] = rx_buffer[3];
                d.u8int[2] = rx_buffer[4];
                d.u8int[3] = rx_buffer[5];

                //distance = rx_buffer[2]; // need to shift 32 bits by 4 to the left
                dist = (d.u32int >> 16);
                turn_left(dist);
                if(bump_flag)
                {
                    tx_buffer[0] = START_CMD_BYTE;
                    tx_buffer[1] = NACK_BYTE;
                    tx_buffer[2] = STOP_CMD_BYTE;

                }
                else
                {
                    tx_buffer[0] = START_CMD_BYTE;
                    tx_buffer[1] = ACK_BYTE;
                    tx_buffer[2] = STOP_CMD_BYTE;
                }
                bump_flag =0; //just in case of weird error
                tx_UART(tx_buffer,3); //send command
                break;
            case MOVE_FORWARD_BYTE:
                d.u8int[0] = rx_buffer[2];
                d.u8int[1] = rx_buffer[3];
                d.u8int[2] = rx_buffer[4];
                d.u8int[3] = rx_buffer[5];

                //distance = rx_buffer[2]; // need to shift 32 bits by 4 to the left
                dist = (d.u32int >> 16);

                moveForward_x(dist);
                if(bump_flag)
                {
                    tx_buffer[0] = START_CMD_BYTE;
                    tx_buffer[1] = NACK_BYTE;
                    tx_buffer[2] = STOP_CMD_BYTE;
                }
                else
                {
                    tx_buffer[0] = START_CMD_BYTE;
                    tx_buffer[1] = ACK_BYTE;
                    tx_buffer[2] = STOP_CMD_BYTE;
                }
                bump_flag =0; //just in case of weird error
                tx_UART(tx_buffer,3); //send command
                break;
            case GET_SENSOR_BYTE:
                f_data.u32int = front;
                l_data.u32int = left;
                r_data.u32int = right;

                tx_buffer[0] = START_CMD_BYTE;
                tx_buffer[1] = l_data.u8int[0];
                tx_buffer[2] = l_data.u8int[1];
                tx_buffer[3] = l_data.u8int[2];
                tx_buffer[4] = l_data.u8int[3];
                tx_buffer[5] = r_data.u8int[0];
                tx_buffer[6] = r_data.u8int[1];
                tx_buffer[7] = r_data.u8int[2];
                tx_buffer[8] = r_data.u8int[3];
                tx_buffer[9] = f_data.u8int[0];
                tx_buffer[10] = f_data.u8int[1];
                tx_buffer[11] = f_data.u8int[2];
                tx_buffer[12] = f_data.u8int[3];
                tx_buffer[13] = STOP_CMD_BYTE;
                tx_UART(tx_buffer,14); //send command
                break;
            default:
                break;
        }
    }
}
