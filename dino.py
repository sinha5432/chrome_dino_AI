import cv2
import keyboard
import threading
import numpy as np
from PIL import Image
from io import BytesIO
from time import time,sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# (357,97)
#  (x1,y1) -------
#  |             |
#  | Refresh box |
#  |             |
#  ---------(x2,y2)  
#          (395,130)

# refresh button coordinates
x1_r, y1_r = 357, 97
x2_r, y2_r = 395, 130
ref_box    = (x1_r, y1_r, x2_r, y2_r)

# text 
fontScale  = 2
lineType   = 2
fontColor  = (0,0,0)
font       = cv2.FONT_HERSHEY_SIMPLEX

# threshold values for top and bottom box
max_value = 227
min_value = 235
duck_thershold = 2

def reset_variables():
    """
        resets variables on game start/when 
        refresh is triggered.
    """

    # (110,117)
    #  (x1,y1) ------
    #  |            |
    #  |  Main box  |
    #  |            |
    #  --------(x2,y2)  
    #          (202,161)

    x1,y1 = 110, 117
    x2,y2 = 202, 161

    factor = 1
    start_time = time()
    return x1,y1,x2,y2,start_time,factor

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
        ducks for 0.3 seconds
    """
    keyboard.press(keyboard.KEY_DOWN)
    sleep(0.3)
    keyboard.release(keyboard.KEY_DOWN)

def jump_higher():
    """
        performs a higher jump than `main_body.send_keys(Keys.SPACE)`
    """
    keyboard.press(keyboard.KEY_UP)


top_threshold    = 227 
bottom_threshold = 235
duck_top_offset  = 10

values = [top_threshold,bottom_threshold,duck_top_offset]

def status(top_box,bott_box,refresh_box,values):
    """
        returns wheather boxes are triggered or not.
        return boolean except for one case in duck.
    """
    # get averages for top and bott
    top_avg  = np.average(top_box)
    bott_avg = np.average(bott_box)

    top_threshold,bottom_threshold,duck_top_offset = values

    top_bool  = None
    bott_bool = None

    ## REFRESH BOX
    # get the sum of pixel values for refresh box
    # and check if they fall in a range. return True
    # if they do, else false
    refbox = np.sum(refresh_box)
    if refbox in range(431691,431950): r_bool = True
    else                             : r_bool = False
    
    ## TOP BOX
    # if it crosses max_value then flase 
    # elif if falls below min_value then true
    # else None       
    if   top_avg > top_threshold : top_bool = False
    elif top_avg < top_threshold : top_bool = True

    ## BOTTOM BOX
    # similar to top box but here duck_top_offset is a 
    # work-around to some problems faced in ducking during 
    # testing
    new_threshold = bottom_threshold+duck_top_offset
    if   bott_avg > new_threshold    : bott_box  = 0
    elif bott_avg > bottom_threshold : bott_bool = False
    elif bott_avg < bottom_threshold : bott_bool = True

    return top_bool,bott_bool,r_bool

if __name__=='__main__':
    # create a cv2 window 
    cv2.namedWindow('dino game')        
    cv2.moveWindow('dino game', 20, 20)   
    
    # get a driver and load website.
    driver = webdriver.Firefox(executable_path=r'D:\Installers\geckodriver.exe')
    driver.get('https://chromedino.com/')

    # get elements on the page
    main_body  = driver.find_element_by_xpath("//html")
    outer_body = driver.find_element_by_id('aswift_0_expand')
    canvas     = driver.find_element_by_css_selector('.runner-canvas')

    x1,y1,x2,y2,start_time,factor = reset_variables()

    start()

    while True:

        img,img_array = get_image()

        # get all boxes 
        main_box    = img_array[ y1:y2,x1:x2,:]
        mid         = main_box.shape[0] // 2
        top_box     = main_box[:mid, :, :]
        bott_box    = main_box[mid:, :, :]
        refresh_box = np.array(img.crop(ref_box))

        # increment 
        if int(time() - start_time) > 15:

            x1+= int(factor * 10)
            x2+= int(factor * 10)

            start_time = time()

            factor += 0.3

            print('shifting',x1,x2)

        
        # get status
        top_bool,bott_bool,r_bool = status(top_box,bott_box,
                                            refresh_box,
                                            values)

        text = None

        ## REFRESH BUTTON
        # if r_bool is true then reset variables
        # and start again. (game ended)
        if r_bool:
            text = "restart"
            x1,y1,x2,y2,start_time,factor = reset_variables()
            start()

        ## LOW JUMP
        # if botton box is triggered but top one isn't 
        # then perform low jump. (small cactus)
        if  bott_bool and not top_bool :
            text = 'low jump'
            main_body.send_keys(Keys.SPACE)

        ## HIGH JUMP
        # else if upper half is triggered then perform high
        # jump. (tall cactus)
        elif top_bool:
            text = 'high jump'
            t = threading.Thread(target=jump_higher)
            t.start()

        ## DUCK
        # if top box is triggered but bottom isn't
        # then duck. (partridge)
        elif top_bool and bott_bool==1:
            text = 'duck'
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
        img_array = cv2.rectangle(img_array,(x1, y1),(x2, y2),(0, 0, 0), 1)

        # put text if not none.
        if not text == None:
            cv2.putText(img_array,text,((w//2) - len(text)*20,h//2), font, fontScale,fontColor,lineType)

        # put coordinates of main box
        cv2.putText(img_array,str(f"({x1},{y1})"),(x1,y1),
                                 font, 0.4,fontColor,lineType)

        cv2.putText(img_array,str(f"({x2},{y2})"),(x2,y2),
                                 font, 0.4,fontColor,lineType)

        # show image and refresh every 1ms
        cv2.imshow('dino game', img_array)
        cv2.waitKey(1)
