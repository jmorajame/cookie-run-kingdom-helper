import time
from utils import adb_tap,find_image_on_screen,confirm_tap_until_button_disappears,capture_screen

def run_garden_event_loop(stop_flag=None, skip_level8_check=False, device_serial=None):

    tap_positions = [
        (740, 400),
        (830, 400),
        (830, 460),
        (740, 460)
    ]
    confirm_position = (170, 470)

    while not (stop_flag and stop_flag.is_set()):
        print("🧺 กำลังเลื่อนวัตถุ...")
        for i in range(3):
            for pos in tap_positions:
                adb_tap(*pos, device_serial=device_serial)
                time.sleep(0.23)
        if not skip_level8_check:
            if not (stop_flag and stop_flag.is_set()):
                print("🔍 ตรวจสอบวัตถุเลเวล 8...")
            capture_screen(device_serial=device_serial)
            is_level_8 = find_image_on_screen("level_8_icon.png")
            if is_level_8:
                print("เจอวัตถุเลเวล 8...")
                #to pause the game  
                adb_tap(*(925,30), device_serial=device_serial)
                time.sleep(2.5)
                #to quit the event and get reward
                adb_tap(*(480,270), device_serial=device_serial)
                time.sleep(2.5)
                #to confirm quit the event
                adb_tap(*(570,390), device_serial=device_serial)
                time.sleep(2.5)
                # Tap anywhere to continue (twice)
                for _ in range(2):
                    adb_tap(480, 300, device_serial=device_serial)
                    time.sleep(1.5)

                # Retry button
                print("🔁 กำลังเริ่มใหม่...")
                confirm_tap_until_button_disappears("retry_button.png", device_serial=device_serial)
                continue
        else:
            print("(Endless loop) ข้ามการตรวจสอบเลเวล 8")
        for _ in range(2):
            adb_tap(*confirm_position, device_serial=device_serial)
            time.sleep(0.2)

    print("🛑 หยุด Auto Garden Event")