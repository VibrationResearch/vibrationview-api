#!/usr/bin/env python
"""
VibrationVIEW Window Process State Detection

This module contains functions to detect the state of VibrationVIEW windows
by process name rather than relying on the VibrationVIEW API.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)

Usage:
    Import this module in test scripts to verify window states
"""

import os
import sys
import time
import logging
import pytest
import win32gui
import win32process
import win32con
import psutil

# Configure logger
logger = logging.getLogger(__name__)

def find_vibrationview_windows():
    """
    Find all windows associated with a VibrationVIEW process.
    
    Returns:
        list: List of window handles associated with VibrationVIEW processes
    """
    vibrationview_windows = []
    
    def enum_window_callback(hwnd, results):
        """Callback function for EnumWindows"""
        if not win32gui.IsWindowVisible(hwnd):
            return True
        
        # Check if this window belongs to a VibrationVIEW process
        try:
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(process_id)
                process_name = process.name().lower()
                
                # Look for VibrationVIEW processes
                if "vibrationview" in process_name:
                    # Get window title
                    title = win32gui.GetWindowText(hwnd)
                    logger.info(f"Found VibrationVIEW window: '{title}' (hwnd={hwnd}, pid={process_id})")
                    results.append((hwnd, process_id, title))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        except Exception as e:
            logger.warning(f"Error checking window process: {e}")
        
        return True
    
    try:
        win32gui.EnumWindows(enum_window_callback, vibrationview_windows)
    except Exception as e:
        logger.error(f"Error enumerating windows: {e}")
    
    return vibrationview_windows

def is_window_minimized(hwnd):
    """
    Check if a window is minimized
    
    Args:
        hwnd: Window handle
        
    Returns:
        bool: True if window is minimized, False otherwise
    """
    try:
        return win32gui.IsIconic(hwnd)
    except Exception as e:
        logger.error(f"Error checking if window is minimized: {e}")
        return None

def is_window_maximized(hwnd):
    """
    Check if a window is maximized
    
    Args:
        hwnd: Window handle
        
    Returns:
        bool: True if window is maximized, False otherwise
    """
    try:
        placement = win32gui.GetWindowPlacement(hwnd)
        return placement[1] == win32con.SW_SHOWMAXIMIZED
    except Exception as e:
        logger.error(f"Error checking if window is maximized: {e}")
        return None

def is_window_normal(hwnd):
    """
    Check if a window is in normal state (not minimized or maximized)
    
    Args:
        hwnd: Window handle
        
    Returns:
        bool: True if window is in normal state, False otherwise
    """
    try:
        placement = win32gui.GetWindowPlacement(hwnd)
        return placement[1] == win32con.SW_SHOWNORMAL
    except Exception as e:
        logger.error(f"Error checking if window is normal: {e}")
        return None

def get_window_state(hwnd):
    """
    Get the state of a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        str: Window state ("minimized", "maximized", "normal", or "unknown")
    """
    if is_window_minimized(hwnd):
        return "minimized"
    elif is_window_maximized(hwnd):
        return "maximized"
    elif is_window_normal(hwnd):
        return "normal"
    else:
        return "unknown"

def get_vibrationview_window_states():
    """
    Get states of all VibrationVIEW windows
    
    Returns:
        list: List of tuples (title, state) for each VibrationVIEW window
    """
    windows = find_vibrationview_windows()
    results = []
    
    for hwnd, pid, title in windows:
        state = get_window_state(hwnd)
        results.append((title, state, hwnd, pid))
        logger.info(f"VibrationVIEW window '{title}' is in {state} state")
    
    return results

def wait_for_window_state(hwnd, expected_state, timeout=5, interval=0.5):
    """
    Wait for a window to reach an expected state
    
    Args:
        hwnd: Window handle
        expected_state: Expected state ("minimized", "maximized", or "normal")
        timeout: Maximum time to wait (seconds)
        interval: Check interval (seconds)
        
    Returns:
        bool: True if window reached expected state, False if timed out
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        current_state = get_window_state(hwnd)
        if current_state == expected_state:
            return True
        time.sleep(interval)
    
    return False

def maximize_window(hwnd):
    """
    Maximize a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        return wait_for_window_state(hwnd, "maximized")
    except Exception as e:
        logger.error(f"Error maximizing window: {e}")
        return False

def minimize_window(hwnd):
    """
    Minimize a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return wait_for_window_state(hwnd, "minimized")
    except Exception as e:
        logger.error(f"Error minimizing window: {e}")
        return False

def restore_window(hwnd):
    """
    Restore a window to normal state
    
    Args:
        hwnd: Window handle
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        return wait_for_window_state(hwnd, "normal")
    except Exception as e:
        logger.error(f"Error restoring window: {e}")
        return False

def activate_window(hwnd):
    """
    Activate (bring to foreground) a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # First make sure the window is not minimized
        if is_window_minimized(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # Set foreground window
        win32gui.SetForegroundWindow(hwnd)
        
        # Check if window is now the foreground window
        foreground_hwnd = win32gui.GetForegroundWindow()
        return foreground_hwnd == hwnd
    except Exception as e:
        logger.error(f"Error activating window: {e}")
        return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("Checking for VibrationVIEW windows...")
    windows = get_vibrationview_window_states()
    
    if not windows:
        print("No VibrationVIEW windows found.")
    else:
        print(f"Found {len(windows)} VibrationVIEW windows:")
        for title, state, hwnd, pid in windows:
            print(f"  - '{title}' is in {state} state (hwnd={hwnd}, pid={pid})")
