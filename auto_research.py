from utils import capture_screen, find_image_on_screen, adb_tap, adb_swipe
import time
import cv2
import numpy as np
import shutil

# Helper to click a button by template name
def click_button(template_name):
    capture_screen()
    pos = find_image_on_screen(f"button-images/{template_name}")
    if pos:
        adb_tap(*pos)
        return True
    return False

# Helper to scroll right (swipe from right to left)
def scroll_right():
    adb_swipe(800, 300, 200, 300, duration_ms=800)

def drag_to_start():
    # Drag all the way left (repeat as needed to ensure you reach the end)
    for _ in range(5):
        adb_swipe(200, 300, 800, 300, duration_ms=800)
        time.sleep(0.5)

def tap_first_slot():
    # Tap at the center of the first slot (adjust as needed)
    adb_tap(400, 300)
    print("Tapped first slot.")

def images_are_similar(img1_path, img2_path, threshold=0.99):
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None or img1.shape != img2.shape:
        return False
    diff = cv2.absdiff(img1, img2)
    nonzero = np.count_nonzero(diff)
    total = diff.size
    similarity = 1 - (nonzero / total)
    return similarity > threshold

# Main automation logic
def main():
    # Step 1: Click activity_button until research_lab_button is found
    max_activity_retries = 10
    for _ in range(max_activity_retries):
        capture_screen()
        if find_image_on_screen("research_lab_button.png"):
            print("Found research_lab_button.")
            break
        print("Clicking activity_button...")
        click_button("activity_button.png")
        time.sleep(1)
    else:
        print("Could not find research_lab_button after clicking activity_button.")
        return

    # Step 2: Click research_lab_button until castle_research_button is found
    max_research_retries = 10
    for _ in range(max_research_retries):
        capture_screen()
        if find_image_on_screen("castle_research_button.png"):
            print("Found castle_research_button.")
            break
        print("Clicking research_lab_button...")
        click_button("research_lab_button.png")
        time.sleep(1)
    else:
        print("Could not find castle_research_button after clicking research_lab_button.")
        capture_screen()
        shutil.copy("screen.png", "debug_no_castle_research_button.png")
        print("Saved debug screenshot as debug_no_castle_research_button.png")
        return

    # Step 3: Click castle_research_button
    click_button("castle_research_button.png")
    print("Found and clicked castle_research_button, proceeding to precise drag and tap...")

    # Step 4: Drag to start, then drag right by one slot and tap
    drag_to_start()
    time.sleep(0.5)
    scroll_right()  # Move right by one slot
    time.sleep(0.5)
    tap_first_slot()
    print("Script finished.")
    # TODO: In the future, add logic to check/tap more slots or scroll left if needed.

def check_research_lab():
    if find_image_on_screen("research_lab_button.png"):
        print("Research lab button found.")
    if find_image_on_screen("castle_research_button.png"):
        print("Castle research button found.")

if __name__ == "__main__":
    main() 