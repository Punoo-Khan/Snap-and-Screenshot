import pyautogui
from plyer import notification
import time
import os

# Create a unique folder for this session's screenshots
folder_name = "nigga"
os.makedirs(folder_name, exist_ok=True)

# Global counter variable
screenshot_counter = 1

def generate_filename():
    global screenshot_counter
    filename = os.path.join(folder_name, f"nigger_{screenshot_counter}.png")
    screenshot_counter += 1
    return filename



def take_screenshot(filename):
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="Snap Screenshot",
        timeout=2  # Duration in seconds
    )

