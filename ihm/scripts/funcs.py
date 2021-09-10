#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import mss
import PIL
import pyautogui
import time


def screen_capture(screen_method, monitor):
    if screen_method == 'mss':
        with mss.mss() as sct: # TODO : peut-être mettre ce with au dessus du while du main pour améliorer fps ?
            try:
                sct_img = sct.grab(sct.monitors[monitor]) # capture en BGRA
            except: # si un seul écran
                sct_img = sct.grab({'left': 0, 'top': 0, 'width': 2160, 'height': 1440}) #TODO : récupérer les paramètres de l'écran pour faire ça
        colormode = 'BGR'
    elif screen_method == 'pyautogui':
        #ATTENTION : avec cette méthode on est en RGB, pas en BGR. On ne peut pas choisir l'écran
        sct_img = pyautogui.screenshot()
        colormode = 'RGB'
    elif screen_method == 'PIL':
         #ATTENTION : avec cette méthode on est en RGB, pas en BGR. On ne peut pas choisir l'écran
        sct_img = PIL.ImageGrab.grab()
        colormode = 'RGB'
    else:
        raise NameError('Invalid SCREENSHOT_METHOD: {}. Must be one of mss, pyautogui, PIL.'.format(screen_method))

    return sct_img, colormode

def get_led_value(side, cropped_screen, neighborhood, corner):

    ########################################
    ##### CROPPING TO GET USEFULL DATA #####
    ########################################
    cscreen_height = cropped_screen.shape[0]
    cscreen_width = cropped_screen.shape[1]
    
    if (side == 'top' or side == 'down'):
        if (corner == 'start'):
            inuse_data = cropped_screen[:, 
                                        0:neighborhood[0], 
                                        :]
        elif (corner == 'end'):
            inuse_data = cropped_screen[:, 
                                        cscreen_width-neighborhood[0]:, 
                                        :]
        else: #corner == None
            inuse_data = cropped_screen[:, 
                                        max(0,int(cscreen_width/2-neighborhood[0])):min(cscreen_width,int(cscreen_width/2+neighborhood[0])), 
                                        :]  
                                        
    elif (side == 'right' or side == 'left'):
        if (corner == 'start'):
            inuse_data = cropped_screen[0:neighborhood[1], 
                                        :, 
                                        :]
        elif (corner == 'end'):
            inuse_data = cropped_screen[cscreen_height-neighborhood[1]:, 
                                        :, 
                                        :]
        else: #corner == None
            inuse_data = cropped_screen[max(0,int(cscreen_height/2-neighborhood[1])):min(cscreen_height,int(cscreen_height/2+neighborhood[1])), 
                                        :, 
                                        :]
    else:
        raise ValueError('Variable side should be top, down, right or left, not {}'.format(side))

    ########################################
    ############# COMPUTE MEAN #############
    ######################################## 
    mean_chann0 = np.mean(inuse_data[:,:,0])
    mean_chann1 = np.mean(inuse_data[:,:,1])
    mean_chann2 = np.mean(inuse_data[:,:,2])

    # threshold to get full black when mean is very low but not zero
    if mean_chann0 <= 5:
        mean_chann0 = 0
    if mean_chann1 <= 5:
        mean_chann1 = 0
    if mean_chann2 <= 5:
        mean_chann2 = 0
    
    return int(round(mean_chann0)), int(round(mean_chann1)), int(round(mean_chann2))


