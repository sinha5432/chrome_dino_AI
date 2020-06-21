from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

import io
import numpy as np

from PIL import Image, ImageDraw
from io import BytesIO

import cv2
import keyboard

driver = webdriver.Firefox(executable_path=r'E:\geckodriver.exe')


def open_game():
    canvas = driver.find_element_by_css_selector('.runner-canvas')
    img = Image.open(BytesIO(canvas.screenshot_as_png)).convert('RGB')

    img_array = np.array(img)

    return img_array


if __name__=='__main__':
    driver.get('https://chromedino.com/')

    left_bound = np.array([117, 110])
    right_bound = np.array([161, 202])

    flag = 0
    start_time = time.time()

    factor = 1

    while True:
        current_time = time.time()

        img = open_game()
        crop_image = img[left_bound[0]:right_bound[0], left_bound[1]:right_bound[1], :]


        img = cv2.rectangle(img, (left_bound[1], left_bound[0]), (right_bound[1], right_bound[0]), (0,0,0), 1)
        #print(img.shape[0])

        bott_image = crop_image[int(crop_image.shape[0]/2):, :, :]
        top_image = crop_image[:int(crop_image.shape[0]/2), :, :]

        #print(bott_image.shape)

        cv2.imshow('game', img)
        cv2.waitKey(1)

        top_avg = np.average(top_image)
        bott_avg = np.average(bott_image)
        #print("bott_avg = ",bott_avg)
        #print("top_avg  = ", top_avg)

        if(flag==1):
            start_time = time.time()

        if(int(current_time-start_time)>30):
            left_bound[1] = left_bound[1] + int(factor*10)
            right_bound[1] = right_bound[1] + int(factor*10)
            start_time = time.time()
            factor = factor + 0.3
            print('inside increment condn')

        print(int(current_time-start_time))

        if(top_avg>227 and bott_avg<235):
            driver.find_element_by_xpath("//html").send_keys(Keys.ARROW_UP)
            flag = 0
            #print('low jump!')
            #print("bott_avg = ", bott_avg)
            #print("top_avg  = ", top_avg)
        elif(bott_avg<235):
            keyboard.press(keyboard.KEY_UP)
            flag = 0
            #print('high jump!')
        elif(top_avg<227 and bott_avg>237):
            keyboard.press(keyboard.KEY_DOWN)
            time.sleep(0.3)
            keyboard.release(keyboard.KEY_DOWN)
            #print('Duck!')




        if keyboard.is_pressed('alt'):
            break
