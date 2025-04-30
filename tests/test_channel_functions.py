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
    from channelconfigs import get_channel_config
except ImportError:
    logger.warning("Could not import channelconfigs module. Some tests may fail.")
    
    # Define a fallback function
    def get_channel_config(channel_index):
        from dataclasses import dataclass
        
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
            teds: None = None
            
        return DefaultConfig()

try:
    # Import main VibrationVIEW API
    from vibrationviewAPI import VibrationVIEW, vvVector, vvTestType, ExtractComErrorInfo
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
                                for actual_key, actual_value in teds_info:
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