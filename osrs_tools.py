'''
ABOUT:
An API for making hard to detect Old School Runescape bots using pixel colors and controlling the users mouse and keyboard

IMPORTANT CLASSES:
area_map -- contains map image and game coordinates at top right of map
click_task -- used to click somewhere relative to an key image - see class doc for more info

IMPORTANT METHODS:
get_win_xy -- get top left position of game window
get_rot -- gets the current rotation of the compass pointer
set_rot -- sets the compass to be exactly north if it isn't already
get_area -- get the name of the area the player is in
get_xy -- get game coordinates of player relative to the area they are in
travel_to -- move to given coordinates of the area the player is currently in
get_text_xy -- return position of text's top left on screen
click_task().exec -- click in a box relative to a key image on screen
wait_to_see -- wait for an image to be somewhere on screen
screenshot -- screenshot game window or primary monitor
match_template -- return the match position and accurary of a given image template in a given image

REQUIREMENTS:
- needs to be used in conjunction with my Human Input API

TO DO:
- ability to make get_text_xy only search for certain text colors
- ability to dismiss random event NPCs using get_text_xy to look for player's name being said
- make travel_to use a node based path navigation to allow for more complex travel_to paths without getting stuck
- make travel_to allow for an end position in a different area if they overlap
- make travel_to able to use agility shortcuts and ,enter buildings, climb stairs, etc.
- in get_xy use masks to use the whole minimap circle as a template image instead of a square inside the circle
- make maps able to automatically add to themselves as you move around
- make fix_compass accept a desired compass rotation parameter instead of always being North
   by using get_rot while sliding mouse in a given safe area to click
- create method to launch game from file path
- create methods for logging into game and entering bank pin using click_tasks
'''

import cv2
import numpy as np
from PIL import ImageGrab as iGrab
from matplotlib import pyplot as plt
import math
import time
import human_input as hi
import random

#fonts used for get_text_xy
def_font = {
                'a':cv2.imread('img\\fonts\\default\\a.png',cv2.IMREAD_UNCHANGED),
                'b':cv2.imread('img\\fonts\\default\\b.png',cv2.IMREAD_UNCHANGED),
                'c':cv2.imread('img\\fonts\\default\\c.png',cv2.IMREAD_UNCHANGED),
                'd':cv2.imread('img\\fonts\\default\\d.png',cv2.IMREAD_UNCHANGED),
                'e':cv2.imread('img\\fonts\\default\\e.png',cv2.IMREAD_UNCHANGED),
                'g':cv2.imread('img\\fonts\\default\\g.png',cv2.IMREAD_UNCHANGED),
                'h':cv2.imread('img\\fonts\\default\\h.png',cv2.IMREAD_UNCHANGED),
                'i':cv2.imread('img\\fonts\\default\\i.png',cv2.IMREAD_UNCHANGED),
                'k':cv2.imread('img\\fonts\\default\\k.png',cv2.IMREAD_UNCHANGED),
                'l':cv2.imread('img\\fonts\\default\\l.png',cv2.IMREAD_UNCHANGED),
                'm':cv2.imread('img\\fonts\\default\\m.png',cv2.IMREAD_UNCHANGED),
                'n':cv2.imread('img\\fonts\\default\\n.png',cv2.IMREAD_UNCHANGED),
                'o':cv2.imread('img\\fonts\\default\\o.png',cv2.IMREAD_UNCHANGED),
                'p':cv2.imread('img\\fonts\\default\\p.png',cv2.IMREAD_UNCHANGED),
                'r':cv2.imread('img\\fonts\\default\\r.png',cv2.IMREAD_UNCHANGED),
                's':cv2.imread('img\\fonts\\default\\s.png',cv2.IMREAD_UNCHANGED),
                't':cv2.imread('img\\fonts\\default\\t.png',cv2.IMREAD_UNCHANGED),
                'w':cv2.imread('img\\fonts\\default\\w.png',cv2.IMREAD_UNCHANGED),
                'x':cv2.imread('img\\fonts\\default\\x.png',cv2.IMREAD_UNCHANGED),
                'y':cv2.imread('img\\fonts\\default\\y.png',cv2.IMREAD_UNCHANGED),

                'B':cv2.imread('img\\fonts\\default\\_b.png',cv2.IMREAD_UNCHANGED),
                'C':cv2.imread('img\\fonts\\default\\_c.png',cv2.IMREAD_UNCHANGED),
                'D':cv2.imread('img\\fonts\\default\\_d.png',cv2.IMREAD_UNCHANGED),
                'F':cv2.imread('img\\fonts\\default\\_f.png',cv2.IMREAD_UNCHANGED),
                'O':cv2.imread('img\\fonts\\default\\_o.png',cv2.IMREAD_UNCHANGED),
                'S':cv2.imread('img\\fonts\\default\\_s.png',cv2.IMREAD_UNCHANGED),
                'U':cv2.imread('img\\fonts\\default\\_u.png',cv2.IMREAD_UNCHANGED),
                'P':cv2.imread('img\\fonts\\default\\_p.png',cv2.IMREAD_UNCHANGED),
                'W':cv2.imread('img\\fonts\\default\\_w.png',cv2.IMREAD_UNCHANGED),
                'T':cv2.imread('img\\fonts\\default\\_t.png',cv2.IMREAD_UNCHANGED),

                '1':cv2.imread('img\\fonts\\default\\1.png',cv2.IMREAD_UNCHANGED),

                '-':cv2.imread('img\\fonts\\default\\-.png',cv2.IMREAD_UNCHANGED),
                '>':cv2.imread('img\\fonts\\default\\arrow.png',cv2.IMREAD_UNCHANGED),
                }
