import keyboard
import numpy as np
from PIL import ImageGrab
import cv2
import pyautogui


dark_obstacle=0
light_obstacle=255

def screen_record():
    print('Entered')
    while True:
        printscreen_pil =  ImageGrab.grab(bbox = (371,540,403,686))
        printscreen_numpy = np.array(printscreen_pil.getdata(),dtype='uint8').reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))
        gray_screen = cv2.cvtColor(printscreen_numpy, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_screen, 0, 255)
        '''cv2.imshow('window',cv2.cvtColor(printscreen_numpy, cv2.COLOR_BGR2GRAY))
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
        '''
        if(keyboard.is_pressed('ctrl')):
            print('Exiting')
            break
        elif(dark_obstacle in edges):
            #print('Detected')
            pyautogui.typewrite(["up"])




if __name__=='__main__':
    while True:
        if(keyboard.is_pressed('ctrl')):
            screen_record()
            break

