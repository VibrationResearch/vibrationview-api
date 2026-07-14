"""
conftest.py - Pytest configuration and shared fixtures for VibrationVIEW tests
"""

import os
import sys
import time
from datetime import datetime

import pytest

# Get the absolute path of the current file's directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Construct the path to the sibling 'src' directory
src_dir = os.path.join(current_dir, '..', 'src')

# Add the 'src' directory to sys.path at the beginning to ensure it takes priority
sys.path.insert(0, src_dir)

# Auto-detect if VibrationVIEW COM server is available
# Set VV_USE_MOCK=1 to force mock mode even when COM is available
VV_COM_AVAILABLE = False
if not os.environ.get('VV_USE_MOCK'):
    try:
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        _test_obj = win32com.client.Dispatch('VibrationVIEW.TestControl')
        VV_COM_AVAILABLE = True
        del _test_obj
        pythoncom.CoUninitialize()
    except Exception:
        pass

# If COM is not available, use static mock
_mock_patcher = None
if not VV_COM_AVAILABLE:
    from unittest.mock import patch

    from .mock_com import create_mock_com_object
    _replayer = create_mock_com_object()
    _mock_patcher = patch('win32com.client.Dispatch', return_value=_replayer)
    _mock_patcher.start()

requires_vv = pytest.mark.skipif(
    not VV_COM_AVAILABLE,
    reason="Requires VibrationVIEW COM server"
)

requires_vv_live = pytest.mark.skipif(
    not VV_COM_AVAILABLE,
    reason="Requires live VibrationVIEW COM server (file I/O)"
)

try:
    # Import main VibrationVIEW API
    from vibrationviewapi import (  # noqa: F401
        ExtractComErrorInfo,
        VibrationVIEW,
        vvTestType,
        vvVector,
    )

except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)


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
        # Normalize the test folder path
        normalized_test_folder = os.path.normpath(test_folder)

        if test_type in test_files:
            test_file = os.path.join(normalized_test_folder, test_files[test_type])
            if os.path.exists(test_file):
                return test_file

        # Try to find any test file with the appropriate extension
        if os.path.exists(normalized_test_folder):
            # Get the extension for the requested test type
            ext = None
            if test_type in test_files:
                ext = os.path.splitext(test_files[test_type])[1]

            # Search for files with that extension
            if ext:
                for file in os.listdir(normalized_test_folder):
                    if file.lower().endswith(ext.lower()):
                        return os.path.join(normalized_test_folder, file)

            # If no file with specific extension found, try any known extension
            for file in os.listdir(normalized_test_folder):
                for _, test_file in test_files.items():
                    if file.lower().endswith(os.path.splitext(test_file)[1].lower()):
                        return os.path.join(normalized_test_folder, file)

        # If no specific file found, return the first available one
        default_test = next(iter(test_files.values()), None)
        if default_test:
            return os.path.join(normalized_test_folder, default_test)

        return None

    return _find_test_file

@pytest.fixture(scope="session")
def vv():
    """Fixture to provide a VibrationVIEW connection"""
    # Set up the VibrationVIEW connection
    connection = VibrationVIEW()
    if connection.vv is None:
        pytest.fail("Connection to VibrationVIEW failed")

    if VV_COM_AVAILABLE:
        try:
            if hasattr(connection, 'SetInputConfigurationFile'):
                connection.SetInputConfigurationFile("10mV per G.vic")
        except Exception as e:
            print(f"Warning: Could not load input configuration: {e}")

        # Ensure recorder is stopped
        if hasattr(connection, 'RecordStop'):
            connection.RecordStop()

        # Ensure any running test is stopped
        if hasattr(connection, 'StopTest'):
            connection.StopTest()

    yield connection

    # Clean up after all tests
    if VV_COM_AVAILABLE:
        try:
            if hasattr(connection, 'IsRunning') and connection.IsRunning():
                connection.StopTest()
        except Exception as e:
            print(f"Warning during test cleanup: {e}")

    # Stop mock patcher if active
    if _mock_patcher is not None:
        _mock_patcher.stop()

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


@pytest.fixture(autouse=True)
def setup_vv_test(vv, wait_for_condition, wait_for_not, find_test_file, script_dir, request):
    """Global setup fixture that runs before each test method in VV test classes"""
    # Only apply to test classes that have test methods (skip conftest.py itself)
    if request.instance is not None:
        print("DEBUG: Starting global fixture setup")
        try:
            # Assign fixtures to the test instance
            request.instance.vv = vv
            print("DEBUG: Assigned vv")
            request.instance.wait_for_condition = wait_for_condition
            request.instance.wait_for_not = wait_for_not
            request.instance.find_test_file = find_test_file
            request.instance.script_dir = script_dir
            print("DEBUG: Assigned all fixture variables")

            # Load "10mV per G.vic" for all tests except TEDS tests
            # Check if this is NOT a TEDS test by checking the test file name
            if VV_COM_AVAILABLE:
                test_file_path = request.fspath.basename
                if test_file_path != "test_teds_functions.py":
                    if hasattr(vv, 'SetInputConfigurationFile'):
                        try:
                            vv.SetInputConfigurationFile("10mV per G.vic")
                            print("DEBUG: Loaded input configuration: 10mV per G.vic")
                        except Exception as e:
                            print(f"DEBUG: Could not load input configuration: {e}")

            print("DEBUG: Global fixture setup completed successfully")
        except Exception as fixture_error:
            print(f"DEBUG: Global fixture setup failed: {fixture_error}")
            import traceback
            traceback.print_exc()
            raise