def_font_masks = {}

for key,it in def_font.items():
    new_char = cv2.cvtColor(it, cv2.COLOR_BGRA2GRAY)
    new_mask = cv2.split(it)[3]
    def_font[key] = new_char
    def_font_masks[key] = new_mask

fonts = {
    'default':def_font
    }

font_masks = {
    'default':def_font_masks
}



#Game window information
win_xy = 0,0 #position of game window's top left corner on screen
win_sz = 765,503 #size of game window on screen

#key images used in get_window_xy
harp_im = cv2.imread('img\\calibration\\harp.png',cv2.IMREAD_COLOR) #harp button icon at bottom right
chat_all_im = cv2.imread('img\\calibration\\all.png',cv2.IMREAD_COLOR) #chat button text at bottom left

#compass image used to check compass is pointed north
compass_im = cv2.imread('img\\calibration\\compass.png',cv2.IMREAD_COLOR) #compass pointer at top right (must be north to )
compass_mid_xy = 605,22 #position of the middle of the compass on screen

#information for using the minimap
map_mid_xy = 684,85 #center position on map
map_sz = 54#radius of minimap from center (uses a square for now)

class botException(Exception):
    pass

class area_map(object):
    def __init__(self,file_name,offset_xy):
        self.map = cv2.imread(file_name, cv2.IMREAD_COLOR)
        self.offset = offset_xy

areas = {
         }

def show(img):
    plt.subplot(122),plt.imshow(img)#,cmap='gray',
    plt.show()

def sum_i(*pnts):
    '''return n dimentional points added together '''
    return [sum(i) for i in zip(*pnts)]

def sub_i(p1,*pnts):
    '''return first n dimentional point minus all others'''
    p1 = p1[:]
    for p in pnts:
        p1 = p1[0] - p[0], p1[1] - p[1]
    return p1

def dist2(p1,p2):
    '''return squared distance between two n dimensional points'''
    return sum([ (p1[i]-p2[i])**2 for i in range(len(p1)) ])

def dist(p1,p2):
    '''return distance between two n dimension points'''
    return math.sqrt(dist2(p1,p2))

def screenshot(box = None,target_game_window=True):
    '''return image at given box on screen

    Keyword arguments:
    box -- box to target on screen (default None)
    target_game_window -- target inside the game window instead of whole screen (default True)'''
    if target_game_window:
        if box == None:
            box = (win_xy[0],
                   win_xy[1],
                   win_xy[0]+win_sz[0],
                   win_xy[1]+win_sz[1])
        else:
            box = (box[0] + win_xy[0],
                   box[1] + win_xy[1],
                   box[2] + win_xy[0],
                   box[3] + win_xy[1])
            
    img = iGrab.grab(box)
    cv_im =  cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return cv_im

