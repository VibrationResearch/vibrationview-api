#!/usr/bin/env python
"""
VibrationVIEW File Operations Test Module

This module contains tests for file operations functionality in the VibrationVIEW API.
These tests focus on opening, saving, and manipulating test files.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
- Main test infrastructure from test_VibrationviewAPI.py

Usage:
    pytest test_file_operations.py -v
"""

import os
import sys
import time
import logging
import pytest
from datetime import datetime


# Configure logger
logger = logging.getLogger(__name__)

# Add necessary paths for imports
current_dir = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

try:
    # Import main VibrationVIEW API from the package
    from vibrationviewapi import VibrationVIEW, ExtractComErrorInfo, vvTestType
except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure it's in your Python path.", allow_module_level=True)

try:
    # Import command line API from the package
    from vibrationviewapi import GenerateTXTFromVV, GenerateUFFFromVV
except ImportError:
    pytest.skip("Could not import VibrationVIEW command line functions. Make sure they're in your Python path.", allow_module_level=True)

class TestFileOperations:
    """Test class for VibrationVIEW file operations functionality"""
    
    @pytest.mark.fileop
    def test_file_operations_basic(self):
        """Test basic file operations (open, save)"""
        # Find a test file
        test_file = self.find_test_file("sine")
        if not test_file:
            logger.warning("No test file found")
            pytest.skip("No test file found for testing")
        
        logger.info(f"Using test file: {test_file}")
        
        # Open the test
        try:
            self.vv.OpenTest(test_file)
            logger.info(f"Opened test file: {test_file}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Opening test file failed: {error_info}")
            pytest.fail(f"Opening test file failed: {error_info}")

        # Get test type
        try:
            test_type = self.vv.TestType
            test_type_name = vvTestType.get_name(test_type) if test_type is not None else "Unknown"
            assert test_type is not None
            logger.info(f"Test type: {test_type_name}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Getting test type failed: {error_info}")
            pytest.fail(f"Getting test type failed: {error_info}")
        
        # Save data if possible
        try:
            # Create a data directory if it doesn't exist
            data_dir = os.path.join(self.script_dir, '..', 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                logger.info(f"Created data directory: {data_dir}")
            
            # Get filename without path and create new path in data folder
            file_name = os.path.basename(test_file)
            base_name, ext = os.path.splitext(file_name)
            
            # Modify the extension for data files
            if len(ext) > 3:  # Ensure the extension is at least 3 characters
                new_ext = ext[:3] + 'd'  # .vrp becomes .vrd
            else:
                new_ext = ext  # If the extension is too short, don't change it
            
            # Construct the new save path in the data directory
            save_path = os.path.join(data_dir, base_name + new_ext)
            
            self.vv.SaveData(save_path)
            logger.info(f"Saved data to: {save_path}")
            
            # Verify file exists and has content
            assert os.path.exists(save_path), f"Data file not found: {save_path}"
            file_size = os.path.getsize(save_path)
            logger.info(f"Data file size: {file_size} bytes")
            assert file_size > 0, "Data file is empty"
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Saving data failed: {error_info}")
            pytest.fail(f"Saving data failed: {error_info}")
    
    @pytest.mark.fileop
    def test_file_operations_with_timestamp(self):
        """Test file operations with timestamp in filename"""
        # Find a test file
        test_file = self.find_test_file("sine")
        if not test_file:
            logger.warning("No test file found")
            pytest.skip("No test file found for testing")
        
        logger.info(f"Using test file: {test_file}")
        
        # Open the test
        self.vv.OpenTest(test_file)
        logger.info(f"Opened test file: {test_file}")
        
        # Create a data directory if it doesn't exist
        data_dir = os.path.join(self.script_dir, '..', 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")
        
        # Get filename without path
        file_name = os.path.basename(test_file)
        base_name, ext = os.path.splitext(file_name)
        
        # Add timestamp to make the filename unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Modify the extension for data files
        if len(ext) > 3:  # Ensure the extension is at least 3 characters
            new_ext = ext[:3] + 'd'  # .vrp becomes .vrd
        else:
            new_ext = ext  # If the extension is too short, don't change it
        
        # Construct the new save path in the data directory
        save_path = os.path.join(data_dir, f"{base_name}_{timestamp}{new_ext}")
        
        # Save the data
        try:
            self.vv.SaveData(save_path)
            logger.info(f"Saved data to: {save_path}")
            
            # give it a second to allow the file save to complete
            time.sleep(1)

            # Verify file exists and has content
            assert os.path.exists(save_path), f"Data file not found: {save_path}"
            file_size = os.path.getsize(save_path)
            logger.info(f"Data file size: {file_size} bytes")
            assert file_size > 0, "Data file is empty"
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Saving data with timestamp failed: {error_info}")
            pytest.fail(f"Saving data with timestamp failed: {error_info}")
    
    @pytest.mark.fileop
    def test_open_multiple_file_types(self):
        """Test opening different types of test files"""
        # Try to find and open different test types
        test_types = ["sine", "random", "shock", "srs"]
        files_opened = 0
        
        for test_type in test_types:
            test_file = self.find_test_file(test_type)
            if test_file:
                try:
                    logger.info(f"Opening {test_type.upper()} test file: {test_file}")
                    self.vv.OpenTest(test_file)
                    
                    # Verify test opened correctly
                    opened_type = self.vv.TestType
                    opened_type_name = vvTestType.get_name(opened_type) if opened_type is not None else "Unknown"
                    logger.info(f"Opened test type: {opened_type_name}")
                    
                    files_opened += 1
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Could not open {test_type} test: {error_info}")
                    continue
        
        # Skip if no files could be opened
        if files_opened == 0:
            logger.warning("Could not open any test files")
            pytest.skip("Could not open any test files")
        else:
            logger.info(f"Successfully opened {files_opened} test files")
    
    @pytest.mark.fileop
    def test_save_and_open_data(self):
        """Test saving and then reopening the saved data file"""
        # Find a test file
        test_file = self.find_test_file("sine")
        if not test_file:
            logger.warning("No test file found")
            pytest.skip("No test file found for testing")
        
        logger.info(f"Using test file: {test_file}")
        
        # Open the test and run it briefly to generate data
        self.vv.OpenTest(test_file)
        logger.info(f"Opened test file: {test_file}")
        
        # Start the test
        try:
            self.vv.StartTest()
            logger.info("Started test")
            
            # Wait for test to run
            running = self.wait_for_condition(self.vv.IsRunning)
            if running:
                # Let it run for a few seconds
                time.sleep(3)
                logger.info("Test ran for 3 seconds")
                
                # Stop the test
                self.vv.StopTest()
                logger.info("Test stopped")
            else:
                logger.warning("Test did not start running")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.warning(f"Error running test: {error_info}")
        
        # Create a data directory if it doesn't exist
        data_dir = os.path.join(self.script_dir, '..', 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.basename(test_file)
        base_name, ext = os.path.splitext(file_name)
        
        # Modify the extension for data files
        if len(ext) > 3:
            new_ext = ext[:3] + 'd'  # .vrp becomes .vrd
        else:
            new_ext = ext
        
        save_path = os.path.join(data_dir, f"{base_name}_{timestamp}{new_ext}")
        
        # Save the data
        try:
            self.vv.SaveData(save_path)
            logger.info(f"Saved data to: {save_path}")
            
            time.sleep(1) # give it a second to save
            
            # Verify file exists
            assert os.path.exists(save_path), f"Data file not found: {save_path}"
            
            # Try to open the saved data file
            try:
                actual_textfilename = GenerateTXTFromVV(save_path,'test.txt')
                assert actual_textfilename is not None
                logger.info(f"Actual text filename: {actual_textfilename}")
                txtfile_size = os.path.getsize(actual_textfilename)
                logger.info(f"Text file size: {txtfile_size} bytes")

                actual_UFFfilename = GenerateUFFFromVV(save_path,'test.uff')
                assert actual_UFFfilename is not None
                logger.info(f"Actual UFF filename: {actual_UFFfilename}")
                ufffile_size = os.path.getsize(actual_UFFfilename)
                logger.info(f"UFF file size: {ufffile_size} bytes")
            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.error(f"Opening saved data file failed: {error_info}")
                pytest.fail(f"Opening saved data file failed: {error_info}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Saving data failed: {error_info}")
            pytest.fail(f"Saving data failed: {error_info}")

    @pytest.mark.fileop
    def test_open_list_close_test(self):
        """Test opening a test, listing open tests, and closing the test"""
        # Find the default sine test file
        test_file = self.find_test_file("sine")
        if not test_file:
            logger.warning("No sine test file found")
            pytest.skip("No sine test file found for testing")

        logger.info(f"Using test file: {test_file}")

        # Get the test profile name from the file path
        profile_name = os.path.basename(test_file)
        logger.info(f"Test profile name: {profile_name}")

        # Open the sine test
        try:
            self.vv.OpenTest(test_file)
            logger.info(f"Successfully opened test: {profile_name}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Opening test failed: {error_info}")
            pytest.fail(f"Opening test failed: {error_info}")

        # List the open tests
        # ListOpenTests returns a 2D array with columns: [tab_index, test_type, file_name, test_name]
        try:
            open_tests = self.vv.ListOpenTests()
            assert open_tests is not None, "ListOpenTests returned None"
            logger.info(f"Number of open tests: {len(open_tests)}")

            # Log all open tests with their details
            for i, test_info in enumerate(open_tests):
                if len(test_info) >= 4:
                    logger.info(f"Open test {i}: tab_index={test_info[0]}, test_type={test_info[1]}, file_name={test_info[2]}, test_name={test_info[3]}")
                else:
                    logger.info(f"Open test {i}: {test_info}")

            # Verify the newly opened test is in the list
            assert len(open_tests) > 0, "No tests found in open tests list"

            # Look for the test we just opened by checking the file_name column (index 2)
            found = False
            found_tab_index = None
            for test_info in open_tests:
                if len(test_info) >= 3:
                    tab_idx = test_info[0]
                    file_name = test_info[2]

                    # Check if our profile matches the filename (only if file_name is not blank)
                    if file_name and profile_name and profile_name.lower() in file_name.lower():
                        found = True
                        found_tab_index = tab_idx
                        logger.info(f"Found test at tab index {tab_idx}: file_name='{file_name}'")
                        break

            assert found, f"Newly opened test '{profile_name}' not found in open tests list"
            logger.info(f"Verified '{profile_name}' is in the open tests list")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Listing open tests failed: {error_info}")
            pytest.fail(f"Listing open tests failed: {error_info}")

        # Close the newly opened test using CloseTest with profile name
        try:
            result = self.vv.CloseTest(test_file)
            assert result, f"CloseTest failed to close '{test_file}'"
            logger.info(f"Successfully closed test: {test_file}")

            # Verify the test was closed by listing open tests again
            open_tests_after = self.vv.ListOpenTests()
            logger.info(f"Number of open tests after closing: {len(open_tests_after) if open_tests_after else 0}")

            # Check that the closed test is no longer in the list
            if open_tests_after:
                found_after = False
                for test_info in open_tests_after:
                    if len(test_info) >= 3:
                        file_name = test_info[2]
                        if file_name and profile_name in file_name:
                            found_after = True
                            break

                assert not found_after, f"Test '{profile_name}' still in open tests list after closing"

            logger.info(f"Verified '{profile_name}' was removed from open tests list")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Closing test failed: {error_info}")
            pytest.fail(f"Closing test failed: {error_info}")

    @pytest.mark.fileop
    def test_open_list_close_test_running_should_fail(self):
        """Test that closing a running test should fail"""
        # Find the default sine test file
        test_file = self.find_test_file("sine")
        if not test_file:
            logger.warning("No sine test file found")
            pytest.skip("No sine test file found for testing")

        logger.info(f"Using test file: {test_file}")

        # Get the test profile name from the file path
        profile_name = os.path.basename(test_file)
        logger.info(f"Test profile name: {profile_name}")

        # Open the sine test
        try:
            self.vv.OpenTest(test_file)
            logger.info(f"Successfully opened test: {profile_name}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Opening test failed: {error_info}")
            pytest.fail(f"Opening test failed: {error_info}")

        # List the open tests
        # ListOpenTests returns a 2D array with columns: [tab_index, test_type, file_name, test_name]
        try:
            open_tests = self.vv.ListOpenTests()
            assert open_tests is not None, "ListOpenTests returned None"
            logger.info(f"Number of open tests: {len(open_tests)}")

            # Log all open tests with their details
            for i, test_info in enumerate(open_tests):
                if len(test_info) >= 4:
                    logger.info(f"Open test {i}: tab_index={test_info[0]}, test_type={test_info[1]}, file_name={test_info[2]}, test_name={test_info[3]}")
                else:
                    logger.info(f"Open test {i}: {test_info}")

            # Verify the newly opened test is in the list
            assert len(open_tests) > 0, "No tests found in open tests list"

            # Look for the test we just opened by checking the file_name column (index 2)
            found = False
            found_tab_index = None
            for test_info in open_tests:
                if len(test_info) >= 3:
                    tab_idx = test_info[0]
                    file_name = test_info[2]

                    # Check if our profile matches the filename (only if file_name is not blank)
                    if file_name and profile_name in file_name:
                        found = True
                        found_tab_index = tab_idx
                        logger.info(f"Found test at tab index {tab_idx}: file_name='{file_name}'")
                        break

            assert found, f"Newly opened test '{profile_name}' not found in open tests list"
            logger.info(f"Verified '{profile_name}' is in the open tests list")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Listing open tests failed: {error_info}")
            pytest.fail(f"Listing open tests failed: {error_info}")

        # Start the test and attempt to close it while running
        try:
            # Start the test
            self.vv.StartTest()
            logger.info("Started test")

            # Wait for test to be running
            running = self.wait_for_condition(self.vv.IsRunning, wait_time=5)
            assert running, "Test did not start running"
            logger.info("Test is running")

            # Attempt to close the test while it's running - this should return False
            result = self.vv.CloseTest(test_file)
            assert result == False, f"CloseTest should return False when test is running, but returned {result}"
            logger.info(f"CloseTest correctly returned False while test is running")

        finally:
            # Always stop the test in the finally block
            try:
                logger.info("Stopping test in finally block")
                self.vv.StopTest()

                # Wait for test to stop
                stopped = self.wait_for_not(self.vv.IsRunning, wait_time=5)
                if not stopped:
                    logger.warning("Test did not stop in expected time")
                else:
                    logger.info("Test stopped successfully")

            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.error(f"Stopping test in finally block failed: {error_info}")

    @pytest.mark.fileop
    def test_open_list_close_test_by_name(self):
        """Test opening a test, listing open tests, and closing the test using profile name"""
        # Find the default sine test file
        test_file = self.find_test_file("sine")
        if not test_file:
            logger.warning("No sine test file found")
            pytest.skip("No sine test file found for testing")

        logger.info(f"Using test file: {test_file}")

        # Open the sine test
        try:
            self.vv.OpenTest(test_file)
            logger.info(f"Successfully opened test: {test_file}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Opening test failed: {error_info}")
            pytest.fail(f"Opening test failed: {error_info}")

        # List the open tests
        # ListOpenTests returns a 2D array with columns: [tab_index, test_type, file_name, test_name]
        try:
            open_tests = self.vv.ListOpenTests()
            assert open_tests is not None, "ListOpenTests returned None"
            logger.info(f"Number of open tests: {len(open_tests)}")

            # Log all open tests with their details
            for i, test_info in enumerate(open_tests):
                if len(test_info) >= 4:
                    logger.info(f"Open test {i}: tab_index={test_info[0]}, test_type={test_info[1]}, file_name={test_info[2]}, test_name={test_info[3]}")
                else:
                    logger.info(f"Open test {i}: {test_info}")

            # Verify the newly opened test is in the list
            assert len(open_tests) > 0, "No tests found in open tests list"

            # Look for the test we just opened by checking the file_name column (index 2)
            found = False
            found_tab_index = None
            tab_name = None
            for test_info in open_tests:
                if len(test_info) >= 3:
                    tab_idx = test_info[0]
                    file_name = test_info[2]
                    tab_name = test_info[3]

                    # Check if our profile matches the filename (only if file_name is not blank)
                    if file_name and test_file in file_name:
                        found = True
                        found_tab_index = tab_idx
                        logger.info(f"Found test at tab index {tab_idx}: file_name='{file_name}'")
                        break

            assert found, f"Newly opened test '{test_file}' not found in open tests list"
            logger.info(f"Verified '{test_file}' is in the open tests list")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Listing open tests failed: {error_info}")
            pytest.fail(f"Listing open tests failed: {error_info}")

        # Close the newly opened test using CloseTest with profile name (basename only)
        try:
            result = self.vv.CloseTest(tab_name)
            assert result, f"CloseTest failed to close '{tab_name}'"
            logger.info(f"Successfully closed test: {tab_name}")

            # Verify the test was closed by listing open tests again
            open_tests_after = self.vv.ListOpenTests()
            logger.info(f"Number of open tests after closing: {len(open_tests_after) if open_tests_after else 0}")

            # Check that the closed test is no longer in the list
            if open_tests_after:
                found_after = False
                for test_info in open_tests_after:
                    if len(test_info) >= 3:
                        file_name = test_info[2]
                        if file_name and test_file in file_name:
                            found_after = True
                            break

                assert not found_after, f"Test '{test_file}' still in open tests list after closing"

            logger.info(f"Verified '{test_file}' was removed from open tests list")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Closing test failed: {error_info}")
            pytest.fail(f"Closing test failed: {error_info}")

    @pytest.mark.fileop
    def test_close_tab_by_index(self):
        """Test closing a test tab by index"""
        # Find the default sine test file
        test_file = self.find_test_file("sine")
        if not test_file:
            logger.warning("No sine test file found")
            pytest.skip("No sine test file found for testing")

        logger.info(f"Using test file: {test_file}")

        # Get the test profile name from the file path
        profile_name = os.path.basename(test_file)

        # Open the sine test
        try:
            self.vv.OpenTest(test_file)
            logger.info(f"Successfully opened test: {profile_name}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Opening test failed: {error_info}")
            pytest.fail(f"Opening test failed: {error_info}")

        # Get the tab index of the newly opened test
        try:
            open_tests = self.vv.ListOpenTests()
            assert open_tests is not None and len(open_tests) > 0, "No open tests found"

            # Find the tab index for our test by checking the filename column (index 2)
            tab_index = None
            for test_info in open_tests:
                if len(test_info) >= 3:
                    tab_idx = test_info[0]
                    file_name = test_info[2]

                    if file_name and profile_name in file_name:
                        tab_index = tab_idx
                        logger.info(f"Found test at tab index: {tab_index}")
                        break

            assert tab_index is not None, f"Could not find tab index for '{profile_name}'"
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Getting tab index failed: {error_info}")
            pytest.fail(f"Getting tab index failed: {error_info}")

        # Close the test using CloseTab with the tab index
        try:
            result = self.vv.CloseTab(tab_index)
            assert result, f"CloseTab failed to close tab at index {tab_index}"
            logger.info(f"Successfully closed tab at index {tab_index}")

            # Verify the test was closed
            open_tests_after = self.vv.ListOpenTests()

            # Check that the closed test is no longer in the list
            if open_tests_after:
                found_after = False
                for test_info in open_tests_after:
                    if len(test_info) >= 1 and test_info[0] == tab_index:
                        found_after = True
                        break

                assert not found_after, f"Tab {tab_index} still in open tests list after closing"

            logger.info(f"Verified tab {tab_index} was closed successfully")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Closing tab failed: {error_info}")
            pytest.fail(f"Closing tab failed: {error_info}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("vibrationview_file_operations_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("="*80)
    print("VibrationVIEW File Operations Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_file_operations.py -v")
    print("="*80)