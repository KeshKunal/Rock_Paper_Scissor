import pyautogui
import time

def simulate_coding():
    pyautogui.click(x=500, y=500)  # Click on VS Code window
    pyautogui.write(' # test comment\n')
    time.sleep(10)  # Every 5 minutes
    simulate_coding()

simulate_coding()
 