def match_template(image,template,min_match=-1,error=False):
    '''returns top left position of best match for image 

    Keyword arguments:
    image -- the image template is inside
    template -- the image to find inside of image
    min_match -- minimum match before fail 0.0-1.0 (default -1.0)
    error -- if fail, raise error instead of return none (default = False)
    '''
    #setup mask layer
    mask = None
    if template.shape[2] == 4:
        t_channels = cv2.split(template)
        template = cv2.merge(t_channels[:3])
        mask = cv2.merge([t_channels[3]]*3)
    
    match = cv2.minMaxLoc(cv2.matchTemplate(image, template ,cv2.TM_CCORR_NORMED,mask=mask))
    if min_match > match[1]:
        if error:
            raise botException("failed to match a template")
        return None

    return match[3],match[1] 

def get_text_xy(
        text,box=None,font_name="default",
        l_gap=1,r_gap=4,t_gap=1,y_height=17,
        relative=False, error=False):
    '''Return position of text in game

    Keyword arguments:
    box -- the area on in the game window to look for the text (default entire game window)
    font_name -- name of font to use (default "default")
    l_gap -- extra left columns to scan for non leading chars (default 1)
    r_gap -- extra right columns to scan for non leading chars (default 3)
    t_gap -- extra above rows to scan for non leading chars (default 1)
    y_height -- total rows to scan for non leading chars (default 17)
    relative -- return xy relative to box top left (default False)
    error -- if fail, raise error instead of return none (default = False)
    '''
    if box == None:
        box = (0,0,*win_sz)
        
    view = screenshot(box)
    mono_view = np.zeros((view.shape[0],view.shape[1]), dtype="uint8")#cv2.inRange(view,(0,0,0),(55,55,55))
    
    font = fonts[font_name]
    font_mask = font_masks[font_name]
    
    for i in range(view.shape[0]):
        for j in range(view.shape[1]):
            if max(view[i,j]) > 70:
               mono_view[i,j] = 208
               
    #For every potential first character
    res = cv2.matchTemplate(mono_view , font[text[0]] ,cv2.TM_CCORR_NORMED,mask=font_mask[text[0]])
    matches = np.where( res > 0.985)
    for pt in zip(*matches[::-1]):

        #for all charactes after
        next_x = pt[0] + font[text[0]].shape[1]
        y = pt[1] - t_gap
        for char in text[1:]:
            view[0,next_x] = [255,0,0]
            if char == ' ':#skip over spaces
                next_x += 4
                continue
            if not char in def_font.keys():
                raise ValueError(char + " isn't included in def_font yet.")
            
            #if char not in expected area stop looking
            char_space = mono_view[y:y+y_height ,next_x-l_gap:next_x + font[char].shape[1]+r_gap] #space character could be in
            _,max_val,_,max_xy = cv2.minMaxLoc(cv2.matchTemplate(char_space, font[char] ,cv2.TM_CCORR_NORMED,mask=font_mask[char]))
            max_xy = max(max_xy[0],0),max_xy[1]
            if max_val < 0.984:
                break
            
            next_x += max_xy[0] + font[char].shape[1] #start of next place to look
        else:
            if relative:
                return pt
            return sum_i(pt,box[:2])
    if error:
        raise botException("could not find text xy")
    return None

def calibrate_win_xy(error=False):
    '''return if successfully set win_xy to xy of window's top left corner on screen'''
    global win_xy
    view = screenshot(target_game_window = False)

    #find key points
    harp_xy = match_template(view,harp_im,0.95)[0]  
    all_xy = match_template(view,chat_all_im,0.95)[0]  
    compass_xy = match_template(view,compass_im,0.98)[0]

    #if key points are in correct relative positions
    if (abs(harp_xy[0] - all_xy[0]-710) < 3 and
        abs(harp_xy[1] - all_xy[1]+13) < 3 and
        abs(harp_xy[0] - compass_xy[0] - 134) < 3 and
        abs(harp_xy[1] - compass_xy[1] - 457) < 10):
        win_xy = (compass_xy[0] - 602, compass_xy[1]-15)
        return True
    if error:
        raise botException("Make sure window is visible and min default size")
    return False

def get_win_xy():
    '''return value of win_xy'''
    return win_xy

NORTH = 0
EAST = 90
SOUTH = 180
WEST = -90

