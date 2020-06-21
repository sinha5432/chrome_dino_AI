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

    left_bound = np.array([117, 119])
    right_bound = np.array([161, 211])

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

        #cv2.imshow('game', img)
        #cv2.waitKey(1)

        top_avg = np.average(top_image)
        bott_avg = np.average(bott_image)
        #print("bott_avg = ",bott_avg)
        print("top_avg  = ", top_avg)

        if(flag==1):
            start_time = time.time()

        if((current_time-start_time)>30):
            left_bound[1] = left_bound[1] + factor*15
            right_bound[1] = right_bound[1] + factor*15
            start_time = time.time()
            factor = factor + 0.2

        if(top_avg>227 and bott_avg<235):
            driver.find_element_by_xpath("//html").send_keys(Keys.ARROW_UP)
            flag = 1
        elif(bott_avg<235):
            keyboard.press(keyboard.KEY_UP)
            flag = 1
        elif(top_avg<230):
            driver.find_element_by_xpath("//html").send_keys(Keys.ARROW_DOWN)



        if keyboard.is_pressed('alt'):
            break
