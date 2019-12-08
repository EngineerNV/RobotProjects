

/**
 *
 * main.c
 */


#include "uart_com.h"
#include "move.h"

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

#include "driverlib/systick.h"

void gpio_start_interrupt(void);
void gpioPort_aInt(void);
void gpioPort_cInt(void);
void gpioPort_dInt(void);

uint32_t irPull(int i); //1 for front, 3 for right , 2 for left
void irInit(void);

//gpio port B base
#define GPIO_PORT_B ((volatile uint32_t *)0x40059000)
//gpio port F base
#define GPIO_PORT_F ((volatile uint32_t *)0x4005D000)

#define GPIO_DATA   (0x3FC >> 2)

//counters for wheel edges
double left_wheel_edge_count=0;
double right_wheel_edge_count=0;

//toggle for led
int toggle =0;
int bump_flag = 0;
//interrupt debounce timers
uint32_t timeA = 0;
uint32_t timeB = 0;


uint8_t obst_flag = 1;

uint32_t right = 0;
uint32_t left = 0;
uint32_t front = 0;

int main(void)
{
    init_UART();
    int thresh = 2047; // this is half of the 12 bit adc value
    IntMasterDisable();
    SysTickPeriodSet(16777216);   //sets the maximum period for the debounce reference clock
    SysTickEnable(); // starts the debounce reference clock
    moveInit(); // this initializes all the gpio ports
    gpio_start_interrupt(); // this initialized the gpio interrupt
    irInit();

    bump_flag = 0;

    while(1){
        if(obst_flag){

            front = irPull(1);

            right = irPull(3);

            left = irPull(2);
        }
        UART_response();
    }
    return 0;
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
    //return 0;
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
