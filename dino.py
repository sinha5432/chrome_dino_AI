import os
import cv2
import shutil
import keyboard
import threading
import numpy as np
import pyautogui
from PIL import Image
from io import BytesIO
from time import time, sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# main box coordinates
X1, Y1 = 110 - 30, 117
X2, Y2 = 202 - 40, 161

# refresh button coordinates

# (357,97)
#  (x1,y1) -------
#  |             |
#  | Refresh box |
#  |             |
#  ---------(x2,y2)
#          (395,130)

X1_R, Y1_R = 357, 97
X2_R, Y2_R = 395, 130
REF_BOX = (X1_R, Y1_R, X2_R, Y2_R)

# text related stuff
LINETYPE = 2
FONTSCALE_LARGE = 2
FONTSCALE_SMALL = 0.4
FONTCOLOR = (0, 0, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX

# threshold values for top and bottom box
DUCK_TOP_OFFSET = 2
TOP_THRESHOLD = 0  # will be overwritten by get thershold
BOTTOM_THRESHOLD = 0  # will be overwritten by get thershold
REF_BOX_RANGE = range(431691, 431950)


# video related stuff
FPS = 4
FRAMES = 100
FOLDER = 'VIDOES'
FOURCC = cv2.VideoWriter_fourcc(*'DIVX')

# rectangle and shading related stuff
COLOR = (0, 0, 0)
BODER_WIDTH = 1


def reset_variables():
    """
        resets variables on game start/when
        refresh is triggered.
    """
    # create a cv2 window
    cv2.destroyAllWindows()
    cv2.namedWindow('dino game')
    cv2.moveWindow('dino game', 20, 20)

    factor = 1
    x1, y1 = X1, Y1
    x2, y2 = X2, Y2
    start_time = factor_start_time = start_time_copy = time()
    return x1, y1, x2, y2, start_time, factor, factor_start_time, start_time_copy


def start():
    """
        Trys to click on canvas. If this fails that
        means the game hasn't been started once. Thus
        it hits SPACE.
    """
    try:
        canvas.click()
    except:
        main_body.send_keys(Keys.SPACE)


def get_image():
    """
        grabs canvas as image and return image with its
        numpy array representation.
    """
    img = Image.open(BytesIO(canvas.screenshot_as_png)).convert('RGB')
    image_array = np.array(img)
    return img, image_array


def duck():
    """
        ducks for 0.4 seconds
    """
    keyboard.press(keyboard.KEY_DOWN)
    sleep(0.4)
    keyboard.release(keyboard.KEY_DOWN)


    


def jump_higher():
    """
        performs a higher jump than `main_body.send_keys(Keys.SPACE)`
    """
    keyboard.press(keyboard.KEY_UP)

def low_jump():
    main_body.send_keys(Keys.SPACE)

   



def get_boxes(img, image_array):
    """
        crop and return all boxes
        as numpy arrays
    """
    main_box = image_array[y1:y2, x1:x2, :]
    mid = main_box.shape[0] // 2 - 7
    top_box = main_box[:mid, :, :]
    bott_box = main_box[mid:, :, :]
    refresh_box = np.array(img.crop(REF_BOX))
    return main_box, mid, top_box, bott_box, refresh_box


def get_threshold():
    '''
        get threshold values by observing top_avg and bott_avg for first 3 seconds
        and assigns them to constants TOP_THRESHOLD and BOTTOM_THRESHOLD
    '''
    top_values = []
    bottom_values = []
    intial_time = time()

    while (time() - intial_time) < 3:
        img, image_array = get_image()
        main_box, mid, top_box, bott_box, refresh_box = get_boxes(img, image_array)

        top_values = np.append(top_values, top_box)
        bottom_values = np.append(bottom_values, bott_box)

    TOP_THRESHOLD = np.floor(np.average(top_values)) - 5
    BOTTOM_THRESHOLD = np.floor(np.average(bottom_values)) - 10

    print('top threshold = ', TOP_THRESHOLD)
    print('bottom threshold = ', BOTTOM_THRESHOLD)
    return TOP_THRESHOLD, BOTTOM_THRESHOLD


def status(top_box, bott_box, refresh_box):
    """
        returns whether boxes are triggered or not.
        return boolean except for one case in duck.
    """
    # get averages for top and bott
    top_avg = np.floor(np.average(top_box))
    bott_avg = np.floor(np.average(bott_box))

    top_bool = None
    bott_bool = None

    #print(bott_avg)

    ## REFRESH BOX
    # get the sum of pixel values for refresh box
    # and check if they fall in a range. return True
    # if they do, else false
    refbox = np.sum(refresh_box)
    if refbox in REF_BOX_RANGE:
        r_bool = True
    else:
        r_bool = False

    ## TOP BOX
    # if it crosses TOP_THRESHOLD then flase
    # elif if falls below TOP_THRESHOLD then true
    # else None
    if top_avg >= TOP_THRESHOLD:
        top_bool = False
    elif top_avg < TOP_THRESHOLD:
        top_bool = True

    ## BOTTOM BOX
    # similar to top box but here DUCK_TOP_OFFSET is a
    # work-around to some problems faced in ducking during
    # testing
    DUCK_THRESHOLD = BOTTOM_THRESHOLD + DUCK_TOP_OFFSET
    if bott_avg > DUCK_THRESHOLD:
        bott_bool = 0
    elif bott_avg >= BOTTOM_THRESHOLD:
        bott_bool = False
    elif bott_avg < BOTTOM_THRESHOLD:
        bott_bool = True

    #print(bott_bool)

    return top_bool, bott_bool, r_bool, top_avg, bott_avg


def append_images(images, image_array):
    """
        appends images in a list until it
        crosses a limited number (FRAMES). Then
        starts to pop before appending.
    """
    if len(images) > FRAMES: images.pop(0)
    images.append(image_array)

    return images


def record_death(images):
    """
        converts stored images to a video and saves it
    """
    if not os.path.exists(FOLDER): os.mkdir(FOLDER)

    vid_num = len(os.listdir(FOLDER)) + 1
    video_path = os.path.join(FOLDER, str(vid_num) + '.avi')

    shape = images[0].shape[1], images[0].shape[0]
    video = cv2.VideoWriter(video_path, FOURCC, FPS, shape)

    for image in images: video.write(image)
    cv2.destroyAllWindows()
    video.release()


if __name__ == '__main__':

    # get a driver and load website.
    driver = webdriver.Firefox(
        executable_path=r'E:\geckodriver.exe')  # D:\Installers\geckodriver.exe # E:\geckodriver.exe
    driver.get('https://chromedino.com/')

    # get elements on the page
    main_body = driver.find_element_by_xpath("//html")
    outer_body = driver.find_element_by_id('aswift_0_expand')
    canvas = driver.find_element_by_css_selector('.runner-canvas')

    x1, y1, x2, y2, start_time, factor, factor_start_time, start_time_copy = reset_variables()

    images = []

    start()

    TOP_THRESHOLD, BOTTOM_THRESHOLD = get_threshold()

    while True:

        img, image_array = get_image()
        main_box, mid, top_box, bott_box, refresh_box = get_boxes(img, image_array)

        # increment x1 and x2
        if int(time() - start_time) > 15 and (time() - start_time_copy) < 120:
            x1 += int(factor * 5)
            x2 += int(factor * 15)
            start_time = time()

        if int(time() - factor_start_time) > 30 and (time() - start_time_copy) < 120:
            factor += 0.1
            factor_start_time = time()

        # get status
        top_bool, bott_bool, r_bool, top_avg, bott_avg = status(top_box, bott_box,
                                                                refresh_box)
        text = None

        images = append_images(images, image_array)

        ## REFRESH BUTTON
        # if r_bool is true then reset variables
        # and start again. (game ended)
        if r_bool:
            text = "restart"
            t = threading.Thread(target=record_death, args=(images,))  # don't remove the comma after images
            t.start()
            t.join()

            x1, y1, x2, y2, start_time, factor, factor_start_time, start_time_copy = reset_variables()
            start()
            TOP_THRESHOLD, BOTTOM_THRESHOLD = get_threshold()

        ## LOW JUMP
        # if botton box is triggered but top one isn't
        # then perform low jump. (small cactus)
        if bott_bool and not top_bool:
            text = "low jump"
            #print('bottom_box')
            t = threading.Thread(target=low_jump)
            t.start()
           


        ## HIGH JUMP
        # else if upper half is triggered then perform high
        # jump. (tall cactus)
        elif top_bool and bott_bool != 0:
            text = "high jump"
            # print('both_box')
            t = threading.Thread(target=jump_higher)
            t.start()

        ## DUCK
        # if top box is triggered but bottom isn't
        # then duck. (Archaeopteryx)
        elif top_bool:
            text = "duck"
            # print('top_box')
            t = threading.Thread(target=duck)
            t.start()

        ## USER STOP COMMAND
        # if user presses ALT key then
        # close everything and break.
        if keyboard.is_pressed('alt'):
            cv2.destroyAllWindows()
            driver.close()
            break

        ## CV2 PART:

        # get image diamentions
        (h, w) = image_array.shape[:2]

        # draw rectangle
        image_array = cv2.rectangle(image_array, (x1, y1), (x2, y2),
                                    COLOR, BODER_WIDTH)

        if top_bool:
            mask = np.full(top_box.shape, 50, np.uint8)
            main_box[:mid, :, :] = cv2.addWeighted(top_box, 0.5, mask, 0.5, 1.0)
            image_array[y1:y2, x1:x2, :] = main_box

        if bott_bool:
            mask = np.full(bott_box.shape, 50, np.uint8)
            main_box[mid:, :, :] = cv2.addWeighted(bott_box, 0.5, mask, 0.5, 1.0)
            image_array[y1:y2, x1:x2, :] = main_box

        # put text if not none.
        if not text == None:
            cv2.putText(image_array, text, ((w // 2) - len(text) * 20, h // 2),
                        FONT, FONTSCALE_LARGE, FONTCOLOR, LINETYPE)

        cv2.putText(image_array, str(f"{top_avg} | {TOP_THRESHOLD}"), (x2, y1),
                    FONT, FONTSCALE_SMALL, FONTCOLOR, LINETYPE)

        cv2.putText(image_array, str(f"{bott_avg} | {BOTTOM_THRESHOLD}"), (x2, y2),
                    FONT, FONTSCALE_SMALL, FONTCOLOR, LINETYPE)

        # show image and refresh every 1ms
        cv2.imshow('dino game', image_array)
        cv2.waitKey(1)