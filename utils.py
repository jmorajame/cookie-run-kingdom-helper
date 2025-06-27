import subprocess
import cv2
import os
import time
import warnings
from config import get_adb_path, get_resource_path

ADB_PATH = get_adb_path()
warnings.filterwarnings('ignore', category=UserWarning)
os.environ['OPENCV_IO_MAX_IMAGE_PIXELS'] = str(pow(2, 40))

def adb_tap(x, y, device_serial=None):
    """Tap on the screen at (x, y) using adb."""
    cmd = [ADB_PATH]
    if device_serial:
        cmd += ['-s', device_serial]
    cmd += ['shell', 'input', 'tap', str(x), str(y)]
    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

def adb_swipe(x1, y1, x2, y2, duration_ms=300, device_serial=None):
    """Swipe on the screen from (x1, y1) to (x2, y2) in `duration_ms`."""
    cmd = [ADB_PATH]
    if device_serial:
        cmd += ['-s', device_serial]
    cmd += ['shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration_ms)]
    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

def adb_drag(start_x, start_y, end_x, end_y, duration_ms=1500, device_serial=None):
    """
    Perform a precise drag from a start point to an end point with no momentum.
    """
    print(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})...")
    adb_swipe(start_x, start_y, end_x, end_y, duration_ms, device_serial=device_serial)

def adb_scroll(direction='down', duration_ms=1200, device_serial=None):
    """
    Perform a scroll gesture in the specified direction.
    Assumes a 960x540 resolution.
    A long duration (~1200ms) results in a precise "drag" that completely eliminates momentum.
    """
    # X-coordinate is the horizontal center of the screen
    x = 480 
    
    # Y-coordinates for the swipe, avoiding the very top/bottom of the screen
    start_y = 400 # ~75% of the way down
    end_y   = 140 # ~25% of the way down

    if direction == 'down':
        # To scroll down, we swipe from bottom to top
        print("Scrolling down...")
        adb_swipe(x, start_y, x, end_y, duration_ms, device_serial=device_serial)
    elif direction == 'up':
        # To scroll up, we swipe from top to bottom
        print("Scrolling up...")
        adb_swipe(x, end_y, x, start_y, duration_ms, device_serial=device_serial)

def capture_screen(device_serial=None):
    """Capture the current screen from the device."""
    try:
        cmd1 = [ADB_PATH]
        if device_serial:
            cmd1 += ['-s', device_serial]
        cmd1 += ['shell', 'screencap', '-p', '/sdcard/screen.png']
        subprocess.run(cmd1, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
        cmd2 = [ADB_PATH]
        if device_serial:
            cmd2 += ['-s', device_serial]
        cmd2 += ['pull', '/sdcard/screen.png', './screen.png']
        subprocess.run(cmd2, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
    except Exception:
        print("Screenshot capture error")

def find_image_on_screen(template_path, threshold=0.85):
    """Find the template image on the current screen. Return (x, y) if found, else None."""
    # Only prepend 'button-images/' if template_path does not contain a folder
    if '/' not in template_path and '\\' not in template_path:
        search_path = f"button-images/{template_path}"
    else:
        search_path = template_path
    try:
        if not os.path.exists('screen.png'):
            return None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            screen = cv2.imread('screen.png', cv2.IMREAD_COLOR)
        if screen is None:
            return None
        full_template_path = get_resource_path(search_path)
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

def wait_and_tap(template_name, delay=1.0, max_checks=10, sleep_interval=0.5, device_serial=None):
    """Wait, capture, tap the button if found, and confirm it disappears."""
    time.sleep(delay)
    capture_screen(device_serial=device_serial)
    # Only prepend 'button-images/' if template_name does not contain a folder
    if '/' not in template_name and '\\' not in template_name:
        search_path = f"button-images/{template_name}"
    else:
        search_path = template_name
    pos = find_image_on_screen(search_path)
    if pos:
        adb_tap(*pos, device_serial=device_serial)
        # Wait for button to disappear
        for _ in range(max_checks):
            time.sleep(sleep_interval)
            capture_screen(device_serial=device_serial)
            if not find_image_on_screen(search_path):
                return True
        return False  # Button did not disappear in time
    return False

def confirm_tap_until_button_disappears(template_name, retries=20, delay=1.0, device_serial=None):
    """Tap the button until it disappears or retries run out, with robust waiting for slow emulators."""
    # Only prepend 'button-images/' if template_name does not contain a folder
    if '/' not in template_name and '\\' not in template_name:
        search_path = f"button-images/{template_name}"
    else:
        search_path = template_name
    not_found_count = 0
    for _ in range(1, retries + 1):
        capture_screen(device_serial=device_serial)
        pos = find_image_on_screen(search_path)
        if pos:
            adb_tap(*pos, device_serial=device_serial)
            # Wait for button to disappear after tap
            for wait_idx in range(10):
                time.sleep(delay)
                capture_screen(device_serial=device_serial)
                if not find_image_on_screen(search_path):
                    return True
        else:
            not_found_count += 1
            if not_found_count >= 3:
                # Force a screen refresh tap in case the emulator is lagging
                adb_tap(480, 300, device_serial=device_serial)
                not_found_count = 0
            else:
                # If not found, assume it's gone
                return True
    # Fallback: try a generic tap if button still present after all retries
    adb_tap(480, 300, device_serial=device_serial)
    time.sleep(2)
    capture_screen(device_serial=device_serial)
    if not find_image_on_screen(search_path):
        return True
    return False

def clean_post_exit_popups(stop_flag=None, device_serial=None):
    """Clean up post-exit popups by tapping known buttons, robust for slow emulators. Respects stop_flag if provided."""
    print("กำลังกดปิด popups...")
    attempts_without_finds = 0
    while attempts_without_finds < 5:
        if stop_flag is not None and stop_flag.is_set():
            break
        capture_screen(device_serial=device_serial)
        found_any = False
        for btn in [
            "receive_reward_button.png",
            "quest_close_button.png",
            "bundle_close_button.png",
            "level_up_continue_button.png",
            "skip_button.png",
            "destroy_button.png",
        ]:
            # Only prepend 'button-images/' if btn does not contain a folder
            if '/' not in btn and '\\' not in btn:
                search_path = f"button-images/{btn}"
            else:
                search_path = btn
            pos = find_image_on_screen(search_path)
            if pos:
                adb_tap(*pos, device_serial=device_serial)
                # Wait for button to disappear after tap
                for _ in range(10):
                    if stop_flag is not None and stop_flag.is_set():
                        break
                    time.sleep(0.5)
                    capture_screen(device_serial=device_serial)
                    if not find_image_on_screen(search_path):
                        break
                found_any = True
        if not found_any:
            attempts_without_finds += 1
        else:
            attempts_without_finds = 0
        time.sleep(1)
    print("ปิด popups ทั้งหมดเรียบร้อย")
    adb_tap(480, 270, device_serial=device_serial)

