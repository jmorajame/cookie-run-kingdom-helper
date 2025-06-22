import time
from utils import capture_screen, find_image_on_screen, wait_and_tap, confirm_tap_until_button_disappears, adb_tap

def wait_until_button_disappears(image_path, max_checks=10, sleep_interval=0.5):
    for _ in range(max_checks):
        capture_screen()
        if not find_image_on_screen(image_path):
            return True
        time.sleep(sleep_interval)
    return False

def run_event_loop(stop_flag=None):
    while not (stop_flag and stop_flag.is_set()):
        # 1. Tap random_effect_button (2 attempts)
        for _ in range(2):
            if stop_flag and stop_flag.is_set():
                return
            print("🎲 สุ่ม effects เพิ่มเติม...")
            capture_screen()
            pos = find_image_on_screen("button-images/random_effect_button.png")
            if pos:
                adb_tap(*pos)
        # 2. Click ready_button
        print("🟢 กำลังรอปุ่มเริ่มต่อสู้...")
        while not (stop_flag and stop_flag.is_set()):
            capture_screen()
            pos = find_image_on_screen("button-images/ready_button.png")
            if pos:
                print("เจอปุ่มเริ่มต่อสู้...")
                wait_and_tap("ready_button.png", delay=0.2)
                break
            print("ไม่พบปุ่มเริ่มต่อสู้...")
            time.sleep(1)
        # 3. During battle, check for continue_event_button
        while not (stop_flag and stop_flag.is_set()):
            capture_screen()
            pos = find_image_on_screen("button-images/continue_event_button.png")
            if pos:
                while not (stop_flag and stop_flag.is_set()):
                    capture_screen()
                    pos = find_image_on_screen("button-images/continue_event_button.png")
                    if pos:
                        wait_and_tap("continue_event_button.png", delay=0.2)
                        wait_until_button_disappears("button-images/continue_event_button.png", max_checks=10, sleep_interval=0.3)
                    else:
                        break
                # 4. Click exit_button
                print("🔚 กดปุ่มออก...")
                while not (stop_flag and stop_flag.is_set()):
                    capture_screen()
                    exit_pos = find_image_on_screen("button-images/exit_button.png")
                    if exit_pos:
                        if confirm_tap_until_button_disappears("exit_button.png"):
                            print("ออกเรียบร้อย — เริ่มต่อสู้ครั้งถัดไป.\n")
                        else:
                            print("[WARNING] ปุ่มออกยังไม่หายไปหลังจากพยายามหลายครั้ง อาจมีปัญหากับ emulator หรือการตรวจจับภาพ")
                        break
                    print("ไม่พบปุ่มออก... กำลังลองใหม่")
                    time.sleep(1)
                break
            print("กำลังต่อสู้...")
            time.sleep(3)