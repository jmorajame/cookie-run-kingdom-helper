import time
import glob
import os
import cv2
from utils import wait_and_tap, find_image_on_screen, capture_screen, adb_swipe, confirm_tap_until_button_disappears, clean_post_exit_popups
from config import get_castle_research_icons, get_material_icons, get_cookie_research_icons, get_material_icons_by_level

# Dynamically find all research slot icons and material icons
# RESEARCH_SLOT_DIR = "cookie_research_icons"
# CASTLE_RESEARCH_DIR = "castle_research_icons"
# MATERIAL_ICON_DIR = "material_icons"
# research_slots = sorted(glob.glob(os.path.join(RESEARCH_SLOT_DIR, "*.png")))
# castle_research_icons = sorted(glob.glob(os.path.join(CASTLE_RESEARCH_DIR, "*.png")))
# material_icons = sorted(glob.glob(os.path.join(MATERIAL_ICON_DIR, "*.png")))

castle_research_icons = get_castle_research_icons()
material_icons = get_material_icons()
research_slots = get_cookie_research_icons()

def wait_for_image(image_name, device_serial, timeout=10, stop_flag=None):
    """Wait for an image to appear on screen with timeout"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if stop_flag and stop_flag.is_set():
            return False
        capture_screen(device_serial=device_serial)
        if find_image_on_screen(image_name):
            return True
        time.sleep(0.5)
    return False

def wait_for_image_disappear(image_name, device_serial, timeout=10, stop_flag=None):
    """Wait for an image to disappear from screen with timeout"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if stop_flag and stop_flag.is_set():
            return False
        capture_screen(device_serial=device_serial)
        if not find_image_on_screen(image_name):
            return True
        time.sleep(0.5)
    return False

def tap_with_fail_check(image_name, device_serial, stop_flag=None, max_attempts=5):
    """Tap an image with fail check - returns True if successful"""
    for attempt in range(max_attempts):
        if stop_flag and stop_flag.is_set():
            return False
        capture_screen(device_serial=device_serial)
        if find_image_on_screen(image_name):
            wait_and_tap(image_name, device_serial=device_serial)
            time.sleep(0.5)
            return True
        time.sleep(0.3)
    # print(f"❌ Failed to find and tap {image_name} after {max_attempts} attempts")
    return False

def close_popup_until_management(device_serial, stop_flag=None):
    """Close popup by clicking quest_close_button until management_button appears"""
    for attempt in range(20):
        if stop_flag and stop_flag.is_set():
            return False
        capture_screen(device_serial=device_serial)
        if find_image_on_screen("management_button.png"):
            print("✅ ปิด popup และพบปุ่มสำนักงานอาณาจักรแล้ว")
            return True
        if find_image_on_screen("quest_close_button.png"):
            wait_and_tap("quest_close_button.png", device_serial=device_serial)
            time.sleep(0.3)
        else:
            time.sleep(0.3)
    print("❌ ไม่สามารถปิด popup และหาปุ่มสำนักงานอาณาจักรได้")
    return False

def find_required_material(device_serial, stop_flag=None):
    """Find which material is required for research by checking material_icons"""
    print("🔍 กำลังค้นหาวัสดุที่ต้องการวิจัย...")
    # print(f"🔍 Checking for materials: {[os.path.basename(icon) for icon in material_icons]}")
    
    # Search for material icons within the not_enough_mats popup
    for attempt in range(3):
        if stop_flag and stop_flag.is_set():
            return None
        
        # print(f"🔍 Material search attempt {attempt + 1}...")
        capture_screen(device_serial=device_serial)
        
        for material_icon in material_icons:
            if stop_flag and stop_flag.is_set():
                return None
            
            material_name = os.path.basename(material_icon)
            pos = find_image_on_screen(material_icon)
            if pos:
                print(f"🔍 เจอ: {material_name} ที่ตำแหน่ง {pos}")
                return material_icon
            else:
                print(f"🔍 ไม่พบ {material_name} ในรอบที่ {attempt + 1}")
        
        # If no materials found, wait a bit and try again
        if attempt < 2:
            print("🔍 ไม่พบวัสดุ, กำลังรอและลองใหม่...")
            time.sleep(0.5)
    
    print("❌ ไม่พบวัสดุที่ต้องการวิจัย")
    # print("🔍 This might be because:")
    # print("   - Material icons have different appearance than expected")
    # print("   - Material icons are positioned differently in the popup")
    # print("   - Screen capture failed")
    # print("   - Material icons are too small or unclear")
    return None

