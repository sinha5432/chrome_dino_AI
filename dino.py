import keyboard
import numpy as np
from PIL import ImageGrab
import cv2
import pyautogui
import webbrowser

def screen_record():
    print('Entered')
    while True:
        printscreen_pil =  ImageGrab.grab(bbox = (727,328,769,383))
        printscreen_numpy = np.array(printscreen_pil.getdata(),dtype='uint8').reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))
        gray_screen = cv2.cvtColor(printscreen_numpy, cv2.COLOR_BGR2GRAY)

        l,b = np.shape(gray_screen);
        middle = int((l)/2)
        upper_box = gray_screen[:middle,:]
        lower_box = gray_screen[middle:,:]

        upper_avg = np.sum(lower_box)/(l*b)
        print(upper_avg)

        '''cv2.imshow('window',cv2.cvtColor(printscreen_numpy, cv2.COLOR_BGR2GRAY))
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
        '''
        if(keyboard.is_pressed('alt')):
            print('exiting')
            break
        elif(upper_avg<110):
            pyautogui.typewrite(["up"])






if __name__=='__main__':
    webbrowser.open('https://chromedino.com/', new=0, autoraise=True)
    while True:
        if(keyboard.is_pressed('ctrl')):
            screen_record()
            break

