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

import logging
import os
import sys
import time

import pytest

# Configure logger
logger = logging.getLogger(__name__)

# Add necessary paths for imports
current_dir = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

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


class TestControlFunctions:
    """Test class for VibrationVIEW test control functionality"""

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
            running = self.wait_for_not(self.vv.IsRunning, wait_time=5)
            if running:
                logger.warning("Test did not stop within timeout period")
            else:
                logger.info("Test stopped successfully")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_start_stop: {error_info}")
            pytest.fail(f"Error in test_start_stop: {error_info}")

            # Ensure test is stopped if an error occurs
            try:
                if self.vv.IsRunning():
                    self.vv.StopTest()
                    logger.info("Test stopped after error")
            except Exception:
                pass

    @pytest.mark.control
    def test_run_test(self):
        """Test RunTest function (combines OpenTest and StartTest)"""
        try:
            # Ensure test is stopped first
            logger.info("Stopping any running test before starting test")
            self.vv.StopTest()

            # Wait for test to fully stop
            running = self.wait_for_not(self.vv.IsRunning, wait_time=5)
            if running:
                logger.warning("Test did not stop within timeout period")
            else:
                logger.info("Test stopped successfully")

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
            running = self.wait_for_not(self.vv.IsRunning, wait_time=5)
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
            except Exception:
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

            if(not self.vv.CanResumeTest):
                pytest.fail("Can not resume the test")


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
            running = self.wait_for_not(self.vv.IsRunning, wait_time=5)
            assert not running, "Test did not stop within timeout period"
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
            except Exception:
                pass

    @pytest.mark.control
    def test_is_demonstration_mode(self):
        """Test ReportField functionality for BoxSerialNumber1"""
        try:
            # Test that the ReportField method exists and can be called
            logger.info("Testing ReportField method for BoxSerialNumber1")

            box_serial = self.vv.ReportField("BoxSerialNumber1")
            assert box_serial is not None
            logger.info(f"BoxSerialNumber1: {box_serial}")

            # Check if it contains "Demonstration"
            if "Demonstration" not in box_serial:
                logger.warning(f"BoxSerialNumber1 does not contain 'Demonstration': {box_serial}")
                pytest.skip("Not in demonstration mode - tests using StartTest, RunTest may fail")
            logger.info("BoxSerialNumber1 contains 'Demonstration' as expected")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_is_demonstration_mode: {error_info}")
            pytest.fail(f"Error in test_is_demonstration_mode: {error_info}")

    @pytest.mark.control
    def test_edit_and_abort_edit(self):
        """Test EditTest and AbortEdit functionality"""
        try:
            # Find a test file
            test_file = self.find_test_file("sine")
            if not test_file:
                logger.warning("No test file found")
                pytest.skip("No test file found for testing EditTest/AbortEdit")

            logger.info(f"Using test file: {test_file}")

            # Open the test in edit mode
            self.vv.EditTest(test_file)
            logger.info("EditTest called successfully")

            # Abort the edit
            self.vv.AbortEdit()
            logger.info("AbortEdit called successfully")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_edit_and_abort_edit: {error_info}")
            pytest.fail(f"Error in test_edit_and_abort_edit: {error_info}")

    @pytest.mark.control
    def test_can_resume_test(self):
        """Test CanResumeTest functionality"""
        try:
            can_resume = self.vv.CanResumeTest()
            logger.info(f"CanResumeTest returned: {can_resume}")
            assert can_resume is not None, "CanResumeTest should return a boolean value"
            assert isinstance(can_resume, bool), f"CanResumeTest should return bool, but returned {type(can_resume)}"
            logger.info(f"CanResumeTest succeeded: {can_resume}")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_can_resume_test: {error_info}")
            pytest.fail(f"Error in test_can_resume_test: {error_info}")

    @pytest.mark.control
    def test_resume_test(self):
        """Test ResumeTest functionality"""
        try:
            # Find a test file
            test_file = self.find_test_file("sine")
            if not test_file:
                logger.warning("No test file found")
                pytest.skip("No test file found for testing ResumeTest")

            logger.info(f"Using test file: {test_file}")

            # Open the test
            self.vv.OpenTest(test_file)
            logger.info("Opened test file")

            # Start the test
            self.vv.StartTest()
            logger.info("Started test")

            # Wait for test to be running
            running = self.wait_for_condition(self.vv.IsRunning, wait_time=10)
            if not running:
                pytest.fail("Test did not start running")

            logger.info("Test is running")

            # Wait a moment
            time.sleep(7)

            # Stop the test
            self.vv.StopTest()
            logger.info("Stopped test")

            # Wait for test to stop
            running = self.wait_for_not(self.vv.IsRunning, wait_time=5)
            if running:
                logger.warning("Test did not stop in expected time")
            else:
                logger.info("Test stopped successfully")

            # Wait a moment
            time.sleep(1)

            # Check if test can be resumed
            can_resume = self.vv.CanResumeTest()
            logger.info(f"CanResumeTest returned: {can_resume}")

            if not can_resume:
                logger.info("Test cannot be resumed after stopping")
                pytest.skip("Test cannot be resumed after stopping")

            # Resume the test
            self.vv.ResumeTest()
            logger.info("ResumeTest called successfully")

            # Wait a moment
            time.sleep(1)

            # Stop the test again
            if self.vv.IsRunning():
                self.vv.StopTest()
                logger.info("Stopped test after resuming")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_resume_test: {error_info}")
            pytest.fail(f"Error in test_resume_test: {error_info}")

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
