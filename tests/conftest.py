"""
conftest.py - Pytest configuration and shared fixtures for VibrationVIEW tests
"""

import os
import sys
import time
import pytest
from datetime import datetime

# Import the VibrationVIEW API wrapper

# Get the absolute path of the current file's directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Construct the path to the sibling 'src' directory
src_dir = os.path.join(current_dir, '..', 'src')

# Add the 'src' directory to sys.path
sys.path.append(src_dir)

try:
    # Import main VibrationVIEW API
    from vibrationviewAPI import VibrationVIEW, vvVector, vvTestType, ExtractComErrorInfo
    
except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)


# Try to import the VibrationVIEW API
# Get the absolute path of the current file's directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Construct the path to the sibling 'src' directory
src_dir = os.path.join(current_dir, '..', 'src')

# Add the 'src' directory to sys.path
sys.path.append(src_dir)

# Private variables for use within conftest.py only
_test_folder = os.path.join(current_dir,'..', "Profiles")
_output_dir = os.path.join(current_dir,'..', "output")


# Create output directory
try:
    if not os.path.exists(_output_dir):
        os.makedirs(_output_dir)
except Exception as e:
    print(f"Warning: Could not create output directory: {e}")
    _output_dir = current_dir

# Dictionary of test files by type - define as a fixture
@pytest.fixture(scope="session")
def test_files():
    """Dictionary of test files by type"""
    return {
        "sine": "Sine.vsp",
        "random": "Random.vrp",
        "shock": "Shock.vkp",
        "transient": "Transient.vtp",
        "DataReplay": "FDR.vrp"
    }

# Path-related fixtures
@pytest.fixture(scope="session")
def script_dir():
    """Path to the script directory"""
    return os.path.abspath(os.path.dirname(__file__))

@pytest.fixture(scope="session")
def test_folder(script_dir):
    """Path to the test profiles folder"""
    return _test_folder

@pytest.fixture(scope="session")
def output_dir(script_dir):
    """Path to the output directory"""
    path = os.path.join(script_dir, "output")
    # Ensure the directory exists
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print(f"Warning: Could not create output directory: {e}")
        path = script_dir
    return path

# Helper functions as fixtures
@pytest.fixture(scope="session")
def wait_for_condition():
    """
    Fixture providing a function to wait for a condition to become True
    
    Returns:
        Function that waits for a condition and returns boolean result
    """
    def _wait_for_condition(condition_func, wait_time=5, check_interval=0.1):
        """
        Wait up to wait_time seconds for condition_func to return True.
        
        Args:
            condition_func: Function that returns a boolean
            wait_time: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            Boolean indicating if condition was met
        """
        start_time = time.time()
        result = False
        
        while time.time() - start_time < wait_time:
            result = condition_func()
            if result:
                break
            time.sleep(check_interval)
            
        return result
    
    return _wait_for_condition

@pytest.fixture(scope="session")
def wait_for_not():
    """
    Fixture providing a function to wait for a condition to become False
    
    Returns:
        Function that waits for a condition to become False and returns boolean result
    """
    def _wait_for_not(condition_func, wait_time=5, check_interval=0.1):
        """
        Wait up to wait_time seconds for condition_func to return False.
        
        Args:
            condition_func: Function that returns a boolean
            wait_time: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            Boolean indicating if condition became False (False when condition becomes False)
        """
        start_time = time.time()
        
        while time.time() - start_time < wait_time:
            result = condition_func()
            if not result:
                return False  # Return False when condition becomes False
            time.sleep(check_interval)
            
        return True  # Timed out, condition still True
    
    return _wait_for_not

@pytest.fixture(scope="session")
def find_test_file(test_folder, test_files):
    """
    Fixture providing a function to find test files
    
    Args:
        test_folder: Path to test folder (fixture)
        test_files: Dictionary of test files (fixture)
        
    Returns:
        Function that finds appropriate test files by type
    """
    def _find_test_file(test_type):
        """Find an appropriate test file for the specified test type"""
        if test_type in test_files:
            test_file = os.path.join(test_folder, test_files[test_type])
            if os.path.exists(test_file):
                return test_file
        
        # Try to find any test file with the appropriate extension
        if os.path.exists(test_folder):
            # Get the extension for the requested test type
            ext = None
            if test_type in test_files:
                ext = os.path.splitext(test_files[test_type])[1]
            
            # Search for files with that extension
            if ext:
                for file in os.listdir(test_folder):
                    if file.lower().endswith(ext.lower()):
                        return os.path.join(test_folder, file)
            
            # If no file with specific extension found, try any known extension
            for file in os.listdir(test_folder):
                for _, test_file in test_files.items():
                    if file.lower().endswith(os.path.splitext(test_file)[1].lower()):
                        return os.path.join(test_folder, file)
        
        # If no specific file found, return the first available one
        default_test = next(iter(test_files.values()), None)
        if default_test:
            return os.path.join(test_folder, default_test)
        
        return None
    
    return _find_test_file

@pytest.fixture(scope="session")
def vv():
    """Fixture to provide a VibrationVIEW connection"""
    # Set up the VibrationVIEW connection
    connection = VibrationVIEW()
    if connection.vv is None:
        pytest.fail("Connection to VibrationVIEW failed")
    
    yield connection
    
    # Clean up after all tests
    try:
        if hasattr(connection, 'IsRunning') and connection.IsRunning():
            connection.StopTest()
    except Exception as e:
        print(f"Warning during test cleanup: {e}")

@pytest.fixture(scope="session")
def log_to_file(output_dir):
    """
    Fixture to provide a logging function
    
    Args:
        output_dir: Path to output directory (fixture)
        
    Returns:
        Function that logs messages to console and file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(output_dir, f"vv_test_results_{timestamp}.txt")
    
    with open(log_file_path, "w") as f:
        f.write(f"VibrationVIEW Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-" * 80 + "\n\n")
    
    def _log(message, success=None):
        """Log test result to console and file"""
        status = ""
        if success is not None:
            status = "[PASS]" if success else "[FAIL]"
        
        log_message = f"{status} {message}"
        print(log_message)
        
        try:
            with open(log_file_path, "a") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    return _log