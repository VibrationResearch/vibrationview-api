#!/usr/bin/env python
"""
VibrationVIEW Recording Test Module

This module contains tests for recording functionality in the VibrationVIEW API.
These tests focus on the recording capabilities introduced in VibrationVIEW version 11.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
- Main test infrastructure from test_VibrationviewAPI.py

Usage:
    pytest test_recording.py -v
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
    from vibrationviewapi import VibrationVIEW, ExtractComErrorInfo
except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure it's in your Python path.", allow_module_level=True)

try:
    # Import command line API from the package
    from vibrationviewapi import GenerateTXTFromVV, GenerateUFFFromVV
except ImportError:
    pytest.skip("Could not import VibrationVIEW command line functions. Make sure they're in your Python path.", allow_module_level=True)
class TestRecording:
    """Test class for VibrationVIEW recording functionality"""
    
    @pytest.fixture(autouse=True)
    def _setup(self, vv, wait_for_condition, wait_for_not, find_test_file, script_dir):
        """Setup method that runs before each test method"""
        self.vv = vv
        self.wait_for_condition = wait_for_condition
        self.wait_for_not = wait_for_not
        self.find_test_file = find_test_file
        self.script_dir = script_dir
    
    @pytest.mark.recording
    def test_recording_basic_functions(self):
        """Test basic recording functions (start, pause, stop)"""
        try:
            # Start recording
            logger.info("Starting recording")
            self.vv.RecordStart()
            
            # Wait a moment
            time.sleep(2)
            logger.info("Recording for 2 seconds")
            
            # Pause recording
            logger.info("Pausing recording")
            self.vv.RecordPause()
            
            # Wait a moment
            time.sleep(1)
            logger.info("Paused for 1 second")
            
            # Stop recording
            logger.info("Stopping recording")
            self.vv.RecordStop()
            
            # Get recording filename
            try:
                filename = self.vv.RecordGetFilename()
                assert filename is not None
                logger.info(f"Recording saved to: {filename}")
                
                # Verify file exists
                assert os.path.exists(filename), f"Recording file not found: {filename}"
                file_size = os.path.getsize(filename)
                logger.info(f"Recording file size: {file_size} bytes")
                assert file_size > 0, "Recording file is empty"
                
            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.error(f"Error getting recording filename: {error_info}")
                pytest.fail(f"Error getting recording filename: {error_info}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in recording functions: {error_info}")
            pytest.fail(f"Error in recording functions: {error_info}")
    
    @pytest.mark.recording
    def test_recording_with_test_running(self):
        """Test recording while a test is running"""
        try:
            # Find and run a test file
            test_file = self.find_test_file("sine")
            if not test_file:
                logger.warning("No test file found")
                pytest.skip("No test file found for testing recording with test running")
            
            logger.info(f"Using test file: {test_file}")
            
            # Open and start the test
            self.vv.OpenTest(test_file)
            logger.info(f"Opened test file: {test_file}")
            
            self.vv.StartTest()
            logger.info("Started test")
            
            # Wait for test to enter running state
            running = self.wait_for_condition(self.vv.IsRunning)
            if not running:
                logger.warning("Test did not enter running state")
                pytest.skip("Test did not enter running state, skipping recording with test running")
            
            logger.info("Test is running, starting recording")
            
            # Start recording
            self.vv.RecordStart()
            logger.info("Recording started")
            
            # Record for a few seconds
            time.sleep(3)
            logger.info("Recorded for 3 seconds")
            
            # Stop recording
            self.vv.RecordStop()
            logger.info("Recording stopped")
            
            # Get recording filename
            filename = self.vv.RecordGetFilename()
            assert filename is not None
            logger.info(f"Recording saved to: {filename}")
            
            # Stop the test
            self.vv.StopTest()
            logger.info("Test stopped")
            
            # Verify recording file
            assert os.path.exists(filename), f"Recording file not found: {filename}"
            file_size = os.path.getsize(filename)
            logger.info(f"Recording file size: {file_size} bytes")
            assert file_size > 0, "Recording file is empty"
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in recording with test running: {error_info}")
            pytest.fail(f"Error in recording with test running: {error_info}")
            
            # Ensure test is stopped if an error occurs
            try:
                if self.vv.IsRunning():
                    self.vv.StopTest()
                    logger.info("Test stopped after error")
            except:
                pass
    
    @pytest.mark.recording
    def test_recording_filename(self):
        """Test recording with custom filename"""
        try:
            # Create a data directory if it doesn't exist
            data_dir = os.path.join(self.script_dir, '..', 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                logger.info(f"Created data directory: {data_dir}")
            
            # Start recording
            logger.info("Starting recording with to test saving to filename")
            self.vv.RecordStart()
            
            # Record for a short time
            time.sleep(2)
            logger.info("Recording for 2 seconds")
            
            # Stop recording
            self.vv.RecordStop()
            logger.info("Recording stopped")
            
            # Get the actual filename used
            actual_filename = self.vv.RecordGetFilename()
            assert actual_filename is not None
            logger.info(f"Actual recording filename: {actual_filename}")
            
            # Verify the file exists
            assert os.path.exists(actual_filename), f"Recording file not found: {actual_filename}"
            file_size = os.path.getsize(actual_filename)
            logger.info(f"Recording file size: {file_size} bytes")
            
            actual_textfilename = GenerateTXTFromVV(actual_filename,'test.txt')
            assert actual_textfilename is not None
            logger.info(f"Actual text filename: {actual_textfilename}")
            txtfile_size = os.path.getsize(actual_textfilename)
            logger.info(f"Text file size: {txtfile_size} bytes")

            actual_UFFfilename = GenerateUFFFromVV(actual_filename,'test.uff')
            assert actual_UFFfilename is not None
            logger.info(f"Actual UFF filename: {actual_UFFfilename}")
            ufffile_size = os.path.getsize(actual_UFFfilename)
            logger.info(f"UFF file size: {ufffile_size} bytes")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in recording with custom filename: {error_info}")
            pytest.fail(f"Error in recording with custom filename: {error_info}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("vibrationview_recording_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("="*80)
    print("VibrationVIEW Recording Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_recording.py -v")
    print("="*80)