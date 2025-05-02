"""
Configuration settings for the VibrationVIEW API.

This module contains the configuration parameters needed for the VibrationVIEW
command-line operations, such as report generation and file exports.
"""

import os
import sys
import winreg
from pathlib import Path

def get_vv_executable_path():
    """
    Get the VibrationVIEW executable path from the Windows registry.
    
    Returns:
        str: Path to VibrationVIEW.exe, or fallback path if registry key not found
    """
    try:
        # Open the registry key containing the path (COM registration)
        key_path = r"CLSID\{10C5DA8D-4909-4BFF-AD10-2799114907EA}\LocalServer32"
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
            # Get the default value, which should be the path to the executable
            value, _ = winreg.QueryValueEx(key, "")
            
            # The value might be surrounded by quotes and have parameters after the exe path
            # First, remove any surrounding quotes
            path = value.strip('"')
            
            # If there are parameters (indicated by .exe followed by space and parameters)
            # extract just the executable path
            exe_end_index = path.lower().find('.exe')
            if exe_end_index > 0:
                # Include the .exe in the path
                path = path[:exe_end_index + 4]
                
            return path
    except (WindowsError, IndexError):
        # Fallback path if registry key not found
        program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        return os.path.join(program_files, "Vibration Research", "VibrationVIEW 2025", "VibrationVIEW.exe")
# Path to VibrationVIEW user data - this is fixed at C:\VibrationVIEW
DEFAULT_VV_USER_PATH = r"C:\VibrationVIEW"

# Get the VibrationVIEW executable path from registry
EXE_NAME = get_vv_executable_path()

# Path to the report templates folder
REPORTS_PATH = os.path.join(DEFAULT_VV_USER_PATH, "Reports")

# Path to the profiles folder
PROFILES_PATH = os.path.join(DEFAULT_VV_USER_PATH, "Profiles")

# Path to store generated reports
REPORT_FOLDER = os.path.join(DEFAULT_VV_USER_PATH, "Reports")

# Path to store temporary files
TEMP_FOLDER = os.path.join(REPORT_FOLDER, "Temporary")
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Initialize logging
def setup_logging():
    """Set up logging for the VibrationVIEW API."""
    import logging
    log_file = os.path.join(TEMP_FOLDER, "vibrationview_api.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('vibrationview_api')

# Logger instance
logger = setup_logging()