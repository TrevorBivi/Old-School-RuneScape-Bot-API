'''
ABOUT:
An example bot. Spin flax into bowstrings at lumbridge castle.

REQUIREMENTS:
- use default minimum window size
- use default minimum zoom
- use resizable mode
- already entered bank pin
- reset camera position (click compass)
- hide chat
- be anywhere on third floor of lumbridge castle
- have inventory selected and full of flax

CYCLE STEPS:
1.0 walk to stairs and climb down

2.0 walk to spinningwheel and use flax
    2.1 use flax on spinwheel from stairs
        2.1.1 successfully walked to spinwheel and used flax
        2.1.2 stuck outside door
              2.1.2.1 door is open now, GOTO 2.2
              2.1.2.2 door is closed, open then GOTO 2.2
    2.2 walk to spinwheel
        2.2.1 sucessfully walked to spinwheel, now use flax
        2.2.1 got stuck outside door
              2.2.1.1 door is open now. GOTO 2.2
              2.2.1.2 door is closed. Open, GOTO 2.2

3.0 craft bowstrings
    3.1 crafted all flax into bows
    3.2 interupted by level up, use flax on spinwheel and craft all to bowstrings again

4.0 walk to stairs and climb up
    4.1 Click on stairs from spinwheel
        4.1.1 successfully made it to stairs, choose climb up
        4.1.2 stuck at door
              4.1.2.1 door open now. GOTO 4.2
              4.1.2.2 door closed. Open then GOTO 4.2
    4.2 Travel to stairs first
        4.2.1 sucessfully made it to stairs, click it, then choose climb up
        4.2.2 stuck at door
              4.2.2.1 door open now. GOTO 4.2
              4.2.2.2 door closed. Open then GOTO 4.2

5.0 walk to 
    5.1 Click on bank from stairs
        5.1.1 successfully made it to bank
        5.1.2 not in bank menu. GOTO 5.2
    5.2 Walk to bank room, then click bank

6.0 use bank

TO DO:
-add more random wait times
-add random unneeded clicks and mouse movements
-make sometimes tab out of game
-make detect when out of flax in bank
'''

from osrs_tools import *
from human_input import*
import random as r
import time as t


input('offscreen point>')
offscreen_point = wgui.GetCursorInfo()[2]

lum2 = area_map('img\\lum2\\map.png',(-75+27*4,-127+58.5*4))
lum3 = area_map('img\\lum3\\map.png',(-75+141,-127+255))

areas = {'lum3':lum3,
         'lum2':lum2}

craft_im = cv2.imread('img\\lum2\\craft.png',cv2.IMREAD_COLOR) #
level_up_im = cv2.imread('img\\lum2\\level up.png',cv2.IMREAD_COLOR) # 
climb_stairs_im = cv2.imread('img\\lum2\\climb stairs.png',cv2.IMREAD_COLOR) # 


#while at the level 2 stairs click the stairs
stair2_stair_tsk = click_task((5,1,45,27),       #box to click in relative to img TL
                              'img\\lum2\\stair stair.png', #img file
                              0.65,              #required img match
                              (175,150,400,475), #box to look for img
                              'Climb Stair',     #primary action that should be seen at TL of game
                              'lum2',            #area task must be in
                              (-1,-1,0,0)        #coordinate box task must be in
                             )

#while at the level 2 stairs click the spinning wheel
stair2_spin_tsk = click_task((-43,21,-32,55),
                            'img\\lum2\\stair cross.png',
                            0.65,
                            (515,115,565,165),
                            "Use Flax -> Spinning wheel",
                            'lum2',
                            (0,0)               #coordinates task must be at
                           )

#from the hallway click the door
hallway_door_tsk = click_task((1,6,8,32),
                             'img\\lum2\\hallway closed door.png',
                             0.65,
                             (375,100,450,250),
                             "Open Door"
                             'lum2',
                             (1,-5)
                           )

#from the spinning wheel room click the door
room_door_tsk = click_task((2,9,11,43),
                          'img\\lum2\\room closed door.png',
                          0.65,
                          (325,150,375,250),
                          "Open Door"
                          'lum2',
                          (2,-6)
                         )

#from the spinning wheel click the spinning wheel
spin_spin_tsk = click_task(((-47,13,-31,64),(-47,-1,-31,10)),
                          'img\\lum2\\spin cross.png',
                          0.65,
                          (400,222,475,300),
                          "Use Flax -> Spinning wheel",
                          'lum2',
                          (3,-5)
                         )

