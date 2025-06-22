import customtkinter as ctk
from customtkinter import StringVar
import threading
import os
import sys
import subprocess
from dungeon_bot import run_dungeon_loop
from event_auto_runner import run_event_loop
from simple_dungeon_bot import run_dungeon_loop_simple
from config import get_adb_path

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
    font_path = os.path.abspath(os.path.join("fonts", "Itim-Regular.ttf"))
    FR_PRIVATE  = 0x10
    FR_NOT_ENUM = 0x20
    ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
    FONT_FAMILY = "Itim"
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

def show_setup_wizard():
    """Show ADB setup wizard for emulators"""
    setup_window = ctk.CTkToplevel(root)
    setup_window.title("Emulator Setup Wizard")
    setup_window.geometry("700x600")
    setup_window.resizable(False, False)
    
    # Make it modal
    setup_window.transient(root)
    setup_window.grab_set()
    
    # Title
    title = ctk.CTkLabel(setup_window, text="🎮 Emulator Setup Wizard", font=(FONT_FAMILY, 20, "bold"))
    title.pack(pady=20)
    
    # Instructions
    instructions = ctk.CTkTextbox(setup_window, height=250, font=(FONT_FAMILY, 12))
    instructions.pack(pady=10, padx=20, fill="x")
    
    instructions_text = """🎮 Emulator Setup Instructions:

1. Choose Your Emulator:
   • NOX Player (requires developer options)
   • LDPlayer (simple ADB setting)
   • BlueStacks (simple ADB setting)

2. Enable ADB:
   • NOX: Enable developer options + USB debugging
   • LDPlayer: Enable "Local connection" in emulator settings
   • BlueStacks: Enable ADB in Preferences

3. Test Connection:
   • Make sure your emulator is running
   • Click "Test Connection" below
   • If successful, you'll see your emulator listed

⚠️  Note: Click the emulator buttons below for specific instructions."""
    
    instructions.insert("1.0", instructions_text)
    instructions.configure(state="disabled")
    
    # Emulator-specific instructions
    emulator_frame = ctk.CTkFrame(setup_window)
    emulator_frame.pack(pady=10, padx=20, fill="x")
    
    emulator_label = ctk.CTkLabel(emulator_frame, text="📱 Emulator-Specific Setup:", font=(FONT_FAMILY, 14, "bold"))
    emulator_label.pack(pady=10)
    
    def show_nox_guide():
        show_emulator_guide("NOX Player", """NOX Player Setup:
1. Start NOX Player
2. Go to Settings (top bar or gear icon)
3. Navigate to "Developer Options"
4. If you don't see it, go to "About tablet" → Tap "Build number" 7 times
5. In Developer Options, enable "USB debugging"
6. That's it! NOX will connect automatically

Note: You need to enable developer options in the Android system for NOX.""")
    
    def show_ldplayer_guide():
        show_emulator_guide("LDPlayer", """LDPlayer Setup:
1. Open LDPlayer
2. Click the gear icon (Settings) in the sidebar
3. Go to "Others" tab
4. Find "ADB debugging"
5. Enable "Local connection"
6. That's it! LDPlayer will connect automatically

Note: No need to enable developer options or USB debugging in the Android system.""")
    
    def show_bluestacks_guide():
        show_emulator_guide("BlueStacks", """BlueStacks Setup:
1. Open BlueStacks
2. Click Settings (gear icon) → Go to Preferences
3. Scroll down and enable ADB (Android Debug Bridge)
4. That's it! BlueStacks will connect automatically

Note: No need to enable developer options or USB debugging in the Android system.""")
    
    # Emulator buttons
    emulator_buttons = ctk.CTkFrame(emulator_frame)
    emulator_buttons.pack(pady=10)
    
    ctk.CTkButton(emulator_buttons, text="NOX Player", command=show_nox_guide, font=(FONT_FAMILY, 11)).pack(side="left", padx=5, pady=5)
    ctk.CTkButton(emulator_buttons, text="LDPlayer", command=show_ldplayer_guide, font=(FONT_FAMILY, 11)).pack(side="left", padx=5, pady=5)
    ctk.CTkButton(emulator_buttons, text="BlueStacks", command=show_bluestacks_guide, font=(FONT_FAMILY, 11)).pack(side="left", padx=5, pady=5)
    
    # Status frame
    status_frame = ctk.CTkFrame(setup_window)
    status_frame.pack(pady=10, padx=20, fill="x")
    
    status_label = ctk.CTkLabel(status_frame, text="Status: Not checked", font=(FONT_FAMILY, 12))
    status_label.pack(pady=10)
    
    # Buttons frame
    button_frame = ctk.CTkFrame(setup_window)
    button_frame.pack(pady=20, padx=20, fill="x")
    
    def test_connection():
        """Test ADB connection"""
        status_label.configure(text="Status: Testing connection...")
        setup_window.update()
        
        is_connected, devices = check_adb_connection()
        
        if is_connected:
            device_info = "\n".join([f"• {device.split('\t')[0]}" for device in devices])
            status_label.configure(text=f"✅ Connected! Found {len(devices)} emulator(s):\n{device_info}")
        else:
            status_label.configure(text="❌ No emulators found. Please check your connection.")
    
    def show_emulator_guide(emulator_name, guide_text):
        """Show specific emulator guide"""
        guide_window = ctk.CTkToplevel(setup_window)
        guide_window.title(f"{emulator_name} Setup Guide")
        guide_window.geometry("500x400")
        
        guide_textbox = ctk.CTkTextbox(guide_window, font=(FONT_FAMILY, 12))
        guide_textbox.pack(pady=20, padx=20, fill="both", expand=True)
        
        guide_textbox.insert("1.0", guide_text)
        guide_textbox.configure(state="disabled")
    
    def open_troubleshooting():
        """Open troubleshooting guide"""
        trouble_window = ctk.CTkToplevel(setup_window)
        trouble_window.title("Troubleshooting Guide")
        trouble_window.geometry("600x500")
        
        trouble_text = ctk.CTkTextbox(trouble_window, font=(FONT_FAMILY, 12))
        trouble_text.pack(pady=20, padx=20, fill="both", expand=True)
        
        trouble_content = """🔧 Emulator Troubleshooting:

Common Issues & Solutions:

1. "No devices found"
   • Make sure your emulator is running
   • Try restarting the emulator
   • Check if ADB debugging is enabled in emulator settings
   • Try different emulator instances

2. "ADB not responding"
   • Restart the emulator
   • Kill ADB server: adb kill-server
   • Start ADB server: adb start-server
   • Try connecting to specific port (if needed)

3. "Permission denied"
   • Make sure you've enabled ADB debugging in emulator settings
   • Try restarting the emulator
   • Check if emulator is fully loaded

4. Emulator-Specific Tips:
   • NOX: Enable developer options + USB debugging in Android settings
   • LDPlayer: Enable "Local connection" in Settings > Others > ADB debugging
   • BlueStacks: Enable ADB in Settings > Preferences

5. Performance Tips:
   • Use 2-4 GB RAM for emulator
   • Enable virtualization in BIOS
   • Close other applications while using bot
   • Use wired connection if possible"""
        
        trouble_text.insert("1.0", trouble_content)
        trouble_text.configure(state="disabled")
    
    test_btn = ctk.CTkButton(button_frame, text="Test Connection", command=test_connection, font=(FONT_FAMILY, 12))
    test_btn.pack(side="left", padx=10, pady=10)
    
    trouble_btn = ctk.CTkButton(button_frame, text="Troubleshooting", command=open_troubleshooting, font=(FONT_FAMILY, 12))
    trouble_btn.pack(side="left", padx=10, pady=10)
    
    close_btn = ctk.CTkButton(button_frame, text="Close", command=setup_window.destroy, font=(FONT_FAMILY, 12))
    close_btn.pack(side="right", padx=10, pady=10)

