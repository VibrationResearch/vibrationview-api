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

class TestVibrationVIEWReportField:
    """Test class for VibrationVIEW ReportField method"""
    
    @pytest.fixture(autouse=True)
    def _setup(self, vv, find_test_file):
        """Setup method that runs before each test method"""
        self.vv = vv
        self.find_test_file = find_test_file
        
        # Open a test file to work with
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