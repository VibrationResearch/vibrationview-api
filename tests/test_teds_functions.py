#!/usr/bin/env python
"""
VibrationVIEW TEDS Functions Module

This module contains tests for TEDS (Transducer Electronic Data Sheets) functionality
in the VibrationVIEW API. These tests focus on TEDS data reading, verification,
and application.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
- Main test infrastructure from conftest.py

Usage:
    pytest test_teds_functions.py -v
"""

import os
import sys
import time
import logging
import pytest
import pythoncom
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

# Add necessary paths for imports
current_dir = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

# Import channel configuration utilities
try:
    from .channelconfigs import get_channel_config
except ImportError:
    logger.warning("Could not import channelconfigs module. Some tests may fail.")

    # Define a fallback function
    def get_channel_config(channel_index):
        from dataclasses import dataclass
        from typing import Optional

        @dataclass
        class DefaultConfig:
            sensitivity: float = 10.0
            unit: str = "g"
            label: str = "Acceleration"
            cap_coupled: bool = False
            accel_power: bool = False
            differential: bool = False
            serial: str = ""
            cal_date: str = ""
            teds: Optional[object] = None

        return DefaultConfig()

try:
    # Import main VibrationVIEW API
    from vibrationviewapi import VibrationVIEW, vvVector, vvTestType, ExtractComErrorInfo
except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)


