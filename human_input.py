'''
ABOUT:
An API for creating realistic human inputs

IMPORTANT METHODS:
rrg -- create a restricted random gaussian number
human_click -- click somewhere
human_move_to -- move mouse to somewhere on screen
human_type -- type keys in a human manner
human_write -- type a string in a human manner

TO DO:
- make rrg not use a while loop to generate an acceptable number
'''


import win32con as wcon
import win32api as wapi
import win32gui as wgui
import win32ui as wui
import time
import random
import warnings

warnings.simplefilter('module', UserWarning)

#virtual key codes for keyboard events
VK_CODE = {'backspace':0x08,
           'tab':0x09,
           'enter':0x0D,
           'shift':0x10,
           'ctrl':0x11,
           'alt':0x12,
           'pause':0x13,
           'caps_lock':0x14,
           'esc':0x1B,
           ' ':0x20,
           'page_up':0x21,
           'page_down':0x22,
           'end':0x23,
           'home':0x24,
           'left_arrow':0x25,
           'up_arrow':0x26,
           'right_arrow':0x27,
           'down_arrow':0x28,
           'print_screen':0x2C,
           'ins':0x2D,
           'del':0x2E,
           '0':0x30,
           '1':0x31,
           '2':0x32,
           '3':0x33,
           '4':0x34,
           '5':0x35,
           '6':0x36,
           '7':0x37,
           '8':0x38,
           '9':0x39,
           'a':0x41,
           'b':0x42,
           'c':0x43,
           'd':0x44,
           'e':0x45,
           'f':0x46,
           'g':0x47,
           'h':0x48,
           'i':0x49,
           'j':0x4A,
           'k':0x4B,
           'l':0x4C,
           'm':0x4D,
           'n':0x4E,
           'o':0x4F,
           'p':0x50,
           'q':0x51,
           'r':0x52,
           's':0x53,
           't':0x54,
           'u':0x55,
           'v':0x56,
           'w':0x57,
           'x':0x58,
           'y':0x59,
           'z':0x5A,
           'F1':0x70,
           'F2':0x71,
           'F3':0x72,
           'F4':0x73,
           'F5':0x74,
           'F6':0x75,
           'F7':0x76,
           'F8':0x77,
           'F9':0x78,
           'F10':0x79,
           'F11':0x7A,
           'F12':0x7B,
           'num_lock':0x90,
           'scroll_lock':0x91,
           'left_shift':0xA0,
           'right_shift ':0xA1,
           'left_control':0xA2,
           'right_control':0xA3,
           '=':0xBB,
           ',':0xBC,
           '-':0xBD,
           '.':0xBE,
           '/':0xBF,
           '`':0xC0,
           ';':0xBA,
           '[':0xDB,
           '\\':0xDC,
           ']':0xDD,
           "'":0xDE,
}

#pretend hardware scan codes for key presses
HS_CODE = {'backspace':0x0E,
           'tab':0x0F,
           'enter':0x1C,
           'shift':0x2A,
           'ctrl':0x1D,
           'alt':0x38,
           'pause':0x13,
           'caps_lock':0x14,
           'esc':0x01,
           ' ':0x39,
           'page_up':0x49,
           'page_down':0x51,
           'end':0x4F,
           'home':0x47,
           'left_arrow':0x4B,
           'up_arrow':0x48,
           'right_arrow':0x4D,
           'down_arrow':0x50,
           'print_screen':0x37,
           'ins':0x52,
           'del':0x53,
           '0':0x0B,
           '1':0x02,
           '2':0x03,
           '3':0x04,
           '4':0x05,
           '5':0x06,
           '6':0x07,
           '7':0x08,
           '8':0x09,
           '9':0x0A,
           'a':0x1E,
           'b':0x30,
           'c':0x2E,
           'd':0x20,
           'e':0x12,
           'f':0x21,
           'g':0x22,
           'h':0x23,
           'i':0x17,
           'j':0x24,
           'k':0x25,
           'l':0x26,
           'm':0x32,
           'n':0x31,
           'o':0x18,
           'p':0x19,
           'q':0x10,
           'r':0x13,
           's':0x1F,
           't':0x1a,
           'u':0x16,
           'v':0x2F,
           'w':0x11,
           'x':0x2D,
           'y':0x15,
           'z':0x2C,
           'F1':0x3B,
           'F2':0x3C,
           'F3':0x3D,
           'F4':0x3E,
           'F5':0x3F,
           'F6':0x40,
           'F7':0x41,
           'F8':0x42,
           'F9':0x43,
           'F10':0x44,
           'F11':0x57,
           'F12':0x58,
           'num_lock':0x45,
           'scroll_lock':0x46,
           'left_shift':0x2A,
           'right_shift ':0x36,
           'left_control':0x1D,
           'right_control':0x1D,
           '=':0x0D,
           ',':0x33,
           '-':0x0C,
           '.':0x34,
           '/':0x35,
           '`':0x29,
           ';':0x27,
           '[':0x1A,
           '\\':0x2B,
           ']':0x1B,
           "'":0x28,
}

