import os
import sys
import platform

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
    # First check environment variable
    tesseract_path = os.getenv('COOKIE_RUN_TESSERACT_PATH')
    if tesseract_path and os.path.exists(tesseract_path):
        return tesseract_path

    # Default paths for different platforms
    if platform.system() == 'Windows':
        default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(default_path):
            return default_path
    else:
        # On Unix-like systems, assume it's in PATH
        return 'tesseract'

    raise FileNotFoundError(
        "Could not find Tesseract executable. Please either:\n"
        "1. Install Tesseract-OCR in the default location\n"
        "2. Set the COOKIE_RUN_TESSERACT_PATH environment variable to point to your tesseract executable"
    ) 