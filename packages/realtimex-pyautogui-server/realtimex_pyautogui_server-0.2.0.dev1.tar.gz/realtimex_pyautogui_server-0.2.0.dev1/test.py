import pyautogui

import pyautogui
import time

# Wait 3 seconds before starting (so you can switch to the browser)
print("You have 3 seconds to switch to your browser window...")
time.sleep(3)

# Scroll settings
scroll_amount = -200  # Negative = scroll down, Positive = scroll up
scroll_times = 1  # How many times to scroll
delay = 0.5  # Delay between scrolls (seconds)

for i in range(scroll_times):
    pyautogui.scroll(scroll_amount)
    print(f"Scrolled {i + 1}/{scroll_times}")
    time.sleep(delay)

print("Scrolling complete!")
