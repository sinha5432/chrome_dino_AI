import keyboard
import numpy as np
from PIL import ImageGrab
import cv2
import pyautogui
import webbrowser
import time
import math

def screen_record():
    print('Entered')
    last_time = time.time()
    while True:
        elapsed_time = time.time()-last_time

        left_b = 724 + int(1.2*math.sqrt(elapsed_time))
        right_b = 825 + int(1.6*math.sqrt(elapsed_time))

        if(left_b>1178):
            left_b = 1178
        if(right_b>1322):
            right_b = 1322

        printscreen_pil =  ImageGrab.grab(bbox = (left_b,330,right_b,383))
        printscreen_numpy = np.array(printscreen_pil.getdata(),dtype='uint8').reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))

        gray_screen = cv2.cvtColor(printscreen_numpy, cv2.COLOR_BGR2GRAY)
        img = cv2.Canny(gray_screen, 20, 250)
        kernel = np.ones((5, 5), np.uint8)
        img = cv2.dilate(img, kernel, iterations=4)

        l,b = np.shape(img);
        middle = int((l)/2)
        upper_box = gray_screen[:middle,:]
        lower_box = gray_screen[middle:,:]

        lower_avg = np.sum(lower_box)/(l*b)
        print(lower_avg)

        if(keyboard.is_pressed('alt')):
            print('exiting')
            break
        elif(lower_avg<120):
            pyautogui.typewrite(["up"])




if __name__=='__main__':
    webbrowser.open('https://chromedino.com/', new=0, autoraise=True)
    while True:
        if(keyboard.is_pressed('space')):
            screen_record()
            break