def get_direction(use_radians = False):
    '''return direction of compass
       N=0,E=90,S=+-180,W=-90
   Keyword arguments:
    use_radians -- return direction in radians instead of degrees
    '''
    NEEDLE_RADIUS = 9

    view = screenshot((compass_mid_xy[0] - NEEDLE_RADIUS,
                       compass_mid_xy[1] - NEEDLE_RADIUS,
                       compass_mid_xy[0] + NEEDLE_RADIUS,
                       compass_mid_xy[1] + NEEDLE_RADIUS))
    
    best_red = None
    red_dist = 7
    
    for x in range(NEEDLE_RADIUS*2):
        for y in range(NEEDLE_RADIUS*2):
            pxl_dist = dist((x - NEEDLE_RADIUS,y - NEEDLE_RADIUS),(0,0,0))
            b_chan,g_chan,r_chan = view[y,x]
            
            if (red_dist < pxl_dist and g_chan < 30
                   and b_chan < 30 and r_chan > 30):
               best_red = math.atan2( x - NEEDLE_RADIUS,NEEDLE_RADIUS-y )
               red_dist = pxl_dist

    if (best_red == None):
        raise botException("Game window must be miscalibrated!")

    return best_red if use_radians else math.degrees(best_red)
                            
compass_box = (596,12,622,33)
def fix_compass():
    '''Adjusts the compass to be north if it is not already.'''
    #if north facing compass pointer not seen
    view = screenshot(compass_box)
    if(match_template(view,compass_im)[1] < 0.985):
        
        click_rxy = [ hi.rrg((compass_box[i]+compass_box[i+2])/2,(compass_box[i]+compass_box[i+2])/3.5,compass_box[i],compass_box[i+2]) for i in range(2)] #where to click relative to center of compass
        hi.human_click(sum_i(win_xy,click_rxy))


def random_point(boxes,gaussian_rand = True):
    '''randomly select a point from a box or list of boxes. chance of choosing a box weighted based on size

    Keywork Arguments:
    boxes -- a box or list of boxes to click in
    gaussian_rand -- use gaussian point spread or evenly spread
    '''
    #Determine pixels per box and total possible pixel choices
    pxl_amnts = [(box[2] - box[0])*(box[3] - box[1]) for box in boxes]
    total_pxls = sum(pxl_amnts)
    
    box_rand = random.uniform(0,1)

    #find selected box
    pxls_checked = 0
    for box_id,pxls in enumerate(pxl_amnts):
        pxls_checked += pxls
        if pxls_checked/total_pxls >= box_rand: #if box chosen

            #return random point in box
            if gaussian_rad:
                return [boxes[box_id][i] + hi.rrg(
                                                             (boxes[box_id][i+2]-boxes[box_id][i])/2, (boxes[box_id][i+2]-boxes[box_id][i])/3, boxes[box_id][i],boxes[box_id][i+2]
                                                             ) for i in range(2)]
            return [boxes[box_id][i] + random.randint(0,boxes[box_id][i+2]-boxes[box_id][i]) for i in range(2)]

def get_area(min_match = -1):
    '''returns the name of the area the player is currently in from areas.'''
    fix_compass()
    best_name = None
    best_match = 0
    view = screenshot((map_mid_xy[0]-map_sz-1,
                       map_mid_xy[1]-map_sz-1,
                       map_mid_xy[0] -1 + map_sz,
                       map_mid_xy[1] -1 + map_sz))

    #find map that matches with highest correlation
    for name,map_ob in areas.items():
        xy,match = match_template(map_ob.map, view)
        if match > best_match:
            best_match = match
            best_name = name

    if best_match < min_match:
        raise ValueError('can not find good map')

    return best_name        

def get_xy(area=None):
    '''return tuple of x y coordinates relative to the current area.

    Keyword arguments:
    area -- name of player's game area, or None to find name using get_area (default None)  
    '''
    if area == None:
        area = get_area()
    else:
        fix_compass()

    view = screenshot((map_mid_xy[0]-map_sz-1,
                       map_mid_xy[1]-map_sz-1,
                       map_mid_xy[0] -1 + map_sz,
                       map_mid_xy[1] -1 + map_sz))

    #get map coords
    xy = match_template(areas[area].map, view, .8)[0]
    if not xy:
        raise botException("can not find position")
    #convert to game coords
    xy = sub_i(xy,areas[area].offset) #xy[0] - areas[area].offset[0], xy[1] - areas[area].offset[1]
    return xy[0]/4,xy[1]/4

