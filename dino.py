import keyboard
import numpy as np
from PIL import ImageGrab
import cv2
import pyautogui
import webbrowser
import time

def screen_record():
    print('Entered')
    last_time = time.time()
    while True:
        elapsed_time = time.time()-last_time

        left_b = 670 + 1.5*elapsed_time
        right_b = 814 + 1.5*elapsed_time

        if(left_b>1178):
            left_b = 1178
        if(right_b>1322):
            right_b = 1322

        printscreen_pil =  ImageGrab.grab(bbox = (left_b,332,right_b,380))
        printscreen_numpy = np.array(printscreen_pil.getdata(),dtype='uint8').reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))
        gray_screen = cv2.cvtColor(printscreen_numpy, cv2.COLOR_BGR2GRAY)

        l,b = np.shape(gray_screen);
        middle = int((l)/2)
        upper_box = gray_screen[:middle,:]
        lower_box = gray_screen[middle:,:]

        lower_avg = np.sum(lower_box)/(2*l*b)
        print(lower_avg)

        '''cv2.imshow('window',cv2.cvtColor(printscreen_numpy, cv2.COLOR_BGR2GRAY))
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
        '''
        if(keyboard.is_pressed('alt')):
            print('exiting')
            break
        elif(lower_avg<60.02):
            pyautogui.typewrite(["up"])






if __name__=='__main__':
    webbrowser.open('https://chromedino.com/', new=0, autoraise=True)
    while True:
        if(keyboard.is_pressed('ctrl')):
            screen_record()
            break

