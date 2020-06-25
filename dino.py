import os
import cv2
import shutil
import keyboard
import threading
import numpy as np
from PIL import Image
from io import BytesIO
from time import time,sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# main box coordinates
X1,Y1 = 110 - 30, 117  
X2,Y2 = 202 - 40, 161

# refresh button coordinates

# (357,97)
#  (x1,y1) -------
#  |             |
#  | Refresh box |
#  |             |
#  ---------(x2,y2)
#          (395,130)

X1_R, Y1_R     = 357, 97
X2_R, Y2_R     = 395, 130
REF_BOX    = (X1_R, Y1_R, X2_R, Y2_R)

# text related stuff
LINETYPE        = 2
FONTSCALE_LARGE = 2
FONTSCALE_SMALL = 0.4
FONTCOLOR       = (0,0,0)
FONT            = cv2.FONT_HERSHEY_SIMPLEX

# threshold values for top and bottom box
DUCK_TOP_OFFSET  = 5
TOP_THRESHOLD    = 227 
BOTTOM_THRESHOLD = 235
REF_BOX_RANGE    = range(431691,431950)
DUCK_THRESHOLD   = BOTTOM_THRESHOLD+DUCK_TOP_OFFSET

# video related stuff
FRAMES = 50
FOLDER = 'VIDOES'

# rectangle and shading related stuff
COLOR = (0,0,0)
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

    x1,y1 = X1, Y1  
    x2,y2 = X2, Y2 
    factor = 1
    start_time = factor_start_time = time()
    return x1, y1, x2, y2, start_time, factor, factor_start_time


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
    img_array = np.array(img)
    return img, img_array


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


def get_boxes(img,image_array):
    """
        crop and return all boxes
        as numpy arrays
    """
    main_box    = img_array[y1:y2,x1:x2,:]
    mid         = main_box.shape[0] // 2
    top_box     = main_box[:mid, :, :]
    bott_box    = main_box[mid:, :, :]
    refresh_box = np.array(img.crop(REF_BOX))
    return main_box,top_box,bott_box,refresh_box

def get_threshold():
    '''
        get threshold values by observing top_avg and bott_avg for first 3 seconds
        and assigns them to constants TOP_THRESHOLD and BOTTOM_THRESHOLD
    '''
    top_values      = []
    bottom_values   = []
    intial_time     = time()

    while (time()-intial_time) < 3:
        img, img_array = get_image()
        main_box,top_box,bott_box,refresh_box = get_boxes(img,image_array)

        top_avg  = np.floor(np.average(top_box))
        bott_avg = np.floor(np.average(bott_box))

        top_values.append(top_avg)
        bottom_values.append(bott_avg)

    TOP_THRESHOLD    = np.average(top_values)    - 20
    BOTTOM_THRESHOLD = np.average(bottom_values) - 5
    print('top threshold = ', TOP_THRESHOLD)
    print('bottom threshold = ', BOTTOM_THRESHOLD)


def status(top_box,bott_box,refresh_box):
    """
        returns whether boxes are triggered or not.
        return boolean except for one case in duck.
    """
    # get averages for top and bott
    top_avg = np.floor(np.average(top_box))
    bott_avg = np.floor(np.average(bott_box))

    top_bool = None
    bott_bool = None


    ## REFRESH BOX
    # get the sum of pixel values for refresh box
    # and check if they fall in a range. return True
    # if they do, else false
    refbox = np.sum(refresh_box)
    if refbox in REF_BOX_RANGE: r_bool = True
    else                      : r_bool = False
    
    ## TOP BOX
    # if it crosses TOP_THRESHOLD then flase 
    # elif if falls below TOP_THRESHOLD then true
    # else None       
    if   top_avg > TOP_THRESHOLD : top_bool = False
    elif top_avg < TOP_THRESHOLD : top_bool = True

    ## BOTTOM BOX
    # similar to top box but here DUCK_TOP_OFFSET is a 
    # work-around to some problems faced in ducking during 
    # testing
    if   bott_avg > DUCK_THRESHOLD   : bott_box  = 0
    elif bott_avg > BOTTOM_THRESHOLD : bott_bool = False
    elif bott_avg < BOTTOM_THRESHOLD : bott_bool = True

    return top_bool,bott_bool,r_bool,top_avg,bott_avg

def append_images(images,img_array):
    """
        appends images in a list until it 
        crosses a limited number (FRAMES). Then 
        starts to pop before appending.
    """
    if len(images) > FRAMES: images.pop(0)
    images.append(img_array)

    return images

