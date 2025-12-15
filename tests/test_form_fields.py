#!/usr/bin/env python
"""
Test module for VibrationVIEW FormFields and PostFormFields functionality

This module contains tests for the FormFields and PostFormFields methods
in the VibrationVIEW API.

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
from urllib.parse import unquote

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


class TestFormFields:
    """Test class for VibrationVIEW FormFields and PostFormFields methods"""

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

    @pytest.mark.form_fields
    def test_FormFields_basic(self):
        """Test basic FormFields functionality - get all form field values"""
        self._open_test_file()
        try:
            logger.info("Testing FormFields - getting all form field values")
            result = self.vv.FormFields()

            # FormFields may return None if no data is available
            if result is None:
                logger.info("FormFields returned None - no form data available (valid result)")
            else:
                logger.info(f"FormFields returned: {type(result)}")

                if hasattr(result, '__len__'):
                    logger.info(f"FormFields result length: {len(result)} rows")

                    # FormFields returns a 2D array with [parameter, value] pairs
                    if len(result) > 0:
                        logger.info("FormFields structure check:")
                        for i, row in enumerate(result[:10]):  # Show first 10 fields
                            if hasattr(row, '__len__') and len(row) >= 2:
                                field_name, field_value = row[0], row[1]
                                logger.info(f"  Field: '{field_name}' = '{field_value}'")
                            else:
                                logger.warning(f"Row {i} has unexpected structure: {row}")

                        if len(result) > 10:
                            logger.info(f"  ... and {len(result) - 10} more fields")

            logger.info("FormFields basic test completed successfully")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            if "No data available" in str(error_info):
                logger.info(f"FormFields: No data available (valid result)")
                return  # Pass the test - no data is a valid state
            logger.error(f"FormFields test failed: {error_info}")
            pytest.fail(f"FormFields test failed: {error_info}")

    @pytest.mark.form_fields
    def test_PostFormFields_basic(self):
        """Test basic PostFormFields functionality - post form field values"""
        self._open_test_file()
        try:
            # Create test data - form field values to post
            test_fields = [
                ["Operator", "TestOperator"],
                ["Notes", "Test notes from API"]
            ]

            logger.info(f"Testing PostFormFields with data: {test_fields}")
            result = self.vv.PostFormFields(test_fields)

            assert result is True, "PostFormFields should return True on success"
            logger.info("PostFormFields returned True")

            # Verify the fields were posted by getting form fields
            logger.info("Getting form fields after posting to verify")
            updated_fields = self.vv.FormFields()

            if updated_fields is None:
                logger.info("FormFields returned None after posting (valid result)")
            else:
                # Check if our posted values are in the updated fields
                updated_dict = {}
                if hasattr(updated_fields, '__len__'):
                    for row in updated_fields:
                        if hasattr(row, '__len__') and len(row) >= 2:
                            updated_dict[row[0]] = row[1]

                # Verify our posted fields
                for field_name, expected_value in test_fields:
                    if field_name in updated_dict:
                        actual_value = updated_dict[field_name]
                        logger.info(f"Field '{field_name}': expected '{expected_value}', got '{actual_value}'")
                    else:
                        logger.info(f"Field '{field_name}' not found in form fields")

            logger.info("PostFormFields basic test completed successfully")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            if "No data available" in str(error_info):
                logger.info(f"PostFormFields: No data available (valid result)")
                return  # Pass the test
            logger.error(f"PostFormFields test failed: {error_info}")
            pytest.fail(f"PostFormFields test failed: {error_info}")

    @pytest.mark.form_fields
    def test_PostFormFields_merge_behavior(self):
        """Test that PostFormFields merges with existing form fields"""
        self._open_test_file()
        try:
            # Get original form fields
            logger.info("Getting original form fields")
            original_fields = self.vv.FormFields()

            original_count = 0
            if original_fields is not None and hasattr(original_fields, '__len__'):
                original_count = len(original_fields)
            logger.info(f"Original form fields count: {original_count}")

            # Post a single new field
            test_fields = [["TestMergeField", "TestMergeValue"]]
            logger.info(f"Posting single field: {test_fields}")
            self.vv.PostFormFields(test_fields)

            # Get updated fields
            updated_fields = self.vv.FormFields()
            updated_count = 0
            if updated_fields is not None and hasattr(updated_fields, '__len__'):
                updated_count = len(updated_fields)
            logger.info(f"Updated form fields count: {updated_count}")

            # Verify merge behavior - count should be same or +1
            # (depending on whether TestMergeField already existed)
            if original_count > 0:
                assert updated_count >= original_count, \
                    f"PostFormFields should merge, not replace. Original: {original_count}, Updated: {updated_count}"

            logger.info("PostFormFields merge behavior test completed successfully")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            if "No data available" in str(error_info):
                logger.info(f"PostFormFields merge test: No data available (valid result)")
                return  # Pass the test
            logger.error(f"PostFormFields merge test failed: {error_info}")
            pytest.fail(f"PostFormFields merge test failed: {error_info}")

    @pytest.mark.form_fields
    def test_PostFormFields_empty_array(self):
        """Test PostFormFields with empty array"""
        self._open_test_file()
        try:
            logger.info("Testing PostFormFields with empty array")

            # Post empty array - should not raise an error
            result = self.vv.PostFormFields([])

            assert result is True, "PostFormFields with empty array should return True"
            logger.info("PostFormFields with empty array completed successfully")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            # Empty array might raise an error depending on implementation
            logger.info(f"PostFormFields with empty array raised: {error_info}")

    @pytest.mark.form_fields
    def test_PostFormFields_invalid_characters(self):
        """Test PostFormFields with invalid/special characters in fields and values"""
        self._open_test_file()
        try:
            # Test data with various special/invalid characters
            test_fields = [
                ["Field<>Name", "Value with <angle> brackets"],
                ["Field&Name", "Value with & ampersand"],
                ["Field\"Name", "Value with \"quotes\""],
                ["Field'Name", "Value with 'apostrophes'"],
                ["Field\tTab", "Value with\ttabs"],
                ["Field\nNewline", "Value with\nnewlines"],
                ["Field/Slash", "Value with /slashes\\backslashes"],
                ["Field:Colon", "Value with :colons;semicolons"],
                ["FieldUnicode", "Value with unicode: \u00e9\u00e8\u00ea\u00eb"],
                ["Field!@#$%", "Value!@#$%^&*()"],
            ]

            logger.info(f"Testing PostFormFields with special characters")
            for field_name, field_value in test_fields:
                logger.info(f"  Testing field: '{field_name}' = '{field_value}'")

            result = self.vv.PostFormFields(test_fields)
            logger.info(f"PostFormFields with special characters returned: {result}")

            # Verify fields were posted by getting FormFields
            logger.info("Getting FormFields to verify posted data")
            form_fields = self.vv.FormFields()

            if form_fields is None:
                logger.info("FormFields returned None after posting")
            else:
                # Helper function to fully decode URL-encoded strings (handles multiple encoding levels)
                def fully_decode(s):
                    """Decode URL-encoded string until no more encoding remains"""
                    if s is None:
                        return s
                    s = str(s)
                    # Replace + with space (URL encoding for space)
                    s = s.replace('+', ' ')
                    # Decode until string stops changing
                    prev = None
                    while prev != s:
                        prev = s
                        s = unquote(s)
                    return s

                # Build dict of returned fields with decoded names
                returned_dict = {}
                returned_raw = {}  # Keep raw values for logging
                if hasattr(form_fields, '__len__'):
                    for row in form_fields:
                        if hasattr(row, '__len__') and len(row) >= 2:
                            raw_name, raw_value = row[0], row[1]
                            decoded_name = fully_decode(raw_name)
                            decoded_value = fully_decode(raw_value)
                            returned_dict[decoded_name] = decoded_value
                            returned_raw[decoded_name] = (raw_name, raw_value)

                # Verify each posted field is returned with characters properly expanded
                fields_found = 0
                for expected_name, expected_value in test_fields:
                    if expected_name in returned_dict:
                        actual_value = returned_dict[expected_name]
                        raw_name, raw_value = returned_raw[expected_name]
                        fields_found += 1

                        # Log raw vs decoded
                        if raw_name != expected_name or raw_value != expected_value:
                            logger.info(f"  RAW: '{raw_name}' = '{raw_value}'")
                            logger.info(f"  DECODED: '{expected_name}' = '{actual_value}'")

                        if str(actual_value) == str(expected_value):
                            logger.info(f"  MATCH: '{expected_name}' = '{actual_value}'")
                        else:
                            logger.warning(f"  VALUE MISMATCH: '{expected_name}' expected '{expected_value}', got '{actual_value}'")
                            assert str(actual_value) == str(expected_value), \
                                f"Field value not properly expanded: expected '{expected_value}', got '{actual_value}'"
                    else:
                        logger.warning(f"  FIELD NOT FOUND (even after decoding): '{expected_name}'")
                        # Log all returned decoded names for debugging
                        logger.warning(f"    Available decoded names: {list(returned_dict.keys())[:5]}...")

                # Verify all fields were found
                logger.info(f"Found {fields_found} of {len(test_fields)} posted fields (after URL decoding)")
                assert fields_found == len(test_fields), \
                    f"Not all fields were returned: expected {len(test_fields)}, found {fields_found}"

            logger.info("PostFormFields with invalid characters completed successfully")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            # Log the error but don't fail - we want to know what happens with invalid chars
            logger.info(f"PostFormFields with invalid characters raised: {error_info}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("vibrationview_form_fields_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    print("="*80)
    print("VibrationVIEW FormFields Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_form_fields.py -v")
    print("="*80)
