#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import serial
import numpy as np
import configparser
from funcs import *
import time

conffile = configparser.ConfigParser()
conffile.read('scripts\\config.ini')
#########################################################################################
#########################################################################################
### MACROS ##############################################################################
#########################################################################################
#########################################################################################

COMPORT = conffile['LIEN_SERIE']['COMPort']
BAUDRATE = conffile['LIEN_SERIE']['Baudrate']
SERIAL_TIMEOUT = float(conffile['LIEN_SERIE']['SerialTimeout']) # en secondes

MONITOR = int(conffile['ECRAN']['Monitor']) # écran à sélectionner

# mesures suivantes en cm
SCREEN_WIDTH_CM = float(conffile['ECRAN']['LargeurEcran'])
SCREEN_HEIGHT_CM = float(conffile['ECRAN']['HauteurEcran'])

#position des leds en cm
LED_POSITION_TOP =  eval(conffile['LEDS']['PositionLedsHaut'])
LED_POSITION_DOWN = eval(conffile['LEDS']['PositionLedsBas'])
LED_POSITION_RIGHT = eval(conffile['LEDS']['PositionLedsDroite'])
LED_POSITION_LEFT = eval(conffile['LEDS']['PositionLedsGauche'])

#coin à partir duquel on commence à numéroter les leds et sens de rotation
# ORDER_START doit être parmi 'tl', 'tr', 'bl', 'br' (top left, top right, bot left, bot right)
# ORDER_WAY doit être 'clockwise' ou 'counterclockwise' (sens pris quand on regarde l'écran, avec les leds derrière l'écran)
# exemple pour 'bl' et 'counterclockwise', on part du coin en bas à gauche de l'écran, puis on va en bas à droite, puis en haut à droite, ...
ORDER_START = conffile['LEDS']['CoinDebutLEDs']
ORDER_WAY = conffile['LEDS']['SensParcoursLEDs']

#nombre de pixels à prendre autour de la LED [leftright, updown] - dans les deux directions quand c'est possible
# exemple pour TOP : [100, 100] = carré de 200x100 (width, height) autour de la led - sauf effet de coin
# exemple pour LEFT : [100, 100] = carré de 100x200 (width, height) autour de la led - sauf effet de coin
NEIGHBORHOOD_TOP = eval(conffile['SCREENSHOT']['VoisinageHaut'])
NEIGHBORHOOD_DOWN = eval(conffile['SCREENSHOT']['VoisinageBas'])
NEIGHBORHOOD_RIGHT = eval(conffile['SCREENSHOT']['VoisinageDroite'])
NEIGHBORHOOD_LEFT = eval(conffile['SCREENSHOT']['VoisinageGauche'])

SCREENSHOT_METHOD = conffile['SCREENSHOT']['MethodeScreenshot'] # mss, pyautogui, PIL

#########################################################################################
#########################################################################################
### FIN MACROS ##########################################################################
#########################################################################################
#########################################################################################


