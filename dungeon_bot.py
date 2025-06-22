import time
from utils import capture_screen, find_image_on_screen, wait_and_tap, confirm_tap_until_button_disappears, clean_post_exit_popups
import random

def run_dungeon_loop():
    last_completed_stage = None
    MAX_STAGE = (3, 30)
    while True:
        skipped_ready_tap = False
        print("Waiting for next stage button to appear...")
        while True:
            if wait_and_tap("next_stage_button.png", delay=2):
                print("Next stage clicked")
                break
            capture_screen()
            pos = find_image_on_screen("button-images/ready_button.png")
            if pos:
                print("Ready button appeared → tapping it now")
                wait_and_tap("ready_button.png", delay=0.2)
                skipped_ready_tap = True
                break
            print("Next stage not found yet... retrying")
        if not skipped_ready_tap:
            print("Checking for ready button...")
            wait_and_tap("ready_button.png", delay=2)
        else:
            print("Already tapped ready → skipping")
        for _ in range(6):
            time.sleep(2)
            capture_screen()
            if not find_image_on_screen("button-images/ready_button.png"):
                print("Ready button gone → combat started")
                break
        print("Waiting for win or skip during battle...")
        while True:
            time.sleep(4)
            capture_screen()
            if find_image_on_screen("button-images/win_icon.png"):
                print("Win detected")
                try:
                    last_completed_stage = extract_stage_from_screen()
                    print("Current stage : ", last_completed_stage)
                except Exception:
                    pass
                break
            pos = find_image_on_screen("button-images/skip_button.png")
            if pos:
                print("Skip found → tapping")
                confirm_tap_until_button_disappears("skip_button.png")
            else:
                print("Still fighting...")
        print("Tapping to dismiss win result and check next stage...")
        found_next = False
        for _ in range(5):
            x = random.randint(420, 480)
            y = random.randint(200, 300)
            # Only generic tap here, not on UI button
            from utils import adb_tap
            adb_tap(x, y)
            time.sleep(2)
            capture_screen()
            if find_image_on_screen("button-images/next_stage_button.png"):
                print("Next stage found")
                if confirm_tap_until_button_disappears("next_stage_button.png"):
                    found_next = True
                break
        if not found_next:
            print("No next stage button → exit and post cleanup")
            wait_and_tap("exit_button.png", delay=1)
            clean_post_exit_popups()
            try:
                next_stage = next_stage_tuple(last_completed_stage)
                if MAX_STAGE and next_stage[1] == MAX_STAGE[1]:
                    print(f"Reached max stage {MAX_STAGE[1]} — stopping")
                    break
                print(f"Looking for next stage {next_stage}...")
                stage_locked = False
                while not stage_locked:
                    stage_locked = find_and_click_stage(next_stage)
                    if not stage_locked:
                        print("Next stage not found — retrying...")
                        time.sleep(2)
                wait_and_tap("prepare_button.png", delay=2)
            except Exception:
                pass
        print("Looping...\n")
        time.sleep(2)