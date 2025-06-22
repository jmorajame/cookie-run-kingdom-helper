import time
from utils import capture_screen, find_image_on_screen, wait_and_tap, confirm_tap_until_button_disappears, clean_post_exit_popups, adb_tap

def find_and_tap_next_button(stop_flag):
    """Try to find and tap either next_stage_button or next_floor_button."""
    for btn in ["next_stage_button.png", "next_floor_button.png"]:
        if wait_and_tap(btn, delay=0.2):
            return btn
    return None

def confirm_next_button_disappeared(btn_name, stop_flag):
    sleep_interval = 0.5
    for _ in range(5):
        if stop_flag.is_set():
            break
        capture_screen()
        if not find_image_on_screen(f"button-images/{btn_name}"):
            break
        time.sleep(sleep_interval)

def run_dungeon_loop_simple(stop_flag):
    print("🟢 Auto explore stage")
    while not stop_flag.is_set():
        skipped_ready_tap = False
        while not stop_flag.is_set():
            for btn in ["next_stage_button.png", "next_floor_button.png"]:
                if wait_and_tap(btn, delay=2):
                    print("ไปด่านถัดไป")
                    break
            else:
                capture_screen()
                pos = find_image_on_screen("button-images/ready_button.png")
                if pos:
                    print("กดปุ่มเริ่มต่อสู้ ...")
                    wait_and_tap("ready_button.png", delay=0.2)
                    skipped_ready_tap = True
                    break
                pos = find_image_on_screen("button-images/prepare_button.png")
                if pos:
                    print("ปุ่มเตรียมพร้อมปรากฎ → กดปุ่มเตรียมพร้อม")
                    wait_and_tap("prepare_button.png", delay=0.2)
                    break
                print("กำลังค้นหาปุ่ม เริ่มต่อสู้,พื้นที่ถัดไป,เตรียมพร้อม ...")
            if skipped_ready_tap:
                break
        if stop_flag.is_set():
            break
        if not skipped_ready_tap:
            print("ค้นหาปุ่มเริ่มต่อสู้...")
            wait_and_tap("ready_button.png", delay=2)
        else:
            print("กดปุ่มเริ่มต่อสู้ไปแล้ว → ข้ามขั้นตอนหาปุ่มเริ่มต่อสู้")
        for _ in range(6):
            if stop_flag.is_set():
                break
            time.sleep(2)
            capture_screen()
            if not find_image_on_screen("button-images/ready_button.png"):
                print("การต่อสู้เริ่มขึ้น")
                break
        if stop_flag.is_set():
            break
        print("กำลังรอด่านจบ...")
        while not stop_flag.is_set():
            time.sleep(4)
            capture_screen()
            if find_image_on_screen("button-images/win_icon.png"):
                print("จบด่านเรียบร้อยแล้ว")
                break
            elif find_image_on_screen("button-images/skip_button.png"):
                print("เจอปุ่ม Skip → กดปุ่ม Skip ...")
                confirm_tap_until_button_disappears("skip_button.png")
            else:
                print("กำลังต่อสู้...")
        if stop_flag.is_set():
            break
        print("กำลังตรวจสอบด่านถัดไป...")
        found_next = False
        for _ in range(5):
            if stop_flag.is_set():
                break
            adb_tap(480, 350)
            time.sleep(2)
            capture_screen()
            for check_btn in ["next_stage_button.png", "next_floor_button.png"]:
                if find_image_on_screen(f"button-images/{check_btn}"):
                    print("เจอด่านถัดไป")
                    if confirm_tap_until_button_disappears(check_btn):
                        found_next = True
                        for _ in range(5):
                            if stop_flag.is_set():
                                break
                            capture_screen()
                            if not find_image_on_screen(f"button-images/{check_btn}"):
                                break
                            time.sleep(0.5)
                    break
            if found_next:
                break
        if not found_next and not stop_flag.is_set():
            print("ไม่เจอด่านถัดไป → กดออกและปิด Popups")
            wait_and_tap("exit_button.png", delay=1)
            sleep_interval = 0.5
            for _ in range(5):
                if stop_flag.is_set():
                    break
                capture_screen()
                if not find_image_on_screen("button-images/exit_button.png"):
                    break
                time.sleep(sleep_interval)
            if not stop_flag.is_set():
                clean_post_exit_popups()
        if not stop_flag.is_set():
            print("เริ่มใหม่...\n")
            time.sleep(2)
