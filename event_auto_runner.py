import time
from utils import capture_screen, find_image_on_screen, wait_and_tap, confirm_tap_until_button_disappears, adb_tap

def wait_until_button_disappears(image_path, max_checks=10, sleep_interval=0.5, device_serial=None):
    for _ in range(max_checks):
        capture_screen(device_serial=device_serial)
        if not find_image_on_screen(image_path):
            return True
        time.sleep(sleep_interval)
    return False

def run_event_loop(stop_flag=None, device_serial=None):
    while not (stop_flag and stop_flag.is_set()):
        # 1. Tap random_effect_button (2 attempts)
        for _ in range(2):
            if stop_flag and stop_flag.is_set():
                return
            print("🎲 สุ่ม effects เพิ่มเติม...")
            capture_screen(device_serial=device_serial)
            pos = find_image_on_screen("random_effect_button.png")
            if pos:
                adb_tap(*pos, device_serial=device_serial)
        # 2. Click ready_button
        print("🟢 กำลังรอปุ่มเริ่มต่อสู้...")
        while not (stop_flag and stop_flag.is_set()):
            capture_screen(device_serial=device_serial)
            pos = find_image_on_screen("ready_button.png")
            if pos:
                print("เจอปุ่มเริ่มต่อสู้...")
                wait_and_tap("ready_button.png", delay=0.2, device_serial=device_serial)
                break
            print("ไม่พบปุ่มเริ่มต่อสู้...")
            time.sleep(1)
        # 3. During battle, check for continue_event_button
        while not (stop_flag and stop_flag.is_set()):
            capture_screen(device_serial=device_serial)
            pos = find_image_on_screen("continue_event_button.png")
            if pos:
                while not (stop_flag and stop_flag.is_set()):
                    capture_screen(device_serial=device_serial)
                    pos = find_image_on_screen("continue_event_button.png")
                    if pos:
                        wait_and_tap("continue_event_button.png", delay=0.2, device_serial=device_serial)
                        wait_until_button_disappears("continue_event_button.png", max_checks=10, sleep_interval=0.3, device_serial=device_serial)
                    else:
                        break
                # 4. Click exit_button
                print("🔚 กดปุ่มออก...")
                while not (stop_flag and stop_flag.is_set()):
                    capture_screen(device_serial=device_serial)
                    exit_pos = find_image_on_screen("exit_button.png")
                    if exit_pos:
                        if confirm_tap_until_button_disappears("exit_button.png", device_serial=device_serial):
                            print("ออกเรียบร้อย — เริ่มต่อสู้ครั้งถัดไป.\n")
                        else:
                            print("[WARNING] ปุ่มออกยังไม่หายไปหลังจากพยายามหลายครั้ง อาจมีปัญหากับ emulator หรือการตรวจจับภาพ")
                        break
                    print("ไม่พบปุ่มออก... กำลังลองใหม่")
                    time.sleep(1)
                break
            print("กำลังต่อสู้...")
            time.sleep(3)