#!/usr/bin/env python
"""
VibrationVIEW Window Control Functions

This module contains tests for window control functions of the VibrationVIEW Python wrapper.
It's extracted from the main test suite to allow for focused testing of window-related functionality.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
- psutil library installed (pip install psutil)

Usage:
    pytest test_window_control_functions.py -v
"""

import os
import sys
import time
import logging
import pytest


# Configure logger
logger = logging.getLogger(__name__)

# Get the absolute path of the current file's directory
current_dir = os.path.abspath(os.path.dirname(__file__))
logger.info(current_dir)

# Construct the path to the sibling 'src' directory
src_dir = os.path.join(current_dir, '..', 'src')

# Add the 'src' directory to sys.path
sys.path.append(src_dir)

try:
    # Import main VibrationVIEW API
    from vibrationviewapi import VibrationVIEW, ExtractComErrorInfo
    
except ImportError:
    logger.info("Could not importVibrationVIEW API.")
    pytest.skip("Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)

# Try to import window process utilities
WINDOW_UTILS_AVAILABLE = False
try:
    import window_process_state
    from window_process_state import (
        find_vibrationview_windows,
        get_window_state,
        is_window_minimized,
        is_window_maximized,
    )
    WINDOW_UTILS_AVAILABLE = True
    logger.info("Successfully imported window_process_state utilities")
except ImportError as e:
    logger.info("Could not import window_process_state.py")
    pytest.skip("Could not import window_process_state.py. Make sure they are in the same directory or in your Python path.", allow_module_level=True)

class TestVibrationVIEWWindow:
    """Test class for VibrationVIEW Window Control functions"""
    
    @pytest.fixture(autouse=True)
    def _setup(self, vv):
        """Setup method that runs before each test method"""
        self.vv = vv
        
        # Find the VibrationVIEW windows
        try:
            windows = find_vibrationview_windows()
            if windows:
                self.window_handles = windows
                logger.info(f"Found {len(windows)} VibrationVIEW windows")
            else:
                logger.warning("No VibrationVIEW windows found")
                self.window_handles = []
        except Exception as e:
            logger.error(f"Error finding VibrationVIEW windows: {str(e)}")
            self.window_handles = []

    @pytest.mark.connection
    def test_connection(self):
        """Test connection to VibrationVIEW"""
        try:
            assert self.vv is not None
            logger.info("Connection to VibrationVIEW established")
            
            # Skip test if no windows found - likely vv is minimized to the tooltray
            if not self.window_handles:
                pytest.skip("No VibrationVIEW windows found")

        except AssertionError as e:
            logger.error(f"Connection test failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in connection test: {str(e)}")
            raise
    
    @pytest.mark.window
    def test_window_control(self):
        """Test window control functions using the VibrationVIEW API"""
        if not self.window_handles:
            pytest.skip("No VibrationVIEW windows found")
            return
            
        hwnd, _, _ = self.window_handles[0]  # Get the first window handle
        
        # Maximize
        try:
            self.vv.Maximize()
            logger.info("Window maximized via API")

            # Verify window state using process check
            time.sleep(0.5)  # Allow time for the window to change state
            assert is_window_maximized(hwnd), "Window was not maximized"
            logger.info("Verified window is maximized")
        except AssertionError as e:
            logger.error(f"Window maximize verification failed: {str(e)}")
            raise
        except Exception as e:
            error_info = ExtractComErrorInfo(e) if 'ExtractComErrorInfo' in locals() else str(e)
            logger.error(f"Error during window maximize: {error_info}")
            raise

        # Minimize
        try:
            self.vv.Minimize()
            logger.info("Window minimized via API")
            
            # Verify window state using process check
            time.sleep(0.5)  # Allow time for the window to change state
            assert is_window_minimized(hwnd), "Window was not minimized"
            logger.info("Verified window is minimized")
        except AssertionError as e:
            logger.error(f"Window minimize verification failed: {str(e)}")
            raise
        except Exception as e:
            error_info = ExtractComErrorInfo(e) if 'ExtractComErrorInfo' in locals() else str(e)
            logger.error(f"Error during window minimize: {error_info}")
            raise
        
        # Restore
        try:
            self.vv.Restore()
            logger.info("Window restored via API")
            
            # Verify window state using process check
            time.sleep(0.5)  # Allow time for the window to change state
            assert not is_window_minimized(hwnd), "Window is still minimized"
            logger.info("Verified window is no longer minimized")
        except AssertionError as e:
            logger.error(f"Window restore verification failed: {str(e)}")
            raise
        except Exception as e:
            error_info = ExtractComErrorInfo(e) if 'ExtractComErrorInfo' in locals() else str(e)
            logger.error(f"Error during window restore: {error_info}")
            raise

        # Activate
        try:
            self.vv.Activate()
            logger.info("Window activated via API")
        except Exception as e:
            error_info = ExtractComErrorInfo(e) if 'ExtractComErrorInfo' in locals() else str(e)
            logger.error(f"Error during window activation: {error_info}")
            raise
    
    @pytest.mark.window
    def test_all_vibrationview_windows(self):
        """Test detection of all VibrationVIEW windows"""
        # Find all VibrationVIEW windows
        try:
            windows = find_vibrationview_windows()
            
            if not windows:
                logger.warning("No VibrationVIEW windows found")
                pytest.skip("No VibrationVIEW windows found")
                return
            
            logger.info(f"Found {len(windows)} VibrationVIEW windows:")
            for hwnd, pid, title in windows:
                try:
                    state = get_window_state(hwnd)
                    logger.info(f"  - '{title}' is in {state} state (hwnd={hwnd}, pid={pid})")
                except Exception as e:
                    logger.error(f"Error getting window state for '{title}': {str(e)}")
            
            # Verify that we have at least one window
            assert len(windows) > 0, "Expected at least one VibrationVIEW window"
        except AssertionError as e:
            logger.error(f"Window detection test failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error detecting VibrationVIEW windows: {str(e)}")
            raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("window_control_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("="*80)
    print("VibrationVIEW Window Control Functions Test")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_window_control.py -v")
    print("="*80)