import os
import sys
import platform

# Global device selection
selected_device_serial = None

def get_base_path():
    """Get the base path for the application, works both in development and when bundled"""
    if getattr(sys, 'frozen', False):
        # Running in a bundle (PyInstaller)
        return sys._MEIPASS
    else:
        # Running in normal Python environment
        return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = get_base_path()
    return os.path.join(base_path, relative_path)

def get_adb_path():
    # First check environment variable
    adb_path = os.getenv('COOKIE_RUN_ADB_PATH')
    if adb_path and os.path.exists(adb_path):
        return adb_path

    # Get the base directory (works both in dev and bundled)
    base_dir = get_base_path()
    
    # Determine executable name based on platform
    adb_exe = 'adb.exe' if platform.system() == 'Windows' else 'adb'
    
    # First check in bundled platform-tools
    bundled_adb = os.path.join(base_dir, 'platform-tools', adb_exe)
    if os.path.exists(bundled_adb):
        return bundled_adb

    # List of possible locations to check
    possible_locations = [
        os.path.join(base_dir, adb_exe),          # Direct in base directory
        os.path.join(os.path.expanduser('~'), 'platform-tools', adb_exe),  # User home directory
        os.path.join(os.path.expanduser('~'), 'Android', 'platform-tools', adb_exe),  # Android SDK location
    ]
    
    # Add Windows-specific Program Files locations
    if platform.system() == 'Windows':
        program_files = [
            os.environ.get('ProgramFiles', 'C:\\Program Files'),
            os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        ]
        for pf in program_files:
            possible_locations.append(os.path.join(pf, 'Android', 'platform-tools', adb_exe))
    
    # Check each location
    for location in possible_locations:
        if os.path.exists(location):
            return location
            
    raise FileNotFoundError(
        "Could not find ADB executable. The application should include platform-tools, "
        "but if it's missing, you can set COOKIE_RUN_ADB_PATH environment variable "
        "to point to your adb executable"
    )

# Get Tesseract path
def get_tesseract_path():
    """Find the Tesseract executable."""
    # Check environment variable first
    tesseract_path = os.getenv('TESSERACT_CMD')
    if tesseract_path and os.path.exists(tesseract_path):
        return tesseract_path
    
    # Check default Windows installation path
    if platform.system() == "Windows":
        # It's common for the installer to add this to the PATH,
        # so just returning 'tesseract' often works if the user selected that option.
        return 'tesseract'

    # For other OS, assume it's in the PATH
    return 'tesseract'

    raise FileNotFoundError(
        "Could not find Tesseract executable. Please either:\n"
        "1. Install Tesseract-OCR in the default location\n"
        "2. Set the COOKIE_RUN_TESSERACT_PATH environment variable to point to your tesseract executable"
    )

# Hardcoded icon filenames for PyInstaller compatibility
CASTLE_RESEARCH_ICON_NAMES = [
    "bakery_production.png",
    "biscuit_production.png",
    "cake_roll_production.png",
    "cookie_house_production.png",
    "sugar_gnome_craftmanship.png",
    "sugar_production.png",
    "tools_production.png",
    "wood_production.png",
    "yam_production.png",
    "yelly_bean_production.png",
    "yelly_berry_production.png",
]

MATERIAL_ICON_NAMES = [
    "axe.png",
    "pickaxe.png",
    "required_pickaxe.png",
    "required_saw.png",
    "required_shovel.png",
    "saw.png",
    "shovel.png",
]

COOKIE_RESEARCH_ICON_NAMES = [
    "increase_def_attacker_slot.png",
    "increase_hp_ambush_slot.png",
    "increase_hp_attacker_slot.png",
    "increase_hp_bomber_slot.png",
    "increase_hp_defender_slot.png",
    "increase_hp_healer_slot.png",
    "increase_hp_magic_slot.png",
    "increase_hp_ranger_slot.png",
    "increase_hp_support_slot.png",
    "increase_overall_hp.png",
]

def get_castle_research_icons():
    from config import get_resource_path
    return [get_resource_path(os.path.join("castle_research_icons", name)) for name in CASTLE_RESEARCH_ICON_NAMES]

def get_material_icons():
    from config import get_resource_path
    return [get_resource_path(os.path.join("material_icons", name)) for name in MATERIAL_ICON_NAMES]

def get_cookie_research_icons():
    from config import get_resource_path
    return [get_resource_path(os.path.join("cookie_research_icons", name)) for name in COOKIE_RESEARCH_ICON_NAMES] 