# === Setup Button ===
setup_frame = ctk.CTkFrame(root)
setup_frame.pack(fill="x", pady=(5, 0))
setup_frame.grid_columnconfigure(0, weight=1)

setup_btn = ctk.CTkButton(setup_frame, text="🎮 Emulator Setup Wizard", command=show_setup_wizard, font=(FONT_FAMILY, 12))
setup_btn.pack(pady=10)

# --- Dungeon Row ---
dungeon_row = ctk.CTkFrame(root)
dungeon_row.pack(fill="x", pady=(5, 0))
dungeon_row.grid_columnconfigure(0, weight=1)
dungeon_name = ctk.CTkLabel(dungeon_row, text=BUTTON_TEXTS['dungeon'][0], anchor="w", font=(FONT_FAMILY, 14))
dungeon_name.grid(row=0, column=0, sticky="w", padx=(20, 5), pady=2)
def dungeon_switch_event():
    if dungeon_switch.get():
        dungeon_stop_flag.clear()
        global dungeon_thread
        dungeon_thread = threading.Thread(target=wrapped_dungeon_loop, daemon=True)
        dungeon_thread.start()
    else:
        dungeon_stop_flag.set()
        print("🛑 กำลังหยุด Auto stage...")
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
        event_stop_flag.clear()
        global event_thread
        event_thread = threading.Thread(target=wrapped_event_loop, daemon=True)
        event_thread.start()
        print("✅ กำลังเริ่ม Auto battle Giant POLY-ROLY")
    else:
        event_stop_flag.set()
        print("🛑 กำลังหยุด Auto battle Giant POLY-ROLY...")
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

garden_switch = ctk.CTkSwitch(garden_row, text="", command=garden_switch_event, font=(FONT_FAMILY, 12))
garden_switch.grid(row=0, column=1, sticky="e", padx=(5, 0), pady=2)

def on_garden_version_change(value):
    if garden_switch.get():
        garden_switch.deselect()
        garden_stop_flag.set()
        print("🛑 กำลังหยุด Auto Garden Event...")

garden_version_var = StringVar(value="Repeat at lv8")
garden_segmented = ctk.CTkSegmentedButton(garden_row, values=["Repeat at lv8", "Endless loop"], variable=garden_version_var, command=on_garden_version_change, font=(FONT_FAMILY, 12))
garden_segmented.grid(row=2, column=0, columnspan=2, sticky="w", padx=(20, 5), pady=(0, 8))
garden_desc = ctk.CTkLabel(garden_row, text="เข้า Event Garden แล้วจะเลื่อนผสมวัตถุให้", font=(FONT_FAMILY, 12), text_color="#888888")
garden_desc.grid(row=1, column=0, columnspan=2, sticky="w", padx=(20, 5), pady=(0, 8))

log = ctk.CTkTextbox(root, height=300, width=500, font=(FONT_FAMILY, 12))
log.pack()

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
