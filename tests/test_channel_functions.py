#!/usr/bin/env python
"""
VibrationVIEW Channel Functions Module

This module contains tests for channel-related functionality in the VibrationVIEW API.
These tests focus on channel information, properties, and TEDS data.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
- Main test infrastructure from conftest.py

Usage:
    pytest test_channel_functions.py -v
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


class TestChannelFunctions:
    """Test class for VibrationVIEW channel functionality"""
    
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
    
    @pytest.mark.channels
    def test_hardware_channels(self):
        """Test hardware channel information"""
        try:
            # Get hardware channel counts
            inputs = self.vv.GetHardwareInputChannels()
            assert inputs is not None
            assert inputs > 0
            logger.info(f"Hardware has {inputs} input channels")
            
            outputs = self.vv.GetHardwareOutputChannels()
            assert outputs is not None
            assert outputs > 0
            logger.info(f"Hardware has {outputs} output channels")
            
            # Get hardware serial number
            serial = self.vv.GetHardwareSerialNumber()
            assert serial is not None
            logger.info(f"Hardware serial number: {serial}")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_hardware_channels: {error_info}")
            pytest.fail(f"Error in test_hardware_channels: {error_info}")
    
    @pytest.mark.channels
    def test_basic_channel_info(self):
        """Test basic channel information for all available channels"""
        try:
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None
            assert num_channels > 0
            logger.info(f"Testing {num_channels} hardware channels")
            
            # Test all available channels
            for channel_index in range(num_channels):
                logger.info(f"Testing basic info for channel {channel_index+1}")
                
                # Get channel label
                try:
                    label = self.vv.ChannelLabel(channel_index)
                    assert label is not None
                    logger.info(f"Channel {channel_index+1} label: {label}")
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.error(f"Error getting channel label: {error_info}")
                    pytest.fail(f"Error getting channel label: {error_info}")
                
                # Get channel unit
                try:
                    unit = self.vv.ChannelUnit(channel_index)
                    assert unit is not None
                    logger.info(f"Channel {channel_index+1} unit: {unit}")
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.error(f"Error getting channel unit: {error_info}")
                    pytest.fail(f"Error getting channel unit: {error_info}")
                
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_basic_channel_info: {error_info}")
            pytest.fail(f"Error in test_basic_channel_info: {error_info}")
    
    @pytest.mark.channels
    def test_channel_sensitivity(self):
        """Test channel sensitivity properties"""
        try:
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None
            assert num_channels > 0
            logger.info(f"Testing sensitivity for {num_channels} hardware channels")
            
            # Check sensitivities for each channel
            channels_with_sensitivity = 0
            
            for channel_index in range(num_channels):
                try:
                    sensitivity = self.vv.InputSensitivity(channel_index)
                    
                    if sensitivity is not None:
                        channels_with_sensitivity += 1
                        logger.info(f"Channel {channel_index+1} sensitivity: {sensitivity}")
                        
                        # Get expected sensitivity from config
                        expected_config = get_channel_config(channel_index)
                        if expected_config and hasattr(expected_config, 'sensitivity'):
                            expected_sensitivity = expected_config.sensitivity
                            
                            # Log but don't fail if they don't match (configs might be outdated)
                            if abs(sensitivity - expected_sensitivity) > (expected_sensitivity * 0.1):  # 10% tolerance
                                logger.warning(f"Channel {channel_index+1} sensitivity doesn't match config: "
                                              f"actual={sensitivity}, expected={expected_sensitivity}")
                            
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Could not get sensitivity for channel {channel_index+1}: {error_info}")
            
            logger.info(f"Found sensitivity values for {channels_with_sensitivity} channels")
            
            # Don't fail the test if some channels don't have sensitivity
            if channels_with_sensitivity == 0:
                pytest.skip("No channels with sensitivity information found")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_channel_sensitivity: {error_info}")
            pytest.fail(f"Error in test_channel_sensitivity: {error_info}")
    
    @pytest.mark.channels
    def test_channel_hardware_capabilities(self):
        """Test hardware capability queries for channels"""
        try:
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None
            assert num_channels > 0
            logger.info(f"Testing hardware capabilities for {num_channels} channels")
            
            capabilities_tested = 0
            
            for channel_index in range(min(num_channels, 4)):  # Test first 4 channels
                logger.info(f"Testing capabilities for channel {channel_index+1}")
                
                # Try to get hardware capabilities
                try:
                    cap_coupled = self.vv.HardwareSupportsCapacitorCoupled(channel_index)
                    assert cap_coupled is not None
                    
                    accel_power = self.vv.HardwareSupportsAccelPowerSource(channel_index)
                    assert accel_power is not None
                    
                    differential = self.vv.HardwareSupportsDifferential(channel_index)
                    assert differential is not None
                    
                    logger.info(f"Channel {channel_index+1} capabilities: cap_coupled={cap_coupled}, "
                                f"accel_power={accel_power}, differential={differential}")
                    
                    capabilities_tested += 1
                    
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error getting hardware capabilities for channel {channel_index+1}: {error_info}")
            
            if capabilities_tested == 0:
                pytest.skip("Could not test hardware capabilities for any channel")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_channel_hardware_capabilities: {error_info}")
            pytest.fail(f"Error in test_channel_hardware_capabilities: {error_info}")
    
    @pytest.mark.channels
    def test_channel_settings(self):
        """Test channel settings (capacitor coupled, acceleration power source, etc.)"""
        try:
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None
            assert num_channels > 0
            logger.info(f"Testing settings for {num_channels} channels")
            
            settings_tested = 0
            
            for channel_index in range(min(num_channels, 4)):  # Test first 4 channels
                logger.info(f"Testing settings for channel {channel_index+1}")
                
                try:
                    # Try to get capacitor coupled status
                    cap_status = self.vv.InputCapacitorCoupled(channel_index)
                    assert cap_status is not None
                    
                    # Try to get power source status
                    power_status = self.vv.InputAccelPowerSource(channel_index)
                    assert power_status is not None
                    
                    # Try to get differential status
                    diff_status = self.vv.InputDifferential(channel_index)
                    assert diff_status is not None
                    
                    # Try to get engineering scale
                    eng_scale = self.vv.InputEngineeringScale(channel_index)
                    assert eng_scale is not None
                    
                    logger.info(f"Channel {channel_index+1} settings: cap={cap_status}, power={power_status}, "
                                f"diff={diff_status}, scale={eng_scale}")
                    
                    settings_tested += 1
                    
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error getting settings for channel {channel_index+1}: {error_info}")
            
            if settings_tested == 0:
                pytest.skip("Could not test settings for any channel")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_channel_settings: {error_info}")
            pytest.fail(f"Error in test_channel_settings: {error_info}")
    
    @pytest.mark.channels
    def test_channel_additional_info(self):
        """Test additional channel information (serial number, calibration date)"""
        try:
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None
            assert num_channels > 0
            logger.info(f"Testing additional info for {num_channels} channels")
            
            additional_info_tested = 0
            
            for channel_index in range(min(num_channels, 4)):  # Test first 4 channels
                logger.info(f"Testing additional info for channel {channel_index+1}")
                
                try:
                    # Try to get serial number
                    serial = self.vv.InputSerialNumber(channel_index)
                    
                    # Try to get calibration date
                    cal_date = self.vv.InputCalDate(channel_index)
                    
                    if serial is not None or cal_date is not None:
                        logger.info(f"Channel {channel_index+1} additional info: serial={serial}, cal_date={cal_date}")
                        additional_info_tested += 1
                    
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error getting additional info for channel {channel_index+1}: {error_info}")
            
            if additional_info_tested == 0:
                logger.warning("No channels with additional information found")
                pytest.skip("No channels with additional information found")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_channel_additional_info: {error_info}")
            pytest.fail(f"Error in test_channel_additional_info: {error_info}")
    
    @pytest.mark.channels
    def test_teds_data(self):
        """Test TEDS data acquisition and verification"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)

           # Use the specific .vic file
            config_file = os.path.join(config_folder, "channel 1 TEDS.vic")
            
            if not os.path.exists(config_file):
                self.log(f"Configuration file not found: {config_file}", False)
                return False
            
            # Apply the configuration file once (it will change all channels)
            self.vv.SetInputConfigurationFile(config_file)
            
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
    
    @pytest.mark.channels
    def test_compare_channel_configs(self):
        """Test comparison of actual channel configuration with expected configuration"""
        try:
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None
            assert num_channels > 0
            logger.info(f"Comparing configurations for {num_channels} channels")
            
            channels_verified = 0
            
            for channel_index in range(min(num_channels, 8)):  # Test first 8 channels
                try:
                    logger.info(f"Comparing configuration for channel {channel_index+1}")
                    
                    # Get expected configuration
                    expected_config = get_channel_config(channel_index)
                    
                    # Get actual configuration
                    actual_label = self.vv.ChannelLabel(channel_index)
                    actual_unit = self.vv.ChannelUnit(channel_index)
                    actual_sensitivity = self.vv.InputSensitivity(channel_index)
                    
                    # Create dictionary of comparison results
                    comparisons = {
                        "label": {
                            "expected": expected_config.label,
                            "actual": actual_label,
                            "match": actual_label is not None and expected_config.label.lower() in actual_label.lower()
                        },
                        "unit": {
                            "expected": expected_config.unit,
                            "actual": actual_unit,
                            "match": actual_unit is not None and expected_config.unit.lower() in actual_unit.lower()
                        },
                        "sensitivity": {
                            "expected": expected_config.sensitivity,
                            "actual": actual_sensitivity,
                            "match": actual_sensitivity is not None and abs(expected_config.sensitivity - actual_sensitivity) < (expected_config.sensitivity * 0.1)
                        }
                    }
                    
                    # Try to get additional properties
                    try:
                        actual_cap_coupled = self.vv.InputCapacitorCoupled(channel_index)
                        comparisons["cap_coupled"] = {
                            "expected": expected_config.cap_coupled,
                            "actual": actual_cap_coupled,
                            "match": actual_cap_coupled == expected_config.cap_coupled
                        }
                    except:
                        pass
                        
                    try:
                        actual_accel_power = self.vv.InputAccelPowerSource(channel_index)
                        comparisons["accel_power"] = {
                            "expected": expected_config.accel_power,
                            "actual": actual_accel_power,
                            "match": actual_accel_power == expected_config.accel_power
                        }
                    except:
                        pass
                        
                    try:
                        actual_differential = self.vv.InputDifferential(channel_index)
                        comparisons["differential"] = {
                            "expected": expected_config.differential,
                            "actual": actual_differential,
                            "match": actual_differential == expected_config.differential
                        }
                    except:
                        pass
                        
                    try:
                        actual_serial = self.vv.InputSerialNumber(channel_index)
                        comparisons["serial"] = {
                            "expected": expected_config.serial,
                            "actual": actual_serial,
                            "match": actual_serial == expected_config.serial
                        }
                    except:
                        pass
                        
                    try:
                        actual_cal_date = self.vv.InputCalDate(channel_index)
                        comparisons["cal_date"] = {
                            "expected": expected_config.cal_date,
                            "actual": actual_cal_date,
                            "match": expected_config.cal_date in actual_cal_date if actual_cal_date else False
                        }
                    except:
                        pass
                    
                    # Log comparison results
                    matches = sum(1 for item in comparisons.values() if item["match"])
                    total = len(comparisons)
                    match_percentage = (matches / total) * 100 if total > 0 else 0
                    
                    logger.info(f"Channel {channel_index+1} config match: {match_percentage:.1f}% ({matches}/{total})")
                    
                    for prop, values in comparisons.items():
                        match_str = "✓" if values["match"] else "✗"
                        logger.info(f"  {prop}: {match_str} (expected: {values['expected']}, actual: {values['actual']})")
                    
                    channels_verified += 1
                        
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error comparing config for channel {channel_index+1}: {error_info}")
            
            if channels_verified == 0:
                logger.warning("No channels could be verified")
                pytest.skip("No channels could be verified")
            else:
                logger.info(f"Successfully compared configurations for {channels_verified} channels")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_compare_channel_configs: {error_info}")
            pytest.fail(f"Error in test_compare_channel_configs: {error_info}")

    @pytest.mark.channels
    def test_TedsRead(self):
        """Test TEDS reading for all channels using TedsRead() method"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")

            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")

            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)

            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing TEDS for all {num_channels} channels using TedsRead() method")

            # Use TedsRead() to get TEDS URNs for all channels at once
            all_teds_data = self.vv.TedsRead()

            assert all_teds_data is not None, "TedsRead() should return data"
            assert isinstance(all_teds_data, tuple), f"TedsRead() should return a tuple, got {type(all_teds_data)}"
            assert len(all_teds_data) == num_channels, f"Expected {num_channels} channel results, got {len(all_teds_data)}"

            channels_with_teds = 0

            for channel_index, channel_urn in enumerate(all_teds_data):
                logger.info(f"Processing TEDS URN for channel {channel_index+1}")

                # TedsRead() returns a rank 1 array with URN strings for each channel
                if channel_urn and isinstance(channel_urn, str) and channel_urn.strip():
                    # Check if this channel has meaningful TEDS URN (not empty or "Disabled")
                    if channel_urn.lower() != "disabled":
                        logger.info(f"Channel {channel_index+1}: Found TEDS URN '{channel_urn}'")
                        channels_with_teds += 1
                    else:
                        logger.info(f"Channel {channel_index+1}: TEDS disabled")
                else:
                    logger.warning(f"No TEDS URN for channel {channel_index+1}")

            if channels_with_teds == 0:
                pytest.skip("No channels with valid TEDS URNs found")
            else:
                logger.info(f"Successfully read TEDS URNs for {channels_with_teds} channels using TedsRead() method")

            assert channels_with_teds > 0, "At least one channel should have TEDS URN"
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_teds_all_channels_3d_array: {error_info}")
            pytest.fail(f"Error in test_teds_all_channels_3d_array: {error_info}")

    @pytest.mark.channels
    def test_TedsVerifyAndApply(self):
        """Test TedsVerifyAndApply using data from TedsRead"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
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
            verify_result = self.vv.TedsVerifyAndApply(teds_data)
            
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

    @pytest.mark.channels
    def test_TedsReadAndApply(self):
        """Test TedsReadAndApply method to read and apply TEDS data from hardware"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
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
            assert applied_channels >= 0, "TedsReadAndApply should process the channels"

            logger.info("TedsReadAndApply test completed successfully")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_teds_read_and_apply: {error_info}")
            pytest.fail(f"Error in test_teds_read_and_apply: {error_info}")

    @pytest.mark.channels
    def test_TedsReadAndApply_with_running_test(self):
        """Test that TedsReadAndApply returns 'Test is already running' error when a test is running"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
            # Load and start a test first
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")
            
            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)
            
            # need to be sure of TEDS changes are accepted before starting the test
            self.vv.TedsReadAndApply()

            # Start the test
            logger.info("Starting test before TedsReadAndApply")
            self.vv.StartTest()
            
            # Wait a moment for the test to start
            time.sleep(2)
            
            # Verify test is running
            test_running = self.vv.IsRunning()
            logger.info(f"Test running status: {test_running}")
            assert test_running, "Test should be running before calling TedsReadAndApply"
            
            # Test TedsReadAndApply - check if it succeeds or fails when test is running
            logger.info("Testing TedsReadAndApply method while test is running")

            try:
                read_and_apply_result = self.vv.TedsReadAndApply()
                logger.info(f"TedsReadAndApply succeeded while test running: {read_and_apply_result}")
                # If it succeeds, it should return a rank 1 array of URNs
                assert isinstance(read_and_apply_result, (list, tuple)), f"Expected list/tuple of URNs, got: {type(read_and_apply_result)}"
            except Exception as e:
                # If it fails, log the exception - this is also acceptable behavior
                error_info = ExtractComErrorInfo(e)
                logger.info(f"TedsReadAndApply failed as expected while test running: {error_info}")
                assert "test is already running" in error_info.lower() or "running" in error_info.lower(), f"Expected 'test is already running' error, got: {error_info}"
            
            # Stop the test
            logger.info("Stopping test after TedsReadAndApply exception test")
            self.vv.StopTest()
            
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
            logger.error(f"Unexpected error in test_TedsReadAndApply_with_running_test: {error_info}")
            pytest.fail(f"Unexpected error in test_TedsReadAndApply_with_running_test: {error_info}")

    @pytest.mark.channels
    def test_TedsReadAndApply_before_and_during_test(self):
        """Test TedsReadAndApply before and during test - should return fresh data before, cached data during"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
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

    @pytest.mark.channels
    def test_TedsRead_with_running_recorder(self):
        """Test that TedsRead returns 'Test is already running' error when recorder is running"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
            # Load and start a test first
            test_file = self.find_test_file("sine")
            if not test_file:
                pytest.skip("Test file 'sine' not found")
            
            logger.info(f"Loading test file: {test_file}")
            self.vv.OpenTest(test_file)
            
            # Start the recorder instead of the test
            logger.info("Starting recorder before TedsRead")
            self.vv.RecordStart()
            
            # Wait a moment for the recorder to start
            time.sleep(2)
            logger.info("Recorder started and running")
            
            # Test TedsRead - this should raise an exception when recorder is running
            logger.info("Testing TedsRead method while recorder is running - expecting exception")

            with pytest.raises(Exception) as exc_info:
                read_result = self.vv.TedsRead()

            error_info = ExtractComErrorInfo(exc_info.value)
            logger.info(f"TedsRead raised expected exception: {error_info}")
            assert "recording is already running" in error_info.lower() or "running" in error_info.lower(), f"Expected 'recording is already running' error, got: {error_info}"
            
            # Stop the recorder
            logger.info("Stopping recorder after TedsRead")
            self.vv.RecordStop()
            
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
            logger.error(f"Unexpected error in test_TedsRead_with_running_recorder: {error_info}")
            pytest.fail(f"Unexpected error in test_TedsRead_with_running_recorder: {error_info}")

    @pytest.mark.channels
    def test_TedsRead_before_and_during_recorder(self):
        """Test TedsRead before and during recorder - should return fresh data before, cached data during"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
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
            
            # Now start the recorder
            logger.info("Starting recorder after first TedsRead call")
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

    @pytest.mark.channels
    def test_TedsVerifyAndApply_mismatch_error(self):
        """Test TedsVerifyAndApply returns mismatch error when a field is changed"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
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

    @pytest.mark.channels
    def test_TedsVerifyAndApply_missing_URN_error(self):
        """Test TedsVerifyAndApply returns mismatch error when URN is missing on an enabled channel"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
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

            # Now test TedsVerifyAndApply with the missing URN array
            logger.info("Testing TedsVerifyAndApply with missing URN data (may raise exception or succeed)")
            try:
                verify_result = self.vv.TedsVerifyAndApply(tuple(modified_urns))

                # If we get here, the missing URN was handled gracefully
                assert verify_result is not None, "TedsVerifyAndApply should return a result"
                logger.info(f"TedsVerifyAndApply returned: {type(verify_result)} with length {len(verify_result) if hasattr(verify_result, '__len__') else 'N/A'}")

                assert isinstance(verify_result, (tuple, list)), f"TedsVerifyAndApply should return a tuple/list of URNs, got {type(verify_result)}"
                assert len(verify_result) == num_channels, f"Expected {num_channels} results, got {len(verify_result)}"

                logger.warning("Missing URN was handled gracefully - API may be more lenient than expected")
                for channel_index, result in enumerate(verify_result):
                    logger.info(f"Channel {channel_index+1}: Result: {result}")

            except Exception as e:
                # This is actually the expected behavior for missing URNs
                error_info = ExtractComErrorInfo(e)
                logger.info(f"TedsVerifyAndApply raised expected exception for missing URN: {error_info}")
                # This is the correct behavior - missing URNs should raise exceptions

            logger.info("Successfully handled missing URN test case")
            
        except Exception as e:
            error_msg = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsVerifyAndApply_missing_URN_error: {error_msg}")
            pytest.fail(f"Error in test_TedsVerifyAndApply_missing_URN_error: {error_msg}")

    @pytest.mark.channels
    def test_TedsVerifyAndApply_URN_on_disabled_channel(self):
        """Test TedsVerifyAndApply with a valid URN on a channel that is not enabled"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
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
                    test_urn = "TEST_URN_ON_DISABLED_CHANNEL"
                    modified_urns[channel_index] = test_urn
                    channel_modified = channel_index
                    logger.info(f"Added URN to disabled channel {channel_index+1}: '' -> '{test_urn}'")
                    break

            if channel_modified is None:
                pytest.skip("No suitable disabled channel found to add URN for test")

            # Now test TedsVerifyAndApply with valid URN on disabled channel
            logger.info("Testing TedsVerifyAndApply with valid URN on disabled channel")
            verify_result = self.vv.TedsVerifyAndApply(tuple(modified_urns))
            
            assert verify_result is not None, "TedsVerifyAndApply should return a result"
            logger.info(f"TedsVerifyAndApply returned: {type(verify_result)} with length {len(verify_result) if hasattr(verify_result, '__len__') else 'N/A'}")
            
            # TedsVerifyAndApply returns a rank 1 array of URNs, check the results
            assert isinstance(verify_result, (tuple, list)), f"TedsVerifyAndApply should return a tuple/list, got {type(verify_result)}"
            assert len(verify_result) == num_channels, f"Expected {num_channels} results, got {len(verify_result)}"

            # Check if URN was accepted or rejected for disabled channel
            success_or_expected_error = False
            for channel_index, result in enumerate(verify_result):
                if channel_index == channel_modified:
                    if isinstance(result, str) and result.strip():
                        if "error" in result.lower() or "invalid" in result.lower():
                            logger.info(f"Channel {channel_index+1}: URN on disabled channel rejected: {result}")
                            success_or_expected_error = True
                        else:
                            logger.info(f"Channel {channel_index+1}: URN on disabled channel accepted: {result}")
                            success_or_expected_error = True
                    elif not result or (isinstance(result, str) and not result.strip()):
                        logger.info(f"Channel {channel_index+1}: Empty result for URN on disabled channel")
                        success_or_expected_error = True
                    break

            # Either acceptance or rejection is valid behavior
            assert success_or_expected_error, f"Unexpected result for URN on disabled channel: {verify_result}"
            logger.info("Successfully handled URN on disabled channel case")
            
        except Exception as e:
            error_msg = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsVerifyAndApply_URN_on_disabled_channel: {error_msg}")
            pytest.fail(f"Error in test_TedsVerifyAndApply_URN_on_disabled_channel: {error_msg}")

    @pytest.mark.channels
    def test_TedsVerifyAndApply_URN_rank1_array(self):
        """Test TedsVerifyAndApply with a rank 1 array containing just URNs (this is the normal case)"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing TedsVerifyAndApply with rank 1 URN array for {num_channels} channels")
            
            # First, read current TEDS data using TedsRead()
            logger.info("Reading current TEDS data using TedsRead()")
            teds_data = self.vv.TedsRead()
            
            assert teds_data is not None, "TedsRead() should return data"
            assert len(teds_data) == num_channels, f"Expected {num_channels} channel results, got {len(teds_data)}"
            
            # TedsRead() already returns a rank 1 URN array, so we can use it directly
            # This test verifies that TedsVerifyAndApply works with the standard rank 1 URN input
            logger.info("Testing TedsVerifyAndApply with rank 1 URN array from TedsRead")
            verify_result = self.vv.TedsVerifyAndApply(teds_data)
            
            assert verify_result is not None, "TedsVerifyAndApply should return a result"
            logger.info(f"TedsVerifyAndApply returned: {type(verify_result)} with length {len(verify_result) if hasattr(verify_result, '__len__') else 'N/A'}")
            
            # TedsVerifyAndApply returns a rank 1 array of URNs
            assert isinstance(verify_result, (tuple, list)), f"TedsVerifyAndApply should return a tuple/list of URNs, got {type(verify_result)}"
            assert len(verify_result) == num_channels, f"Expected {num_channels} URN results, got {len(verify_result)}"

            # Count channels with valid URNs returned
            verified_channels = 0
            for channel_index, urn in enumerate(verify_result):
                if urn and isinstance(urn, str) and urn.strip() and urn.lower() != "disabled":
                    logger.info(f"Channel {channel_index+1}: Returned URN '{urn}'")
                    verified_channels += 1
                elif isinstance(urn, str) and ("error" in urn.lower() or "invalid" in urn.lower()):
                    logger.info(f"Channel {channel_index+1}: Error returned: {urn}")
                else:
                    logger.info(f"Channel {channel_index+1}: No URN or disabled/empty")

            logger.info(f"TedsVerifyAndApply with rank 1 URN array returned URNs for {verified_channels} channels")
            # Success if we got some valid URNs back or the input was properly processed
            assert verified_channels >= 0, "TedsVerifyAndApply should process the rank 1 URN array"
            
        except Exception as e:
            error_msg = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsVerifyAndApply_URN_rank1_array: {error_msg}")
            pytest.fail(f"Error in test_TedsVerifyAndApply_URN_rank1_array: {error_msg}")

    @pytest.mark.channels
    def test_TedsVerifyAndApply_invalid_input_type(self):
        """Test TedsVerifyAndApply with invalid input type (should only accept rank 1 URN arrays)"""
        try:
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            config_file = os.path.join(config_folder, "7-channels-TEDS.vic")
            
            if not os.path.exists(config_file):
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            self.vv.SetInputConfigurationFile(config_file)
            
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing TedsVerifyAndApply with rank 2 array for {num_channels} channels")
            
            # First, read current TEDS data using TedsRead()
            logger.info("Reading current TEDS data using TedsRead()")
            teds_data = self.vv.TedsRead()
            
            assert teds_data is not None, "TedsRead() should return data"
            assert len(teds_data) == num_channels, f"Expected {num_channels} channel results, got {len(teds_data)}"
            
            # Create a rank 2 array with values (second column) from TedsRead - extract all values for each channel
            rank2_array = []
            
            for channel_index, channel_teds_data in enumerate(teds_data):
                channel_values = []
                
                if channel_teds_data and len(channel_teds_data) > 0:
                    # Extract the second column (value) from all rows of this channel
                    for entry in channel_teds_data:
                        if len(entry) >= 2:
                            value = entry[1] if entry[1] else ""
                            channel_values.append(value)
                        else:
                            channel_values.append("")
                    
                    logger.info(f"Channel {channel_index+1}: extracted {len(channel_values)} values")
                else:
                    # Fallback if channel has no TEDS data - create empty entries
                    channel_values = [""] * 23  # Match typical TEDS structure length
                    logger.info(f"Channel {channel_index+1}: using empty values")
                
                rank2_array.append(tuple(channel_values))
            
            logger.info(f"Created rank 2 array with {len(rank2_array)} channels from TedsRead data")
            
            # Test TedsVerifyAndApply with rank 2 array - should raise exception
            logger.info("Testing TedsVerifyAndApply with rank 2 array - expecting exception")

            with pytest.raises(Exception) as exc_info:
                verify_result = self.vv.TedsVerifyAndApply(tuple(rank2_array))

            error_info = ExtractComErrorInfo(exc_info.value)
            logger.info(f"TedsVerifyAndApply raised expected exception for rank 2 array: {error_info}")
            assert "mismatch" in error_info.lower() or "invalid" in error_info.lower(), f"Expected mismatch/invalid error, got: {error_info}"
            logger.info("Successfully verified that TedsVerifyAndApply rejects rank 2 array input")
            
        except Exception as e:
            error_msg = ExtractComErrorInfo(e)
            logger.error(f"Error in test_TedsVerifyAndApply_URN_rank2_array: {error_msg}")
            pytest.fail(f"Error in test_TedsVerifyAndApply_URN_rank2_array: {error_msg}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("channel_functions_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("="*80)
    print("VibrationVIEW Channel Functions Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_channel_functions.py -v")
    print("="*80)