def scroll_and_find_and_produce(material_icon, device_serial, times=12, stop_flag=None):
    """Scroll up to the top, then find the material icon, then click it multiple times at all found positions, including after a bonus short scroll."""
    # Scroll up to the top first (longer and more times)
    # print("[DEBUG] Scrolling up to the top before searching for material icon...")
    # print(f"[DEBUG] stop_flag is set: {stop_flag.is_set() if stop_flag else False}")
    for up_scroll in range(8):
        if stop_flag and stop_flag.is_set():
            # print(f"[DEBUG] stop_flag set during scroll up at iteration {up_scroll+1}")
            return False
        # print(f"[DEBUG] Scroll up {up_scroll+1}/8: adb_swipe(480, 600, 480, 100, duration_ms=600)")
        adb_swipe(480, 100, 480, 460, duration_ms=600, device_serial=device_serial)  # longer swipe from bottom to top
        # print(f"[DEBUG] Finished swipe {up_scroll+1}/8")
        time.sleep(0.5)
    # Capture and check for the material icon at the top
    capture_screen(device_serial=device_serial)
    from auto_research_material import find_all_images_on_screen
    positions = find_all_images_on_screen(material_icon)
    if positions:
        print(f"พบไอคอน {material_icon} ที่ {positions} กำลังผลิต... (top after scroll up)")
        for pos in positions:
            for _ in range(times):
                if stop_flag and stop_flag.is_set():
                    return False
                from utils import adb_tap
                adb_tap(*pos, device_serial=device_serial)
                time.sleep(0.02)
        found_any = True
        # Bonus short scroll and check again
        # print("[DEBUG] Bonus short scroll after first found batch...")
        adb_swipe(480, 400, 480, 300, duration_ms=350, device_serial=device_serial)
        time.sleep(0.7)
        capture_screen(device_serial=device_serial)
        positions2 = find_all_images_on_screen(material_icon)
        if positions2:
            #print(f"[DEBUG] Bonus found {len(positions2)} more positions: {positions2}")
            for pos in positions2:
                for _ in range(times):
                    if stop_flag and stop_flag.is_set():
                        return False
                    from utils import adb_tap
                    adb_tap(*pos, device_serial=device_serial)
                    time.sleep(0.02)
        return True
    # Now proceed with the original search logic (shorter scroll down)
    for scroll_attempt in range(20):
        if stop_flag and stop_flag.is_set():
            return False
        capture_screen(device_serial=device_serial)
        positions = find_all_images_on_screen(material_icon)
        if positions:
            print(f"พบไอคอน {material_icon} ที่ {positions} กำลังผลิต...")
            for pos in positions:
                for _ in range(times):
                    if stop_flag and stop_flag.is_set():
                        return False
                    from utils import adb_tap
                    adb_tap(*pos, device_serial=device_serial)
                    time.sleep(0.02)
            # Bonus short scroll and check again
            print("[DEBUG] Bonus short scroll after found batch in scroll loop...")
            adb_swipe(480, 400, 480, 300, duration_ms=350, device_serial=device_serial)
            time.sleep(0.7)
            capture_screen(device_serial=device_serial)
            positions2 = find_all_images_on_screen(material_icon)
            if positions2:
                print(f"[DEBUG] Bonus found {len(positions2)} more positions: {positions2}")
                for pos in positions2:
                    for _ in range(times):
                        if stop_flag and stop_flag.is_set():
                            return False
                        from utils import adb_tap
                        adb_tap(*pos, device_serial=device_serial)
                        time.sleep(0.02)
            return True
        # Shorter scroll down to avoid skipping
        print("เลื่อนลงเพื่อค้นหาไอคอนวัสดุ (short scroll)...")
        adb_swipe(480, 400, 480, 300, duration_ms=350, device_serial=device_serial)
        time.sleep(0.7)
    print("❌ ไม่พบไอคอนวัสดุที่ต้องการ")
    return False

