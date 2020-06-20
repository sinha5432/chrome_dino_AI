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
    img = Image.open(BytesIO(canvas.screenshot_as_png))
    img_arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    return img_arr


if __name__=='__main__':
    driver.get('https://chromedino.com/')

    left_bound = np.array([107, 114])
    right_bound = np.array([182, 162])

    #last_time = time.time()

    while True:
        img = open_game()
        crop_image = img[left_bound[0]:right_bound[0], left_bound[1]:right_bound[1]]
        img = cv2.rectangle(img, (left_bound[0], left_bound[1]), (right_bound[0], right_bound[1]), (0,0,0), 1)
        cv2.imshow('game', img)
        cv2.waitKey(1)

        #top_image = crop_image[int(left_bound[1]/2):, :]
        #bott_image = crop_image[:int(left_bound[1]/2), :]

        avg = np.average(crop_image)
        print(avg)
        if(avg<230):
            driver.find_element_by_xpath("//html").send_keys(Keys.SPACE)
            left_bound[0] = left_bound[0] + 3
            right_bound[0] = right_bound[0] + 3

        elif keyboard.is_pressed('alt'):
            break
