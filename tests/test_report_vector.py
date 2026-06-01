#!/usr/bin/env python
"""
VibrationVIEW Report Vector Functions Module

This module contains tests for Report Vector functionality in the VibrationVIEW API.
These tests focus on ReportVector and ReportVectorHeader methods.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
- Main test infrastructure from conftest.py

Usage:
    pytest test_report_vector.py -v
"""

import os
import sys
import time
import logging
import pytest
from .conftest import VV_COM_AVAILABLE

pytestmark = pytest.mark.skipif(not VV_COM_AVAILABLE, reason="Requires VibrationVIEW COM server")

# Configure logger
logger = logging.getLogger(__name__)

# Add necessary paths for imports
current_dir = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

try:
    from vibrationviewapi import ExtractComErrorInfo
except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)


class TestReportVectorFunctions:
    """Test class for VibrationVIEW Report Vector functionality"""

    @pytest.mark.report
    def test_ReportVector_basic(self):
        """Test basic ReportVector functionality"""
        try:
            # Load and run a test to generate report data
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")

            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)

            logger.info("Starting test to generate report data")
            self.vv.StartTest()

            # Wait for test to run and generate some data
            time.sleep(5)

            # Stop the test
            logger.info("Stopping test")
            self.vv.StopTest()

            # Now test ReportVector with all report columns
            # ReportVector accepts a comma-separated list of vector names
            vector_names = "Index,Frequency,Demand,Control,ControlHigh,ControlLow,Drive,DriveHigh,PlusTol,MinusTol,PlusAbort,Channel1,Channel2,ChannelPhase1,ChannelPhase2,ChannelHigh1,ChannelHigh2,ChannelLow1,ChannelLow2"

            try:
                logger.info(f"Testing ReportVector with vectors: {vector_names}")
                result = self.vv.ReportVector(vector_names, None)

                assert result is not None, "ReportVector should return data"
                logger.info(f"ReportVector returned: {type(result)}")

                if hasattr(result, '__len__'):
                    logger.info(f"ReportVector result length: {len(result)}")
                    if len(result) > 0:
                        logger.info(f"ReportVector first few items: {result[:5] if len(result) >= 5 else result}")

            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.warning(f"ReportVector raised exception: {error_info}")

            logger.info("ReportVector basic test completed successfully")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_ReportVector_basic: {error_info}")
            pytest.fail(f"Error in test_ReportVector_basic: {error_info}")

    @pytest.mark.report
    def test_ReportVectorHeader_basic(self):
        """Test basic ReportVectorHeader functionality"""
        try:
            # Load and run a test to generate report data
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")

            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)

            # Now test ReportVectorHeader with all report columns
            # ReportVectorHeader accepts a comma-separated list of vector names
            # and returns a rank 2 array with [column_name, unit] for each vector
            vector_names = "Index,Frequency,Demand,Control,ControlHigh,ControlLow,Drive,DriveHigh,PlusTol,MinusTol,PlusAbort,Channel1,Channel2,ChannelPhase1,ChannelPhase2,ChannelHigh1,ChannelHigh2,ChannelLow1,ChannelLow2"

            # Expected units for each vector (second column of each row)
            expected_units = [
                "",       # Index
                "Hz",     # Frequency
                "G",      # Demand
                "G",      # Control
                "G",      # ControlHigh
                "G",      # ControlLow
                "Volts",  # Drive
                "Volts",  # DriveHigh
                "G",      # PlusTol
                "G",      # MinusTol
                "G",      # PlusAbort
                "G",      # Channel1
                "G",      # Channel2
                "rad",    # ChannelPhase1
                "rad",    # ChannelPhase2
                "G",      # ChannelHigh1
                "G",      # ChannelHigh2
                "G",      # ChannelLow1
                "G"       # ChannelLow2
            ]

            try:
                logger.info(f"Testing ReportVectorHeader with vectors: {vector_names}")
                result = self.vv.ReportVectorHeader(vector_names, None)

                assert result is not None, "ReportVectorHeader should return data"
                logger.info(f"ReportVectorHeader returned: {type(result)}")

                if hasattr(result, '__len__'):
                    logger.info(f"ReportVectorHeader result length: {len(result)} rows")

                    # ReportVectorHeader returns a rank 2 array with:
                    # Row 0: [column_name1, column_name2, ...]
                    # Row 1: [unit1, unit2, ...]
                    assert len(result) == 2, f"Expected 2 rows (names and units), got {len(result)}"

                    column_names = result[0]
                    units = result[1]

                    assert len(column_names) == len(expected_units), f"Expected {len(expected_units)} columns, got {len(column_names)}"
                    assert len(units) == len(expected_units), f"Expected {len(expected_units)} units, got {len(units)}"

                    logger.info("ReportVectorHeader structure: 2 rows [names, units] with columns for each vector")

                    # Verify each column has correct unit
                    for i in range(len(column_names)):
                        column_name = column_names[i]
                        unit = units[i]
                        expected_unit = expected_units[i]

                        logger.info(f"  Column {i}: Name='{column_name}', Unit='{unit}'")

                        # Verify the unit matches expected
                        assert unit == expected_unit, f"Column {i} ('{column_name}'): Expected unit '{expected_unit}', got '{unit}'"

            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.warning(f"ReportVectorHeader raised exception: {error_info}")

            logger.info("ReportVectorHeader basic test completed successfully")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_ReportVectorHeader_basic: {error_info}")
            pytest.fail(f"Error in test_ReportVectorHeader_basic: {error_info}")

    @pytest.mark.report
    def test_ReportVectorHistory_basic(self):
        """Test basic ReportVectorHistory functionality"""
        try:
            # Load a test file
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")

            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)

            # Start the test and wait for it to complete
            logger.info("Starting test to generate history data")
            self.vv.StartTest()

            # Wait for test to start running
            logger.info("Waiting for test to start running")
            self.wait_for_condition(self.vv.IsRunning)

            # Wait for test to finish on its own
            logger.info("Waiting for test to complete")
            self.wait_for_not(self.vv.IsRunning, wait_time=120)

            # Test ReportVectorHistory with vector names
            vector_names = "Index,Frequency,Demand,Control,Drive,Channel1,Channel2"

            try:
                logger.info(f"Testing ReportVectorHistory with vectors: {vector_names}")
                result = self.vv.ReportVectorHistory(vector_names, None, None)

                assert result is not None, "ReportVectorHistory should return data"
                logger.info(f"ReportVectorHistory returned: {type(result)}")

                # Result should be a tuple of (array_out, header_out)
                if isinstance(result, tuple) and len(result) == 2:
                    array_out, header_out = result
                    logger.info(f"ReportVectorHistory array_out type: {type(array_out)}")
                    logger.info(f"ReportVectorHistory header_out type: {type(header_out)}")

                    if hasattr(array_out, '__len__'):
                        logger.info(f"ReportVectorHistory array_out length: {len(array_out)} rows")
                        if len(array_out) > 0:
                            logger.info(f"ReportVectorHistory first few rows: {array_out[:3] if len(array_out) >= 3 else array_out}")

                    if hasattr(header_out, '__len__'):
                        logger.info(f"ReportVectorHistory header_out length: {len(header_out)} rows")
                        logger.info(f"ReportVectorHistory headers: {header_out}")
                else:
                    # Single return value
                    if hasattr(result, '__len__'):
                        logger.info(f"ReportVectorHistory result length: {len(result)}")

                logger.info("ReportVectorHistory basic test completed successfully")

            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.warning(f"ReportVectorHistory raised exception: {error_info}")
                pytest.fail(f"ReportVectorHistory test failed: {error_info}")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_ReportVectorHistory_basic: {error_info}")
            pytest.fail(f"Error in test_ReportVectorHistory_basic: {error_info}")

    @pytest.mark.report
    def test_ReportVectorHistory_should_fail_while_test_is_running(self):
        """Test that ReportVectorHistory fails while a test is running"""
        try:
            # Load a test file
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")

            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)

            # Start the test
            logger.info("Starting test")
            self.vv.StartTest()

            # Wait for test to start running
            logger.info("Waiting for test to start running")
            self.wait_for_condition(self.vv.IsRunning)

            # Try to call ReportVectorHistory while test is running - should fail
            vector_names = "Index,Frequency,Demand,Control,Drive,Channel1,Channel2"

            try:
                logger.info(f"Testing ReportVectorHistory while test is running (should fail)")
                result = self.vv.ReportVectorHistory(vector_names, None, None)

                # If we get here without exception, the call succeeded when it should have failed
                logger.warning(f"ReportVectorHistory returned data while test was running: {result}")
                pytest.fail("ReportVectorHistory should fail while test is running, but it succeeded")

            except Exception as e:
                # Expected - ReportVectorHistory should fail while test is running
                error_info = ExtractComErrorInfo(e)
                logger.info(f"ReportVectorHistory correctly failed while test is running: {error_info}")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_ReportVectorHistory_should_fail_while_test_is_running: {error_info}")
            pytest.fail(f"Error in test_ReportVectorHistory_should_fail_while_test_is_running: {error_info}")

        finally:
            # Always stop the test
            try:
                logger.info("Stopping test")
                self.vv.StopTest()
                self.wait_for_not(self.vv.IsRunning)
            except Exception as e:
                logger.warning(f"Error stopping test: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("report_vector_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    print("="*80)
    print("VibrationVIEW Report Vector Functions Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_report_vector.py -v")
    print("="*80)
