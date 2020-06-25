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
X1,Y1 = 110-20, 117+3  
X2,Y2 = 202-40, 161 ##### nerfed on purpose for dubugging . remove later.

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


# X1,Y1,X2,Y2 = 90, 120, 162, 161
# def print_box():
#     def foo(a,b):
#         if a<b: return ((b-a)//2)+a
#         else  : return ((a-b)//2)+b

#     center_line = foo(X1,X2),foo(Y1,Y2)
#     tc  = foo(X1,center_line[0]),foo(Y1,center_line[1])
#     bc = foo(X2,center_line[0]),foo(Y2,center_line[1])
    
#     string = f"""
#            Main box 

#      {(X1,Y1)}
#      (x1,y1) ------------
#      |                  |
#      |     Top box      |  
#       |    {tc}    |
#      |                  |
#      |------------------| {center_line}
#      |                  |
#      |    Bottom box    |  
#      |    {   bc   }    |
#      |                  |
#      -------------(x2,y2)  
#                 {(X2,Y2)}
#              """
#     columns = shutil.get_terminal_size().columns
#     print("\n".join(line.center(columns)  for line in string.split("\n"))) # MULTI LINE STRING WITH NEW LINES
# print_box()

# def print_box():
#     def foo(a,b):
#         if a<b:
#             return ((b-a)//2)+a
#         else:
#             return ((a-b)//2)+b


#     center_line = foo(X1,X2),foo(Y1,Y2)
#     tc  = foo(X1,center_line[0]),foo(Y1,center_line[1])
#     bc = foo(X2,center_line[0]),foo(Y2,center_line[1])
    
#     string = f"""
#            Main box 

#      {(X1,Y1)}
#      (x1,y1) ------------
#      |                  |
#      |     Top box      |  
#      |    {   tc   }    |
#      |                  |
#      |------------------| {center_line}
#      |                  |
#      |    Bottom box    |  
#      |    {   bc   }    |
#      |                  |
#      -------------(x2,y2)  
#                 {(X2,Y2)}
#              """
#     columns = shutil.get_terminal_size().columns
#     print(columns)
#     print(string.center(columns))

# print_box()

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

def status(top_box,bott_box,refresh_box):
    """
        returns wheather boxes are triggered or not.
        return boolean except for one case in duck.
    """
    # get averages for top and bott
    top_avg  = np.floor(np.average(top_box))
    bott_avg = np.floor(np.average(bott_box))

    # if VERBOSITY == 2:print(top_avg,bott_avg)

    top_bool  = None
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

def append(images,img_array):
    """
        appends images in a list until it 
        crosses a limited number (FRAMES). Then 
        starts to pop before appending.
    """
    if len(images) > FRAMES:
        images.pop(0)
    images.append(img_array)

    return images

def record_death(images):
    """
        converts stored images to a video and saves it
    """
    if not os.path.exists(FOLDER):
        os.mkdir(FOLDER)

    vid_num = len(os.listdir(FOLDER)) + 1
    video_path = os.path.join(FOLDER,str(vid_num)+'.avi')

    shape = images[0].shape[1], images[0].shape[0]
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    fps = 2
    video = cv2.VideoWriter(video_path,fourcc,fps, shape)  

    for image in images:  
        video.write(image)

    cv2.destroyAllWindows()  
    video.release()  

if __name__=='__main__':
    
    # get a driver and load website.
    driver = webdriver.Firefox(executable_path=r'D:\Installers\geckodriver.exe')
    driver.get('https://chromedino.com/')

    # get elements on the page
    main_body  = driver.find_element_by_xpath("//html")
    outer_body = driver.find_element_by_id('aswift_0_expand')
    canvas     = driver.find_element_by_css_selector('.runner-canvas')

    x1,y1,x2,y2,start_time,factor = reset_variables()

    images = []

    start()

    while True:

        img,img_array = get_image()

        # get all boxes 
        main_box    = img_array[y1:y2,x1:x2,:]
        mid         = main_box.shape[0] // 2
        print(mid)
        top_box     = main_box[:mid, :, :]
        bott_box    = main_box[mid:, :, :]
        refresh_box = np.array(img.crop(REF_BOX))

        # increment 
        if int(time() - start_time) > 15:

            x1+= int(factor * 10)
            x2+= int(factor * 10)

            start_time = time()

            factor += 0.3

            print('shifting',x1,x2)

        
        # get status
        top_bool,bott_bool,r_bool,top_avg,bott_avg = status(top_box,bott_box,
                                                            refresh_box)

        text = None

        images = append(images,img_array)

        ## REFRESH BUTTON
        # if r_bool is true then reset variables
        # and start again. (game ended)
        if r_bool:
            text = "restart"
            t = threading.Thread(target=record_death,args=(images,)) #don't remove this comma after images
            t.start()
            t.join()
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
        elif top_bool and bott_bool!=0:
            text = 'high jump'
            t = threading.Thread(target=jump_higher)
            t.start()

        ## DUCK
        # if top box is triggered but bottom isn't
        # then duck. (partridge)
        elif top_bool and bott_bool==0:
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
