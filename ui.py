import customtkinter as ctk
from customtkinter import StringVar
import threading
import os
import sys
import subprocess
from dungeon_bot import run_dungeon_loop
from event_auto_runner import run_event_loop
from simple_dungeon_bot import run_dungeon_loop_simple
from config import get_adb_path, get_resource_path

# === Global Control Flags ===
event_thread = None
event_stop_flag = threading.Event()

dungeon_thread = None
dungeon_stop_flag = threading.Event()

garden_thread = None
garden_stop_flag = threading.Event()

# --- Load Google Font (Itim) on Windows ---
if sys.platform == "win32":
    import ctypes
    try:
        # Use resource path resolution for bundled executable
        font_path = get_resource_path("fonts/Itim-Regular.ttf")
        if os.path.exists(font_path):
            FR_PRIVATE  = 0x10
            FR_NOT_ENUM = 0x20
            ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
            FONT_FAMILY = "Itim"
        else:
            print(f"Font file not found: {font_path}")
            FONT_FAMILY = "Arial"
    except Exception as e:
        print(f"Font loading error: {e}")
        FONT_FAMILY = "Arial"
else:
    FONT_FAMILY = "Arial"

# --- Button and Status Texts ---
BUTTON_TEXTS = {
    'dungeon': ["Auto explore stage", "Stop Dungeon Bot"],
    'event': ["Auto battle Giant POLY-ROLY", "หยุด bot ล้มลุก event"],
    'garden': ["Auto play Garden event", "Stop Garden Bot"]
}

# Find the max width needed for all button texts
max_button_text = max([text for pair in BUTTON_TEXTS.values() for text in pair], key=len)
BUTTON_WIDTH = len(max_button_text)  # No extra padding

# --- Status Labels ---
dungeon_status = None
event_status = None
garden_status = None

ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("ไข่ดำ ไข่ดาว เป็นพี่น้องกัน")

