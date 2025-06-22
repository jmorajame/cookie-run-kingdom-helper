import subprocess
import cv2
import os
import time
import warnings
from config import get_adb_path, get_resource_path

ADB_PATH = get_adb_path()
warnings.filterwarnings('ignore', category=UserWarning)
os.environ['OPENCV_IO_MAX_IMAGE_PIXELS'] = str(pow(2, 40))

def adb_tap(x, y):
    """Tap on the screen at (x, y) using adb."""
    subprocess.run([ADB_PATH, 'shell', 'input', 'tap', str(x), str(y)], creationflags=subprocess.CREATE_NO_WINDOW)

def capture_screen():
    """Capture the current screen from the device."""
    try:
        subprocess.run([ADB_PATH, 'shell', 'screencap', '-p', '/sdcard/screen.png'], creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
        subprocess.run([ADB_PATH, 'pull', '/sdcard/screen.png', './screen.png'], creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
    except Exception:
        print("Screenshot capture error")

def find_image_on_screen(template_path, threshold=0.85):
    """Find the template image on the current screen. Return (x, y) if found, else None."""
    try:
        if not os.path.exists('screen.png'):
            return None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            screen = cv2.imread('screen.png', cv2.IMREAD_COLOR)
        if screen is None:
            return None
        full_template_path = get_resource_path(template_path)
        template = cv2.imread(full_template_path, cv2.IMREAD_COLOR)
        if template is None:
            return None
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            h, w = template.shape[:2]
            return (max_loc[0] + w // 2, max_loc[1] + h // 2)
        return None
    except Exception:
        return None

def wait_and_tap(template_name, delay=1.0, max_checks=10, sleep_interval=0.5):
    """Wait, capture, tap the button if found, and confirm it disappears."""
    time.sleep(delay)
    capture_screen()
    pos = find_image_on_screen(f"button-images/{template_name}")
    if pos:
        adb_tap(*pos)
        # Wait for button to disappear
        for _ in range(max_checks):
            time.sleep(sleep_interval)
            capture_screen()
            if not find_image_on_screen(f"button-images/{template_name}"):
                return True
        return False  # Button did not disappear in time
    return False

def confirm_tap_until_button_disappears(template_name, retries=20, delay=1.0):
    """Tap the button until it disappears or retries run out, with robust waiting for slow emulators."""
    print(f"[DEBUG] Trying to tap '{template_name}' until it disappears (max {retries} retries)...")
    not_found_count = 0
    for attempt in range(1, retries + 1):
        capture_screen()
        pos = find_image_on_screen(f"button-images/{template_name}")
        if pos:
            print(f"[DEBUG] Attempt {attempt}: Found '{template_name}' at {pos}, tapping...")
            adb_tap(*pos)
            # Wait for button to disappear after tap
            for wait_idx in range(10):
                time.sleep(delay)
                capture_screen()
                if not find_image_on_screen(f"button-images/{template_name}"):
                    print(f"[DEBUG] '{template_name}' disappeared after tap (wait {wait_idx+1})")
                    return True
                else:
                    print(f"[DEBUG] '{template_name}' still present after tap (wait {wait_idx+1})")
        else:
            not_found_count += 1
            print(f"[DEBUG] Attempt {attempt}: '{template_name}' not found (not_found_count={not_found_count})")
            if not_found_count >= 3:
                # Force a screen refresh tap in case the emulator is lagging
                print("[DEBUG] Forcing screen refresh with a generic tap (480, 300)")
                adb_tap(480, 300)
                not_found_count = 0
            else:
                # If not found, assume it's gone
                print(f"[DEBUG] '{template_name}' assumed gone after {attempt} attempts.")
                return True
    # Fallback: try a generic tap if button still present after all retries
    print(f"[WARNING] '{template_name}' still present after {retries} retries. Trying fallback tap at (480, 300)...")
    adb_tap(480, 300)
    time.sleep(2)
    capture_screen()
    if not find_image_on_screen(f"button-images/{template_name}"):
        print(f"[DEBUG] '{template_name}' disappeared after fallback tap.")
        return True
    print(f"[ERROR] '{template_name}' still present after all attempts and fallback. Giving up.")
    return False

def clean_post_exit_popups():
    """Clean up post-exit popups by tapping known buttons, robust for slow emulators."""
    print("กำลังกดปิด popups...")
    attempts_without_finds = 0
    while attempts_without_finds < 5:
        capture_screen()
        found_any = False
        for btn in [
            "receive_reward_button.png",
            "quest_close_button.png",
            "bundle_close_button.png",
            "level_up_continue_button.png",
            "skip_button.png",
        ]:
            pos = find_image_on_screen(f"button-images/{btn}")
            if pos:
                adb_tap(*pos)
                # Wait for button to disappear after tap
                for _ in range(10):
                    time.sleep(0.5)
                    capture_screen()
                    if not find_image_on_screen(f"button-images/{btn}"):
                        break
                found_any = True
        if not found_any:
            attempts_without_finds += 1
        else:
            attempts_without_finds = 0
        time.sleep(1)
    print("ปิด popups ทั้งหมดเรียบร้อย")
    adb_tap(480, 270)

