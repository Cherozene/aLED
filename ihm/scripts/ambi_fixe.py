#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import serial
import configparser
from funcs import send_data


conffile = configparser.ConfigParser()
conffile.read('scripts\\config.ini')

COMPORT = conffile['LIEN_SERIE']['COMPort']
BAUDRATE = conffile['LIEN_SERIE']['Baudrate']
SERIAL_TIMEOUT = float(conffile['LIEN_SERIE']['SerialTimeout']) # en secondes

#position des leds en cm
LED_POSITION_TOP =  eval(conffile['LEDS']['PositionLedsHaut'])
LED_POSITION_DOWN = eval(conffile['LEDS']['PositionLedsBas'])
LED_POSITION_RIGHT = eval(conffile['LEDS']['PositionLedsDroite'])
LED_POSITION_LEFT = eval(conffile['LEDS']['PositionLedsGauche'])
N_LEDS = len(LED_POSITION_TOP) + len(LED_POSITION_DOWN) + len(LED_POSITION_RIGHT) + len(LED_POSITION_LEFT)
#print(N_LEDS)

def set_unicolor_leds(n_leds, r, g, b, ser):
    data = ''
    for i in range(n_leds):
        data += '{},{},{},{};'.format(i, r, g, b)
    data += '!' # délimiteur pour Arduino
    #print(data)
    send_data(ser, data) 

if __name__ == '__main__':
    if len(sys.argv) == 4:
        red = int(sys.argv[1])
        green = int(sys.argv[2])
        blue = int(sys.argv[3])

        # initilisation du lien série avec l'Arduino
        ser = serial.Serial(COMPORT, BAUDRATE, timeout=SERIAL_TIMEOUT)
        set_unicolor_leds(N_LEDS, red, green, blue, ser)
    else:
        print('Usage: python ambi_fixe.py <number of leds> <red> <green> <blue> <port COM> <baudrate>')


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    