def wait_to_move(area=None,max_time=10,check_freq=0.75,error=False):
    '''return game xy player stops moving at or None if taking too long.

    Keyword arguments:
    area -- name of player's game area, or None to find name using get_area (default None)
    max_time -- wait time before fail (default 10.0)
    check_freq -- time between checks for xy change (default 0.75)
    error -- if fail, raise error instead of return none (default = False)
    '''
    if area == None:
        area = get_area()
        
    start_xy = get_xy(area)
    start_time = time.time()

    while (time.time()-start_time < max_time):
        if start_xy != get_xy(area):
            return True
        time.sleep(check_freq)
    if error:
        raise botException("never detected movement")
    return False

def get_stop_xy(area=None,max_time=10,check_freq = 0.75, error=False):
    '''return game xy player stops moving at or None if taking too long.

    Keyword arguments:
    area -- name of player's game area, or None to find name using get_area (default None)
    max_time -- wait time before fail (default 10.0)
    check_freq -- time between checks for xy change (default 0.75)
    error -- if fail, raise error instead of return none (default = False)
    '''
    if area == None:
        area = get_area()

    last_xy = get_xy(area)
    start_time = time.time()
    
    while (time.time()-start_time < max_time):
        new_xy = get_xy(area)
        if last_xy == get_xy(area):
            return new_xy
        last_xy = new_xy
        time.sleep(check_freq)

    if error:
        raise botException("never detected stop of movement")
    return None


