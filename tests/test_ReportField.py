#!/usr/bin/env python
"""
Test module for VibrationVIEW ReportField functionality

This module contains tests for the ReportField method in the VibrationVIEW API,
which retrieves report values by field name.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
"""

import os
import sys
import time
import logging
import pytest

# Configure logger
logger = logging.getLogger(__name__)

# Add necessary paths for imports
current_dir = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

try:
    from vibrationviewapi import ExtractComErrorInfo
except ImportError:
    pytest.skip("Could not import VibrationVIEW API.", allow_module_level=True)

class TestVibrationVIEWReportField:
    """Test class for VibrationVIEW ReportField method"""

    def _open_test_file(self):
        """Helper method to open a test file"""
        test_file = self.find_test_file("sine")
        if not test_file:
            logger.warning("No sine test file found for testing")
            pytest.skip("No sine test file found for testing")

        try:
            self.vv.OpenTest(test_file)
            logger.info(f"Opened test file: {test_file}")
            self.test_file = test_file
        except Exception as e:
            logger.error(f"Error opening test file: {e}")
            pytest.skip(f"Error opening test file: {e}")
    
    
    def test_report_field_invalid(self):
        """Test ReportField method with invalid field name"""
        self._open_test_file()
        try:
            # Try to get a report field with an invalid name
            value = self.vv.ReportField("NonExistentField")
            
            # The method might return a default value or None for invalid fields
            logger.info(f"Report field 'NonExistentField' value: {value}")
            
            # Some implementations might return empty string or None for invalid fields
            # This test checks the behavior rather than asserting specific values
            if value is None or (isinstance(value, str) and value.strip() == ""):
                logger.info("Invalid field name returns None or empty string as expected")
            else:
                logger.warning(f"Invalid field name returned unexpected value: {value}")
            
        except Exception as e:
            # Some implementations might throw an exception for invalid fields
            logger.info(f"Invalid field name throws exception as expected: {e}")
    
    
    def test_multiple_report_fields(self):
        """Test retrieving multiple report fields in sequence"""
        self._open_test_file()
        fields_to_test = [
            "ChName1", 
            "ChAcp1", 
            "ChSensitivity1", 
            "ChCalDue1", 
            "StopCode"
        ]
        
        results = {}
        
        try:
            # Get values for multiple fields
            for field in fields_to_test:
                value = self.vv.ReportField(field)
                results[field] = value
                logger.info(f"Report field '{field}' value: {value}")
            
            # Verify that we got values for all fields
            assert len(results) == len(fields_to_test), f"Got {len(results)} results, expected {len(fields_to_test)}"
            
            # Verify that all fields returned non-None values
            for field, value in results.items():
                assert value is not None, f"Report field '{field}' returned None"
            
            logger.info("Successfully retrieved multiple report fields")

        except Exception as e:
            logger.error(f"Error getting multiple report fields: {e}")
            raise

    @pytest.mark.report
    def test_ReportFields_basic(self):
        """Test basic ReportFields functionality"""
        try:
            # Load a test file
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")

            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)

            # Test ReportFields with common report fields
            # ReportFields accepts a comma-separated list of field names
            # and returns a 2D array with [field_name, value] pairs
            field_names = "ChName1,ChAcp1,ChSensitivity1,StopCode,TestType"

            try:
                logger.info(f"Testing ReportFields with fields: {field_names}")
                result = self.vv.ReportFields(field_names, None)

                assert result is not None, "ReportFields should return data"
                logger.info(f"ReportFields returned: {type(result)}")

                if hasattr(result, '__len__'):
                    logger.info(f"ReportFields result length: {len(result)} rows")

                    # ReportFields returns a 2D array with [parameter, value] pairs
                    # Each row should have 2 elements: [field_name, field_value]
                    if len(result) > 0:
                        logger.info(f"ReportFields structure check:")
                        for i, row in enumerate(result):
                            if hasattr(row, '__len__'):
                                assert len(row) == 2, f"Row {i} should have 2 elements [field_name, value], got {len(row)}"
                                field_name, field_value = row
                                logger.info(f"  Field: '{field_name}' = '{field_value}'")
                            else:
                                logger.warning(f"Row {i} is not iterable: {row}")

                        # Verify we got the expected number of fields
                        expected_count = len(field_names.split(','))
                        assert len(result) == expected_count, f"Expected {expected_count} fields, got {len(result)}"

                logger.info("ReportFields basic test completed successfully")

            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.warning(f"ReportFields raised exception: {error_info}")
                pytest.fail(f"ReportFields test failed: {error_info}")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_ReportFields_basic: {error_info}")
            pytest.fail(f"Error in test_ReportFields_basic: {error_info}")

    @pytest.mark.report
    def test_ReportFieldsHistory_basic(self):
        """Test basic ReportFieldsHistory functionality"""
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

            # Test ReportFieldsHistory with common report fields
            # ReportFieldsHistory accepts a comma-separated list of field names
            # and returns a 2D array with [field_name, value1, value2, ...] rows
            # where each value column represents a history file
            field_names = "ChName1,ChAcp1,ChSensitivity1,StopCode,TestType,TestName"

            try:
                logger.info(f"Testing ReportFieldsHistory with fields: {field_names}")
                result = self.vv.ReportFieldsHistory(field_names, None)

                assert result is not None, "ReportFieldsHistory should return data"
                logger.info(f"ReportFieldsHistory returned: {type(result)}")

                if hasattr(result, '__len__'):
                    logger.info(f"ReportFieldsHistory result length: {len(result)} rows")

                    # ReportFieldsHistory returns a 2D array with [parameter, value1, value2, ...] rows
                    # Each row should have at least 1 element (field_name), plus values from history files
                    if len(result) > 0:
                        logger.info(f"ReportFieldsHistory structure check:")
                        for i, row in enumerate(result):
                            if hasattr(row, '__len__'):
                                assert len(row) >= 1, f"Row {i} should have at least 1 element [field_name, ...], got {len(row)}"
                                field_name = row[0]
                                values = row[1:] if len(row) > 1 else []
                                logger.info(f"  Field: '{field_name}' = {values}")
                            else:
                                logger.warning(f"Row {i} is not iterable: {row}")

                        # Verify we got the expected number of fields
                        expected_count = len(field_names.split(','))
                        assert len(result) == expected_count, f"Expected {expected_count} fields, got {len(result)}"

                logger.info("ReportFieldsHistory basic test completed successfully")

            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.warning(f"ReportFieldsHistory raised exception: {error_info}")
                pytest.fail(f"ReportFieldsHistory test failed: {error_info}")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_ReportFieldsHistory_basic: {error_info}")
            pytest.fail(f"Error in test_ReportFieldsHistory_basic: {error_info}")

    @pytest.mark.report
    def test_ReportFieldsHistory_should_fail_while_test_is_running(self):
        """Test that ReportFieldsHistory fails while a test is running"""
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

            # Try to call ReportFieldsHistory while test is running - should fail
            field_names = "ChName1,ChAcp1,ChSensitivity1,StopCode,TestType,TestName"

            try:
                logger.info(f"Testing ReportFieldsHistory while test is running (should fail)")
                result = self.vv.ReportFieldsHistory(field_names, None)

                # If we get here without exception, the call succeeded when it should have failed
                logger.warning(f"ReportFieldsHistory returned data while test was running: {result}")
                pytest.fail("ReportFieldsHistory should fail while test is running, but it succeeded")

            except Exception as e:
                # Expected - ReportFieldsHistory should fail while test is running
                error_info = ExtractComErrorInfo(e)
                logger.info(f"ReportFieldsHistory correctly failed while test is running: {error_info}")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_ReportFieldsHistory_should_fail_while_test_is_running: {error_info}")
            pytest.fail(f"Error in test_ReportFieldsHistory_should_fail_while_test_is_running: {error_info}")

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
            logging.FileHandler("vibrationview_report_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("="*80)
    print("VibrationVIEW ReportField Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_report_field.py -v")
    print("="*80)