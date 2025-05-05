#!/usr/bin/env python
"""
VibrationVIEW Data Acquisition Test Module

This module contains tests for data acquisition functionality in the VibrationVIEW API.
These tests focus on vector acquisition, vector properties, and data handling.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
- Main test infrastructure from test_VibrationviewAPI.py

Usage:
    pytest test_data_acquisition.py -v
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


class TestDataAcquisition:
    """Test class for VibrationVIEW data acquisition functionality"""
    
    @pytest.fixture(autouse=True)
    def _setup(self, vv, wait_for_condition, wait_for_not, find_test_file, script_dir):
        """Setup method that runs before each test method"""
        self.vv = vv
        self.wait_for_condition = wait_for_condition
        self.wait_for_not = wait_for_not
        self.find_test_file = find_test_file
        self.script_dir = script_dir
    
    @pytest.mark.data
    def test_data_acquisition_basic(self):
        """Test basic data acquisition functions"""
        try:
            # Use the fixture to find the sine test file
            sine_test = self.find_test_file("sine")
            if sine_test:
                try:
                    self.vv.RunTest(sine_test)
                    test_type = self.vv.TestType()
                    if test_type != vvTestType.TEST_SINE:
                        logger.warning("Not a SINE test")
                        pytest.skip("Could not run a sine test, vectors will have unexpected results")
                    logger.info(f"Running sine test: {sine_test}")
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Could not run sine test: {error_info}")
                    pytest.skip("Could not run a sine test, vectors will have unexpected results")
                
                # Wait up to 5 seconds for IsRunning
                logger.info("Waiting for test to start...")
                starting = self.wait_for_not(self.vv.IsStarting)
                running = self.wait_for_condition(self.vv.IsRunning)
                if running:
                    logger.info("Test running, holding sweep")
                    self.vv.SweepHold()
                else:
                    logger.warning("Test did not enter running state")

            vectors_tested = 0
            for vector_name in ["WAVEFORMAXIS", "FREQUENCYAXIS", "TIMEHISTORYAXIS"]:
                vector_enum = getattr(vvVector, vector_name)
                logger.info(f"Testing vector: {vector_name}")
                try:
                    # Get vector length
                    length = self.vv.VectorLength(vector_enum)
                    assert length is not None
                    logger.info(f"{vector_name} length: {length}")
                    
                    # Get vector data
                    inputs = self.vv.GetHardwareInputChannels()
                    data = self.vv.Vector(vector_enum, inputs + 1)  # X-Axis + all channels
                    assert data is not None
                    
                    data_len = len(data) if data else 0
                    num_columns = len(data[0]) if data and data[0] else 0
                    logger.info(f"{vector_name} data: {data_len} rows, {num_columns} columns")
                    
                    vector_labels = []
                    vector_units = []
                    for column_index in range(num_columns):
                        # Get vector unit
                        unit = self.vv.VectorUnit(vector_enum + column_index)
                        assert unit is not None
                        vector_units.append(unit)
                    
                        # Get vector label
                        label = self.vv.VectorLabel(vector_enum + column_index)
                        assert label is not None
                        vector_labels.append(label)
                    
                    logger.info(f"{vector_name} labels: {vector_labels}")
                    logger.info(f"{vector_name} units: {vector_units}")
                    vectors_tested += 1
                    
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.error(f"Error with {vector_name}: {error_info}")
                    pytest.xfail(f"Vector test failed for {vector_name}")
            
            logger.info(f"Successfully tested {vectors_tested} vectors")
            assert vectors_tested > 0, "No vectors were successfully tested"
            
            # Clean up - stop test if it's running
            if self.vv.IsRunning():
                logger.info("Stopping test")
                self.vv.StopTest()
                
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in vector acquisition tests: {error_info}")
            pytest.fail(f"Error in vector acquisition tests: {error_info}")
            
            # Ensure test is stopped if an error occurs
            try:
                if self.vv.IsRunning():
                    self.vv.StopTest()
                    logger.info("Test stopped after error")
            except:
                pass
    
    @pytest.mark.data
    def test_data_save_and_export(self):
        """Test saving and exporting data"""
        try:
            # Use the fixture to find a test file
            test_file = self.find_test_file("sine")
            if not test_file:
                logger.warning("No test file found")
                pytest.skip("No test file found for testing data save/export")
            
            logger.info(f"Using test file: {test_file}")
            
            # Open the test
            self.vv.OpenTest(test_file)
            logger.info(f"Opened test file: {test_file}")
            
            # Start the test to generate some data
            self.vv.StartTest()
            logger.info("Started test")
            
            # Wait for test to enter running state
            running = self.wait_for_condition(self.vv.IsRunning)
            if not running:
                logger.warning("Test did not enter running state")
                pytest.skip("Test did not enter running state, skipping data save/export")
            
            # Run for a few seconds to generate data
            logger.info("Running test for a few seconds to generate data")
            time.sleep(3)
            
            # Stop the test
            self.vv.StopTest()
            logger.info("Test stopped")
            
            # Create a data directory if it doesn't exist
            data_dir = os.path.join(self.script_dir, '..', 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                logger.info(f"Created data directory: {data_dir}")
            
            # Generate timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save data file
            file_name = os.path.basename(test_file)
            base_name, ext = os.path.splitext(file_name)
            
            # Modify the extension for data files
            if len(ext) > 3:  # Ensure the extension is at least 3 characters
                new_ext = ext[:3] + 'd'  # .vrp becomes .vrd
            else:
                new_ext = ext  # If the extension is too short, don't change it
            
            # Construct the save path for the data file
            save_path = os.path.join(data_dir, f"{base_name}_{timestamp}{new_ext}")
            
            # Save the data
            logger.info(f"Saving data to: {save_path}")
            self.vv.SaveData(save_path)
            
            time.sleep(1) # give it a second to save
            # Verify file exists and has content
            assert os.path.exists(save_path), f"Data file not found: {save_path}"
            file_size = os.path.getsize(save_path)
            logger.info(f"Data file size: {file_size} bytes")
            assert file_size > 0, "Data file is empty"
            
            # Test exporting data to CSV if the function exists
            if hasattr(self.vv, 'ExportData'):
                # Construct CSV export path
                csv_path = os.path.join(data_dir, f"{base_name}_{timestamp}.csv")
                
                try:
                    logger.info(f"Exporting data to CSV: {csv_path}")
                    self.vv.ExportData(csv_path, 'CSV')
                    
                    # Verify CSV file exists and has content
                    assert os.path.exists(csv_path), f"CSV file not found: {csv_path}"
                    csv_size = os.path.getsize(csv_path)
                    logger.info(f"CSV file size: {csv_size} bytes")
                    assert csv_size > 0, "CSV file is empty"
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error exporting to CSV: {error_info}")
                    pytest.xfail("CSV export failed")
            else:
                logger.info("ExportData method not available, skipping CSV export test")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in data save/export tests: {error_info}")
            pytest.fail(f"Error in data save/export tests: {error_info}")
            
            # Ensure test is stopped if an error occurs
            try:
                if self.vv.IsRunning():
                    self.vv.StopTest()
                    logger.info("Test stopped after error")
            except:
                pass
    
    @pytest.mark.data
    def test_vector_specific_acquisition(self):
        """Test acquisition of specific vectors"""
        try:
            # Use the fixture to find the sine test file
            sine_test = self.find_test_file("sine")
            if not sine_test:
                logger.warning("No sine test file found")
                pytest.skip("No sine test file found for vector-specific testing")
            
            # Run the test
            self.vv.RunTest(sine_test)
            logger.info(f"Running sine test: {sine_test}")
            
            # Wait for test to enter running state
            running = self.wait_for_condition(self.vv.IsRunning)
            if not running:
                logger.warning("Test did not enter running state")
                pytest.skip("Test did not enter running state, skipping vector-specific tests")
            
            # Test common vector acquisitions
            vector_tests = [
                {"name": "Frequency Response", "vector": vvVector.FREQUENCYRESPONSE, "expected_columns": 2},  # X and Y
                {"name": "Frequency Axis", "vector": vvVector.FREQUENCYAXIS, "expected_columns": 1},  # Just frequency
                {"name": "Time History Axis", "vector": vvVector.TIMEHISTORYAXIS, "expected_columns": 1},  # Just time
                {"name": "Waveform data", "vector": vvVector.WAVEFORMAXIS, "expected_columns": 5}   # time and 4 channels
            ]
            
            vectors_verified = 0
            for test in vector_tests:
                try:
                    # Get vector data
                    logger.info(f"Testing {test['name']} vector")
                    
                    # Get vector length
                    length = self.vv.VectorLength(test["vector"])
                    assert length is not None
                    logger.info(f"{test['name']} length: {length}")
                    
                    # Get vector data (requesting expected number of columns)
                    data = self.vv.Vector(test["vector"], test["expected_columns"])
                    assert data is not None
                    
                    # Verify data structure
                    data_len = len(data) if data else 0
                    num_columns = len(data[0]) if data and data[0] else 0
                    
                    logger.info(f"{test['name']} data: {data_len} rows, {num_columns} columns")
                    assert num_columns == test["expected_columns"], \
                        f"Expected {test['expected_columns']} columns, got {num_columns}"
                    
                    # Sample some values for verification
                    if data_len > 0:
                        sample_row = min(5, data_len - 1)  # Get 6th row or last row if fewer
                        logger.info(f"{test['name']} sample row {sample_row}: {data[sample_row]}")
                        
                        # Basic validation of data values
                        for col in range(num_columns):
                            assert isinstance(data[sample_row][col], (int, float)), \
                                f"Expected numeric data, got {type(data[sample_row][col])}"
                    
                    vectors_verified += 1
                    
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error testing {test['name']} vector: {error_info}")
                    continue
            
            logger.info(f"Successfully verified {vectors_verified} specific vectors")
            assert vectors_verified > 0, "No specific vectors were successfully verified"
            
            # Clean up - stop test
            logger.info("Stopping test")
            self.vv.StopTest()
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in vector-specific tests: {error_info}")
            pytest.fail(f"Error in vector-specific tests: {error_info}")
            
            # Ensure test is stopped if an error occurs
            try:
                if self.vv.IsRunning():
                    self.vv.StopTest()
                    logger.info("Test stopped after error")
            except:
                pass


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("vibrationview_data_acquisition_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("="*80)
    print("VibrationVIEW Data Acquisition Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_data_acquisition.py -v")
    print("="*80)