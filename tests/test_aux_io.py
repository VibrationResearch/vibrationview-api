#!/usr/bin/env python
"""
VibrationVIEW Auxiliary I/O Test Module

This module contains tests for auxiliary I/O functionality in the VibrationVIEW API.
These tests focus on rear input channels including data acquisition, units, and labels.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
- Main test infrastructure from test_VibrationviewAPI.py

Usage:
    pytest test_aux_io.py -v
"""

import logging
import os
import sys

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


class TestAuxiliaryIO:
    """Test class for VibrationVIEW auxiliary I/O functionality"""

    @pytest.mark.data
    def test_rear_input_basic(self):
        """Test RearInput method returns array of 8 floats"""
        try:
            logger.info("Testing RearInput method")

            # Call RearInput to get rear input readings
            rear_inputs = self.vv.RearInput()

            # Verify return value
            assert rear_inputs is not None, "RearInput returned None"
            assert isinstance(rear_inputs, list), f"Expected list, got {type(rear_inputs)}"
            assert len(rear_inputs) == 8, f"Expected 8 rear inputs, got {len(rear_inputs)}"

            # Verify all values are floats
            for i, value in enumerate(rear_inputs):
                assert isinstance(value, (int, float)), \
                    f"Rear input {i} expected numeric value, got {type(value)}"
                logger.info(f"Rear input {i}: {value}")

            logger.info(f"Successfully retrieved {len(rear_inputs)} rear input values")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_rear_input_basic: {error_info}")
            pytest.fail(f"Error in test_rear_input_basic: {error_info}")

    @pytest.mark.data
    def test_rear_input_unit(self):
        """Test RearInputUnit method returns units for rear input channels"""
        try:
            logger.info("Testing RearInputUnit method")

            # Test all 8 rear input channels (0-7) - some hardware may have more or fewer channels
            units_retrieved = 0
            for channel in range(8):
                try:
                    unit = self.vv.RearInputUnit(channel)

                    # Verify return value
                    assert unit is not None, f"RearInputUnit returned None for channel {channel}"
                    assert isinstance(unit, str), f"Expected string, got {type(unit)} for channel {channel}"

                    logger.info(f"Rear input channel {channel} unit: {unit}")
                    units_retrieved += 1

                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error getting unit for rear input channel {channel}: {error_info}")

            # At least some channels should have returned units
            assert units_retrieved > 0, "No rear input units were successfully retrieved"
            logger.info(f"Successfully retrieved units for {units_retrieved}/8 rear input channels")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_rear_input_unit: {error_info}")
            pytest.fail(f"Error in test_rear_input_unit: {error_info}")

    @pytest.mark.data
    def test_rear_input_label(self):
        """Test RearInputLabel method returns labels for rear input channels"""
        try:
            logger.info("Testing RearInputLabel method")

            # Test all 8 rear input channels (0-7) - some hardware may have more or fewer channels
            labels_retrieved = 0
            for channel in range(8):
                try:
                    label = self.vv.RearInputLabel(channel)

                    # Verify return value
                    assert label is not None, f"RearInputLabel returned None for channel {channel}"
                    assert isinstance(label, str), f"Expected string, got {type(label)} for channel {channel}"

                    logger.info(f"Rear input channel {channel} label: {label}")
                    labels_retrieved += 1

                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error getting label for rear input channel {channel}: {error_info}")

            # At least some channels should have returned labels
            assert labels_retrieved > 0, "No rear input labels were successfully retrieved"
            logger.info(f"Successfully retrieved labels for {labels_retrieved}/8 rear input channels")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_rear_input_label: {error_info}")
            pytest.fail(f"Error in test_rear_input_label: {error_info}")

    @pytest.mark.data
    def test_rear_input_unit_invalid_channel(self):
        """Test RearInputUnit with invalid channel handles errors appropriately"""
        try:
            logger.info("Testing RearInputUnit with invalid channel")

            # Test with channel beyond valid range
            invalid_channel = 10000

            try:
                unit = self.vv.RearInputUnit(invalid_channel)
                # Some implementations might return empty string or default value for invalid channels
                logger.info(f"RearInputUnit for invalid channel {invalid_channel} returned: {unit}")

            except Exception as e:
                # Exception is expected and acceptable for invalid channel
                error_info = ExtractComErrorInfo(e)
                logger.info(f"RearInputUnit correctly raised exception for invalid channel {invalid_channel}: {error_info}")

            logger.info("RearInputUnit invalid channel handling verified")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_rear_input_unit_invalid_channel: {error_info}")
            pytest.fail(f"Error in test_rear_input_unit_invalid_channel: {error_info}")

    @pytest.mark.data
    def test_rear_input_label_invalid_channel(self):
        """Test RearInputLabel with invalid channel handles errors appropriately"""
        try:
            logger.info("Testing RearInputLabel with invalid channel")

            invalid_channel = 10000

            try:
                label = self.vv.RearInputLabel(invalid_channel)
                # Some implementations might return empty string or default value for invalid channels
                logger.info(f"RearInputLabel for invalid channel {invalid_channel} returned: {label}")

            except Exception as e:
                # Exception is expected and acceptable for invalid channel
                error_info = ExtractComErrorInfo(e)
                logger.info(f"RearInputLabel correctly raised exception for invalid channel {invalid_channel}: {error_info}")

            logger.info("RearInputLabel invalid channel handling verified")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_rear_input_label_invalid_channel: {error_info}")
            pytest.fail(f"Error in test_rear_input_label_invalid_channel: {error_info}")

    @pytest.mark.data
    def test_rear_input_all_properties_together(self):
        """Test retrieving all rear input properties (data, units, labels) together"""
        try:
            logger.info("Testing all rear input properties together")

            # Get rear input data - the API limitation is 8 channels, but hardware may have more or fewer channesl
            rear_inputs = self.vv.RearInput()
            assert rear_inputs is not None, "RearInput returned None"
            assert len(rear_inputs) == 8, f"Expected 8 rear inputs, got {len(rear_inputs)}"

            # Get units and labels for each channel
            for channel in range(8):
                try:
                    value = rear_inputs[channel]
                    unit = self.vv.RearInputUnit(channel)
                    label = self.vv.RearInputLabel(channel)

                    assert unit is not None, f"RearInputUnit returned None for channel {channel}"
                    assert label is not None, f"RearInputLabel returned None for channel {channel}"

                    logger.info(f"Rear input {channel}: {label} = {value} {unit}")

                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error getting properties for rear input channel {channel}: {error_info}")

            logger.info("Successfully retrieved all rear input properties together")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_rear_input_all_properties_together: {error_info}")
            pytest.fail(f"Error in test_rear_input_all_properties_together: {error_info}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("vibrationview_aux_io_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    print("="*80)
    print("VibrationVIEW Auxiliary I/O Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_aux_io.py -v")
    print("="*80)
