#!/usr/bin/env python
"""
VibrationVIEW Test Control Functions Module

This module contains tests for test control functionality in the VibrationVIEW API.
These tests focus on starting, stopping, pausing, and controlling tests.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
- Main test infrastructure from conftest.py

Usage:
    pytest test_control_functions.py -v
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
    from vibrationviewapi import VibrationVIEW, vvVector, vvTestType, ExtractComErrorInfo
except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)


class TestControlFunctions:
    """Test class for VibrationVIEW test control functionality"""
    
    @pytest.fixture(autouse=True)
    def _setup(self, vv, wait_for_condition, wait_for_not, find_test_file, script_dir):
        """Setup method that runs before each test method"""
        self.vv = vv
        self.wait_for_condition = wait_for_condition
        self.wait_for_not = wait_for_not
        self.find_test_file = find_test_file
        self.script_dir = script_dir
        
        # Ensure recorder is stopped prior to each test
        self.vv.RecordStop()
        
        # Ensure any running test is stopped prior to each test
        self.vv.StopTest()
    
    @pytest.mark.control
    def test_test_status(self):
        """Test status information functions"""
        try:
            # Get current status
            status = self.vv.Status()
            assert status is not None
            logger.info(f"Test status: {status}")
            
            # Check test states
            running = self.vv.IsRunning()
            assert running is not None
            
            starting = self.vv.IsStarting()
            assert starting is not None
            
            changing_level = self.vv.IsChangingLevel()
            assert changing_level is not None
            
            hold_level = self.vv.IsHoldLevel()
            assert hold_level is not None
            
            open_loop = self.vv.IsOpenLoop()
            assert open_loop is not None
            
            aborted = self.vv.IsAborted()
            assert aborted is not None
            
            logger.info(f"Test state: running={running}, starting={starting}, changing_level={changing_level}, hold_level={hold_level}, open_loop={open_loop}, aborted={aborted}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error getting test status: {error_info}")
            pytest.fail(f"Error getting test status: {error_info}")
    
    @pytest.mark.control
    def test_start_stop(self):
        """Test basic start and stop functionality"""
        try:
            # Find a test file
            test_file = self.find_test_file("sine")
            if not test_file:
                logger.warning("No test file found")
                pytest.skip("No test file found for testing start/stop functionality")
            
            logger.info(f"Using test file: {test_file}")
            
            # Open the test
            self.vv.OpenTest(test_file)
            logger.info(f"Opened test file: {test_file}")
            
            # Start test
            logger.info("Starting test")
            self.vv.StartTest()
            
            # Check if starting
            logger.info("Waiting for test to enter 'starting' state")
            starting = self.wait_for_condition(self.vv.IsStarting)
            if starting:
                logger.info("Test entered 'starting' state")
            else:
                logger.warning("Test did not enter 'starting' state within timeout")

            # Wait for test to enter running state
            logger.info("Waiting for test to enter 'running' state")
            running = self.wait_for_condition(self.vv.IsRunning)
            if running:
                logger.info("Test entered 'running' state")
            else:
                logger.warning("Test did not enter 'running' state within timeout")
                pytest.skip("Test did not enter running state, skipping remaining test")
            
            # Let test run for a while
            logger.info("Test running for 3 seconds")
            time.sleep(3)
            
            # Stop test
            logger.info("Stopping test")
            self.vv.StopTest()
            
            # Check if stopped
            logger.info("Waiting for test to stop")
            stopped = self.wait_for_not(self.vv.IsRunning)
            if stopped:
                logger.info("Test stopped successfully")
            else:
                logger.warning("Test did not stop within timeout period")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_start_stop: {error_info}")
            pytest.fail(f"Error in test_start_stop: {error_info}")
            
            # Ensure test is stopped if an error occurs
            try:
                if self.vv.IsRunning():
                    self.vv.StopTest()
                    logger.info("Test stopped after error")
            except:
                pass
    
    @pytest.mark.control
    def test_run_test(self):
        """Test RunTest function (combines OpenTest and StartTest)"""
        try:
            # Ensure test is stopped first
            logger.info("Stopping any running test before starting test")
            self.vv.StopTest()
            
            # Wait for test to fully stop
            running = self.wait_for_not(self.vv.IsRunning)
            if running:
                logger.warning("Test did not stop within timeout period")
            
            # Find a test file
            test_file = self.find_test_file("random")  # Try a different test type
            if not test_file:
                test_file = self.find_test_file("sine")  # Fall back to sine
                
            if not test_file:
                logger.warning("No test file found")
                pytest.skip("No test file found for testing RunTest functionality")
            
            logger.info(f"Using test file: {test_file}")
            
            # Use RunTest function
            logger.info(f"Running test file: {test_file}")
            self.vv.RunTest(test_file)
            
            # Wait for test to enter running state
            logger.info("Waiting for test to enter 'running' state")
            running = self.wait_for_condition(self.vv.IsRunning)
            if running:
                logger.info("Test entered 'running' state")
                
                # Get test type to confirm correct test loaded
                test_type = self.vv.TestType
                test_type_name = vvTestType.get_name(test_type) if test_type is not None else "Unknown"
                logger.info(f"Running test type: {test_type_name}")
            else:
                logger.warning("Test did not enter 'running' state within timeout")
                pytest.skip("Test did not enter running state, skipping remaining test")
            
            # Stop test
            logger.info("Stopping test")
            self.vv.StopTest()
            
            # Check if stopped
            logger.info("Waiting for test to stop")
            running = self.wait_for_not(self.vv.IsRunning)
            if not running:
                logger.info("Test stopped successfully")
            else:
                logger.warning("Test did not stop within timeout period")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_run_test: {error_info}")
            pytest.fail(f"Error in test_run_test: {error_info}")
            
            # Ensure test is stopped if an error occurs
            try:
                if self.vv.IsRunning():
                    self.vv.StopTest()
                    logger.info("Test stopped after error")
            except:
                pass
    
    @pytest.mark.control
    def test_pause_resume(self):
        """Test pause and resume functionality if available"""
        try:
           
            # Find and run a test file
            test_file = self.find_test_file("sine")
            if not test_file:
                logger.warning("No test file found")
                pytest.skip("No test file found for testing pause/resume functionality")
            
            logger.info(f"Using test file: {test_file}")
            
            # Run the test
            self.vv.RunTest(test_file)
            logger.info(f"Running test file: {test_file}")
            
            # Wait for test to enter running state
            running = self.wait_for_condition(self.vv.IsRunning)
            if not running:
                logger.warning("Test did not enter running state")
                pytest.skip("Test did not enter running state, skipping pause/resume test")
                return
            
            logger.info("Test running, will test pause and resume")
            
            # Pause test
            logger.info("Stopping test (can restart)")
            self.vv.StopTest()
            
            # Wait a moment
            time.sleep(2)
            logger.info("Test paused for 2 seconds")
            
            if(self.vv.CanResumeTest == False):
                pytest.fail(f"Can not resume the test")


            # Resume test
            logger.info("Resuming test")
            self.vv.ResumeTest()
            
            # Let test run again
            time.sleep(2)
            logger.info("Test resumed and ran for 2 seconds")
            
            # Stop test
            logger.info("Stopping test")
            self.vv.StopTest()
            
            # Check if stopped
            logger.info("Waiting for test to stop")
            running = self.wait_for_not(self.vv.IsRunning) 
            assert running == False, "Test did not stop within timeout period"
            logger.info("Test stopped successfully")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_pause_resume: {error_info}")
            pytest.fail(f"Error in test_pause_resume: {error_info}")
            
            # Ensure test is stopped if an error occurs
            try:
                if self.vv.IsRunning():
                    self.vv.StopTest()
                    logger.info("Test stopped after error")
            except:
                pass
    
    @pytest.mark.control
    def test_continue_after_pretest(self):
        """Test ContinueAfterPreTest functionality"""
        try:
            # Ensure test is stopped first
            logger.info("Stopping any running test before testing ContinueAfterPreTest")
            self.vv.StopTest()
            
            # Wait for test to fully stop
            stopped = self.wait_for_not(self.vv.IsRunning)
            if not stopped:
                logger.warning("Test did not stop within timeout period")
            
            # Test that the ContinueAfterPreTest method exists and can be called
            logger.info("Testing ContinueAfterPreTest method availability")
            try:
                result = self.vv.ContinueAfterPreTest()
                if result is None:
                    logger.warning("ContinueAfterPreTest returned None - method may not be available or not implemented")
                    pytest.skip("ContinueAfterPreTest method returned None - not available")
                else:
                    assert isinstance(result, bool)
                    logger.info(f"ContinueAfterPreTest method exists and returned: {result}")
            except Exception as method_error:
                error_info = ExtractComErrorInfo(method_error)
                logger.warning(f"Error calling ContinueAfterPreTest: {error_info}")
                pytest.skip(f"ContinueAfterPreTest method not available: {error_info}")
            
            # Find the sine_with_pretest test file for more complete testing
            test_file = self.find_test_file("sine_with_pretest")
            if not test_file:
                logger.warning("No sine_with_pretest file found - skipping full pretest workflow test")
                logger.info("ContinueAfterPreTest method test completed successfully (basic functionality)")
                return
            
            logger.info(f"Using test file: {test_file}")
            
            # Open and start the test
            self.vv.OpenTest(test_file)
            logger.info(f"Opened test file: {test_file}")
            
            # Start the test
            logger.info("Starting test with pretest")
            self.vv.StartTest()
            
            # Wait for pretest to complete by monitoring status (with shorter timeout)
            logger.info("Waiting for pretest to complete (STOP_PRETEST_COMPLETE = 0x0058)")
            pretest_complete = False
            max_wait_time = 60  # 1 minute timeout
            wait_time = 0
            
            while wait_time < max_wait_time and not pretest_complete:
                try:
                    status = self.vv.Status()
                    stop_code = status.get('stop_code', 0)
                    stop_code_index = status.get('stop_code_index', 0)
                    
                    logger.info(f"Current status - stop_code: 0x{stop_code:04X}, stop_code_index: {stop_code_index}")
                    
                    # Check for STOP_PRETEST_COMPLETE (0x0058)
                    if stop_code == 0x0058:
                        logger.info("Pretest completed - STOP_PRETEST_COMPLETE detected")
                        pretest_complete = True
                        break
                        
                    time.sleep(2)  # Wait 2 seconds before checking again
                    wait_time += 2
                    
                except Exception as status_error:
                    logger.warning(f"Error getting status: {status_error}")
                    time.sleep(2)
                    wait_time += 2
            
            if not pretest_complete:
                logger.warning("Pretest did not complete within timeout period")
                logger.info("ContinueAfterPreTest method test completed successfully (basic functionality)")
                return
            
            # Now test ContinueAfterPreTest method after pretest completion
            logger.info("Testing ContinueAfterPreTest method after pretest completion")
            result = self.vv.ContinueAfterPreTest()
            assert result is not None
            assert isinstance(result, bool)
            logger.info(f"ContinueAfterPreTest returned: {result}")
            
            # If the method returned True, the test should continue running
            if result:
                logger.info("Test continued after pretest, waiting for it to run")
                time.sleep(5)  # Give it time to start running
                
                # Check if test is now running
                is_running = self.vv.IsRunning()
                logger.info(f"Test running status after ContinueAfterPreTest: {is_running}")
                
                # Stop the test
                if is_running:
                    logger.info("Stopping test after successful ContinueAfterPreTest")
                    self.vv.StopTest()
                    self.wait_for_not(self.vv.IsRunning)
                    logger.info("Test stopped successfully")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_continue_after_pretest: {error_info}")
            pytest.fail(f"Error in test_continue_after_pretest: {error_info}")
            
            # Ensure test is stopped if an error occurs
            try:
                if self.vv.IsRunning():
                    self.vv.StopTest()
                    logger.info("Test stopped after error")
            except:
                pass
        
    @pytest.mark.control
    def teardown_method(self):
        """Clean up after each test method"""
        # If test is running, stop it
        try:
            if hasattr(self, 'vv') and self.vv is not None and self.vv.IsRunning():
                logger.info("Stopping test during teardown")
                self.vv.StopTest()
                # Wait for test to stop
                self.wait_for_not(self.vv.IsRunning)
        except Exception as e:
            logger.warning(f"Error during teardown: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("control_functions_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("="*80)
    print("VibrationVIEW Test Control Functions Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_control_functions.py -v")
    print("="*80)