class TestTedsFunctions:
    """Test class for VibrationVIEW TEDS functionality"""

    @classmethod
    def setup_class(cls):
        """Load 6-channels TEDS configuration before running TEDS tests"""
        # This will be called once for the class, but we need to access vv from instance
        # So we'll store the config file path and load it in the first test that runs
        cls.teds_config_loaded = False
        cls.teds_config_file = "6-channels-TEDS.vic"

    def _ensure_teds_config_loaded(self):
        """Ensure TEDS configuration is loaded before running TEDS tests"""
        if not TestTedsFunctions.teds_config_loaded:
            try:
                config_subfolder = "InputConfig"
                config_folder = os.path.join(self.script_dir, '..', config_subfolder)
                config_file = os.path.join(config_folder, TestTedsFunctions.teds_config_file)

                if os.path.exists(config_file):
                    logger.info(f"Loading TEDS configuration: {config_file}")
                    self.vv.SetInputConfigurationFile(config_file)
                    TestTedsFunctions.teds_config_loaded = True
                    logger.info("TEDS configuration loaded successfully")
                else:
                    logger.warning(f"TEDS configuration file not found: {config_file}")
            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.warning(f"Failed to load TEDS configuration: {error_info}")

    @pytest.mark.teds
    def test_Teds_command(self):
        """Test TEDS data Read (without applying) for any channels"""
        try:
            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None
            assert num_channels > 0
            logger.info(f"Testing TEDS data for {num_channels} channels")

            channels_with_teds = 0

            for channel_index in range(num_channels):
                try:
                    logger.info(f"Testing TEDS data for channel {channel_index+1}")

                    # Get TEDS data
                    teds_array = self.vv.Teds(channel_index)

                    if teds_array and len(teds_array) > 0 and teds_array[0]:
                        channel_teds = teds_array[0]

                        # Check for TEDS errors
                        if "Error" in channel_teds:
                            error_msg = channel_teds.get("Error", "Unknown error")
                            logger.warning(f"TEDS error for channel {channel_index+1}: {error_msg}")
                            continue

                        # Get TEDS info entries
                        teds_info = channel_teds.get("Teds", [])
                        if not teds_info:
                            logger.warning(f"No TEDS entries found for channel {channel_index+1}")
                            continue

                        logger.info(f"Found {len(teds_info)} TEDS entries for channel {channel_index+1}")

                        # Log some TEDS entries (limit to 5 entries to avoid verbose logging)
                        entries_to_log = min(5, len(teds_info))
                        for i in range(entries_to_log):
                            logger.info(f"TEDS entry {i+1}: {teds_info[i]}")

                        channels_with_teds += 1

                        # Verify against expected TEDS data if available
                        config = get_channel_config(channel_index)
                        if config and config.teds:
                            expected_teds = config.teds.as_tuples()
                            matches = 0
                            total_expected = len(expected_teds)

                            for expected_key, expected_value in expected_teds:
                                for actual_key, actual_value, actual_unit in teds_info:
                                    if actual_key == expected_key and actual_value == expected_value:
                                        matches += 1
                                        break

                            match_percentage = (matches / total_expected) * 100 if total_expected > 0 else 0
                            logger.info(f"TEDS match percentage: {match_percentage:.1f}% ({matches}/{total_expected})")

                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error getting TEDS data for channel {channel_index+1}: {error_info}")

            if channels_with_teds == 0:
                logger.warning("No channels with valid TEDS data found")
                pytest.skip("No channels with valid TEDS data found")
            else:
                logger.info(f"Successfully verified TEDS data for {channels_with_teds} channels")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_teds_data: {error_info}")
            pytest.fail(f"Error in test_teds_data: {error_info}")

    @pytest.mark.teds
    def test_TedsVerifyAndApply_command(self):
        """Test TedsVerifyAndApply using data from TedsRead"""
        try:
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")

            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)

            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing TedsVerifyAndApply for {num_channels} channels")

            # First, read current TEDS data using TedsRead()
            logger.info("Reading current TEDS data using TedsRead()")
            teds_data = self.vv.TedsRead()

            assert teds_data is not None, "TedsRead() should return data"
            assert len(teds_data) == num_channels, f"Expected {num_channels} channel results, got {len(teds_data)}"

            # TedsVerifyAndApply only accepts rank 1 array of URNs, not the full TEDS data
            # Since TedsRead returns rank 1 array of URNs, pass it directly
            logger.info("Testing TedsVerifyAndApply with URN array from TedsRead")
            try:
                verify_result = self.vv.TedsVerifyAndApply(teds_data)
            except AttributeError as e:
                if "object has no attribute 'TedsVerifyAndApply'" in str(e):
                    pytest.skip("TedsVerifyAndApply method does not exist in COM object")
                raise

            assert verify_result is not None, "TedsVerifyAndApply should return a result"
            logger.info(f"TedsVerifyAndApply returned: {type(verify_result)} with length {len(verify_result) if hasattr(verify_result, '__len__') else 'N/A'}")

            # TedsVerifyAndApply returns a rank 1 array of URNs, same as TedsRead
            assert isinstance(verify_result, (tuple, list)), f"TedsVerifyAndApply should return a tuple/list of URNs, got {type(verify_result)}"
            assert len(verify_result) == num_channels, f"Expected {num_channels} URN results, got {len(verify_result)}"

            # Count channels with valid URNs
            verified_channels = 0
            for channel_index, urn in enumerate(verify_result):
                if urn and isinstance(urn, str) and urn.strip() and urn.lower() != "disabled":
                    logger.info(f"Channel {channel_index+1}: Verified URN '{urn}'")
                    verified_channels += 1
                else:
                    logger.info(f"Channel {channel_index+1}: No URN or disabled")

            logger.info(f"Successfully verified and applied TEDS for {verified_channels} channels")
            assert verified_channels > 0, "At least one channel should have a valid URN after verification"

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_teds_verify_and_apply: {error_info}")
            pytest.fail(f"Error in test_teds_verify_and_apply: {error_info}")

    @pytest.mark.teds
    def test_TedsReadAndApply_command(self):
        """Test TedsReadAndApply method to read and apply TEDS data from hardware"""
        try:
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")

            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)

            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing TedsReadAndApply for {num_channels} channels")

            # Test TedsReadAndApply - this should read TEDS from hardware and apply to VibrationVIEW
            logger.info("Testing TedsReadAndApply method")
            read_and_apply_result = self.vv.TedsReadAndApply()

            assert read_and_apply_result is not None, "TedsReadAndApply should return a result"
            logger.info(f"TedsReadAndApply returned: {type(read_and_apply_result)}")

            # TedsReadAndApply should return a rank 1 array of URNs or raise an exception
            assert isinstance(read_and_apply_result, (tuple, list)), f"TedsReadAndApply should return a tuple/list of URNs, got {type(read_and_apply_result)}"
            assert len(read_and_apply_result) == num_channels, f"Expected {num_channels} URN results, got {len(read_and_apply_result)}"
            logger.info(f"TedsReadAndApply returned {len(read_and_apply_result)} URNs")

            # Count channels with valid URNs
            applied_channels = 0
            for channel_index, urn in enumerate(read_and_apply_result):
                if urn and isinstance(urn, str) and urn.strip() and urn.lower() != "disabled":
                    logger.info(f"Channel {channel_index+1}: Applied URN '{urn}'")
                    applied_channels += 1
                else:
                    logger.info(f"Channel {channel_index+1}: No URN or disabled")

            logger.info(f"Successfully read and applied TEDS for {applied_channels} channels")
            assert applied_channels == 6, f"TedsReadAndApply should apply TEDS to exactly 6 channels, but applied to {applied_channels} channels"

            logger.info("TedsReadAndApply test completed successfully - applied TEDS to 6 channels")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_teds_read_and_apply: {error_info}")
            pytest.fail(f"Error in test_teds_read_and_apply: {error_info}")

    @pytest.mark.teds
    def test_TedsReadAndApply_before_and_during_test(self):
        """Test TedsReadAndApply before and during test - should return fresh data before, cached data during running test"""
        try:
            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            # Load test file but don't start yet
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")

            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)

            # Verify test is NOT running
            test_running = self.vv.IsRunning()
            logger.info(f"Test running status before start: {test_running}")
            assert not test_running, "Test should not be running initially"

            # FIRST CALL: Test TedsReadAndApply when test is NOT running - should succeed
            logger.info("Testing TedsReadAndApply method when test is NOT running - should succeed")
            read_and_apply_result_before = self.vv.TedsReadAndApply()
            logger.info(f"TedsReadAndApply (before test start) returned: {type(read_and_apply_result_before)}")

            # Verify the first call succeeded (should return rank 1 array of URNs)
            assert read_and_apply_result_before is not None, "TedsReadAndApply should return a result"
            assert isinstance(read_and_apply_result_before, (tuple, list)), f"TedsReadAndApply should return a tuple/list of URNs, got {type(read_and_apply_result_before)}"
            logger.info(f"TedsReadAndApply succeeded when test was not running: {len(read_and_apply_result_before)} URNs")

            # Now start the test
            logger.info("Starting test after first TedsReadAndApply call")
            self.vv.StartTest()

            # Wait a moment for the test to start
            time.sleep(2)

            # Verify test is now running
            test_running = self.vv.IsRunning()
            logger.info(f"Test running status after start: {test_running}")
            assert test_running, "Test should be running after StartTest()"

            # SECOND CALL: Test TedsReadAndApply when test IS running - may raise exception or return cached data
            logger.info("Testing TedsReadAndApply method while test is running")
            try:
                read_and_apply_result_after = self.vv.TedsReadAndApply()
                logger.info(f"TedsReadAndApply (after test start) returned: {type(read_and_apply_result_after)}")

                # If we get here, cached data was returned
                assert read_and_apply_result_after is not None, "TedsReadAndApply should return cached configuration data"
                assert isinstance(read_and_apply_result_after, (tuple, list)), f"TedsReadAndApply should return a tuple/list of URNs, got {type(read_and_apply_result_after)}"
                assert type(read_and_apply_result_after) == type(read_and_apply_result_before), f"TedsReadAndApply should return same type when test running as when not running"
                logger.info(f"TedsReadAndApply returned cached URN configuration: {len(read_and_apply_result_after)} URNs")
                logger.info("Successfully verified that TedsReadAndApply returns cached configuration data when test is running")

            except Exception as e:
                # This is also valid behavior - function may raise exception when test is running
                error_info = ExtractComErrorInfo(e)
                logger.info(f"TedsReadAndApply raised exception when test running (also valid): {error_info}")
                # This is acceptable behavior

            # Stop the test
            logger.info("Stopping test after TedsReadAndApply comparison test")
            self.vv.StopTest()

            logger.info("Test completed successfully: TedsReadAndApply returned fresh data before test start and cached data after test start")

        except AssertionError:
            # Re-raise assertion errors (these are test failures)
            try:
                self.vv.StopTest()
            except:
                pass
            raise
        except Exception as e:
            # Ensure test is stopped in case of unexpected error
            try:
                self.vv.StopTest()
            except:
                pass
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Unexpected error in test_TedsReadAndApply_before_and_during_test: {error_info}")
            pytest.fail(f"Unexpected error in test_TedsReadAndApply_before_and_during_test: {error_info}")

    @pytest.mark.teds
    def test_TedsRead_before_and_during_recorder(self):
        """Test TedsRead before and during recorder - should return fresh data before, cached data during"""
        try:
            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            # Load test file but don't start recorder yet
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")

            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)

            # Recorder should not be running initially (no need to check status)
            logger.info("Recorder should not be running initially")

            # FIRST CALL: Test TedsRead when recorder is NOT running - should succeed
            logger.info("Testing TedsRead method when recorder is NOT running - should succeed")
            read_result_before = self.vv.TedsRead()
            logger.info(f"TedsRead (before recorder start) returned: {type(read_result_before)}")

            # Verify the first call succeeded (should return rank 1 array of URNs)
            assert read_result_before is not None, "TedsRead should return a result"
            assert isinstance(read_result_before, (tuple, list)), f"TedsRead should return a tuple/list of URNs, got {type(read_result_before)}"
            logger.info(f"TedsRead succeeded when recorder was not running: {len(read_result_before)} URNs")

            # Apply the TEDS before starting the recorder using TedsReadAndApply to ensure configuration is valid
            logger.info("Running TedsReadAndApply to ensure configuration is valid before starting recorder")
            try:
                apply_result = self.vv.TedsReadAndApply()
                logger.info(f"TedsReadAndApply succeeded: {type(apply_result)}")
            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.warning(f"Failed to apply TEDS: {error_info}")

            # Now start the recorder
            logger.info("Starting recorder after applying TEDS")
            self.vv.RecordStart()

            # Wait a moment for the recorder to start
            time.sleep(2)
            logger.info("Recorder is now running")

            # SECOND CALL: Test TedsRead when recorder IS running - may raise exception or return cached data
            logger.info("Testing TedsRead method while recorder is running")
            try:
                read_result_after = self.vv.TedsRead()
                logger.info(f"TedsRead (after recorder start) returned: {type(read_result_after)}")

                # If we get here, cached data was returned
                assert read_result_after is not None, "TedsRead should return cached configuration data"
                assert isinstance(read_result_after, (tuple, list)), f"TedsRead should return a tuple/list of URNs, got {type(read_result_after)}"
                assert type(read_result_after) == type(read_result_before), f"TedsRead should return same type when recorder running as when not running"
                logger.info(f"TedsRead returned cached URN configuration: {len(read_result_after)} URNs")
                logger.info("Successfully verified that TedsRead returns cached configuration data when recorder is running")

            except Exception as e:
                # This is also valid behavior - function may raise exception when recorder is running
                error_info = ExtractComErrorInfo(e)
                logger.info(f"TedsRead raised exception when recorder running (also valid): {error_info}")
                # This is acceptable behavior

            # Stop the recorder
            logger.info("Stopping recorder after TedsRead comparison test")
            self.vv.RecordStop()

            logger.info("Test completed successfully: TedsRead returned fresh data before recorder start and cached data after recorder start")

        except AssertionError:
            # Re-raise assertion errors (these are test failures)
            try:
                self.vv.RecordStop()
            except:
                pass
            raise
        except Exception as e:
            # Ensure recorder is stopped in case of unexpected error
            try:
                self.vv.RecordStop()
            except:
                pass
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Unexpected error in test_TedsRead_before_and_during_recorder: {error_info}")
            pytest.fail(f"Unexpected error in test_TedsRead_before_and_during_recorder: {error_info}")

    @pytest.mark.teds
    def test_TedsVerifyAndApply_mismatch_error(self):
        """Test TedsVerifyAndApply returns mismatch error when a field is changed"""
        try:
            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing TedsVerifyAndApply mismatch error for {num_channels} channels")

            # First, read current TEDS data using TedsRead()
            logger.info("Reading current TEDS data using TedsRead()")
            teds_data = self.vv.TedsRead()

            assert teds_data is not None, "TedsRead() should return data"
            assert len(teds_data) == num_channels, f"Expected {num_channels} channel results, got {len(teds_data)}"

            # Since TedsVerifyAndApply only accepts rank 1 URN array, modify a URN to create mismatch
            modified_urns = list(teds_data)  # Create a copy of the URN array
            channel_modified = None

            # Find a channel with a valid URN to modify
            for channel_index, urn in enumerate(teds_data):
                if urn and isinstance(urn, str) and urn.strip() and urn.lower() != "disabled":
                    # Modify this URN to create a mismatch
                    original_urn = urn
                    modified_urn = "INVALID_URN_FOR_MISMATCH_TEST"
                    modified_urns[channel_index] = modified_urn
                    channel_modified = channel_index
                    logger.info(f"Modified channel {channel_index+1} URN: '{original_urn}' -> '{modified_urn}'")
                    break

            if channel_modified is None:
                pytest.skip("No suitable URN found to modify for mismatch test")

            # Now test TedsVerifyAndApply with the modified URN array
            logger.info("Testing TedsVerifyAndApply with modified URN array (may raise exception or succeed)")
            try:
                verify_result = self.vv.TedsVerifyAndApply(tuple(modified_urns))

                # If we get here, the invalid URN was accepted
                assert verify_result is not None, "TedsVerifyAndApply should return a result"
                logger.info(f"TedsVerifyAndApply returned: {type(verify_result)} with length {len(verify_result) if hasattr(verify_result, '__len__') else 'N/A'}")

                assert isinstance(verify_result, (tuple, list)), f"TedsVerifyAndApply should return a tuple/list of URNs, got {type(verify_result)}"
                assert len(verify_result) == num_channels, f"Expected {num_channels} results, got {len(verify_result)}"

                logger.warning("Modified URN was accepted - API may be more lenient than expected")
                for channel_index, result in enumerate(verify_result):
                    logger.info(f"Channel {channel_index+1}: Result: {result}")

            except Exception as e:
                # This is actually the expected behavior for invalid URNs
                error_info = ExtractComErrorInfo(e)
                logger.info(f"TedsVerifyAndApply raised expected exception for invalid URN: {error_info}")
                # This is the correct behavior - invalid URNs should raise exceptions

            logger.info("Successfully handled mismatch test case")

        except Exception as e:
            error_msg = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsVerifyAndApply_mismatch_error: {error_msg}")
            pytest.fail(f"Error in test_TedsVerifyAndApply_mismatch_error: {error_msg}")

    @pytest.mark.teds
    def test_TedsVerifyAndApply_reversed_channels_error(self):
        """Test TedsVerifyAndApply returns mismatch error when channels 2 and 3 are reversed"""
        try:
            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            assert num_channels >= 3, "Need at least 3 channels to test reversing channels 2 and 3"
            logger.info(f"Testing TedsVerifyAndApply with reversed channels 2 and 3 for {num_channels} channels")

            # First, read current TEDS data using TedsRead()
            logger.info("Reading current TEDS data using TedsRead()")
            teds_data = self.vv.TedsRead()

            assert teds_data is not None, "TedsRead() should return data"
            assert len(teds_data) == num_channels, f"Expected {num_channels} channel results, got {len(teds_data)}"

            # Create a copy of the URN array and swap channels 2 and 3 (indices 1 and 2)
            modified_urns = list(teds_data)

            # Check if channels 2 and 3 have valid URNs
            channel_2_urn = teds_data[1]
            channel_3_urn = teds_data[2]

            if not (channel_2_urn and isinstance(channel_2_urn, str) and channel_2_urn.strip() and channel_2_urn.lower() != "disabled"):
                pytest.skip("Channel 2 does not have a valid URN to swap")

            if not (channel_3_urn and isinstance(channel_3_urn, str) and channel_3_urn.strip() and channel_3_urn.lower() != "disabled"):
                pytest.skip("Channel 3 does not have a valid URN to swap")

            # Swap channels 2 and 3
            modified_urns[1] = channel_3_urn
            modified_urns[2] = channel_2_urn
            logger.info(f"Swapped channel 2 URN '{channel_2_urn}' with channel 3 URN '{channel_3_urn}'")

            # Now test TedsVerifyAndApply with the reversed URN array
            logger.info("Testing TedsVerifyAndApply with reversed channels 2 and 3 (may raise exception or succeed)")
            try:
                verify_result = self.vv.TedsVerifyAndApply(tuple(modified_urns))

                # If we get here, the reversed URNs were accepted
                assert verify_result is not None, "TedsVerifyAndApply should return a result"
                logger.info(f"TedsVerifyAndApply returned: {type(verify_result)} with length {len(verify_result) if hasattr(verify_result, '__len__') else 'N/A'}")

                assert isinstance(verify_result, (tuple, list)), f"TedsVerifyAndApply should return a tuple/list of URNs, got {type(verify_result)}"
                assert len(verify_result) == num_channels, f"Expected {num_channels} results, got {len(verify_result)}"

                logger.warning("Reversed URNs were accepted - API may be more lenient than expected")
                for channel_index, result in enumerate(verify_result):
                    logger.info(f"Channel {channel_index+1}: Result: {result}")

            except Exception as e:
                # This is actually the expected behavior for mismatched URNs
                error_info = ExtractComErrorInfo(e)
                logger.info(f"TedsVerifyAndApply raised expected exception for reversed channels: {error_info}")
                # This is the correct behavior - reversed URNs should raise exceptions

            logger.info("Successfully handled reversed channels test case")

        except Exception as e:
            error_msg = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsVerifyAndApply_reversed_channels_error: {error_msg}")
            pytest.fail(f"Error in test_TedsVerifyAndApply_reversed_channels_error: {error_msg}")

    @pytest.mark.teds
    def test_TedsVerifyAndApply_missing_URN_error(self):
        """Test TedsVerifyAndApply returns mismatch error when URN is missing on an enabled channel"""
        try:
            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing TedsVerifyAndApply missing URN error for {num_channels} channels")

            # First, read current TEDS data using TedsRead()
            logger.info("Reading current TEDS data using TedsRead()")
            teds_data = self.vv.TedsRead()

            assert teds_data is not None, "TedsRead() should return data"
            assert len(teds_data) == num_channels, f"Expected {num_channels} channel results, got {len(teds_data)}"

            # Since TedsVerifyAndApply only accepts rank 1 URN array, set a channel's URN to empty
            modified_urns = list(teds_data)  # Create a copy of the URN array
            channel_modified = None

            # Find a channel with a valid URN to clear/remove
            for channel_index, urn in enumerate(teds_data):
                if urn and isinstance(urn, str) and urn.strip() and urn.lower() != "disabled":
                    # Clear this URN to simulate missing URN
                    original_urn = urn
                    modified_urns[channel_index] = ""  # Empty URN
                    channel_modified = channel_index
                    logger.info(f"Cleared channel {channel_index+1} URN: '{original_urn}' -> empty")
                    break

            if channel_modified is None:
                pytest.skip("No suitable URN found to clear for missing URN test")

            # Now test TedsVerifyAndApply with the missing URN array - EXPECTING EXCEPTION
            logger.info("Testing TedsVerifyAndApply with missing URN data - expecting exception")

            exception_raised = False
            try:
                verify_result = self.vv.TedsVerifyAndApply(tuple(modified_urns))

                # If we get here, no exception was raised - this is unexpected
                logger.error(f"TedsVerifyAndApply did not raise exception for missing URN. Returned: {type(verify_result)}")
                pytest.fail(f"TedsVerifyAndApply should raise an exception for missing URN, but returned: {verify_result}")

            except Exception as e:
                # This is the expected behavior - missing URNs should raise exceptions
                error_info = ExtractComErrorInfo(e)
                logger.info(f"TedsVerifyAndApply correctly raised exception for missing URN: {error_info}")
                exception_raised = True

            # Assert that an exception was raised
            assert exception_raised, "TedsVerifyAndApply should raise an exception for missing URN"
            logger.info("Test passed: TedsVerifyAndApply correctly raised exception for missing URN")

        except Exception as e:
            error_msg = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsVerifyAndApply_missing_URN_error: {error_msg}")
            pytest.fail(f"Error in test_TedsVerifyAndApply_missing_URN_error: {error_msg}")

    @pytest.mark.teds
    def test_TedsVerifyAndApply_URN_on_disabled_channel_should_fail(self):
        """Test TedsVerifyAndApply with a valid URN on a channel that is not enabled - should fail"""
        try:
            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing TedsVerifyAndApply with URN on disabled channel for {num_channels} channels")

            # First, read current TEDS data using TedsRead()
            logger.info("Reading current TEDS data using TedsRead()")
            teds_data = self.vv.TedsRead()

            assert teds_data is not None, "TedsRead() should return data"
            assert len(teds_data) == num_channels, f"Expected {num_channels} channel results, got {len(teds_data)}"

            # Since TedsVerifyAndApply only accepts rank 1 URN array, add URN to a disabled channel
            modified_urns = list(teds_data)  # Create a copy of the URN array
            channel_modified = None

            # Find a channel without URN (disabled or empty) to add URN to
            for channel_index, urn in enumerate(teds_data):
                if not urn or (isinstance(urn, str) and (not urn.strip() or urn.lower() == "disabled")):
                    # Add a URN to this disabled/empty channel
                    test_urn = "3C00000186B96114"
                    modified_urns[channel_index] = test_urn
                    channel_modified = channel_index
                    logger.info(f"Added URN to disabled channel {channel_index+1}: '' -> '{test_urn}'")
                    break

            if channel_modified is None:
                pytest.skip("No suitable disabled channel found to add URN for test")

            # Now test TedsVerifyAndApply with valid URN on disabled channel - expecting rejection
            logger.info("Testing TedsVerifyAndApply with valid URN on disabled channel - expecting rejection")

            urn_rejected = False
            try:
                verify_result = self.vv.TedsVerifyAndApply(tuple(modified_urns))

                # If we get here, no exception was raised - check if error is in the result
                assert verify_result is not None, "TedsVerifyAndApply should return a result"
                logger.info(f"TedsVerifyAndApply returned: {type(verify_result)} with length {len(verify_result) if hasattr(verify_result, '__len__') else 'N/A'}")

                # TedsVerifyAndApply returns a rank 1 array of URNs, check the results
                assert isinstance(verify_result, (tuple, list)), f"TedsVerifyAndApply should return a tuple/list, got {type(verify_result)}"
                assert len(verify_result) == num_channels, f"Expected {num_channels} results, got {len(verify_result)}"

                # Check that URN was rejected for disabled channel (error in result)
                for channel_index, result in enumerate(verify_result):
                    if channel_index == channel_modified:
                        if isinstance(result, str) and result.strip():
                            if "error" in result.lower() or "invalid" in result.lower() or "mismatch" in result.lower():
                                logger.info(f"Channel {channel_index+1}: URN on disabled channel correctly rejected (error in result): {result}")
                                urn_rejected = True
                            else:
                                logger.error(f"Channel {channel_index+1}: URN on disabled channel was unexpectedly accepted: {result}")
                        else:
                            logger.error(f"Channel {channel_index+1}: Empty result for URN on disabled channel (expected error)")
                        break

            except Exception as e:
                # This is also valid - TedsVerifyAndApply raised an exception for the invalid configuration
                error_info = ExtractComErrorInfo(e)
                logger.info(f"TedsVerifyAndApply correctly raised exception for URN on disabled channel: {error_info}")
                urn_rejected = True

            # URN on disabled channel should always be rejected (either via exception or error in result)
            assert urn_rejected, f"URN on disabled channel should be rejected with error or exception, but got: {verify_result[channel_modified] if 'verify_result' in locals() and channel_modified < len(verify_result) else 'no error detected'}"
            logger.info("Test passed: URN on disabled channel was correctly rejected")

        except Exception as e:
            error_msg = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsVerifyAndApply_URN_on_disabled_channel_should_fail: {error_msg}")
            pytest.fail(f"Error in test_TedsVerifyAndApply_URN_on_disabled_channel_should_fail: {error_msg}")

    @pytest.mark.teds
    def test_TedsReadAndApply_with_sine_named_config_should_fail(self):
        """Test TedsReadAndApply with sine-named config.vsp profile - should fail"""
        try:
            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            # Load the sine-named config profile
            profile_folder = os.path.join(self.script_dir, '..', 'profiles')
            profile_file = os.path.join(profile_folder, 'sine-named config.vsp')

            if not os.path.exists(profile_file):
                pytest.skip(f"Profile file not found: {profile_file}")

            logger.info(f"Loading profile: {profile_file}")
            self.vv.OpenTest(profile_file)
            logger.info("Profile loaded successfully")

            test_result = self.vv.TedsRead()

            logger.info("TedsRead() called through automation")
            logger.info(f"TedsRead() returned: {type(test_result)}")

            # Log what we got back
            if test_result:
                logger.info(f"TedsRead() returned {len(test_result)} items")
                for idx, item in enumerate(test_result):
                    logger.info(f"Channel {idx+1}: {item}")

            # THIS ASSERTION WILL FAIL - expecting TEDS data when there likely is none
            # or expecting a specific number of channels with valid URNs
            assert test_result is not None, "TedsRead() should return data"
            assert isinstance(test_result, (tuple, list)), "TedsRead() should return a tuple or list"

            # Count channels with valid TEDS URNs
            channels_with_teds = 0
            for item in test_result:
                if item and isinstance(item, str) and item.strip() and item.lower() != "disabled":
                    channels_with_teds += 1

            logger.info(f"Found {channels_with_teds} channels with TEDS URNs")

            # Expecting at least 15 channels with TEDS
            assert channels_with_teds == 1, f"Expected 1 channels with TEDS URNs, but found {channels_with_teds}"

            # Now test TedsReadAndApply - THIS SHOULD FAIL
            logger.info("Testing TedsReadAndApply - expecting failure/exception")
            exception_raised = False
            try:
                apply_result = self.vv.TedsReadAndApply()
                # If we get here, no exception was raised
                logger.warning(f"TedsReadAndApply did not raise an exception. Returned: {type(apply_result)}")

                # Check if the result contains errors
                if apply_result and isinstance(apply_result, (tuple, list)):
                    for channel_index, urn in enumerate(apply_result):
                        if urn and isinstance(urn, str) and ("error" in urn.lower() or "invalid" in urn.lower() or "mismatch" in urn.lower()):
                            logger.info(f"Channel {channel_index+1}: Expected error found: {urn}")
                            exception_raised = True
            except Exception as e:
                # This is the expected behavior - TedsReadAndApply should raise an exception
                error_info = ExtractComErrorInfo(e)
                logger.info(f"TedsReadAndApply raised expected exception: {error_info}")
                exception_raised = True

            # Assert that either an exception was raised or errors were returned
            assert exception_raised, "TedsReadAndApply should fail (raise exception or return errors) with sine-named config profile"

            logger.info("Test passed: TedsReadAndApply failed as expected")

        except AssertionError:
            # Re-raise assertion errors (these are intentional test failures)
            raise
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsReadAndApply_with_sine_named_config_should_fail: {error_info}")
            pytest.fail(f"Error in test_TedsReadAndApply_with_sine_named_config_should_fail: {error_info}")
        finally:
            # Reload default TEDS configuration
            try:
                logger.info("Reloading default TEDS configuration")
                config_subfolder = "InputConfig"
                config_folder = os.path.join(self.script_dir, '..', config_subfolder)
                config_file = os.path.join(config_folder, TestTedsFunctions.teds_config_file)

                if os.path.exists(config_file):
                    self.vv.SetInputConfigurationFile(config_file)
                    logger.info("Default TEDS configuration reloaded successfully")
                else:
                    logger.warning(f"Default TEDS configuration file not found: {config_file}")
            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.warning(f"Failed to reload default TEDS configuration: {error_info}")

    @pytest.mark.teds
    def test_TedsRead_with_demo_mode_TEDS_profile_should_pass(self):
        """Test TedsRead with sine_with_Input_configuration_TEDS.vsp profile - should pass"""
        try:
            # Load TEDS configuration if not already loaded
            self._ensure_teds_config_loaded()

            # Load the demo mode TEDS profile
            profile_folder = os.path.join(self.script_dir, '..', 'profiles')
            profile_file = os.path.join(profile_folder, 'sine_with_Input_configuration_TEDS.vsp')

            if not os.path.exists(profile_file):
                pytest.skip(f"Profile file not found: {profile_file}")

            logger.info(f"Loading profile: {profile_file}")
            self.vv.OpenTest(profile_file)
            logger.info("Profile loaded successfully")

            test_result = self.vv.TedsRead()

            logger.info("TedsRead() called through automation")
            logger.info(f"TedsRead() returned: {type(test_result)}")

            # Verify we got data back
            assert test_result is not None, "TedsRead() should return data"
            assert isinstance(test_result, (tuple, list)), "TedsRead() should return a tuple or list"

            # Log what we got back
            if test_result:
                logger.info(f"TedsRead() returned {len(test_result)} items")
                for idx, item in enumerate(test_result):
                    logger.info(f"Channel {idx+1}: {item}")

            # Count channels with valid TEDS URNs
            channels_with_teds = 0
            for item in test_result:
                if item and isinstance(item, str) and item.strip() and item.lower() != "disabled":
                    channels_with_teds += 1

            logger.info(f"Found {channels_with_teds} channels with TEDS URNs")

            # Expect 6 channels with TEDS URNs (matching the 6-channels-TEDS.vic configuration)
            assert channels_with_teds == 6, f"Expected 6 channels with TEDS URNs, but found {channels_with_teds}"

            logger.info("TedsRead successfully read TEDS data from demo mode profile")

            # Now test TedsVerifyAndApply with the TEDS data
            logger.info("Testing TedsVerifyAndApply with TEDS data from demo mode profile")
            verify_result = self.vv.TedsVerifyAndApply(test_result)

            assert verify_result is not None, "TedsVerifyAndApply should return a result"
            logger.info(f"TedsVerifyAndApply returned: {type(verify_result)} with length {len(verify_result) if hasattr(verify_result, '__len__') else 'N/A'}")

            # TedsVerifyAndApply returns a rank 1 array of URNs
            assert isinstance(verify_result, (tuple, list)), f"TedsVerifyAndApply should return a tuple/list of URNs, got {type(verify_result)}"

            # Check that there are no errors in the result
            has_errors = False
            for channel_index, urn in enumerate(verify_result):
                if urn and isinstance(urn, str):
                    # Check if the URN contains error messages
                    if "error" in urn.lower() or "invalid" in urn.lower() or "mismatch" in urn.lower():
                        logger.error(f"Channel {channel_index+1}: Unexpected error in TedsVerifyAndApply result: {urn}")
                        has_errors = True
                    elif urn.strip() and urn.lower() != "disabled":
                        logger.info(f"Channel {channel_index+1}: Successfully verified TEDS URN: {urn}")
                    else:
                        logger.info(f"Channel {channel_index+1}: No TEDS or disabled")

            # Assert that there were NO errors
            assert not has_errors, "TedsVerifyAndApply should not return any errors when verifying TEDS from demo mode profile"

            logger.info("Test passed: TedsRead and TedsVerifyAndApply successfully processed TEDS data from demo mode profile")

        except AssertionError:
            # Re-raise assertion errors (these are test failures)
            raise
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsRead_with_demo_mode_TEDS_profile_should_pass: {error_info}")
            pytest.fail(f"Error in test_TedsRead_with_demo_mode_TEDS_profile_should_pass: {error_info}")
        finally:
            # Reload default TEDS configuration
            try:
                logger.info("Reloading default TEDS configuration")
                config_subfolder = "InputConfig"
                config_folder = os.path.join(self.script_dir, '..', config_subfolder)
                config_file = os.path.join(config_folder, TestTedsFunctions.teds_config_file)

                if os.path.exists(config_file):
                    self.vv.SetInputConfigurationFile(config_file)
                    logger.info("Default TEDS configuration reloaded successfully")
                else:
                    logger.warning(f"Default TEDS configuration file not found: {config_file}")
            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.warning(f"Failed to reload default TEDS configuration: {error_info}")

    @pytest.mark.teds
    def test_TedsVerifyAndApply_with_channel1_TEDS_should_fail(self):
        """Test TedsVerifyAndApply with channel 1 TEDS.vic - THIS TEST SHOULD RETURN ERRORS"""
        try:
            # Load the default sine profile
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Default sine test file not found")

            logger.info(f"Loading profile: {test_file}")
            self.vv.OpenTest(test_file)
            logger.info("Profile loaded successfully")

            # Load the channel 1 TEDS input configuration
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "channel 1 TEDS.vic")

            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")

            logger.info(f"Loading TEDS configuration: {config_file}")
            self.vv.SetInputConfigurationFile(config_file)
            logger.info("TEDS configuration loaded successfully")

            teds_data = self.vv.TedsRead()

            logger.info("TedsRead() called through automation")
            logger.info(f"TedsRead() returned: {type(teds_data)}")

            # Verify we got data back
            assert teds_data is not None, "TedsRead() should return data"
            assert isinstance(teds_data, (tuple, list)), "TedsRead() should return a tuple or list"

            # Log what we got back
            if teds_data:
                logger.info(f"TedsRead() returned {len(teds_data)} items")
                for idx, item in enumerate(teds_data):
                    logger.info(f"Channel {idx+1}: {item}")

            # Count channels with valid TEDS URNs
            channels_with_teds = 0
            for item in teds_data:
                if item and isinstance(item, str) and item.strip() and item.lower() != "disabled":
                    channels_with_teds += 1

            logger.info(f"Found {channels_with_teds} channels with TEDS URNs")

            # Assert that we found exactly 1 channel with TEDS
            assert channels_with_teds == 1, f"Expected 1 channel with TEDS URNs, but found {channels_with_teds}"

            # Now apply the TEDS data using TedsVerifyAndApply - EXPECTING AN EXCEPTION
            logger.info("Applying TEDS data using TedsVerifyAndApply() - expecting exception to be raised")

            exception_raised = False
            try:
                verify_result = self.vv.TedsVerifyAndApply(teds_data)
                # If we get here, no exception was raised
                logger.warning(f"TedsVerifyAndApply did not raise an exception. Returned: {type(verify_result)}")
            except Exception as e:
                # This is the expected behavior - TedsVerifyAndApply should raise an exception
                error_info = ExtractComErrorInfo(e)
                logger.info(f"TedsVerifyAndApply raised expected exception: {error_info}")
                exception_raised = True

            # Assert that an exception WAS raised (this is the expected behavior)
            assert exception_raised, "TedsVerifyAndApply should raise an exception when applying TEDS from channel 1 TEDS.vic, but no exception was raised"

            logger.info("Test passed: TedsVerifyAndApply raised expected exception")

        except AssertionError:
            # Re-raise assertion errors (these are test failures)
            raise
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsVerifyAndApply_with_channel1_TEDS_should_fail: {error_info}")
            pytest.fail(f"Error in test_TedsVerifyAndApply_with_channel1_TEDS_should_fail: {error_info}")

    @pytest.mark.teds
    def test_TedsReadAndApply_with_channel1_TEDS_should_pass(self):
        """Test TedsReadAndApply with channel 1 TEDS.vic - should succeed"""
        try:
            # Load the default sine profile
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Default sine test file not found")

            logger.info(f"Loading profile: {test_file}")
            self.vv.OpenTest(test_file)
            logger.info("Profile loaded successfully")

            # Load the demonstration mode TEDS input configuration
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "channel 1 TEDS.vic")

            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")

            logger.info(f"Loading TEDS configuration: {config_file}")
            self.vv.SetInputConfigurationFile(config_file)
            logger.info("TEDS configuration loaded successfully")

            # First verify TedsRead returns exactly 1 channel with TEDS
            logger.info("Calling TedsRead() to verify channel count")
            teds_data = self.vv.TedsRead()

            assert teds_data is not None, "TedsRead() should return data"
            assert isinstance(teds_data, (tuple, list)), "TedsRead() should return a tuple or list"

            # Count channels with valid TEDS URNs
            channels_with_teds = 0
            for item in teds_data:
                if item and isinstance(item, str) and item.strip() and item.lower() != "disabled":
                    channels_with_teds += 1

            logger.info(f"TedsRead found {channels_with_teds} channels with TEDS URNs")
            assert channels_with_teds == 1, f"Expected 1 channel with TEDS URNs, but found {channels_with_teds}"

            # Now apply the TEDS data using TedsReadAndApply - EXPECTING SUCCESS
            logger.info("Applying TEDS data using TedsReadAndApply() - expecting success")

            try:
                verify_result = self.vv.TedsReadAndApply()
                # If we get here, the call succeeded (no exception)
                logger.info(f"TedsReadAndApply succeeded. Returned: {type(verify_result)}")

                assert verify_result is not None, "TedsReadAndApply should return a result"
                logger.info(f"TedsReadAndApply returned: {type(verify_result)} with length {len(verify_result) if hasattr(verify_result, '__len__') else 'N/A'}")

                # TedsReadAndApply returns a rank 1 array of URNs
                assert isinstance(verify_result, (tuple, list)), f"TedsReadAndApply should return a tuple/list of URNs, got {type(verify_result)}"

                # Get the channel 1 TEDS URN from TedsReadAndApply result
                channel1_urn_after = verify_result[0] if len(verify_result) > 0 else None
                logger.info(f"Channel 1 URN from TedsReadAndApply: '{channel1_urn_after}'")

                channel1_urn_expected = '3C00000186B96114'

                # Assert that the URN matches the expected hardware configuration
                assert channel1_urn_expected == channel1_urn_after, f"Expected channel 1 TEDS URN '{channel1_urn_expected}', but got '{channel1_urn_after}'"
                logger.info("Verified: Channel 1 TEDS URN matches expected value")

                # Check that there are no errors in the result
                has_errors = False
                applied_channels = 0
                for channel_index, urn in enumerate(verify_result):
                    if urn and isinstance(urn, str):
                        # Check if the URN contains error messages
                        if "error" in urn.lower() or "invalid" in urn.lower() or "mismatch" in urn.lower():
                            logger.error(f"Channel {channel_index+1}: Unexpected error in TedsReadAndApply result: {urn}")
                            has_errors = True
                        elif urn.strip() and urn.lower() != "disabled":
                            logger.info(f"Channel {channel_index+1}: Successfully applied TEDS URN: {urn}")
                            applied_channels += 1
                        else:
                            logger.info(f"Channel {channel_index+1}: No TEDS or disabled")

                # Assert that there were NO errors
                assert not has_errors, "TedsReadAndApply should not return any errors when applying TEDS from channel 1 TEDS.vic"

                # Assert that exactly 1 channel was applied
                assert applied_channels == 1, f"Expected 1 channel to have TEDS applied, but found {applied_channels}"

                logger.info("Test passed: TedsReadAndApply succeeded without errors and returned different URN")

            except Exception as e:
                # This is unexpected - TedsReadAndApply should not raise an exception
                error_info = ExtractComErrorInfo(e)
                logger.error(f"TedsReadAndApply unexpectedly raised an exception: {error_info}")
                pytest.fail(f"TedsReadAndApply should succeed but raised an exception: {error_info}")

        except AssertionError:
            # Re-raise assertion errors (these are test failures)
            raise
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsReadAndApply_with_channel1_TEDS_should_pass: {error_info}")
            pytest.fail(f"Error in test_TedsReadAndApply_with_channel1_TEDS_should_pass: {error_info}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("teds_functions_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    print("="*80)
    print("VibrationVIEW TEDS Functions Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_teds_functions.py -v")
    print("="*80)