def restrict(val,max_val,min_val):
    '''return val restricted to a range'''
    return max( min(val,max_val), min_val )

def rrg(mu,sigma,min_limit,max_limit):
    '''returns a restricted random gaussian float

    Keyword arguments:
    mu -- average value returned
    sigma -- average deviation
             68.3% of values are within 1*sigma of mu 
             95.5% of values are within 2*sigma of mu
             99.7% of values are within 3*sigma of mu
    min_limit -- minimum limit
    max_limit -- maximum limit
    '''
    #if gaussian distribution rarely produces usable numbers warn user
    if (mu - sigma / 2 < min_limit
            and mu + sigma / 2 > max_limit):
        warnings.warn("abnormal random gaussian limits")

    #continuosly try making a usable number
    rand = random.gauss(mu,sigma)
    while not (min_limit < rand < max_limit ):
        rand = random.gauss(mu,sigma)
    
    return rand
        
def key_down(key):
    '''send key down event to keyboard input stream'''
    wapi.keybd_event(VK_CODE[key], HS_CODE[key],0,0)

def key_up(key):
    '''send key up event to the keyboard input stream'''
    wapi.keybd_event(VK_CODE[key], HS_CODE[key],wcon.KEYEVENTF_KEYUP ,0)

def mouse_move(xy,relative_xy=(0,0)):
    '''send mouse move event to mouse input stream

    Keyword arguments:
    xy -- position to move to on screen
    relative_xy -- point to move relative to (default (0,0))
    '''
    #convert to [system]
    new_x,new_y = [(xy[i]+relative_xy[i]+1)*65535/wapi.GetSystemMetrics(i) for i in range(2)]

    #send input to mouse stream
    wapi.mouse_event(wcon.MOUSEEVENTF_ABSOLUTE|wcon.MOUSEEVENTF_MOVE,int(new_x),int(new_y))

