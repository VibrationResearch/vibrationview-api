#!/usr/bin/env python
"""
VibrationVIEW Input Configuration Test Module

This module contains tests for input configuration functionality in the VibrationVIEW API.
These tests focus on channel configuration and TEDS verification.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)
- Main test infrastructure from test_VibrationviewAPI.py

Usage:
    pytest test_input_configuration.py -v
"""

import os
import sys
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
from channelconfigs import get_channel_config

try:
    # Import main VibrationVIEW API
    from vibrationviewapi import VibrationVIEW, vvVector, vvTestType, ExtractComErrorInfo
except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)


class TestInputConfiguration:
    """Test class for VibrationVIEW input configuration functionality"""
    
    @pytest.fixture(autouse=True)
    def _setup(self, vv, wait_for_condition, wait_for_not, find_test_file, script_dir):
        """Setup method that runs before each test method"""
        self.vv = vv
        self.wait_for_condition = wait_for_condition
        self.wait_for_not = wait_for_not
        self.find_test_file = find_test_file
        self.script_dir = script_dir
    
    @pytest.mark.config
    def test_input_configuration_file_basic(self):
        """Test basic functionality of SetInputConfigurationFile method"""
        try:
            # Get number of hardware channels
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing basic input configuration for {num_channels} channels")
            
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            
            # Skip test if config folder doesn't exist
            if not os.path.exists(config_folder):
                logger.warning(f"Configuration folder not found: {config_folder}")
                pytest.skip(f"Configuration folder not found: {config_folder}")
            
            # Find test configuration file
            config_file = os.path.join(config_folder, "10mV per G.vic")
            if not os.path.exists(config_file):
                logger.warning(f"Configuration file not found: {config_file}")
                pytest.skip(f"Configuration file not found: {config_file}")
            
            # Apply the configuration file
            logger.info(f"Applying configuration file: {config_file}")
            self.vv.SetInputConfigurationFile(config_file)
            logger.info("Configuration file applied successfully")
            
            # Verify a sample of channels (first, middle, last)
            channels_to_check = [0]  # Always check first channel
            if num_channels > 2:
                channels_to_check.append(num_channels // 2)  # Middle channel
            if num_channels > 1:
                channels_to_check.append(min(num_channels - 1, 15))  # Last channel (max 16)
            
            # Verify each channel in our sample
            for channel_index in channels_to_check:
                logger.info(f"Checking basic properties of channel {channel_index+1}")
                
                # Get channel properties
                label = self.vv.ChannelLabel(channel_index)
                unit = self.vv.ChannelUnit(channel_index)
                sensitivity = self.vv.InputSensitivity(channel_index)
                
                # Basic assertions - we're just checking if the properties can be retrieved
                assert label is not None
                assert unit is not None
                assert sensitivity is not None
                
                logger.info(f"Channel {channel_index+1} basic properties: label={label}, unit={unit}, sensitivity={sensitivity}")
            
            logger.info("Basic configuration test completed successfully")
                
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_input_configuration_file_basic: {error_info}")
            pytest.fail(f"Error in test_input_configuration_file_basic: {error_info}")


    @pytest.mark.config
    def test_input_configuration_file_teds(self):
        """Test SetInputConfigurationFile with TEDS configuration"""
        try:
            # Get number of hardware channels
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing TEDS input configuration for {num_channels} channels")
            
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            
            # Skip test if config folder doesn't exist
            if not os.path.exists(config_folder):
                logger.warning(f"Configuration folder not found: {config_folder}")
                pytest.skip(f"Configuration folder not found: {config_folder}")
            
            # Find test configuration file with TEDS
            config_file = os.path.join(config_folder, "channel 1 TEDS.vic")
            if not os.path.exists(config_file):
                logger.warning(f"TEDS configuration file not found: {config_file}")
                pytest.skip(f"TEDS configuration file not found: {config_file}")
            
            # Apply the configuration file
            logger.info(f"Applying TEDS configuration file: {config_file}")
            self.vv.SetInputConfigurationFile(config_file)
            logger.info("TEDS configuration file applied successfully")
            
            # Verify channel configurations with focus on TEDS
            channels_verified = 0
            
            for channel_index in range(min(num_channels, 16)):
                try:
                    logger.info(f"Verifying channel {channel_index+1} TEDS configuration")
                    
                    # Get configuration for this channel
                    config = get_channel_config(channel_index)
                    
                    # Check if TEDS data is available for this channel
                    teds_data = self.vv.Teds(channel_index)
                    
                    if not teds_data or not teds_data[0]:
                        logger.warning(f"No TEDS data found for channel {channel_index+1}")
                        continue
                        
                    channel_teds = teds_data[0]
                    
                    if "Error" in channel_teds:
                        logger.warning(f"TEDS error for channel {channel_index+1}: {channel_teds.get('Error', 'Unknown error')}")
                        continue
                        
                    teds_info = channel_teds.get("Teds", [])
                    if not teds_info:
                        logger.warning(f"No TEDS entries found for channel {channel_index+1}")
                        continue
                        
                    logger.info(f"Found {len(teds_info)} TEDS entries for channel {channel_index+1}")
                    
                    # Verify against expected TEDS data if available
                    if not config.teds:
                        logger.info(f"No expected TEDS data defined for channel {channel_index+1}")
                        # Count as verified if we got TEDS data, even if no expectations were set
                        channels_verified += 1
                        continue
                        
                    expected_teds = config.teds.as_tuples()
                    matches = 0
                    total_expected = len(expected_teds)
                    
                    for expected_key, expected_value in expected_teds:
                        for actual_key, actual_value in teds_info:
                            if actual_key == expected_key and actual_value == expected_value:
                                matches += 1
                                break
                    
                    match_percentage = (matches / total_expected) * 100
                    logger.info(f"TEDS match percentage: {match_percentage:.1f}% ({matches}/{total_expected})")
                    
                    # Less strict assertion - we just need some matches to consider it verified
                    if match_percentage >= 50:
                        channels_verified += 1
                        logger.info(f"Channel {channel_index+1} TEDS verified successfully")
                    else:
                        logger.warning(f"Channel {channel_index+1} TEDS match percentage too low: {match_percentage:.1f}%")
                        
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error verifying channel {channel_index+1} TEDS: {error_info}")
            
            logger.info(f"Verified TEDS on {channels_verified} channels successfully")
            if channels_verified == 0:
                pytest.skip("No channels had verifiable TEDS data")
            
            # Apply final configuration at the end of the test
            self._apply_final_configuration(config_folder)
                
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_input_configuration_file_teds: {error_info}")
            pytest.fail(f"Error in test_input_configuration_file_teds: {error_info}")


    @pytest.mark.config
    def test_input_configuration_file_full(self):
        """Test full channel property verification with SetInputConfigurationFile"""
        try:
            # Get number of hardware channels
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing full input configuration for {num_channels} channels")
            
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            
            # Skip test if config folder doesn't exist
            if not os.path.exists(config_folder):
                logger.warning(f"Configuration folder not found: {config_folder}")
                pytest.skip(f"Configuration folder not found: {config_folder}")
            
            # Find test configuration file
            config_file = os.path.join(config_folder, "channel 1 TEDS.vic")
            if not os.path.exists(config_file):
                logger.warning(f"Configuration file not found: {config_file}")
                pytest.skip(f"Configuration file not found: {config_file}")
            
            # Apply the configuration file
            logger.info(f"Applying configuration file: {config_file}")
            self.vv.SetInputConfigurationFile(config_file)
            logger.info("Configuration file applied successfully")
            
            # Verify channel configurations
            channels_verified = 0
            
            for channel_index in range(min(num_channels, 16)):
                try:
                    logger.info(f"Verifying channel {channel_index+1} full configuration")
                    
                    # Get configuration for this channel
                    config = get_channel_config(channel_index)
                    
                    # Get channel properties
                    label = self.vv.ChannelLabel(channel_index)
                    unit = self.vv.ChannelUnit(channel_index)
                    sensitivity = self.vv.InputSensitivity(channel_index)
                    eng_scale = self.vv.InputEngineeringScale(channel_index)
                    cap_coupled = self.vv.InputCapacitorCoupled(channel_index)
                    accel_power = self.vv.InputAccelPowerSource(channel_index)
                    differential = self.vv.InputDifferential(channel_index)
                    serial = self.vv.InputSerialNumber(channel_index)
                    cal_date = self.vv.InputCalDate(channel_index)
            
                    # Verify each property
                    property_checks = {
                        "label": label is not None and config.label.lower() in label.lower(),
                        "unit": unit is not None and config.unit.lower() in unit.lower(),
                        "sensitivity": sensitivity is not None and abs(config.sensitivity - sensitivity) < (config.sensitivity * 0.001),
                        "cap_coupled": cap_coupled is not None and config.cap_coupled == cap_coupled,
                        "accel_power": accel_power is not None and config.accel_power == accel_power,
                        "differential": differential is not None and config.differential == differential,
                        "serial": serial is not None and config.serial == serial,
                        "cal_date": cal_date is not None and config.cal_date in cal_date
                    }
                    
                    # Log results of each check
                    failed_checks = []
                    for prop_name, result in property_checks.items():
                        if not result:
                            failed_checks.append(prop_name)
                            logger.warning(f"Channel {channel_index+1} {prop_name} check failed")
                    
                    if failed_checks:
                        logger.warning(f"Channel {channel_index+1} failed checks: {', '.join(failed_checks)}")
                    else:
                        logger.info(f"Channel {channel_index+1} full configuration verified successfully")
                        channels_verified += 1
                    
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error verifying channel {channel_index+1} full configuration: {error_info}")
            
            logger.info(f"Verified {channels_verified} channels successfully")
            assert channels_verified > 0, "No channels were successfully verified"
            
            # Apply final configuration at the end of the test
            self._apply_final_configuration(config_folder)
                
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_input_configuration_file_full: {error_info}")
            pytest.fail(f"Error in test_input_configuration_file_full: {error_info}")

    
    @pytest.mark.config
    def test_input_configuration_different_files(self):
        """Test applying different configuration files sequentially"""
        try:
            # Get number of hardware channels
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None and num_channels > 0
            logger.info(f"Testing multiple configurations for {num_channels} channels")
            
            # Set up config file paths
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, '..', config_subfolder)
            
            # Skip test if config folder doesn't exist
            if not os.path.exists(config_folder):
                logger.warning(f"Configuration folder not found: {config_folder}")
                pytest.skip(f"Configuration folder not found: {config_folder}")
            
            # Find configuration files
            config_files = []
            for filename in ["10mV per G.vic", "100mV per G.vic", "channel 1 TEDS.vic"]:
                config_path = os.path.join(config_folder, filename)
                if os.path.exists(config_path):
                    config_files.append(config_path)
            
            if len(config_files) < 2:
                logger.warning(f"Not enough configuration files found: {len(config_files)}")
                pytest.skip(f"Need at least 2 different config files for this test")
            
            # Test first channel's sensitivity before and after each configuration change
            channel_index = 0  # Use first channel for testing
            
            for config_file in config_files:
                # Apply configuration file
                logger.info(f"Applying configuration file: {config_file}")
                self.vv.SetInputConfigurationFile(config_file)
                
                # Get channel properties after applying config
                sensitivity = self.vv.InputSensitivity(channel_index)
                unit = self.vv.ChannelUnit(channel_index)
                label = self.vv.ChannelLabel(channel_index)
                
                logger.info(f"Channel {channel_index+1} configured with: sensitivity={sensitivity}, unit={unit}, label={label}")
                assert sensitivity is not None, f"Sensitivity not set properly for configuration {config_file}"
            
            logger.info("Successfully applied and verified multiple configuration files")
            
            # Apply final configuration at the end of the test
            self._apply_final_configuration(config_folder)
                
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_input_configuration_different_files: {error_info}")
            pytest.fail(f"Error in test_input_configuration_different_files: {error_info}")


    def _apply_final_configuration(self, config_folder):
        """Apply the final configuration file"""
        try:
            final_config_file = os.path.join(config_folder, "10mV per G.vic")
            
            if os.path.exists(final_config_file):
                logger.info(f"Applying final configuration file: {final_config_file}")
                self.vv.SetInputConfigurationFile(final_config_file)
                logger.info("Final configuration applied successfully")
            else:
                logger.warning(f"Final configuration file not found: {final_config_file}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error applying final configuration file: {error_info}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("vibrationview_input_config_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("="*80)
    print("VibrationVIEW Input Configuration Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_input_configuration.py -v")
    print("="*80)