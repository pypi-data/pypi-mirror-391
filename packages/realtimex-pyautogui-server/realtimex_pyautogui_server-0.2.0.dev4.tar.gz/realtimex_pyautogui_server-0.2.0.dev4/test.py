import time

# import pytesseract
import pyautogui

# Wait 3 seconds before starting (so you can switch to the browser)
print("You have 3 seconds to switch to your browser window...")
time.sleep(3)

start_time = time.time()
poll_interval = 1.0
timeout = 10

# while (time.time() - start_time) < timeout:
#     # Take screenshot of region
#     screenshot = pyautogui.screenshot(region=(150, 490, 150, 100))

#     # OCR the screenshot
#     detected_text = pytesseract.image_to_string(screenshot)

#     print("Detected text:", detected_text)

#     if "tên đăng nhập" in detected_text.lower():
#         break

#     time.sleep(poll_interval)

location = pyautogui.locateOnScreen("./elements/fpt/login_button.png", confidence=0.8)

if location:
    center = pyautogui.center(location)
    pyautogui.moveTo(center.x, center.y, duration=2)

print(location)

print("End time in second", time.time() - start_time)