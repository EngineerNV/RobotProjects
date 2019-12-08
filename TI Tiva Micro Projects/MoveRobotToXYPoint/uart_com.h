/*
 * uart_com.h
 *
 *  Created on: Apr 10, 2018
 *      Author: Nick
 */

#ifndef UART_COM_H_
#define UART_COM_H_

void init_UART(void);
void tx_UART(char array[], int num);
void rx_UART(char array[]);
void UART_response(void);
#endif /* UART_COM_H_ */