#from the spinning wheel click the stairs
spin_stair_tsk = click_task((-20,4,49,15),
                           'img\\lum2\\spin stair.png',
                           0.65,
                          (0,350,200,500),
                           "Climb Staircase",
                          'lum2',
                          (3,-5)
                         )

#from the level 3 stairs click the stairs
stair3_stair_tsk = click_task((4,4,44,22),
                             'img\\lum3\\stair stair.png',
                             0.65,
                             (325,225,425,325),
                             "Climb-down Staircase",
                             'lum3',
                             (0,0)
                            )

#from the level 3 stairs click the bank booth
stair3_bank_tsk = click_task((4,4,43,26),
                            'img\\lum3\\stair bank door.png',
                            0.65,
                            (28,10,475,100),
                            "Bank Bank booth",
                            'lum3',
                            (0,0)#coordinate box task must be in
                          )

#from the bank room click the bank booth
bank_bank_tsk = click_task((38,-9,100,13),
                          'img\\lum3\\bank bank door.png',
                          0.65,
                          (200,175,325,250),
                          "Bank Bank booth",
                          'lum3',
                          (3,-11,5,-10) 
                          )

#from the bank menu click the flax in bank
bankui_flax_tsk = click_task((2,0,25,19),
                             'img\\bank\\bank flax.png',
                             0.65,
                             (0,0,500,300),
                             "Withdraw-1 Flax",
                             key='right' #click with right mouse button
                            )

#from the bank menu choose the withdraw option
bankui_withdraw_tsk = click_task((0,-1,100,13),
                            'img\\bank\\bank withdraw all.png',
                            
                            )

#from the bank menu click the deposit button
bankui_deposit_tsk = click_task((0,-1,90,13),
                               'img\\bank\\bank deposit all.png'
                              )

#from the bank menu click the close option
bankui_close_tsk = click_task((4,4,21,21),
                             'img\\bank\\bank close.png',
)

def spin_from_stairs():
    '''return if sucessfully use spinwheel from lum2 stairs. open door if fail'''
    print('2.1 use spinning wheel from stairs')
    print('>click flax in inventory')
    click_inv(r.randint(0,27))
    print('>clicking spinning wheel')
    if not stair2_spin_tsk.exec() or not wait_to_move('lum2') or get_stop_xy('lum2') != (3,-5):
        print('>detected fail, traveling to door')
        travel_to((1,-5),'lum2')
        print('>opening door if needed')
        hallway_door_tsk.exec()
        return False
    return True

def spin_from_anywhere():
    '''return if sucessfully use spinwheel from lum2. open door if fail'''
    print('2.2 walk to spinning wheel')
    print('>walk to spinning wheel')
    travel_to((3,-5),'lum2')
    if get_xy() != (3,-5):
        print('>detected fail, walk to door')
        travel_to((1,-5),'lum2')
        print('>open door if needed')
        hallway_door_tsk.exec()
        return False
    print('>click flax in inventory')
    click_inv(r.randint(0,27))
    print('>click spinning wheel')
    if not spin_spin_tsk.exec():
        raise clickTaskException("2.2.1 could not use flax on spin wheel")
    return True

def stairs_from_spin():
    '''return if sucessfully use stairs from lum2 spinning wheel. open door if fail'''
    print('4.1 climb stairs from spinning wheel')
    print('>clicking stairs')
    if spin_stair_tsk.exec() and wait_to_move('lum2'):
        x,y = get_stop_xy('lum2')
        if (-1 <= x <= 0 and -1 <= y <= 0):
            return True
    print('>detected fail, walk to door')
    travel_to((2,-6),'lum2')
    print('>open door if needed')
    room_door_tsk.exec()
    return False

def stairs_from_anywhere():
    '''return if sucessfully use stairs from lum2. open door if fail'''
    print('4.2 walk to stairs then climb')
    print('>walking to stairs')
    travel_to((r.randint(-1,0),r.randint(-1,0)),'lum2')
    x,y = get_xy()
    if not ( -1 <= x <= 0 and -1 <= y <= 0 ):
        print('>detected fail, walk to door')
        travel_to((2,-6),'lum2')
        print('>open door if needed')
        room_door_tsk.exec()
        return False
    print('>click on stairs')
    stair2_stair_tsk.exec()
    return True

