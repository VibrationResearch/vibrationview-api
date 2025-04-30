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
    # Import main VibrationVIEW API
    from vibrationviewAPI import VibrationVIEW, vvVector, vvTestType, ExtractComErrorInfo
except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)

try:
    # Import main VibrationVIEW API
    from vibrationviewCommandLine import GenerateTXTFromVV,GenerateUFFFromVV
except ImportError:
    pytest.skip("Could not import vibrationviewCommandLine API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)

class TestFileOperations:
    """Test class for VibrationVIEW file operations functionality"""
    
    @pytest.fixture(autouse=True)
    def _setup(self, vv, wait_for_condition, wait_for_not, find_test_file, script_dir):
        """Setup method that runs before each test method"""
        self.vv = vv
        self.wait_for_condition = wait_for_condition
        self.wait_for_not = wait_for_not
        self.find_test_file = find_test_file
        self.script_dir = script_dir
    
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
            test_type = self.vv.TestType()
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
                    opened_type = self.vv.TestType()
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