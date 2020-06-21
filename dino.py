import io
import cv2
import time
import keyboard
import threading
import numpy as np
from io import BytesIO
from selenium import webdriver
from PIL import Image, ImageDraw
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# refresh button
x1_r,y1_r = 357,97
x2_r,y2_r = 395,130
ref_box = (x1_r,y1_r,x2_r,y2_r)


def start():
    try:
        canvas.click()
    except:
        main_body.send_keys(Keys.SPACE)

def get_image():
    img = Image.open(BytesIO(canvas.screenshot_as_png)).convert('RGB')
    img_array = np.array(img)
    return img,img_array

def duck():
    keyboard.press(keyboard.KEY_DOWN)
    time.sleep(0.3)
    keyboard.release(keyboard.KEY_DOWN)


def jump_higher():
    keyboard.press(keyboard.KEY_UP)

    # main_body.key_down(Keys.SPACE) #press down
    # time.sleep(0.2)
    # main_body.key_up(Keys.SPACE) 

    # ActionChains(driver) \
    # .key_down(Keys.SPACE) \
    # .pause(0.2) \
    # .key_up(Keys.SPACE) \
    # .perform()

font                   = cv2.FONT_HERSHEY_SIMPLEX
fontScale              = 2
fontColor              = (0,0,0)
lineType               = 2




if __name__=='__main__':
    cv2.namedWindow('dino game')        
    cv2.moveWindow('dino game', 20, 20)   
    
    driver = webdriver.Firefox(executable_path=r'D:\Installers\geckodriver.exe')
    driver.get('https://chromedino.com/')
    canvas = driver.find_element_by_css_selector('.runner-canvas')
    outer_body = driver.find_element_by_id('aswift_0_expand')
    main_body = driver.find_element_by_xpath("//html")
    
    left_bound = np.array([117, 110])
    right_bound = np.array([161, 202])

    start_time = time.time()
    flag = 0
    factor = 1
    

    start()
    
    while True:
        current_time = time.time()

        img,img_array = get_image()
        (h, w) = img_array.shape[:2] #get image diamentions for putting text in center

        refbox   = np.sum(np.array(img.crop(ref_box)))
        crop_image = img_array[left_bound[0]:right_bound[0], left_bound[1]:right_bound[1], :]

        img_array = cv2.rectangle(img_array, (left_bound[1], left_bound[0]), (right_bound[1], right_bound[0]), (0,0,0), 1)

        bott_image = crop_image[int(crop_image.shape[0]/2):, :, :]
        top_image = crop_image[:int(crop_image.shape[0]/2), :, :]


        top_avg = np.average(top_image)
        bott_avg = np.average(bott_image)

        if(flag==1):
            start_time = time.time()

        if(int(current_time-start_time)>30):
            left_bound[1] = left_bound[1] + int(factor*10)
            right_bound[1] = right_bound[1] + int(factor*10)
            start_time = time.time()
            factor = factor + 0.3

        text = None
            
        if refbox in range(431691,431950) :
            start_time = time.time()
            flag = 0
            factor = 1
            start()

        if(top_avg>227 and bott_avg<235):#low jump
            text = 'low jump'
            print(text)
            main_body.send_keys(Keys.SPACE)
            flag = 0

        elif(bott_avg<235):#high jump
            text = 'high jump'
            print(text)

            t = threading.Thread(target=jump_higher)
            t.start()
            flag = 0
            
        elif(top_avg<227 and bott_avg>237): #duck
            text = 'duck'
            print(text)

            t = threading.Thread(target=duck)
            t.start()

        if keyboard.is_pressed('alt'):
            cv2.destroyAllWindows()
            driver.close()
            break

        if not text == None:
            cv2.putText(img_array,text,((w//2) - 20,h//2), font, fontScale,fontColor,lineType)

        cv2.imshow('dino game', img_array)
        cv2.waitKey(1)