def record_death(images):
    """
        converts stored images to a video and saves it
    """
    if not os.path.exists(FOLDER): os.mkdir(FOLDER)

    vid_num = len(os.listdir(FOLDER)) + 1
    video_path = os.path.join(FOLDER,str(vid_num)+'.avi')

    shape = images[0].shape[1], images[0].shape[0]
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    fps = 2
    video = cv2.VideoWriter(video_path,fourcc,fps, shape)  

    for image in images: video.write(image)
    cv2.destroyAllWindows()  
    video.release()  

if __name__=='__main__':

    # get a driver and load website.
    driver = webdriver.Firefox(executable_path=r'D:\Installers\geckodriver.exe')
    driver.get('https://chromedino.com/')

    # get elements on the page
    main_body = driver.find_element_by_xpath("//html")
    outer_body = driver.find_element_by_id('aswift_0_expand')
    canvas = driver.find_element_by_css_selector('.runner-canvas')

    x1, y1, x2, y2, start_time, factor, factor_start_time = reset_variables()

    images = []

    start()

    # get threshold values and make them global
    get_threshold()

    while True:

        img, img_array = get_image()
        main_box,top_box,bott_box,refresh_box = get_boxes(img, img_array)

        # increment
        if int(time() - start_time) > 15 and time() - end_time < 120:
            x1 += int(factor * 20)
            x2 += int(factor * 20)

            start_time = time()
            #print('shifting', x1, x2)

        if int(time() - factor_start_time) > 30 and time() - end_time < 150:
            factor += 0.1
            factor_start_time = time()

        # get status
        top_bool,bott_bool,r_bool,top_avg,bott_avg = status(top_box,bott_box,
                                                            refresh_box)
        text = None

        images = append_images(images,img_array)

        ## REFRESH BUTTON
        # if r_bool is true then reset variables
        # and start again. (game ended)
        if r_bool:
            text = "restart"
            t = threading.Thread(target=record_death,args=(images,)) #don't remove the comma after images
            t.start()
            t.join()

            x1, y1, x2, y2, start_time, factor, factor_start_time = reset_variables()
            start()
            get_threshold()

        ## LOW JUMP
        # if botton box is triggered but top one isn't
        # then perform low jump. (small cactus)
        if bott_bool and not top_bool:
            print('bottom_box')
            main_body.send_keys(Keys.SPACE)

        ## HIGH JUMP
        # else if upper half is triggered then perform high
        # jump. (tall cactus)
        elif top_bool and bott_bool!=0:
            print('both_box')
            t = threading.Thread(target=jump_higher)
            t.start()

        ## DUCK
        # if top box is triggered but bottom isn't
        # then duck. (Archaeopteryx)
        elif top_bool:
            print('top_box')
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

        #get image diamentions
        (h, w) = img_array.shape[:2] 

        # draw rectangle
        img_array = cv2.rectangle(img_array,(x1, y1),(x2, y2),
                                 COLOR, BODER_WIDTH)

        if top_bool:
            mask = np.full(top_box.shape, 50, np.uint8)
            main_box[:mid, :, :] = cv2.addWeighted(top_box, 0.5, mask, 0.5, 1.0)
            img_array[y1:y2,x1:x2,:] = main_box


        if bott_bool:
            mask = np.full(bott_box.shape, 50, np.uint8)
            main_box[mid:, :, :] = cv2.addWeighted(bott_box, 0.5, mask, 0.5, 1.0)
            img_array[y1:y2,x1:x2,:] = main_box

        # put text if not none.
        if not text == None:
            cv2.putText(img_array,text,((w//2) - len(text)*20,h//2),
                         FONT, FONTSCALE_LARGE,FONTCOLOR,LINETYPE)

        # put coordinates of main box
        print(top_box.shape,bott_box.shape)
        mid_top_box_x  = x2 + top_box.shape[1]//2
        mid_top_box_y  =  top_box.shape[0]//2

        mid_bott_box_x = x2 + bott_box.shape[1]//2
        mid_bott_box_y = y2 - bott_box.shape[0]//2

        print(mid_top_box_x,mid_top_box_y,mid_bott_box_x,mid_bott_box_y)

        cv2.putText(img_array,str(f"{top_avg}"),(mid_top_box_x,mid_top_box_y),
                                 FONT, FONTSCALE_SMALL,FONTCOLOR,LINETYPE)

        cv2.putText(img_array,str(f"{bott_avg}"),(mid_bott_box_x,mid_bott_box_y),
                                 FONT, FONTSCALE_SMALL,FONTCOLOR,LINETYPE)


        # show image and refresh every 1ms
        cv2.imshow('dino game', img_array)
        cv2.waitKey(1)
