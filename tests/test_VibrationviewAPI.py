#!/usr/bin/env python
"""
VibrationVIEW Test Application using pytest

This script tests all functions of the VibrationVIEW Python wrapper.
It attempts to exercise every method to verify functionality.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)

Usage:
    pytest test_vibrationview.py -v

Note: Some tests may be skipped if not applicable to the current setup.
"""

import os
import sys
import time
import logging
import pytest
from datetime import datetime

from .channelconfigs import get_channel_config

# Configure logger
logger = logging.getLogger(__name__)

# Get the absolute path of the current file's directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Construct the path to the sibling 'src' directory
src_dir = os.path.join(current_dir, '..', 'src')

# Add the 'src' directory to sys.path
sys.path.append(src_dir)

try:
    # Import main VibrationVIEW API
    from vibrationviewapi import VibrationVIEW, vvVector, vvTestType, ExtractComErrorInfo
    
except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)

class TestVibrationVIEW:
    """Test class for VibrationVIEW pytest implementation"""
    
    @pytest.fixture(autouse=True)
    def _setup(self, vv, wait_for_condition, wait_for_not, find_test_file, script_dir):
        """Setup method that runs before each test method"""
        self.vv = vv
        self.wait_for_condition = wait_for_condition
        self.wait_for_not = wait_for_not
        self.find_test_file = find_test_file
        self.script_dir = script_dir
    
    @pytest.mark.connection
    def test_connection(self):
        """Test connection to VibrationVIEW"""
        assert self.vv is not None
        logger.info("Connection to VibrationVIEW established")
    
    @pytest.mark.connection
    def test_basic_properties(self):
        """Test basic property getters"""
        # Test hardware properties
        inputs = self.vv.GetHardwareInputChannels()
        assert inputs is not None
        assert inputs in [4, 8, 12, 16]
        logger.info(f"Hardware has {inputs} input channels")
      
        outputs = self.vv.GetHardwareOutputChannels()
        assert outputs is not None
        assert outputs in [1, 2, 3, 4]
        logger.info(f"Hardware has {outputs} output channels")
        
        serial = self.vv.GetHardwareSerialNumber()
        assert serial is not None
        logger.info(f"Hardware serial number: {serial}")
        
        version = self.vv.GetSoftwareVersion()
        assert version is not None
        logger.info(f"Software version: {version}")
        
        is_ready = self.vv.IsReady()
        assert is_ready is True
        logger.info("VibrationVIEW is ready")
    
   
    @pytest.mark.channels
    def test_channel_info(self):
        """Test channel information for all available channels"""
        try:
            num_channels = self.vv.GetHardwareInputChannels()
            assert num_channels is not None
            assert num_channels > 0
            logger.info(f"Testing {num_channels} hardware channels")
            
            # Test all available channels
            for channel_index in range(num_channels):
                logger.info(f"Testing channel {channel_index+1}")
                
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
                
                # Try to get sensitivity
                try:
                    sensitivity = self.vv.InputSensitivity(channel_index)
                    assert sensitivity is not None
                    logger.info(f"Channel {channel_index+1} sensitivity: {sensitivity}")
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Channel {channel_index+1} sensitivity: {error_info}")
                    # This might fail for some channels, so just note it
                    pytest.xfail(f"Could not get sensitivity for channel {channel_index+1}")
                
                # Try to get TEDS data
                try:
                    # Create an array to receive the TEDS data
                    teds_array = self.vv.Teds(channel_index)
                    assert teds_array is not None
                    logger.info(f"Channel {channel_index+1} TEDS data: {len(teds_array)} entries")
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Channel {channel_index+1} TEDS data: {error_info}")
                    # This might fail for some channels, so just note it
                    pytest.xfail(f"Could not get TEDS data for channel {channel_index+1}")
                
                # Try to get hardware capabilities
                try:
                    cap_coupled = self.vv.HardwareSupportsCapacitorCoupled(channel_index)
                    assert cap_coupled is not None
                    
                    accel_power = self.vv.HardwareSupportsAccelPowerSource(channel_index)
                    assert accel_power is not None
                    
                    differential = self.vv.HardwareSupportsDifferential(channel_index)
                    assert differential is not None
                    
                    logger.info(f"Channel {channel_index+1} capabilities: cap_coupled={cap_coupled}, accel_power={accel_power}, differential={differential}")
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.error(f"Error getting hardware capabilities: {error_info}")
                    pytest.fail(f"Error getting hardware capabilities: {error_info}")
                    
                # Get additional channel information if available
                try:
                    # Try to get serial number
                    serial = self.vv.InputSerialNumber(channel_index)
                    assert serial is not None
                    logger.info(f"Channel {channel_index+1} serial: {serial}")
                    
                    # Try to get calibration date
                    cal_date = self.vv.InputCalDate(channel_index)
                    assert cal_date is not None
                    logger.info(f"Channel {channel_index+1} cal date: {cal_date}")
                    
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
                    
                    logger.info(f"Channel {channel_index+1} settings: cap={cap_status}, power={power_status}, diff={diff_status}, scale={eng_scale}")
                except Exception as e:
                    error_info = ExtractComErrorInfo(e)
                    logger.warning(f"Error getting additional channel information: {error_info}")
                    # This might fail for some channels, so just note it
                    pytest.xfail(f"Could not get additional info for channel {channel_index+1}")
                    
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_channel_info: {error_info}")
            pytest.fail(f"Error in test_channel_info: {error_info}")
    
    @pytest.mark.control
    def test_test_control(self):
        """Test test control functions"""
        # Get current status
        try:
            status = self.vv.Status()
            assert status is not None
            logger.info(f"Test status: {status}")
            
            running = self.vv.IsRunning()
            assert running is not None
            
            starting = self.vv.IsStarting()
            assert starting is not None
            
            changing_level = self.vv.IsChangingLevel()
            assert changing_level is not None
            
            hold_level = self.vv.IsHoldLevel()
            assert hold_level is not None
            
            open_loop = self.vv.IsOpenLoop()
            assert open_loop is not None
            
            aborted = self.vv.IsAborted()
            assert aborted is not None
            
            logger.info(f"Test state: running={running}, starting={starting}, changing_level={changing_level}, hold_level={hold_level}, open_loop={open_loop}, aborted={aborted}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error getting test status: {error_info}")
            pytest.fail(f"Error getting test status: {error_info}")
        
        logger.info("Stopping any active test")
        self.vv.StopTest()

        # Test starting and stopping if not already running
        running = self.wait_for_not(self.vv.IsRunning)
        time.sleep(1)
        if not running:
            try:
                # Start test
                logger.info("Starting test")
                self.vv.StartTest()
                
                # Check if starting
                logger.info("Waiting for test to enter 'starting' state")
                starting = self.wait_for_condition(self.vv.IsStarting)
                assert starting is True
                logger.info("Test entered 'starting' state")

                # Wait up to 5 seconds for IsRunning
                logger.info("Waiting for test to enter 'running' state")
                running = self.wait_for_condition(self.vv.IsRunning)
                if running:
                    logger.info("Test entered 'running' state")
                else:
                    logger.warning("Test did not enter 'running' state within timeout")

                # Stop test
                logger.info("Stopping test")
                self.vv.StopTest()
                
                # Check if stopped
                logger.info("Waiting for test to stop")
                running = self.wait_for_not(self.vv.IsRunning)
                assert not running  # Should be False when test is stopped
                logger.info("Test stopped successfully")
            except Exception as e:
                error_info = ExtractComErrorInfo(e)
                logger.error(f"Error in test start/stop: {error_info}")
                pytest.fail(f"Error in test start/stop: {error_info}")
        else:
            logger.warning("Test already running, skipping start/stop test")
            pytest.skip("Test already running, skipping start/stop test")
        
        logger.info("Ensuring test is stopped")
        self.vv.StopTest()
    
    
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("vibrationview_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("="*80)
    print("VibrationVIEW Python Wrapper Test with pytest")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest test_VibrationviewAPI.py -v")
    print("="*80)