def prep_data(led_val_top, led_val_down, led_val_right, led_val_left, first_led='bl', order='clockwise'):
    # les LED_ID doivent être dans l'ordre attendu par le led strip... 
    # => first_led = tl, tr, bl ou br (top left, top right, bot left, bot right)
    # => order = clockwise ou counterclockwise
    
    # on met les listes dans l'ordre
    if order == 'clockwise':
        if first_led == 'tl':
            ordered_lists = led_val_top + led_val_right + led_val_down[::-1] + led_val_left[::-1]
        elif first_led == 'tr':
            ordered_lists = led_val_right + led_val_down[::-1] + led_val_left[::-1] + led_val_top
        elif first_led == 'bl':
            ordered_lists = led_val_left[::-1] + led_val_top + led_val_right + led_val_down[::-1] 
        elif first_led == 'br':
            ordered_lists = led_val_down[::-1] + led_val_left[::-1] + led_val_top + led_val_right
        else:
            raise ValueError('first_led should be one of tl, tr, bl or br, not {}.'.format(first_led))
            
    elif order == 'counterclockwise':
        if first_led == 'tl':
            ordered_lists = led_val_left + led_val_down + led_val_right[::-1] + led_val_top[::-1]
        elif first_led == 'tr':
            ordered_lists = led_val_top[::-1] + led_val_left + led_val_down + led_val_right[::-1]
        elif first_led == 'bl':
            ordered_lists = led_val_down + led_val_right[::-1] + led_val_top[::-1] + led_val_left
        elif first_led == 'br':
            ordered_lists = led_val_right[::-1] + led_val_top[::-1] + led_val_left + led_val_down
        else:
            raise ValueError('first_led should be one of tl, tr, bl or br, not {}.'.format(first_led))
    else:
        raise ValueError('order should be clockwise or counterclockwise, not {}.'.format(order))

    # mise en forme des données à transférer, au format LED_ID,R,G,B;LED_ID,R,G,B;LED_ID,R,G,B;...;LED_ID,R,G,B;
    data = ''
    for i in range(len(ordered_lists)):
        red =   ordered_lists[i][0]
        green = ordered_lists[i][1]
        blue =  ordered_lists[i][2]
        data += '{},{},{},{};'.format(i, red, green, blue)

    data += '!' # delimiteur utilisé par l'Arduino pour savoir quand s'arrêter de lire.
    return data   
   
    
def send_data(ser, data):
    #décommenter ligne ci-dessous pour exemple 3 leds, pour tester cette fonction et le code de décodage arduino
    #data = "0,230,45,50;1,86,125,53;2,43,200,230;" 
    data = data.encode()
    ser.write(data)

def init_serial(ser, timeout):
    send_data(ser, "0,0,0,0;!")
    time.sleep(timeout)
    send_data(ser, "0,0,0,0;!")
    time.sleep(timeout)
    
def visualize_screen_n_leds(screen, led_val_top, led_val_down, led_val_right, led_val_left, led_pos_top_pix, led_pos_down_pix, led_pos_right_pix, led_pos_left_pix, space_between_leds_pix):
    import matplotlib.pyplot as plt
    
    screen_height = screen.shape[0]
    screen_width = screen.shape[1]
    
    # matrice de 0 taille de l'écran +50 pix au dessus, 50 dessous, 50 droite, 50 gauche
    mat = np.zeros((screen_height+100, screen_width+100, screen.shape[2]), dtype='uint8') 
    # on remplit le milieu avec la capture d'écran
    mat[50:-50, 50:-50, :] = screen
    
    # on remplit les bords avec les valeurs des leds
    for i in range(max(len(led_val_top), len(led_val_down))):
        if (i < len(led_val_top)):
            ledpos = led_pos_top_pix[i]
            # top red
            mat[:50, max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_width+50), 0] = led_val_top[i][0]
            # top green
            mat[:50, max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_width+50), 1] = led_val_top[i][1]
            # top blue
            mat[:50, max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_width+50), 2] = led_val_top[i][2]
        
        if (i < len(led_val_down)):
            ledpos = led_pos_down_pix[i]
            # down red
            mat[-50:, max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_width+50), 0] = led_val_down[i][0]
            # down green
            mat[-50:, max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_width+50), 1] = led_val_down[i][1]
            # down blue
            mat[-50:, max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_width+50), 2] = led_val_down[i][2]
        
        if (i < len(led_val_right)): # pour éviter une boucle en plus, on calcule les right et left ici aussi (suppose écran plus large que haut).
            ledpos = led_pos_right_pix[i]
            # right red
            mat[max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_height+50), -50:, 0] = led_val_right[i][0]
            # right green
            mat[max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_height+50), -50:, 1] = led_val_right[i][1]
            # right blue
            mat[max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_height+50), -50:, 2] = led_val_right[i][2]
            
        if (i < len(led_val_left)):
            ledpos = led_pos_left_pix[i]
            # left red
            mat[max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_height+50), :50, 0] = led_val_left[i][0]
            # left green
            mat[max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_height+50), :50, 1] = led_val_left[i][1]
            # left blue
            mat[max(ledpos-space_between_leds_pix+50, 50):min(ledpos+space_between_leds_pix,screen_height+50), :50, 2] = led_val_left[i][2]
    
    plt.imshow(mat)
    plt.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    