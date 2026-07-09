# Import the relevant modules
import pyautogui
import time
import keyboard as kl

# Spiral drawing using pyautogui
time.sleep(1)  # Gives you 2 seconds to move the mouse to the desired location
distance = 300

try:
    while distance > 0:
        # Check if 'x' is pressed to exit
        if kl.is_pressed('x'):
            print("Exiting...")
            break
        
        pyautogui.dragRel(distance, 0, 0.5, button="left")  # Move right
        distance -= 10
        
        pyautogui.dragRel(0, distance, 0.5, button="left")  # Move down
        pyautogui.dragRel(-distance, 0, 0.5, button="left")  # Move left
        distance -= 10
        
        pyautogui.dragRel(0, -distance, 0.5, button="left")  # Move up

except KeyboardInterrupt:
    print("Interrupted manually!")

print("Exit")