# Set window icon
try:
    icon_path = get_resource_path("cat_icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
except Exception as e:
    print(f"Could not load icon: {e}")

# === ADB Setup Functions ===
def check_adb_connection():
    """Check if ADB is working and device is connected"""
    try:
        result = subprocess.run([get_adb_path(), 'devices'], 
                               capture_output=True, text=True, 
                               creationflags=subprocess.CREATE_NO_WINDOW)
        lines = result.stdout.strip().split('\n')
        devices = [line for line in lines if '\tdevice' in line]
        return len(devices) > 0, devices
    except Exception as e:
        return False, [str(e)]

def test_connection_quick():
    """Quick test connection and show result"""
    is_connected, devices = check_adb_connection()
    
    if is_connected:
        device_info = "\n".join([f"• {device.split('\t')[0]}" for device in devices])
        print(f"✅ เชื่อมต่อ ADB สำเร็จ! พบ emulator {len(devices)} เครื่อง:")
        print(device_info)
        print("คุณสามารถใช้ฟังก์ชัน bot ได้แล้ว!")
    else:
        print("❌ ไม่พบ emulator กรุณาเปิดใช้งาน ADB debugging ก่อน")

def check_adb_before_start():
    """Check ADB connection before starting any bot function"""
    is_connected, devices = check_adb_connection()
    if not is_connected:
        print("❌ ไม่ได้เชื่อมต่อ ADB! กรุณาเปิดใช้งาน ADB debugging ก่อน")
        return False
    return True

def show_setup_wizard():
    """Show ADB setup wizard for emulators"""
    setup_window = ctk.CTkToplevel(root)
    setup_window.title("ตัวช่วยตั้งค่า Emulator")
    setup_window.geometry("800x700")  # Increased window size
    setup_window.resizable(False, False)
    
    # Make it modal and bring to front
    setup_window.transient(root)
    setup_window.grab_set()
    setup_window.focus_force()
    setup_window.lift()
    
    # Title
    title = ctk.CTkLabel(setup_window, text="🎮 ตัวช่วยตั้งค่า Emulator", font=(FONT_FAMILY, 20, "bold"))
    title.pack(pady=20)
    
    # Instructions
    instructions = ctk.CTkTextbox(setup_window, height=250, font=(FONT_FAMILY, 12))
    instructions.pack(pady=10, padx=20, fill="x")
    
    instructions_text = """🎮 คำแนะนำการตั้งค่า Emulator:

1. เลือก Emulator ของคุณ:
   • NOX Player (ต้องเปิด developer options)
   • LDPlayer
   • BlueStacks

2. เปิดใช้งาน ADB:
   • NOX: เปิด developer options + USB debugging
   • LDPlayer: เปิด "Local connection" ในตั้งค่า emulator
   • BlueStacks: เปิด ADB ใน Preferences

3. ตั้งค่าความละเอียดหน้าจอ:
   • ตั้งค่า emulator เป็น 960x540 (160 DPI)
   • ความละเอียดนี้จำเป็นสำหรับการตรวจจับปุ่มที่ถูกต้อง

4. ทดสอบการเชื่อมต่อ:
   • ตรวจสอบว่า emulator กำลังทำงานอยู่
   • คลิก "ทดสอบการเชื่อมต่อ" ด้านล่าง
   • หากสำเร็จ จะเห็น emulator ของคุณในรายการ

⚠️ หมายเหตุ: คลิกปุ่ม emulator ด้านล่างเพื่อดูคำแนะนำเฉพาะ"""
    
    instructions.insert("1.0", instructions_text)
    instructions.configure(state="disabled")
    
    # Emulator-specific instructions
    emulator_frame = ctk.CTkFrame(setup_window)
    emulator_frame.pack(pady=10, padx=20, fill="x")
    
    emulator_label = ctk.CTkLabel(emulator_frame, text="📱 การตั้งค่าเฉพาะ Emulator:", font=(FONT_FAMILY, 14, "bold"))
    emulator_label.pack(pady=10)
    
    def show_nox_guide():
        show_emulator_guide("NOX Player", """การตั้งค่า NOX Player:
1. เปิด NOX Player
2. ไปที่ Settings (แถบด้านบนหรือไอคอนเฟือง)
3. ไปที่ "Developer Options"
4. หากไม่เห็น ให้ไปที่ "About tablet" → แตะ "Build number" 7 ครั้ง
5. ใน Developer Options เปิด "USB debugging"
6. เสร็จแล้ว! NOX จะเชื่อมต่อโดยอัตโนมัติ

หมายเหตุ: คุณต้องเปิด developer options ในระบบ Android สำหรับ NOX""")
    
    def show_ldplayer_guide():
        show_emulator_guide("LDPlayer", """การตั้งค่า LDPlayer:
1. เปิด LDPlayer
2. คลิกไอคอนเฟือง (Settings) ในแถบด้านข้าง
3. ไปที่แท็บ "Others"
4. หา "ADB debugging"
5. เปิด "Local connection"
6. เสร็จแล้ว! LDPlayer จะเชื่อมต่อโดยอัตโนมัติ

หมายเหตุ: ไม่ต้องเปิด developer options หรือ USB debugging ในระบบ Android""")
    
    def show_bluestacks_guide():
        show_emulator_guide("BlueStacks", """การตั้งค่า BlueStacks:
1. เปิด BlueStacks
2. คลิก Settings (ไอคอนเฟือง) → ไปที่ Preferences
3. เลื่อนลงและเปิด ADB (Android Debug Bridge)
4. เสร็จแล้ว! BlueStacks จะเชื่อมต่อโดยอัตโนมัติ

หมายเหตุ: ไม่ต้องเปิด developer options หรือ USB debugging ในระบบ Android""")
    
    # Emulator buttons - make them bigger
    emulator_buttons = ctk.CTkFrame(emulator_frame)
    emulator_buttons.pack(pady=10)
    
    ctk.CTkButton(emulator_buttons, text="NOX Player", command=show_nox_guide, 
                 font=(FONT_FAMILY, 12), height=35, width=120).pack(side="left", padx=8, pady=8)
    ctk.CTkButton(emulator_buttons, text="LDPlayer", command=show_ldplayer_guide, 
                 font=(FONT_FAMILY, 12), height=35, width=120).pack(side="left", padx=8, pady=8)
    ctk.CTkButton(emulator_buttons, text="BlueStacks", command=show_bluestacks_guide, 
                 font=(FONT_FAMILY, 12), height=35, width=120).pack(side="left", padx=8, pady=8)
    
    # Status frame
    status_frame = ctk.CTkFrame(setup_window)
    status_frame.pack(pady=10, padx=20, fill="x")
    
    status_label = ctk.CTkLabel(status_frame, text="สถานะ: ยังไม่ได้ตรวจสอบ", font=(FONT_FAMILY, 12))
    status_label.pack(pady=10)
    
    # Buttons frame - improved layout
    button_frame = ctk.CTkFrame(setup_window)
    button_frame.pack(pady=20, padx=20, fill="x")
    
    def test_connection():
        """Test ADB connection"""
        status_label.configure(text="สถานะ: กำลังทดสอบการเชื่อมต่อ...")
        setup_window.update()
        
        is_connected, devices = check_adb_connection()
        
        if is_connected:
            device_info = "\n".join([f"• {device.split('\t')[0]}" for device in devices])
            status_label.configure(text=f"✅ เชื่อมต่อสำเร็จ! พบ emulator {len(devices)} เครื่อง:\n{device_info}")
        else:
            status_label.configure(text="❌ ไม่พบ emulator กรุณาตรวจสอบการเชื่อมต่อ")
    
    def show_emulator_guide(emulator_name, guide_text):
        """Show specific emulator guide"""
        guide_window = ctk.CTkToplevel(setup_window)
        guide_window.title(f"คำแนะนำการตั้งค่า {emulator_name}")
        guide_window.geometry("600x500")  # Increased size
        
        # Make popup appear in front
        guide_window.transient(setup_window)
        guide_window.grab_set()
        guide_window.focus_force()
        guide_window.lift()
        
        guide_textbox = ctk.CTkTextbox(guide_window, font=(FONT_FAMILY, 12))
        guide_textbox.pack(pady=20, padx=20, fill="both", expand=True)
        
        guide_textbox.insert("1.0", guide_text)
        guide_textbox.configure(state="disabled")
    
    def open_troubleshooting():
        """Open troubleshooting guide"""
        trouble_window = ctk.CTkToplevel(setup_window)
        trouble_window.title("คู่มือแก้ไขปัญหา")
        trouble_window.geometry("700x600")  # Increased size
        
        # Make popup appear in front
        trouble_window.transient(setup_window)
        trouble_window.grab_set()
        trouble_window.focus_force()
        trouble_window.lift()
        
        trouble_text = ctk.CTkTextbox(trouble_window, font=(FONT_FAMILY, 12))
        trouble_text.pack(pady=20, padx=20, fill="both", expand=True)
        
        trouble_content = """🔧 การแก้ไขปัญหา Emulator:

ปัญหาที่พบบ่อยและวิธีแก้ไข:

1. "ไม่พบอุปกรณ์"
   • ตรวจสอบว่า emulator กำลังทำงานอยู่
   • ลองรีสตาร์ท emulator
   • ตรวจสอบว่าเปิด ADB debugging ในตั้งค่า emulator แล้ว
   • ลองใช้ emulator instance อื่น

2. "ADB ไม่ตอบสนอง"
   • รีสตาร์ท emulator
   • หยุด ADB server: adb kill-server
   • เริ่ม ADB server: adb start-server
   • ลองเชื่อมต่อผ่านพอร์ตเฉพาะ (หากจำเป็น)

3. "สิทธิ์ถูกปฏิเสธ"
   • ตรวจสอบว่าเปิด ADB debugging ในตั้งค่า emulator แล้ว
   • ลองรีสตาร์ท emulator
   • ตรวจสอบว่า emulator โหลดเสร็จแล้ว

4. เคล็ดลับเฉพาะ Emulator:
   • NOX: เปิด developer options + USB debugging ในตั้งค่า Android
   • LDPlayer: เปิด "Local connection" ใน Settings > Others > ADB debugging
   • BlueStacks: เปิด ADB ใน Settings > Preferences

5. เคล็ดลับประสิทธิภาพ:
   • ใช้ RAM 2-4 GB สำหรับ emulator
   • เปิด virtualization ใน BIOS
   • ปิดแอปพลิเคชันอื่นๆ ขณะใช้ bot
   • ใช้การเชื่อมต่อแบบมีสายหากเป็นไปได้"""
        
        trouble_text.insert("1.0", trouble_content)
        trouble_text.configure(state="disabled")
    
    # Improved button layout with better sizing
    test_btn = ctk.CTkButton(button_frame, text="🔍 ทดสอบการเชื่อมต่อ", command=test_connection, 
                            font=(FONT_FAMILY, 14), height=45, width=200)
    test_btn.pack(side="left", padx=15, pady=15)
    
    trouble_btn = ctk.CTkButton(button_frame, text="🔧 แก้ไขปัญหา", command=open_troubleshooting, 
                              font=(FONT_FAMILY, 14), height=45, width=180)
    trouble_btn.pack(side="left", padx=15, pady=15)
    
    close_btn = ctk.CTkButton(button_frame, text="ปิด", command=setup_window.destroy, 
                            font=(FONT_FAMILY, 14), height=45, width=120)
    close_btn.pack(side="right", padx=15, pady=15)

# === Resolution Notice ===
resolution_frame = ctk.CTkFrame(root)
resolution_frame.pack(fill="x", pady=(5, 0))

resolution_label = ctk.CTkLabel(resolution_frame, text="📱 ต้องการความละเอียดหน้าจอ: 960x540 (160 DPI)", 
                               font=(FONT_FAMILY, 11), text_color="#666666")
resolution_label.pack(pady=5)

# --- Dungeon Row ---
dungeon_row = ctk.CTkFrame(root)
dungeon_row.pack(fill="x", pady=(5, 0))
dungeon_row.grid_columnconfigure(0, weight=1)
dungeon_name = ctk.CTkLabel(dungeon_row, text=BUTTON_TEXTS['dungeon'][0], anchor="w", font=(FONT_FAMILY, 14))
dungeon_name.grid(row=0, column=0, sticky="w", padx=(20, 5), pady=2)
def dungeon_switch_event():
    if dungeon_switch.get():
        if not check_adb_before_start():
            dungeon_switch.deselect()
            return
        # Stop other functions and clear log
        stop_all_other_functions('dungeon')
        clear_log()
        dungeon_stop_flag.clear()
        global dungeon_thread
        dungeon_thread = threading.Thread(target=wrapped_dungeon_loop, daemon=True)
        dungeon_thread.start()
    else:
        print("🛑 กำลังหยุด Auto stage...")
        dungeon_stop_flag.set()
        clear_log()
        print("🛑 หยุด Auto explore stage แล้ว")
dungeon_switch = ctk.CTkSwitch(dungeon_row, text="", command=dungeon_switch_event, font=(FONT_FAMILY, 12))
dungeon_switch.grid(row=0, column=1, sticky="e", padx=(5, 0), pady=2)
dungeon_desc = ctk.CTkLabel(dungeon_row, text="เข้าด่านถึงจะเริ่มหาจากปุ่มเหล่านี้ เริ่มต่อสู้,พื้นที่ถัดไป,เตรียมพร้อม", font=(FONT_FAMILY, 12), text_color="#888888")
dungeon_desc.grid(row=1, column=0, columnspan=2, sticky="w", padx=(20, 5), pady=(0, 8))

# --- Event Row ---
event_row = ctk.CTkFrame(root)
event_row.pack(fill="x", pady=(5, 0))
event_row.grid_columnconfigure(0, weight=1)
event_name = ctk.CTkLabel(event_row, text=BUTTON_TEXTS['event'][0], anchor="w", font=(FONT_FAMILY, 14))
event_name.grid(row=0, column=0, sticky="w", padx=(20, 5), pady=2)
def event_switch_event():
    if event_switch.get():
        if not check_adb_before_start():
            event_switch.deselect()
            return
        # Stop other functions and clear log
        stop_all_other_functions('event')
        clear_log()
        event_stop_flag.clear()
        global event_thread
        event_thread = threading.Thread(target=wrapped_event_loop, daemon=True)
        event_thread.start()
        print("✅ กำลังเริ่ม Auto battle Giant POLY-ROLY")
    else:
        event_stop_flag.set()
        clear_log()
        print("🛑 หยุด Auto battle Giant POLY-ROLY เรียบร้อยแล้ว")
event_switch = ctk.CTkSwitch(event_row, text="", command=event_switch_event, font=(FONT_FAMILY, 12))
event_switch.grid(row=0, column=1, sticky="e", padx=(5, 0), pady=2)
event_desc = ctk.CTkLabel(event_row, text="เข้า Event ไปถึงหน้ากดปุ่มต่อสู้", font=(FONT_FAMILY, 12), text_color="#888888")
event_desc.grid(row=1, column=0, columnspan=2, sticky="w", padx=(20, 5), pady=(0, 8))

# --- Garden Row ---
garden_row = ctk.CTkFrame(root)
garden_row.pack(fill="x", pady=(5, 0))
garden_row.grid_columnconfigure(0, weight=1)
garden_name = ctk.CTkLabel(garden_row, text=BUTTON_TEXTS['garden'][0], anchor="w", font=(FONT_FAMILY, 14))
garden_name.grid(row=0, column=0, sticky="w", padx=(20, 5), pady=2)

def endless_garden_loop(stop_flag):
    from garden_event_runner import run_garden_event_loop
    run_garden_event_loop(stop_flag, skip_level8_check=True)

def garden_switch_event():
    if garden_switch.get():
        if not check_adb_before_start():
            garden_switch.deselect()
            return
        # Stop other functions and clear log
        stop_all_other_functions('garden')
        clear_log()
        garden_stop_flag.clear()
        global garden_thread
        version = garden_version_var.get()
        if version == "Repeat at lv8":
            print("🌱 Auto Garden Event: Repeat at lv8")
            garden_thread = threading.Thread(target=wrapped_garden_loop, daemon=True)
        else:
            print("🌱 Auto Garden Event: Endless loop")
            garden_thread = threading.Thread(target=endless_garden_loop, args=(garden_stop_flag,), daemon=True)
        garden_thread.start()
    else:
        garden_stop_flag.set()
        clear_log()
        print("🛑 หยุด Auto Garden Event เรียบร้อยแล้ว")

garden_switch = ctk.CTkSwitch(garden_row, text="", command=garden_switch_event, font=(FONT_FAMILY, 12))
garden_switch.grid(row=0, column=1, sticky="e", padx=(5, 0), pady=2)

def on_garden_version_change(value):
    if garden_switch.get():
        garden_switch.deselect()
        garden_stop_flag.set()
        clear_log()
        print("🛑 กำลังหยุด Auto Garden Event...")

garden_version_var = StringVar(value="Repeat at lv8")
garden_segmented = ctk.CTkSegmentedButton(garden_row, values=["Repeat at lv8", "Endless loop"], variable=garden_version_var, command=on_garden_version_change, font=(FONT_FAMILY, 12))
garden_segmented.grid(row=2, column=0, columnspan=2, sticky="w", padx=(20, 5), pady=(0, 8))
garden_desc = ctk.CTkLabel(garden_row, text="เข้า Event Garden แล้วจะเลื่อนผสมวัตถุให้", font=(FONT_FAMILY, 12), text_color="#888888")
garden_desc.grid(row=1, column=0, columnspan=2, sticky="w", padx=(20, 5), pady=(0, 8))

# === Log Section ===
log_frame = ctk.CTkFrame(root)
log_frame.pack(fill="both", expand=True, pady=(5, 0))

log = ctk.CTkTextbox(log_frame, height=300, width=500, font=(FONT_FAMILY, 12))
log.pack(fill="both", expand=True, padx=5, pady=5)

# === Footer ===
footer_frame = ctk.CTkFrame(root)
footer_frame.pack(fill="x", pady=(10, 5))

# Setup button on the left
setup_btn = ctk.CTkButton(footer_frame, text="🎮 ตัวช่วยตั้งค่า Emulator", command=show_setup_wizard, 
                         font=(FONT_FAMILY, 12), height=30)
setup_btn.pack(side="left", padx=(20, 0), pady=5)

# Author text on the right
footer_label = ctk.CTkLabel(footer_frame, text="Kaidum Kaidaow เป็นพี่น้องกัน", font=(FONT_FAMILY, 12), text_color="#888888", anchor="e")
footer_label.pack(side="right", padx=(0, 20), pady=5)

# === Log Management ===
def clear_log():
    log.delete("1.0", "end")

def stop_all_other_functions(current_function):
    """Stop all other functions except the current one"""
    if current_function != 'dungeon' and dungeon_switch.get():
        dungeon_switch.deselect()
        dungeon_stop_flag.set()
        print("🛑 กำลังหยุด Auto stage...")
    
    if current_function != 'event' and event_switch.get():
        event_switch.deselect()
        event_stop_flag.set()
        print("🛑 กำลังหยุด Auto battle Giant POLY-ROLY...")
    
    if current_function != 'garden' and garden_switch.get():
        garden_switch.deselect()
        garden_stop_flag.set()
        print("🛑 กำลังหยุด Auto Garden Event...")

# Optional: redirect print to the UI
class Redirect:
    def write(self, text):
        log.insert("end", text)
        log.see("end")
    def flush(self): pass
sys.stdout = sys.stderr = Redirect()

def wrapped_garden_loop():
    from garden_event_runner import run_garden_event_loop
    run_garden_event_loop(garden_stop_flag, skip_level8_check=False)

def wrapped_event_loop():
    run_event_loop(event_stop_flag)

def wrapped_dungeon_loop():
    run_dungeon_loop_simple(dungeon_stop_flag)

root.mainloop()
