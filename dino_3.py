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

    while True:
        current_time = time.time()

        img = open_game()
        crop_image = img[left_bound[0]:right_bound[0], left_bound[1]:right_bound[1], :]
        #print(img.shape)
        img = cv2.rectangle(img, (left_bound[1], left_bound[0]), (right_bound[1], right_bound[0]), (0,0,0), 1)
        cv2.imshow('game', img)
        cv2.waitKey(1)

        top_image = crop_image[int(left_bound[0]/2):, :, :]
        bott_image = crop_image[:int(left_bound[0]/2), :, :]

        avg = np.average(bott_image)
        print(avg)

        if(flag==1):
            start_time = time.time()

        if((current_time-start_time)>40):
            left_bound[1] = left_bound[1] + 10
            right_bound[1] = right_bound[1] + 10
            start_time = time.time()

        if(avg<235):
            #driver.find_element_by_xpath("//html").send_keys(Keys.ARROW_UP)
            keyboard.press(keyboard.KEY_UP)
            flag = 1

        elif keyboard.is_pressed('alt'):
            break
