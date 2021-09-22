#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import serial
import configparser
from funcs import send_data, init_serial

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
LUMINOSITY = int(conffile['LEDS']['Luminosity'])/100

def set_unicolor_leds(n_leds, r, g, b, ser):
    data = bytearray()
    r = int(r*LUMINOSITY)
    g = int(g*LUMINOSITY)
    b = int(b*LUMINOSITY)

    # 0x01 et 0x02 sont utilisés comme octets de début/fin de message
    if r <= 2:
        r = 0
    if g <= 2:
        g = 0
    if b <= 2:
        b = 0

    data.append(1) # start byte
    for i in range(n_leds):
        data.append(r)
        data.append(g)
        data.append(b)
    data.append(2) # end byte
    
    send_data(ser, data) 

if __name__ == '__main__':
    if len(sys.argv) == 4:
        red = int(sys.argv[1])
        green = int(sys.argv[2])
        blue = int(sys.argv[3])

        # initilisation du lien série avec l'Arduino
        ser = serial.Serial(COMPORT, BAUDRATE, timeout=SERIAL_TIMEOUT)
        init_serial(ser, SERIAL_TIMEOUT, N_LEDS)
        
        set_unicolor_leds(N_LEDS, red, green, blue, ser)
    else:
        print('Usage: python ambi_fixe.py <red> <green> <blue>')


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    