def mouse_down(key='left',xy=None):
    '''send mouse down event to the mouse input stream'''

    #get position to press at
    x,y = None,None
    if xy:
        x,y = xy
    else:
        x,y = wgui.GetCursorInfo()[2]

    #perform correctpress
    if key == 'left':
        wapi.mouse_event(wcon.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    elif key == 'right':
        wapi.mouse_event(wcon.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
    else:
        raise ValueError('invalid key')

def mouse_up(key='left',xy=None):
    '''send mouse up event to the mouse input stream'''
    #get position to release at
    x,y = None,None
    if xy:
        x,y = xy
    else:
        x,y = wgui.GetCursorInfo()[2]

    #perform correct release
    if key == 'left':
        wapi.mouse_event(wcon.MOUSEEVENTF_LEFTUP,x,y,0,0)
    elif key == 'right':
        wapi.mouse_event(wcon.MOUSEEVENTF_RIGHTUP,x,y,0,0)
    else:
        raise ValueError('invalid key')

def new_rec(end_wait=0.5):
    '''record then return a new mouse movement recording

    Keyword arguments:
    end_wait -- time mouse must stay still to signify end of recording
    '''
    actions=[]#list of actions making up recording

    start_x,start_y = wgui.GetCursorInfo()[2]
    old_pos = start_pos[:]

    start_time = None
    new_time = time.time()
    last_move_time = new_time
    
    while (new_time - last_move_time < end_wait #hasn't waited for max time
            or not start_time): #hasn't move
        new_time = time.time()
        new_pos = wgui.GetCursorInfo()[2]
        if new_pos != old_pos:

            # start recording if first move
            if(start_time == None):
                print("recording")
                start_time = new_time
            
            actions.append(( new_pos[0]-start_x,
                             new_pos[1]-start_y,
                             new_time-start_time))
            last_move_time = new_time
            old_pos = new_pos
            
    return actions


def rec_session(end_wait=0.5):
    '''return recordings made during session

    Keyword arguments:
    end_wait -- time mouse must stay still to signify end of recording
    '''
    print('''--------------------------------------------
You are now using the recording maker.

Commands:
(empty)      -- Make a mouse recording. Finishes when mouse stops moving for 0.5s
p            -- play back last recording
p<int>       -- play back recording at index
p<int>:<int> -- play back multiple recordings
d            -- delete last recording
d<int>       -- delete recording at index
d<int>:<int> -- delete multiple recordings
f            -- finish and return recordings
''')
    recs = []
    while True:
        inp = input(">")
        ln = len(inp)
        if( ln == 0):
            print("waiting")
            recs.append(new_rec(end_wait))
            print("done - # recordings:",len(recs))
            continue
        else:
            split = inp.find(":")
            v1 = -1
            v2 = None

            #param(s) given
            if ln > 1: 
                try:
                    if split == -1:#1 int
                        v1 = int(inp[1:])
                    else:#2 ints
                        v1 = int(inp[1:split])
                        v2 = min( int(inp[split+1:]), len(recs))
                except ValueError:
                    print("invalid parameters")
                    continue
                
            rec_amnt = len(recs)
            c = inp[0]

            #stop session
            if c == "f" and v1 == -1 and v2 == None: 
                print("\nYou are no longer using the recording maker.\n--------------------------------------------")
                return recs

            #playback
            elif c == "p" and rec_amnt > 0: 
                start_xy = wgui.GetCursorInfo()[2]
                if v2:
                    for i in range(v1,v2):
                        perform_rec(recs[i],start_xy)
                        time.sleep(0.25)
                else:
                    perform_rec(recs[v1],start_xy)

            #delete
            elif c == "d" and rec_amnt > 0: 
                 if v2:
                    recs = recs[0:v1] + recs[v2:]
                 else:
                    del recs[v1]
                 print("# recordings:",len(recs))

def read_recs(filename):
    '''return list of mouse movement recordings that are saved to the harddrive'''
    moves = []
    file = open(filename,'r')
    actions = []
    
    for line in file:
        
        if(len(line) < 3):
            moves.append(actions)
            actions = []
        else:
            i = line.index(',')
            j = line[i+1:].index(',') + i + 1

            x_disp = int(line[:i])
            y_disp = int(line[i+1:j])
            t_disp = float(line[j+1:])
            actions.append( ( x_disp,y_disp,t_disp ) )
    return moves

def conv_recs_to_txt(recs):
    '''return a text version of mouse recording'''
    txt = ""
    for rec in recs:
        for act in rec:
            txt += str(act[0])+','+str(act[1])+','+ str(act[2])[0:9] +'\n'
        txt += '\n'
    return txt

def write_recs(filename,recs):
    '''write text version of a mouse recording to a file'''
    file = open(filename,'w')
    full_txt = conv_recs_to_txt(recs)
    file.write(full_txt)
    file.close()


def distort_rec(rec,x_scale,y_scale,t_scale):
    '''distort the scale of a mouse recording'''
    new_act = []
    for pos,ac in enumerate(rec):
        new_act.append( (ac[0]*x_scale,ac[1]*y_scale,ac[2]*t_scale) )
    return new_act        


def perform_rec(actions,start_xy):
    '''perform a mouse recording

    Keyword arguments:
    rec -- the mouse recording to preform
    start_xy -- the start position of the movement
    '''
    
    start_time = time.time()
    elapsed_time = 0
    
    for ac in actions:
        time.sleep( max(ac[2]-elapsed_time,0 ))
        mouse_move(ac[0:2],start_xy)
        elapsed_time = time.time() - start_time

    return elapsed_time - start_time


default_recordings = read_recs('small moves 01') + read_recs('med moves 0')

def human_move_to(xy,recordings = default_recordings):
    '''move to a position on screen by playing back a human mouse movement

    Keyword arguments:
    new_xy -- position to move to on screen
    recordings -- list of recordings that can be played    
    '''

    x,y = wgui.GetCursorInfo()[2]
    dx = xy[0]-x
    dy = xy[1]-y
    
    if not (dx == 0 and dy == 0):
        chosen_act = None
        chosen_diff = 99999999
        for ac in recordings:
            if((ac[-1][0] > 0) == (dx > 0) and (ac[-1][1] > 0) == (dy > 0)):
                new_diff = (ac[-1][0] - dx) ** 2 + (ac[-1][1] - dy) ** 2
                if new_diff < chosen_diff:
                    chosen_act = ac
                    chosen_diff = new_diff
        
        #get scale
        if chosen_act[-1][0] == 0:
            x_scale = 1.5
        else:
            x_scale = dx/chosen_act[-1][0]     
        if  chosen_act[-1][1] == 0:
            y_scale = 1.5
        else:
            y_scale = dy/chosen_act[-1][1]

        t_scale = random.uniform(0.9,1.1)
        perform_rec(  distort_rec(chosen_act,x_scale,y_scale,t_scale),(x,y))

def human_click(xy=None,key='left',up_speed=1,down_speed=1,recordings=default_recordings):
    '''moves to a point and clicks with a realistic wait before click and release
    wait times are a gaussian random between 0.2 and 1

    Keyword arguments:
    xy -- position to move to for click (default None)
    up_speed -- multiplier for initial wait time (default 1)
    down_speed -- multiplier for release wait time (default 1)
    recordings -- recordings to choose from for move to xy
    '''
    if xy:
        human_move_to(xy,recordings)
        
    time.sleep(rrg(0.2,.15,0.2,1))
    mouse_down(key)
    time.sleep(rrg(0.2,.15,0.2,5))
    mouse_up(key)

def human_type(*keys,speed = 1):
    '''type keys with human like delays'''
    for i,key in enumerate(keys):
        press_type = 0
        if(len(key) > 1):
            if(key[0] == '/'): # is key down only
                press_type = 1
                key = key[1:]
            elif(key[0] == '\\'): # is key up only
                press_type = 2
                key = key[1:]
              
        if key == 'pass':
            time.sleep(rrg( 0.5*speed,.15*speed,0.25*speed,0.9*speed))
        else:
            if press_type != 2:#need to press
                if key == ' ' or key == 'shift' or (i != 0 and keys[i-1] == key):
                    time.sleep(rrg( 0.1*speed,.05*speed,0.07*speed,0.9*speed))
                else:
                    time.sleep(rrg( 0.17*speed,.075*speed,0.04*speed,1*speed))
                key_down(key)

            if press_type != 1:#need to release
                time.sleep(rrg(0.13*speed,.06*speed,0.06*speed,0.4*speed))
                key_up(key)
        
shifted_chars =   '!@#$%^&*()ABCDEFGHIJKLMNOPQRSTUVWXYZ~_+{}:"|<>?'
unshifted_chars = "1234567890abcdefghijklmnopqrstuvwxyz`-=[];'\\,./"

def unshift_key(val):
    '''return unshifted key value'''
    index = shifted_chars.find(val)
    if index != -1:
        return unshifted_chars[index]
    
    return val


def human_write(txt,spd = 1,err_chance = -1,err_keys=unshifted_chars[:36]):
    '''type string with human like delays
    
    Keyword arguments:
    txt -- string to type
    speed -- speed to type at
    err_chance -- chance of making a typo and needed to backspace
    err_keys -- keys that can be used to create fake typos
    '''
    
    shift = False
    keys = []
    len_txt = len(txt)

    #for every char to type
    for pos,char in enumerate(txt):
        index = shifted_chars.find(char)

        #if is capital handle shift press
        if index != -1:
            if not shift:
                shift = True
                keys.append('/shift')
            keys.append(unshifted_chars[index])

        #if isn't capital handle shift release
        else:
            if shift:
                shift = False
                keys.append('\shift')
            keys.append(char)
            
        #if faking a typo
        if err_chance > random.uniform(0,1):
            correct_delay = int(abs( rrg(0,2.5,-5,5 ) )) + 1
            keys[-1:-1] = [
                           err_keys[random.randint(0,len(err_keys) - 1)],#add random char instead of key
                           *[unshift_key(i) for i in txt[pos+1:min(pos+correct_delay,len_txt)] ],#characters before error is detected
                           'pass',#delay
                           *['backspace' for i in range(min(correct_delay,len_txt-pos))]#start hitting backspace
                          ]
    human_type(*keys,speed=spd)
