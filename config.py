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
    "blue_jar.png",
    "cake_roll_production.png",
    "coffee.png",
    "cookie_house_production.png",
    "flower_production.png",
    "milk.png",
    "pot_production.png",
    "red_yam_production.png",
    "sugar_gnome_craftmanship.png",
    "sugar_production.png",
    "tools_production.png",
    "waterfall_production.png",
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
    "required_axe.png",
    "required_pretzel.png",
    "saw.png",
    "shovel.png",
    "pretzel.png"
]

COOKIE_RESEARCH_ICON_NAMES = [
    "increase_bounty_reward.png",
    "increase_def_ambush.png",
    "increase_def_attacker_slot.png",
    "increase_def_bomber.png",
    "increase_def_healer.png",
    "increase_def_ranger.png",
    "increase_def_support.png",
    "increase_hp_ambush_slot.png",
    "increase_hp_attacker_slot.png",
    "increase_hp_bomber_slot.png",
    "increase_hp_defender_slot.png",
    "increase_hp_healer_slot.png",
    "increase_hp_magic_slot.png",
    "increase_hp_ranger_slot.png",
    "increase_hp_support_slot.png",
    "increase_overall_def.png",
    "increase_overall_hp.png",
    "reduce_topping_price.png",
]

# Button images for PyInstaller compatibility
BUTTON_IMAGES = [
    "activity_button.png",
    "alt_win_icon.png",
    "available_to_research.png",
    "bundle_close_button.png",
    "castle_research_button.png",
    "check_button.png",
    "collect_gnome.png",
    "confirm_button.png",
    "confirm_gnome_upgrade_button.png",
    "continue_event_button.png",
    "continue_research_button.png",
    "cookie_research_button.png",
    "destroy_button.png",
    "exit_button.png",
    "level_8_icon.png",
    "level_up_continue_button.png",
    "management_button.png",
    "next_episode_button.png",
    "next_floor_button.png",
    "next_stage_button.png",
    "next_stage_icon.png",
    "next_stage_logo.png",
    "not_available_research_button.png",
    "not_available_to_research.png",
    "not_enough_mats.png",
    "prepare_button.png",
    "production_management.png",
    "quest_close_button.png",
    "random_effect_button.png",
    "receive_reward_button.png",
    "ready_button.png",
    "refill_all_button.png",
    "refill_all_confirm_button.png",
    "refill_all_icon.png",
    "research_button.png",
    "research_found_icon.png",
    "research_lab_button.png",
    "researching_icon.png",
    "retry_button.png",
    "skip_button.png",
    "win_icon.png",
    "zero_progress_icon.png",
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

def get_material_icons_by_level(max_level):
    """
    Get material icons filtered by max level.
    Level mapping:
    lv1 = required_axe
    lv2 = required_pickaxe  
    lv3 = required_saw
    lv4 = required_shovel
    lv5 = required_pretzel
    lv6-10 = (future materials, currently empty)
    """
    level_materials = {
        1: ["required_axe.png"],
        2: ["required_axe.png", "required_pickaxe.png"],
        3: ["required_axe.png", "required_pickaxe.png", "required_saw.png"],
        4: ["required_axe.png", "required_pickaxe.png", "required_saw.png", "required_shovel.png"],
        5: ["required_axe.png", "required_pickaxe.png", "required_saw.png", "required_shovel.png", "required_pretzel.png"],
        6: ["required_axe.png", "required_pickaxe.png", "required_saw.png", "required_shovel.png", "required_pretzel.png"],  # Future: add new material
        7: ["required_axe.png", "required_pickaxe.png", "required_saw.png", "required_shovel.png", "required_pretzel.png"],  # Future: add new material
        8: ["required_axe.png", "required_pickaxe.png", "required_saw.png", "required_shovel.png", "required_pretzel.png"],  # Future: add new material
        9: ["required_axe.png", "required_pickaxe.png", "required_saw.png", "required_shovel.png", "required_pretzel.png"],  # Future: add new material
        10: ["required_axe.png", "required_pickaxe.png", "required_saw.png", "required_shovel.png", "required_pretzel.png"],  # Future: add new material
    }
    
    if max_level not in level_materials:
        return []
    
    from config import get_resource_path
    return [get_resource_path(os.path.join("material_icons", name)) for name in level_materials[max_level]] 