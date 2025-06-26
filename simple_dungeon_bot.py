import time
from utils import capture_screen, find_image_on_screen, wait_and_tap, confirm_tap_until_button_disappears, clean_post_exit_popups, adb_tap

def get_selected_device():
    """Get the currently selected device serial"""
    import config
    return config.selected_device_serial

def find_and_tap_next_button(stop_flag):
    """Try to find and tap either next_stage_button or next_floor_button."""
    device_serial = get_selected_device()
    for btn in ["next_stage_button.png", "next_floor_button.png"]:
        if wait_and_tap(btn, delay=0.2, device_serial=device_serial):
            return btn
    return None

def confirm_next_button_disappeared(btn_name, stop_flag):
    device_serial = get_selected_device()
    sleep_interval = 0.5
    for _ in range(5):
        if stop_flag.is_set():
            break
        capture_screen(device_serial=device_serial)
        if not find_image_on_screen(btn_name):
            break
        time.sleep(sleep_interval)

def run_dungeon_loop_simple(stop_flag):
    print("🟢 Auto explore stage")
    while not stop_flag.is_set():
        device_serial = get_selected_device()
        if not device_serial:
            print("❌ ไม่ได้เลือกอุปกรณ์! หยุดการทำงาน")
            break
            
        skipped_ready_tap = False
        while not stop_flag.is_set():
            for btn in ["next_stage_button.png", "next_floor_button.png"]:
                if wait_and_tap(btn, delay=1, device_serial=device_serial):
                    print("ไปด่านถัดไป")
                    break
            else:
                capture_screen(device_serial=device_serial)
                pos = find_image_on_screen("ready_button.png")
                if pos:
                    print("กดปุ่มเริ่มต่อสู้ ...")
                    wait_and_tap("ready_button.png", delay=0.2, device_serial=device_serial)
                    skipped_ready_tap = True
                    break
                pos = find_image_on_screen("prepare_button.png")
                if pos:
                    print("ปุ่มเตรียมพร้อมปรากฎ → กดปุ่มเตรียมพร้อม")
                    wait_and_tap("prepare_button.png", delay=0.2, device_serial=device_serial)
                    break
                print("กำลังค้นหาปุ่ม เริ่มต่อสู้,พื้นที่ถัดไป,เตรียมพร้อม ...")
            if skipped_ready_tap:
                break
        if stop_flag.is_set():
            break
        if not skipped_ready_tap:
            print("ค้นหาปุ่มเริ่มต่อสู้...")
            wait_and_tap("ready_button.png", delay=2, device_serial=device_serial)
        else:
            print("กดปุ่มเริ่มต่อสู้ไปแล้ว → ข้ามขั้นตอนหาปุ่มเริ่มต่อสู้")
        for _ in range(6):
            if stop_flag.is_set():
                break
            time.sleep(2)
            capture_screen(device_serial=device_serial)
            if not find_image_on_screen("ready_button.png"):
                print("การต่อสู้เริ่มขึ้น")
                break
        if stop_flag.is_set():
            break
        print("กำลังรอด่านจบ...")
        while not stop_flag.is_set():
            time.sleep(3)
            capture_screen(device_serial=device_serial)
            if find_image_on_screen("win_icon.png"):
                if not stop_flag.is_set():
                    print("จบด่านเรียบร้อยแล้ว")
                break
            elif find_image_on_screen("skip_button.png"):
                if not stop_flag.is_set():
                    print("เจอปุ่ม Skip → กดปุ่ม Skip ...")
                confirm_tap_until_button_disappears("skip_button.png", device_serial=device_serial)
            else:
                if not stop_flag.is_set():
                    print("กำลังต่อสู้...")
        if stop_flag.is_set():
            break
        print("กำลังตรวจสอบด่านถัดไป...")
        found_next = False
        for _ in range(5):
            if stop_flag.is_set():
                break
            adb_tap(480, 350, device_serial=device_serial)
            adb_tap(480, 350, device_serial=device_serial)
            time.sleep(1)
            capture_screen(device_serial=device_serial)
            for check_btn in ["next_stage_button.png", "next_floor_button.png"]:
                if find_image_on_screen(check_btn):
                    print("เจอด่านถัดไป")
                    if confirm_tap_until_button_disappears(check_btn, device_serial=device_serial):
                        found_next = True
                        for _ in range(5):
                            if stop_flag.is_set():
                                break
                            capture_screen(device_serial=device_serial)
                            if not find_image_on_screen(check_btn):
                                break
                            time.sleep(0.5)
                    break
            if found_next:
                break
        if not found_next and not stop_flag.is_set():
            print("ไม่เจอด่านถัดไป → กดออกและปิด Popups")
            wait_and_tap("exit_button.png", delay=1, device_serial=device_serial)
            sleep_interval = 0.5
            for _ in range(5):
                if stop_flag.is_set():
                    break
                capture_screen(device_serial=device_serial)
                if not find_image_on_screen("exit_button.png"):
                    break
                time.sleep(sleep_interval)
            if not stop_flag.is_set():
                clean_post_exit_popups(stop_flag, device_serial=device_serial)

        # At the very end, check for a next episode/stage icon (max 3 times)
        if not stop_flag.is_set():
            for i in range(3):
                capture_screen(device_serial=device_serial)
                pos = find_image_on_screen("next_stage_icon.png")
                if pos:
                    time.sleep(1)
                    adb_tap(*pos, device_serial=device_serial)
                    break
                else:
                    time.sleep(0.5) # Wait before next check

        if not stop_flag.is_set():
            print("เริ่มใหม่...\n")