def screencap(ser):
    #times_save = []
    with mss.mss() as sct: 
        while True:
            #start_time = time.time()

            # capture de l'écran numéro #MONITOR, avec l'outil #SCREENSHOT_METHOD
            sct_img, colormode = screen_capture(SCREENSHOT_METHOD, MONITOR, sct)
            
            screen = np.array(sct_img)[:,:,:3] # on ne prend pas le paramètre Alpha (BGRA)
            if colormode == 'BGR':
                screen = np.flip(screen,2)
            screen_height = screen.shape[0]
            screen_width = screen.shape[1]

            #position des leds en pixel
            led_pos_top_pix = [int(screen_width * i / SCREEN_WIDTH_CM) for i in LED_POSITION_TOP]
            led_pos_down_pix = [int(screen_width * i / SCREEN_WIDTH_CM) for i in LED_POSITION_DOWN]
            led_pos_right_pix = [int(screen_height * i / SCREEN_HEIGHT_CM) for i in LED_POSITION_RIGHT]
            led_pos_left_pix = [int(screen_height * i / SCREEN_HEIGHT_CM) for i in LED_POSITION_LEFT]
            space_between_leds_pix = int(led_pos_top_pix[1]-led_pos_top_pix[0])

            # on calcule les valeurs RGB des LEDs du haut, du bas de la gauche et de la droite de l'écran
            # led_val_top va du coin haut gauche de l'écran au coin haut droite
            # led_val_down va du coin bas gauche au coin bas droite
            # led_val_right va du coin haut droite au coin bas droite
            # led_val_left va du coin haut gauche au coin bas gauche
            led_val_top = []
            led_val_down = []
            led_val_right = []
            led_val_left = []
        
            n_leds_top = len(led_pos_top_pix)
            n_leds_down = len(led_pos_down_pix)
            n_leds_right = len(led_pos_right_pix)
            n_leds_left = len(led_pos_left_pix)
            for i in range(0, max(n_leds_top, n_leds_down)):
                
                # variable corner nécessaire pour la gestion des coins, plus loin (dans funcs.get_led_value)
                if (i==0):
                    corner = 'start'
                elif (i==n_leds_top-1):
                    corner = 'end'
                else:
                    corner = None
                
                if (i < n_leds_top):
                    ### On prépare le sous-écran à utiliser pour calculer la moyenne sur strip du haut
                    ledpos_top = led_pos_top_pix[i]
                    cropped_screen_top = screen[:NEIGHBORHOOD_TOP[1], 
                                                max(ledpos_top-space_between_leds_pix,0):min(ledpos_top+space_between_leds_pix,screen_width),
                                                :]
                    ### Calcul de la moyenne + ajout à la liste
                    led_val_top.append(get_led_value('top', cropped_screen_top, NEIGHBORHOOD_TOP, corner))

                if (i < n_leds_down):
                    ### On prépare le sous-écran à utiliser pour calculer la moyenne sur strip du bas
                    ledpos_down = led_pos_down_pix[i]
                    cropped_screen_down = screen[screen_height-NEIGHBORHOOD_DOWN[1]:, 
                                                max(ledpos_down-space_between_leds_pix,0):min(ledpos_down+space_between_leds_pix,screen_width),
                                                :]
                    ### Calcul de la moyenne + ajout à la liste
                    led_val_down.append(get_led_value('down', cropped_screen_down, NEIGHBORHOOD_DOWN, corner))
                
                if (i < n_leds_right): # pour éviter une boucle en plus, on calcule les right et left ici aussi (suppose écran plus large que haut).

                    ### On prépare le sous-écran à utiliser pour calculer la moyenne sur strip droit
                    led_pos_right = led_pos_right_pix[i]
                    cropped_screen_right = screen[max(led_pos_right-space_between_leds_pix,0):min(led_pos_right+space_between_leds_pix,screen_height), 
                                                screen_width-NEIGHBORHOOD_RIGHT[0]:,
                                                :]
                    ### Calcul de la moyenne + ajout à la liste                             
                    led_val_right.append(get_led_value('right', cropped_screen_right, NEIGHBORHOOD_RIGHT, corner))

                if (i < n_leds_left):
                    ### On prépare le sous-écran à utiliser pour calculer la moyenne sur strip gauche
                    led_pos_left = led_pos_left_pix[i]
                    cropped_screen_left = screen[max(led_pos_left-space_between_leds_pix,0):min(led_pos_left+space_between_leds_pix,screen_height),
                                                :NEIGHBORHOOD_LEFT[0],
                                                :]
                    ### Calcul de la moyenne + ajout à la liste    
                    led_val_left.append(get_led_value('left', cropped_screen_left, NEIGHBORHOOD_LEFT, corner))

            ### pour visualiser l'écran avec les couleurs des leds autour
            #visualize_screen_n_leds(screen, led_val_top, led_val_down, led_val_right, led_val_left, led_pos_top_pix, led_pos_down_pix, led_pos_right_pix, led_pos_left_pix, space_between_leds_pix)
            
            ### à partir des tableaux led_val_ZZZZ crée le bon string data
            data = prep_data(led_val_top, led_val_down, led_val_right, led_val_left, first_led=ORDER_START, order=ORDER_WAY)

            ### on envoie le string "data" au format LED_ID,R,G,B;LED_ID,R,G,B;LED_ID,R,G,B;...;LED_ID,R,G,B;
            send_data(ser, data)     
            
            #end_time = time.time()
            #print(end_time - start_time)
            #times_save.append(end_time - start_time) #en moyenne sur 1000 tours, 0.0654s avec mss. 0.08 avec pyautogui
            #print(data)
            #time.sleep(0.3)

if __name__ == '__main__':

    # initilisation du lien série avec l'Arduino
    ser = serial.Serial(COMPORT, BAUDRATE, timeout=SERIAL_TIMEOUT)
    init_serial(ser, SERIAL_TIMEOUT)
    screencap(ser)

#import pdb;pdb.set_trace()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    