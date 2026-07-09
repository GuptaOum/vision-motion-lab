from pyautogui import *
import pyautogui
import time
import keyboard
import random
import win32api, win32con

#Tile 1 Position: X:  328 Y:  400 RGB: ( 78,  80, 115)
#Tile 2 Position: X:  406 Y:  400 RGB: (  0,   0,   0)
#Tile 3 Position: X:  498 Y:  400 RGB: ( 78,  80, 115)
#Tile 4 Position: X:  586 Y:  400 RGB: ( 80,  81, 115)

def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(0.03) #This pauses the script for 0.1 seconqds
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

while keyboard.is_pressed('q') == False:
    
    if pyautogui.pixel(328, 400)[0] == 0:
        click(328, 400)
    if pyautogui.pixel(406, 400)[0] == 0:
        click(406, 400)
    if pyautogui.pixel(498, 400)[0] == 0:
        click(498, 400)
    if pyautogui.pixel(586, 400)[0] == 0:
        click(586, 400) 
    