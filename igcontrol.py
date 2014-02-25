import os
import sys
sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/')

from autopy import mouse, key
from numpy import add
import cv2
import matching
import time

reload(matching)

CMD_RESIZE_FF = """osascript -e 'tell application "Firefox" to set visible of windows to true'"""
CMD_ACTIVATE_FF = """osascript -e 'tell application "Firefox" to activate'"""

SH_FILENAME = 'img/screenshot.png'
TICKET_SELL = (230,130)
TICKET_BUY  = (330,130)
TICKET_SIZE = (110,100)
TICKET_STOP = (90, 245)
TICKET_EDIT = (230,65)
TICKET_EDIT_STOP = (125,260)

LONG = 0
SHORT = 1

REFRESH_TIMEOUT = 10
MATCH_OK = 0.98

def load_file(filename):
    return cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2GRAY)

def multi_load_file(filename):
    return [load_file('img/' + f) for f in os.listdir(os.path.join(os.getcwd(), 'img')) if filename in f]

ticket_dax_deal = multi_load_file('ticket_dax_deal')
ticket_dax_open = multi_load_file('ticket_dax_open')
close_btn = multi_load_file('close')
submit_btn = multi_load_file('submit')
watchlists = multi_load_file('watchlists')
open_positions = multi_load_file('open_positions')
cfd_list = {'dax': multi_load_file('dax_list')}

def activate_firefox():
    os.system(CMD_RESIZE_FF)
    os.system(CMD_ACTIVATE_FF)
    time.sleep(1.5)

def get_screenshot():
    os.system('screencapture -x ' + SH_FILENAME)
    return load_file(SH_FILENAME)

def load_prev_screenshot():
    return load_file(SH_FILENAME)

def get_match(screen, img_arr, max_level):
    max_element = (0,(0,0))
    maxval = 0
    for i in range(0, len(img_arr)):
        m, p = matching.fast_template_matching(screen, img_arr[i], max_level)
        if m > maxval:
            maxval = m
            max_element = (m,p)
        if m > MATCH_OK:
            break

    return max_element

def wait_for_window(win_img, max_level):
    maxval = 0
    count = 0
    while maxval <= MATCH_OK and count < REFRESH_TIMEOUT:
        maxval, pos = get_match(get_screenshot(), win_img, max_level)
        count += 1
    if maxval <= MATCH_OK:
        return False
    else:
        return pos

def moveclick(xpos, ypos):
    mouse.move(xpos, ypos)
    time.sleep(0.05)
    mouse.click()

def set_size(ticket_pos, size):
    type_text(add(ticket_pos, TICKET_SIZE), size)

def set_stop(ticket_pos, stop):
    type_text(add(ticket_pos, TICKET_STOP), stop)

def set_edit_stop(ticket_pos, stop):
    type_text(add(ticket_pos, TICKET_EDIT_STOP), stop)
    
def type_text(pos, text):
    moveclick(*pos)
    if isinstance(text,int):
        text = str(text)
    for i in range(10):
        key.tap(key.K_BACKSPACE)
    for k in text:
        key.tap(k)

def is_position_open(symbol):
    pos = wait_for_window(open_positions, 1)
    if pos:
        screen = load_prev_screenshot()
    else:
        return False
    
    win_pos = pos
    maxval, pos = get_match(screen[win_pos[1]:win_pos[1]+300,
                                   win_pos[0]:win_pos[0]+500], cfd_list[symbol], 1)
    if maxval > MATCH_OK:
        return True
    else:
        return False


def open_position(symbol, longshort, size, stop):
    open_cfd(symbol, 'watchlists')
    pos = wait_for_window(ticket_dax_deal, 3)
    if pos:
        set_size(pos, size)
        set_stop(pos, stop)
        if longshort == LONG:
            moveclick(*add(pos, TICKET_BUY))
        else:
            moveclick(*add(pos, TICKET_SELL))
        close_window()
        return True
    else:
        print 'ERROR: Deal Ticket not found'
        return False


def close_position(symbol, longshort, size):
    open_cfd(symbol, 'open_positions')
    pos = wait_for_window(ticket_dax_open, 3)
    if pos:
        set_size(pos, size)
        if longshort == LONG:
            moveclick(*add(pos, TICKET_SELL))
        else:
            moveclick(*add(pos, TICKET_BUY))
        close_window()
        return True
    else:
        print 'ERROR: Open Position Ticket not found'
        return False


def change_stop(symbol, newstop):
    open_cfd(symbol, 'open_positions')
    pos = wait_for_window(ticket_dax_open, 3)
    if pos:
        # Press edit
        moveclick(*add(pos, TICKET_EDIT))
        time.sleep(0.2)
        set_edit_stop(pos, newstop)
        if submit_window() and close_window():
            return True
        else:
            return False
    else:
        print 'ERROR: Open Position Ticket not found'
        return False


def open_cfd(cfd, which_window):
    if which_window == 'watchlists':
        win = watchlists
    elif which_window == 'open_positions':
        win = open_positions
    else:
        raise Exception('Window not defined')

    pos = wait_for_window(win, 1)
    if pos:
        screen = load_prev_screenshot()
        moveclick(*add(pos, (5,5))) # To activate Window (if not)
    else:
        print 'ERROR: ' + which_window + ' not found'
        return False

    win_pos = pos
    maxval, pos = get_match(screen[win_pos[1]:win_pos[1]+200,
                                   win_pos[0]:win_pos[0]+400], cfd_list[cfd], 1)
    pos = add(win_pos, pos)
    if maxval > MATCH_OK:
        moveclick(*add(pos, (5,5)))
    else:
        print 'CFD ' + cfd + ' not found in Screen'
        return False
    
    return True

    
def close_window():
    pos = wait_for_window(close_btn, 1)
    if pos:
        moveclick(*add(pos, (5,5)))
        return True
    else:
        return False

def submit_window():
    pos = wait_for_window(submit_btn, 1)
    if pos:
        moveclick(*add(pos, (5,5)))
        return True
    else:
        return False