def find_all_images_on_screen(template_path, threshold=0.85):
    """Find all instances of the template image on the current screen. Return list of (x, y) positions."""
    import os
    from config import get_resource_path
    # Only prepend 'button-images/' if template_path does not contain a folder
    if '/' not in template_path and '\\' not in template_path:
        search_path = f"button-images/{template_path}"
    else:
        search_path = template_path
    positions = []
    try:
        if not os.path.exists('screen.png'):
            return []
        screen = cv2.imread('screen.png', cv2.IMREAD_COLOR)
        if screen is None:
            return []
        full_template_path = get_resource_path(search_path)
        template = cv2.imread(full_template_path, cv2.IMREAD_COLOR)
        if template is None:
            return []
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        yloc, xloc = (result >= threshold).nonzero()
        h, w = template.shape[:2]
        seen = set()
        for (x, y) in zip(xloc, yloc):
            center = (x + w // 2, y + h // 2)
            # Avoid duplicates (close points)
            if all(abs(center[0] - sx) > 10 or abs(center[1] - sy) > 10 for (sx, sy) in seen):
                positions.append(center)
                seen.add(center)
        return positions
    except Exception as e:
        print(f"[DEBUG] Error in find_all_images_on_screen: {e}")
        return []

def auto_research_material(stop_flag, device_serial, research_type="castle", max_level=5):
    """
    Main auto research material function with proper fail checks
    research_type: "castle" or "cookie"
    max_level: 1-5, determines which material icons to use
    """
    print(f"🔄 เริ่มวนหาและผลิตวัสดุสำหรับวิจัย ({research_type}) - Max Level: {max_level}")
    
    # Determine which research icons to use
    if research_type == "castle":
        research_icons = castle_research_icons
        research_button = "castle_research_button.png"
    else:
        research_icons = research_slots
        research_button = "cookie_research_button.png"
    
    # Get material icons filtered by level
    global material_icons
    material_icons = get_material_icons_by_level(max_level)
    # print(f"🔍 Using material icons for level {max_level}: {[os.path.basename(icon) for icon in material_icons]}")
    
    # 1. Click on activity_button (check research_lab_button if this button show up on screen)
    print("1. กำลังกดปุ่ม กิจกรรมอาณาจักร...")
    if not tap_with_fail_check("activity_button.png", device_serial, stop_flag):
        print("❌ กดปุ่ม กิจกรรมอาณาจักร ไม่สำเร็จ")
        return False
    
    # Wait and check if research_lab_button appears
    if not wait_for_image("research_lab_button.png", device_serial, stop_flag=stop_flag):
        print("❌ ปุ่มวิจัยอาณาจักรไม่ปรากฏหลังจากกดปุ่ม กิจกรรมอาณาจักร")
        return False
    
    # 2. Click on research_lab_button (check castle_research_button)
    print("2. กำลังกดปุ่ม ศูนย์วิจัยของโนมน้ำตาล...")
    if not tap_with_fail_check("research_lab_button.png", device_serial, stop_flag):
        print("❌ กดปุ่ม ศูนย์วิจัยของโนมน้ำตาล ไม่สำเร็จ")
        return False
    
    # Wait and check if research_button appears, handle continue_research_button popups
    # print(f"[DEBUG] Checking for {research_button} or continue_research_button popups...")
    found_research_button = False
    for attempt in range(10):
        if stop_flag and stop_flag.is_set():
            return False
        capture_screen(device_serial=device_serial)
        if find_image_on_screen(research_button):
            # print(f"[DEBUG] Found {research_button} on attempt {attempt+1}")
            tap_with_fail_check(research_button, device_serial, stop_flag)
            found_research_button = True
            break
        elif find_image_on_screen("continue_research_button.png"):
            # print(f"[DEBUG] Found continue_research_button on attempt {attempt+1}, tapping it...")
            wait_and_tap("continue_research_button.png", device_serial=device_serial)
            time.sleep(0.5)
        else:
            # print(f"[DEBUG] Neither {research_button} nor continue_research_button found on attempt {attempt+1}")
            time.sleep(0.5)
    if not found_research_button:
        # print(f"❌ {research_button} did not appear after clicking research_lab_button and handling popups")
        return False
    
    # Wait for research screen to load
    time.sleep(2)
    
    # 3. Scroll to left side 5 times to make sure we're at the start
    print("3. กำลังเลื่อนไปทางซ้ายเพื่อเริ่มที่ตำแหน่งเริ่มต้น...")
    for _ in range(5):
        if stop_flag and stop_flag.is_set():
            return False
        adb_swipe(200, 400, 800, 400, duration_ms=800, device_serial=device_serial)
        time.sleep(0.5)
    
    # 4. Find and click on research images
    print("4. กำลังค้นหาและกดปุ่มวิจัย...")
    found_research = False
    required_material = None
    
    for _ in range(10):  # Try scrolling right up to 10 times
        if stop_flag and stop_flag.is_set():
            return False
        
        # 5. Capture screen and find research icons
        capture_screen(device_serial=device_serial)
        tapped_positions = set()
        for research_icon in research_icons:
            if stop_flag and stop_flag.is_set():
                return False
            pos = find_image_on_screen(research_icon)
            if pos:
                # Skip if this position was already tapped in this loop
                if pos in tapped_positions:
                    # print(f"[DEBUG] Skipping already tapped research icon at {pos}")
                    continue
                tapped_positions.add(pos)
                print(f"🔍 เจอ icon: {os.path.basename(research_icon)} ที่ตำแหน่ง {pos}")
                # 7. Click on the research image
                wait_and_tap(research_icon, device_serial=device_serial)
                time.sleep(0.5)
                # 8. Check if we really clicked by looking for research_found_icon
                if not wait_for_image("research_found_icon.png", device_serial, timeout=3, stop_flag=stop_flag):
                    # print("❌ research_found_icon did not appear after clicking research")
                    continue
                print("✅ เข้ามาในหน้าวิจัยแล้ว")
                # 9. Click on research_button and handle conditions
                capture_screen(device_serial=device_serial)
                research_btn_found = find_image_on_screen("research_button.png")
                if not research_btn_found:
                    print("📊 Research is still in progress (no research_button)")
                    for close_attempt in range(10):
                        if stop_flag and stop_flag.is_set():
                            return False
                        if not find_image_on_screen("research_found_icon.png"):
                            print("✅ ปิดหน้าวิจัยแล้ว")
                            break
                        if find_image_on_screen("quest_close_button.png"):
                            wait_and_tap("quest_close_button.png", device_serial=device_serial)
                            time.sleep(0.3)
                        else:
                            time.sleep(0.3)
                    continue
                else:
                    print("🔬 กำลังตรวจสอบสถานะของวิจัยนี้...")
                    for click_attempt in range(10):
                        # print(" click_attempt: ", click_attempt)
                        if stop_flag and stop_flag.is_set():
                            return False
                        wait_and_tap("research_button.png", device_serial=device_serial)
                        time.sleep(0.3)
                        capture_screen(device_serial=device_serial)
                        not_enough = find_image_on_screen("not_enough_mats.png")
                        not_available_to_research = find_image_on_screen("not_available_to_research.png")
                        research_btn_still_there = find_image_on_screen("research_button.png")
                        not_available_research_button = find_image_on_screen("not_available_research_button.png")
                        if not_enough:
                            print("❌ ไม่มีวัสดุพอสำหรับวิจัย")
                            required_material = find_required_material(device_serial, stop_flag)
                            # print(f"[DEBUG] required_material after detection: {required_material}")
                            if required_material is None:
                                #print("[DEBUG] No required material found, closing popups and continuing to next research slot.")
                                for close_attempt in range(10):
                                    if stop_flag and stop_flag.is_set():
                                        return False
                                    capture_screen(device_serial=device_serial)
                                    if not find_image_on_screen("not_enough_mats.png"):
                                        print("✅ ปิดหน้าวิจัยแล้ว")
                                        break
                                    close_positions = find_all_images_on_screen("quest_close_button.png")
                                    if close_positions:
                                        # print(f"[DEBUG] Attempting to close not_enough_mats popup for non material, attempt {close_attempt+1}, found {len(close_positions)} close buttons.")
                                        for idx, pos in enumerate(close_positions):
                                            #print(f"[DEBUG] Tapping quest_close_button at {pos} (index {idx})")
                                            from utils import adb_tap
                                            adb_tap(*pos, device_serial=device_serial)
                                            time.sleep(0.5)
                                    else:
                                        # print(f"[DEBUG] quest_close_button not found for non material on attempt {close_attempt+1}")
                                        time.sleep(0.3)
                                # print("[DEBUG] Finished not_enough_mats popup for non material closing loop.")
                                tapped_positions.add(pos)
                                break
                            found_research = True
                            for close_attempt in range(10):
                                if stop_flag and stop_flag.is_set():
                                    # print("[DEBUG] Stop flag set during not_enough_mats popup closing loop.")
                                    return False
                                capture_screen(device_serial=device_serial)
                                if not find_image_on_screen("not_enough_mats.png"):
                                    print("✅ ปิดหน้าวิจัยแล้ว")
                                    break
                                close_positions = find_all_images_on_screen("quest_close_button.png")
                                if close_positions:
                                    # print(f"[DEBUG] Attempting to close not_enough_mats popup, attempt {close_attempt+1}, found {len(close_positions)} close buttons.")
                                    for idx, pos in enumerate(close_positions):
                                        # print(f"[DEBUG] Tapping quest_close_button at {pos} (index {idx})")
                                        from utils import adb_tap
                                        adb_tap(*pos, device_serial=device_serial)
                                        time.sleep(0.2)
                                else:
                                    # print(f"[DEBUG] quest_close_button not found on attempt {close_attempt+1}")
                                    time.sleep(0.3)
                            # print("[DEBUG] Finished not_enough_mats popup closing loop.")
                            break
                        elif not_available_to_research or not_available_research_button:
                            print("❌ โนมน้ำตาลไม่พร้อมสำหรับวิจัย ,ปิดหน้าวิจัยแล้ว")
                            collect_gnome = find_image_on_screen("collect_gnome.png")
                            if collect_gnome:
                                print("🔍 กำลังกดโนมน้ำตาลที่วิจัยสำเร็จแล้ว...")
                                # Tap collect_gnome until it disappears
                                for _ in range(10):
                                    if stop_flag and stop_flag.is_set():
                                        return False
                                    if not find_image_on_screen("collect_gnome.png"):
                                        # print("✅ collect_gnome button disappeared.")
                                        break
                                    wait_and_tap("collect_gnome.png", device_serial=device_serial)
                                    time.sleep(0.5)
                                # After collect_gnome disappears, tap check_button closest to center until confirm_button appears
                                # print("🔍 Looking for check_button closest to center...")
                                center = (480, 270)
                                for attempt in range(10):
                                    if stop_flag and stop_flag.is_set():
                                        return False
                                    capture_screen(device_serial=device_serial)
                                    if find_image_on_screen("confirm_button.png"):
                                        print("✅ พบปุ่มตกลงแล้ว")
                                        break
                                    check_positions = find_all_images_on_screen("check_button.png")
                                    if check_positions:
                                        closest_pos = min(check_positions, key=lambda p: (p[0] - center[0])**2 + (p[1] - center[1])**2)
                                        # print(f"[DEBUG] Tapping check_button at {closest_pos}")
                                        from utils import adb_tap
                                        adb_tap(*closest_pos, device_serial=device_serial)
                                        time.sleep(0.5)
                                        # After tapping, check if the same button is gone (with tolerance)
                                        capture_screen(device_serial=device_serial)
                                        check_positions_after = find_all_images_on_screen("check_button.png")
                                        def is_same_button_gone(tapped, positions, tol=15):
                                            return not any(abs(tapped[0]-p[0])<=tol and abs(tapped[1]-p[1])<=tol for p in positions)
                                        if is_same_button_gone(closest_pos, check_positions_after):
                                            # print("✅ The tapped check_button disappeared after tap.")
                                            break
                                    else:
                                        # print("[DEBUG] No check_button found, waiting...")
                                        time.sleep(0.3)
                                # Tap confirm_button until it disappears
                                # print("🔍 Tapping confirm_button until it disappears...")
                                time.sleep(0.5)
                                for _ in range(10):
                                    if stop_flag and stop_flag.is_set():
                                        return False
                                    capture_screen(device_serial=device_serial)
                                    if not find_image_on_screen("confirm_gnome_upgrade_button.png"):
                                        #print("✅ confirm_button disappeared.")
                                        break
                                    wait_and_tap("confirm_gnome_upgrade_button.png", device_serial=device_serial)
                                    time.sleep(0.5)
                                found_research = True
                                break
                            for close_attempt in range(10):
                                if stop_flag and stop_flag.is_set():
                                    return False
                                capture_screen(device_serial=device_serial)
                                if not find_image_on_screen("not_available_to_research.png"):
                                    print("✅ ปิดหน้าวิจัยแล้ว")
                                    break
                                close_positions = find_all_images_on_screen("quest_close_button.png")
                                if close_positions:
                                    # print(f"[DEBUG] Attempting to close not_enough_mats popup for non material, attempt {close_attempt+1}, found {len(close_positions)} close buttons.")
                                    for idx, pos in enumerate(close_positions):
                                        # print(f"[DEBUG] Tapping quest_close_button at {pos} (index {idx})")
                                        from utils import adb_tap
                                        adb_tap(*pos, device_serial=device_serial)
                                        time.sleep(0.5)
                                else:
                                    # print(f"[DEBUG] quest_close_button not found for non material on attempt {close_attempt+1}")
                                    time.sleep(0.3)
                            # print("[DEBUG] Finished not_enough_mats popup for non material closing loop.")
                            found_research = True
                            break
                        elif not research_btn_still_there:
                            print("✅ วิจัยเริ่มต้นสำเร็จ")
                            # The game auto-closes the popup, so just wait and refresh
                            time.sleep(1)
                            capture_screen(device_serial=device_serial)
                            continue
                for close_attempt in range(10):
                    if stop_flag and stop_flag.is_set():
                        return False
                    if not find_image_on_screen("research_found_icon.png"):
                        print("✅ ปิดหน้าวิจัยแล้ว")
                        break
                    if find_image_on_screen("quest_close_button.png"):
                        wait_and_tap("quest_close_button.png", device_serial=device_serial)
                        time.sleep(0.3)
                    else:
                        time.sleep(0.3)
            if found_research:
                break
        
        if found_research:
            break
        
        # 8. If nothing found, scroll to the right
        print("6. ไม่พบวิจัยที่พร้อมสำหรับวิจัย, กำลังเลื่อนไปทางขวา...")
        adb_swipe(800, 400, 200, 400, duration_ms=800, device_serial=device_serial)
        time.sleep(1)
    
    if not found_research:
        print("❌ ไม่พบวิจัยที่พร้อมสำหรับวิจัย")
        # Close popup and return to management
        close_popup_until_management(device_serial, stop_flag)
        return False
    
    # Close popup until management_button appears
    if not close_popup_until_management(device_serial, stop_flag):
        return False
    
    # If we need materials, produce them
    if required_material:
        # Map required material to production material icon
        required_material_name = os.path.basename(required_material)
        if required_material_name.startswith("required_"):
            production_material_name = required_material_name.replace("required_", "")
        else:
            production_material_name = required_material_name
        production_material_path = os.path.join('material_icons', production_material_name)
        print(f"🛠️ ต้องการผลิต: {production_material_name}")
        # print(f"[DEBUG] About to click management_button to go to management screen.")
        # Click management_button to go to management screen
        if not tap_with_fail_check("management_button.png", device_serial, stop_flag):
            print("❌ กดปุ่มสำนักงานอาณาจักร ไม่สำเร็จ")
            return False
        # print(f"[DEBUG] management_button clicked, waiting for production_management button.")
        # Wait and check if production_management button appears (to confirm we're on management page)
        if not wait_for_image("production_management.png", device_serial, stop_flag=stop_flag):
            print("❌ ปุ่มดูการผลิตทั้งหมดของอาณาจักรไม่ปรากฏหลังจากกดปุ่มสำนักงานอาณาจักร")
            return False
        # print(f"[DEBUG] production_management button appeared, about to click it.")
        # Click production_management button
        if not tap_with_fail_check("production_management.png", device_serial, stop_flag):
            print("❌ กดปุ่มดูการผลิตทั้งหมดของอาณาจักร ไม่สำเร็จ")
            return False
        # print(f"[DEBUG] production_management button clicked, about to produce material.")
        # Produce the required material (use mapped production_material_path)
        if not scroll_and_find_and_produce(production_material_path, device_serial, stop_flag=stop_flag):
            print("❌ ผลิตวัสดุที่ต้องการไม่สำเร็จ")
            return False
        # print(f"[DEBUG] Finished producing material, proceeding to refill all.")
        # Click refill_all_button
        # print("[DEBUG] Clicking refill_all_button...")
        if not tap_with_fail_check("refill_all_button.png", device_serial, stop_flag):
            print("❌ กดปุ่มเติมวัสดุทั้งหมด ไม่สำเร็จ")
            return False
        # Wait for refill_all_confirm_button to appear
        # print("[DEBUG] Waiting for refill_all_confirm_button to appear...")
        if not wait_for_image("refill_all_confirm_button.png", device_serial, stop_flag=stop_flag):
            print("❌ ปุ่มยืนยันเติมวัสดุทั้งหมดไม่ปรากฏหลังจากกดปุ่มเติมวัสดุทั้งหมด")
            return False
        # Click refill_all_confirm_button until it disappears
        # print("[DEBUG] Clicking refill_all_confirm_button until it disappears...")
        for attempt in range(10):
            if stop_flag and stop_flag.is_set():
                return False
            capture_screen(device_serial=device_serial)
            if not find_image_on_screen("refill_all_confirm_button.png"):
                # print("[DEBUG] refill_all_confirm_button disappeared.")
                break
            tap_with_fail_check("refill_all_confirm_button.png", device_serial, stop_flag)
            time.sleep(0.3)
        # Close quest popups until activity_button is found
        # print("[DEBUG] Closing quest popups until activity_button is found...")
        for attempt in range(15):
            if stop_flag and stop_flag.is_set():
                return False
            capture_screen(device_serial=device_serial)
            if find_image_on_screen("activity_button.png"):
                # print("[DEBUG] Found activity_button, ready to restart research loop.")
                break
            close_positions = find_all_images_on_screen("quest_close_button.png")
            if close_positions:
                for pos in close_positions:
                    from utils import adb_tap
                    adb_tap(*pos, device_serial=device_serial)
                    time.sleep(0.2)
            else:
                time.sleep(0.3)
        # Restart the research loop
        # print("[DEBUG] Restarting auto_research_material loop...")
        clean_post_exit_popups(stop_flag, device_serial, middle_tap=False)
        return auto_research_material(stop_flag, device_serial, research_type, max_level)

    if not required_material:

        # print(f"[DEBUG] About to click management_button to go to management screen.")
        # Click management_button to go to management screen
        if not tap_with_fail_check("management_button.png", device_serial, stop_flag):
            print("❌ กดปุ่มสำนักงานอาณาจักร ไม่สำเร็จ")
            return False
        # print(f"[DEBUG] management_button clicked, waiting for production_management button.")
        # Wait and check if production_management button appears (to confirm we're on management page)
        if not wait_for_image("production_management.png", device_serial, stop_flag=stop_flag):
            print("❌ ปุ่มดูการผลิตทั้งหมดของอาณาจักรไม่ปรากฏหลังจากกดปุ่มสำนักงานอาณาจักร")
            return False
        # print(f"[DEBUG] production_management button appeared, about to click it.")
        # Click production_management button
        if not tap_with_fail_check("production_management.png", device_serial, stop_flag):
            print("❌ กดปุ่มดูการผลิตทั้งหมดของอาณาจักร ไม่สำเร็จ")
            return False
        # print(f"[DEBUG] production_management button clicked, about to produce material.")

        # print(f"[DEBUG] proceeding to refill all.")
        # Click refill_all_button
        # print("[DEBUG] Clicking refill_all_button...")
        if not tap_with_fail_check("refill_all_button.png", device_serial, stop_flag):
            print("❌ กดปุ่มเติมวัสดุทั้งหมด ไม่สำเร็จ")
            return False
        # Wait for refill_all_confirm_button to appear
        # print("[DEBUG] Waiting for refill_all_confirm_button to appear...")
        if not wait_for_image("refill_all_confirm_button.png", device_serial, stop_flag=stop_flag):
            print("❌ ปุ่มยืนยันเติมวัสดุทั้งหมดไม่ปรากฏหลังจากกดปุ่มเติมวัสดุทั้งหมด")
            return False
        # Click refill_all_confirm_button until it disappears
        # print("[DEBUG] Clicking refill_all_confirm_button until it disappears...")
        for attempt in range(10):
            if stop_flag and stop_flag.is_set():
                return False
            capture_screen(device_serial=device_serial)
            if not find_image_on_screen("refill_all_confirm_button.png"):
                # print("[DEBUG] refill_all_confirm_button disappeared.")
                break
            tap_with_fail_check("refill_all_confirm_button.png", device_serial, stop_flag)
            time.sleep(0.3)
        # Close quest popups until activity_button is found
        # print("[DEBUG] Closing quest popups until activity_button is found...")
        for attempt in range(15):
            if stop_flag and stop_flag.is_set():
                return False
            capture_screen(device_serial=device_serial)
            if find_image_on_screen("activity_button.png"):
                # print("[DEBUG] Found activity_button, ready to restart research loop.")
                break
            close_positions = find_all_images_on_screen("quest_close_button.png")
            if close_positions:
                for pos in close_positions:
                    from utils import adb_tap
                    adb_tap(*pos, device_serial=device_serial)
                    time.sleep(0.2)
            else:
                time.sleep(0.3)
        # Restart the research loop
        clean_post_exit_popups(stop_flag, device_serial, middle_tap=False)
        #print("[DEBUG] Restarting auto_research_material loop...")
        return auto_research_material(stop_flag, device_serial, research_type, max_level)
    
    print("✅ Research material automation completed successfully!")
    return True

def run_auto_research_material(stop_flag, device_serial=None):
    """Wrapper function to run auto research material"""
    if stop_flag and stop_flag.is_set():
        return
    return auto_research_material(stop_flag, device_serial, "castle") 