def click_on_map(xy,cur_xy,click_closest = True):
    '''returns whether clicked xy or clicked closest visible xy on minimap'''
    if xy == cur_xy:
        return True

    MAP_RADIUS = 18
    map_to_rxy = sub_i(xy,cur_xy) #relative new pos in game xy
    move_dist =  dist(xy,cur_xy)   
    
    if move_dist < MAP_RADIUS: #convert to screen xy
        map_to_rxy = [i * 4 for i in map_to_rxy]       
    else:
        if not click_closest:
            return False
        map_to_rxy = [map_to_rxy[i] * 72 // move_dist for i in range(2)] # 72 = 4 * 18 

    fix_compass()
    hi.human_click(sum_i(map_to_rxy,map_mid_xy,win_xy))
    return move_dist < MAP_RADIUS
    
def travel_to(xy,area=None,wait_speed=1,max_time=15,return_early=False,readjust=True,error = False):
    '''return if succesfully moved to position xy of area by clicking the minimap 

    Keyword arguments:
    xy -- game area coordinates to move to
    area -- name of player's game area, or None to find name using get_area (default None)
    wait_speed -- time between map clicks (default 0.5)
    max_time -- time before an issue has occured and should return False (default 15.0)
    return_early -- return on last click instead of once in position (default False)
                    using True can cause character to not be perfectly positioned
    readjust -- readjust if not at xy after last click when not returning early
                this can be needed on slower computers or when running
    error -- if fail, raise error instead of return none (default = False)
    '''

    start_time = time.time()
    
    if area==None:
        area = get_area()
    start_xy = get_xy(area)
    
    #click on map till click on proper value
    while not click_on_map(xy,get_xy(area)):
        time.sleep(hi.rrg(4,1,3,5)*wait_speed)
        if(time.time() - start_time > max_time):#return False if taking too long
            break

    else:
        if not return_early:

            wait_to_move(area,5)            
            cur_xy = get_stop_xy(area)
            
            if( cur_xy != xy and readjust): #readjust if not in position
                click_on_map(xy,cur_xy)
                get_stop_xy()
        return True
    return False


def wait_to_see(img,box=None,min_match=0.9,max_time=10,check_freq=0.33,leave = False,error=False):
    '''returns whether or not saw image within wait time

    Keywork arguments:
    img -- the image to scan for
    box -- region within screen to limit scan (default None)
    min_match -- minimim amount the image must match (default 0.9)
    max_time -- wait time before fail (default 10)
    check_freq -- time between checks for image (default 0.33)
    leave -- if waiting for img to leave instead of appear (default False)
    error -- if fail, raise error instead of return none (default = False)
    '''
    start_time = time.time()
    while (time.time()-start_time < max_time):
        if (match_template(screenshot(box),img,min_match) != None) != leave:
            return True
        time.sleep(check_freq)
    if error:
        if leave:
            raise botException("image never left vision")
        raise botException("never saw image")
    return False

def click_inv(slot=0,key='left'):
    '''click on an inventory slot

    Keyword arguments:
    slot -- slot number to click
    key -- mouse key to click'''
    slot_rxy = (slot % 4)*42,(slot // 4)*36
    start_xy = hi.rrg(581,5,570,592),hi.rrg(228,5,218,235)
    hi.human_move_to(sum_i(slot_rxy,start_xy,win_xy))
    hi.human_click(None,key)

class click_task(object):
    '''class to click in a box relative to a key image somewhere on screen 

    Keyword arguments:
    img_file -- file used for key image
    img_box -- area in game window to scan for key image
    img_acc -- minimum image match needed to perform task
    click_boxes -- box or list of boxes to click in on screen relative to top left corner of key image
    area -- name of required game area, or None for ignore area and ignore xy_box (default None)
    xy_box -- coordinate box player must be in or coordinates to be turned into a 1x1 box
              or None for ignore xy restriction (default None)
    mouse_key -- name of mouse key to click (default 'left')
    action_text -- string found in top left action text when mouse is position  (default None)
    '''
    def __init__(self,click_boxes,img_file,img_match=0.8,img_box=None,action_text=None,area=None,xy_box=None,key='left'):
        #image vars
        self.img_file = img_file #filename
        self.img = cv2.imread(img_file,cv2.IMREAD_COLOR)# file
        if img_box:
            self.img_box = img_box #area to scan for image
        else:
            self.img_box = (0,0,*win_sz)
        self.img_match = img_match #match accuracy needed

        #click vars
        if type(click_boxes[0]) is int:#click boxes
            self.click_boxes = (click_boxes,)
        else:
            self.click_boxes = click_boxes
        self.key = key

        #action text vars
        self.action_text = action_text

        #position vars
        self.area = area
        if xy_box == None:
            self.xy_box = None
        elif len(xy_box) == 4:
            self.xy_box = xy_box
        else:
            self.xy_box = xy_box+xy_box

    def is_positioned(self):
        '''return if in needed area and xy box'''
        #task needs no position
        if self.xy_box == None or self.area == None: 
            return True

        #in required position
        cur_area = get_area()
        cur_xy = get_xy(cur_area)
        return (self.xy_box[0] <= cur_xy [0] <= self.xy_box[2] and self.xy_box[1] <= cur_xy [1] <= self.xy_box[3]) and cur_area == self.area
        
    def get_img_xy(self):
        '''get game screen position of task's key image'''
        fix_compass()
        if self.is_positioned():
            lm_view = screenshot( self.img_box )
            max_xy,max_match = match_template(lm_view,self.img)

            if max_match > self.img_match:
                return sum_i(max_xy,self.img_box[:2])    
        return None
    
    def ready_wait(self,max_time=10,check_freq=0.33,leave=False,error=True):
        '''wait to be in position and able to see img
        
        Keyword arguments:
        max_time -- wait time before fail (default 10.0)
        check_freq -- time between checks for xy change (default 0.75)
        leave -- wait to not be ready instead (defult None)
        error -- if fail, raise error instead of return none (default = False)
        '''
        start_time = time.time()
        while ( time.time() - start_time < max_time):
            if (self.is_positioned() and self.get_img_xy()!=None ) != leave:
                return True
            time.sleep(check_freq)

        if error:
            raise botException("never stopped being ready")
        raise botException("never ready")
        return False
    
    def exec(self,click_box_id=None,error = False):
        '''try to perform click task

        Keyword arguments:
        click_box_id -- the index of the click box that should be use in the list of click boxes
                        or None for random box (default None)
        error -- if fail, raise error instead of return none (default = False)
        '''

        #find reference image location
        if not self.is_positioned():
            return False
        img_xy = self.get_img_xy()
        if img_xy == None:
            return False

        #try to click on right area
        for i in range(5):
            
            box = None
            if click_box_id == None:
                box = self.click_boxes[random.randint(0,len(self.click_boxes)-1)]
            else:
                box = self.click_boxes[click_box_id]
            click_rxy = [ hi.rrg((box[i]+box[i+2])/2,
                                 (box[i]+box[i+2])/3.5,
                                 box[i],
                                 box[i+2]) for i in range(2)]
            
            fix_compass()
            hi.human_move_to(sum_i(win_xy,img_xy,click_rxy))
            if self.action_text == None or get_text_xy(self.action_text,(0,3,450,22)):
                hi.human_click(key=self.key)
                return True
            time.sleep(hi.rrg(0.25,0.1,0.175,2))
        if error:
            raise botException("failed to click")
        return False
