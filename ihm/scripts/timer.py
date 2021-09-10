#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import serial
import configparser
from funcs import send_data, init_serial
import time

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

timercolors_file = open('scripts\\timer_colors.txt','r')
colors_lines = timercolors_file.read().splitlines()

def run_timer(n_leds, duration, ser):
    # combien de temps faut-il passer sur chaque couleur pour respecter le timer
    split_duration = duration / len(colors_lines)

    for i in range(len(colors_lines)):
        process_start_time = time.time() #utilisé pour connaitre le temps d'envoi des données et le soustraire au timer
        r, g, b = colors_lines[i].split()
        data = ''
        for i in range(n_leds):
            data += '{},{},{},{};'.format(i, r, g, b)
        data += '!' # délimiteur pour Arduino
        send_data(ser, data) 
        process_end_time = time.time() #utilisé pour connaitre le temps d'envoi des données et le soustraire au timer
        
        # tempo du timer - on soustrait le temps d'envoi des données
        time.sleep(max(0, split_duration - (process_end_time - process_start_time)))

    # Quand le timer est terminé, on fait clignoter en rouge !
    while True:
        data = ''
        for i in range(n_leds):
            data += '{},0,0,0;'.format(i)
        data += '!' # délimiteur pour Arduino
        send_data(ser, data) 
        time.sleep(0.2)
        data = ''
        for i in range(n_leds):
            data += '{},255,0,0;'.format(i)
        data += '!' # délimiteur pour Arduino
        send_data(ser, data) 
        time.sleep(0.5)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        duration = int(sys.argv[1])

        # initilisation du lien série avec l'Arduino
        ser = serial.Serial(COMPORT, BAUDRATE, timeout=SERIAL_TIMEOUT)
        init_serial(ser, SERIAL_TIMEOUT)
        
        run_timer(N_LEDS, duration, ser)
    else:
        print('Usage: python timer.py <duration in seconds>')


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    