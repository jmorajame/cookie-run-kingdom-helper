import time
from utils import wait_and_tap, find_image_on_screen, confirm_tap_until_button_disappears, capture_screen

def run_material_production_loop(stop_flag, device_serial):
    print("🔄 Simple material production")
    while not stop_flag.is_set():
        # 1. Click management_button until it disappears
        while not stop_flag.is_set():
            capture_screen(device_serial=device_serial)
            pos = find_image_on_screen("button-images/management_button.png")
            if pos:
                print("คลิกปุ่มจัดการ...")
                wait_and_tap("management_button.png", delay=0.2, device_serial=device_serial)
                time.sleep(0.3)
            else:
                break
        if stop_flag.is_set():
            break
        # 2. Click refill_all_button until refill_all_icon appears
        print("คลิกปุ่มเติมทั้งหมด...")
        while not stop_flag.is_set():
            wait_and_tap("refill_all_button.png", delay=0.2, device_serial=device_serial)
            capture_screen(device_serial=device_serial)
            if find_image_on_screen("button-images/refill_all_icon.png"):
                print("เจอ popup ยืนยันเติมทั้งหมด")
                break
            time.sleep(0.5)
        if stop_flag.is_set():
            break
        # 3. Click refill_all_confirm_button and wait for it to disappear
        print("คลิกปุ่มยืนยันเติมทั้งหมด...")
        confirm_tap_until_button_disappears("refill_all_confirm_button.png", device_serial=device_serial)
        if stop_flag.is_set():
            break
        # 4. Repeat from management_button (not the whole process)
        print("เติมทั้งหมดใหม่ในอีก 1 นาที...")
        time.sleep(60)
    print("🛑 หยุด Simple material production")

def run_simple_material_production(stop_flag, device_serial=None):
    # Management button
    pos = find_image_on_screen("management_button.png")
    if pos:
        wait_and_tap("management_button.png", delay=0.2, device_serial=device_serial)
    if stop_flag.is_set():
        return
    # Refill all
    wait_and_tap("refill_all_button.png", delay=0.2, device_serial=device_serial)
    if stop_flag.is_set():
        return
    # Confirm refill
    confirm_tap_until_button_disappears("refill_all_confirm_button.png", device_serial=device_serial)
    if stop_flag.is_set():
        return
    # Check for refill icon
    if find_image_on_screen("refill_all_icon.png"):
        print("Refill all icon found.") 