def bank_from_stairs():
    '''from lum3 stairs, try using bank'''
    print('5.1 use bank from stairs')
    print('>click bank booth')
    if stair3_bank_tsk.exec() and wait_to_move('lum3'):
        x,y = get_stop_xy('lum3')
        successful = (3 <= x <= 4 and y == -11)
        if successful:
            return True
    print('>detected fail')
    return False

def bank_from_anywhere():
    '''from lum3, try using bank'''
    print('5.2 walk to bank then use')
    print('>walk to bank')
    travel_to((r.randint(3,5),r.randint(-11,-10)),'lum3')
    print('click on bank')
    successful = bank_bank_tsk.exec()
    if not successful:
        print('>detected fail')
    return successful

loops = 0
while True:
    print('1.0 walk to stairs and climb down')
    print('>walk to stairs')
    travel_to((0,0),'lum3')
    t.sleep(rrg(1,1.5,0.25,20))
    print('>climb down')
    stair3_stair_tsk.exec()
    t.sleep(rrg(2,1,1,20))


    print('2.0 use flax on spinning wheel')
    successful = None
    if r.randint(0,3): #randomly choose how to make first attempt
        successful = spin_from_stairs()
    else:
        successful = spin_from_anywhere()

    if not successful:
        for i in range(4):
            if spin_from_anywhere():
                break
        else:
            raise clickTaskException("could not use flax on spinning wheel")


    print('3.0 craft bowstrings')
    print('>wait to see crafting menu')
    if not wait_to_see(craft_im,(200,325,325,475),0.98,4): #wait for craft menu
        raise clickTaskException("never saw crafting menu")
    print('>select craft all')
    human_type(' ')
    
    start_craft_time = t.time()
    print('>wait to finish crafting')
    if wait_to_see(level_up_im,(0,325,150,475),0.98, rrg( 58,5,54,72  )  ):
        t.sleep(rrg(2,1,0.5,4))
        print('>detected level up interupt, reuse flax on spinning wheel')                                               
        if spin_from_anywhere():
            print('>wait to see crafting menu')
            wait_to_see(craft_im,(200,325,325,475),0.98,4) 
            print('>select craft all')
            human_type(' ')                               
            t.sleep( 56 + start_craft_time - t.time())


    print('4.0 walk to stairs and climb up')
    if(r.randint(0,2)): #randomly choose how to make first attempt
        successful = stairs_from_spin()
    else:
        successful = stairs_from_anywhere()
    if not successful:
        for i in range(4):
            if stairs_from_anywhere():
                break
        else:
            raise clickTaskException("could not climb stairs")
    print('>wait to see stair climb options')
    if not wait_to_see(climb_stairs_im,(25,325,150,400),0.98,5):
        raise clickTaskError("could not see climb popup")
    print('>select climb up')
    human_type('1') #choose climb up
    print('>wait to finish loading')
    wait_to_see(climb_stairs_im,(25,325,150,400),0.98,5,leave=True) #wait til done loading
    t.sleep(0.1)

    
    print('5.0 access bank')
    if (r.randint(0,2)):
        successful = bank_from_stairs()
    else:
        successful = bank_from_anywhere()
    if not successful:
        for i in range(2):
            if bank_from_anywhere():
                break
        else:
            raise clickTaskException("could not access bank")

     
    print('6.0 use bank')
    print('>wait for bank menu')
    if not bankui_close_tsk.wait_to_see(5): #wait for bank menu to pop up
        raise clickTaskException("could not see bank ui")
    print('>show inventory bowstring options')
    click_inv(r.randint(0,27),'right') #select a bowstring in inventory
    print('>select deposit all bowstrings')
    bankui_deposit_tsk.exec()          #deposit bowstrings
    t.sleep(rrg(0.2,.2,0.1,.3))
    print('>show bank flax options')
    bankui_flax_tsk.exec()             #select flax in bank
    t.sleep(rrg(0.2,.2,0.1,.3))
    print('>select withdraw all')
    bankui_withdraw_tsk.exec()         #withdraw flax
    t.sleep(rrg(1.5,1,0.1,20))
    print('>select close bank menu')
    bankui_close_tsk.exec()            #exit bank
    loops += 1
    print('COMPLETED LOOP #' + str(loops))
