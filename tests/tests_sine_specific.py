#!/usr/bin/env python
"""
VibrationVIEW Sine Tests

This module contains tests for sine-specific functions of the VibrationVIEW Python wrapper.
It tests various sine sweep functions and parameters to verify functionality.

Prerequisites:
- VibrationVIEW software installed
- PyWin32 library installed (pip install pywin32)
- pytest library installed (pip install pytest)

Usage:
    pytest sine_tests.py -v
"""

import os
import sys
import time
import logging
import pytest

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
    from vibrationviewAPI import VibrationVIEW, vvTestType, ExtractComErrorInfo
    
except ImportError:
    pytest.skip("Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.", allow_module_level=True)

class TestVibrationVIEWSine:
    """Test class for VibrationVIEW Sine functions"""
    
    @pytest.fixture(autouse=True)
    def _setup(self, vv, wait_for_condition, wait_for_not, find_test_file):
        """Setup method that runs before each test method"""
        self.vv = vv
        self.wait_for_condition = wait_for_condition
        self.wait_for_not = wait_for_not
        self.find_test_file = find_test_file
    
    @pytest.mark.connection
    def test_connection(self):
        """Test connection to VibrationVIEW"""
        assert self.vv is not None
        logger.info("Connection to VibrationVIEW established")
    
    @pytest.mark.sine
    def test_load_sine_test(self):
        """Test loading a sine test file"""
        try:
            test_type = self.vv.TestType()
            if test_type != vvTestType.TEST_SINE:
                # Try to open a sine test
                logger.info("Current test is not SINE, trying to find a SINE test")
                sine_test = self.find_test_file("sine")
                if sine_test:
                    try:
                        logger.info(f"Opening SINE test: {sine_test}")
                        self.vv.OpenTest(sine_test)
                        test_type = self.vv.TestType()
                        if test_type != vvTestType.TEST_SINE:
                            logger.warning("Opened file is not a SINE test")
                            pytest.skip("Could not open a sine test, skipping sine-specific tests")
                        logger.info("Successfully opened SINE test")
                    except Exception as e:
                        error_info = ExtractComErrorInfo(e)
                        logger.error(f"Could not open SINE test: {error_info}")
                        pytest.skip("Could not open a sine test, skipping sine-specific tests")
                else:
                    logger.warning("No SINE test found")
                    pytest.skip("No sine test available, skipping sine-specific tests")
            else:
                logger.info("Current test is already SINE, test file loading not needed")
            
            # Verify it's a sine test
            test_type = self.vv.TestType()
            assert test_type == vvTestType.TEST_SINE
            logger.info("Confirmed current test is a SINE test")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_load_sine_test: {error_info}")
            pytest.fail(f"Error in test_load_sine_test: {error_info}")
    
    @pytest.mark.sine
    def test_sine_frequency(self):
        """Test sine frequency getters"""
        # First ensure we have a sine test
        try:
            self.test_load_sine_test()
            
            # Get sine frequency
            freq = self.vv.SineFrequency()
            assert freq is not None
            logger.info(f"SINE frequency: {freq} Hz")
            
            # Test min and max frequencies if applicable
            if hasattr(self.vv, 'GetMinimumFrequency'):
                min_freq = self.vv.GetMinimumFrequency()
                assert min_freq is not None
                logger.info(f"Minimum frequency: {min_freq} Hz")
            
            if hasattr(self.vv, 'GetMaximumFrequency'):
                max_freq = self.vv.GetMaximumFrequency()
                assert max_freq is not None
                logger.info(f"Maximum frequency: {max_freq} Hz")
                
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_sine_frequency: {error_info}")
            pytest.fail(f"Error in test_sine_frequency: {error_info}")
    
    @pytest.mark.sine
    def test_sweep_multiplier(self):
        """Test sweep multiplier getter and setter"""
        # First ensure we have a sine test
        try:
            self.test_load_sine_test()
            
            # Get sweep multiplier
            sweep_mult = self.vv.SweepMultiplier()
            assert sweep_mult is not None
            logger.info(f"Sweep multiplier: {sweep_mult}")
            
            # Set sweep multiplier 
            if sweep_mult is not None:
                new_sweep_mult = sweep_mult * 0.5
                logger.info(f"Setting sweep multiplier to: {new_sweep_mult}")
                self.vv.SweepMultiplier(new_sweep_mult)  # Set to test setter
                updated_sweep_mult = self.vv.SweepMultiplier()
                assert updated_sweep_mult is not None
                assert abs(new_sweep_mult - updated_sweep_mult) < 0.0001  # Compare with tolerance
                logger.info(f"Sweep multiplier successfully set to: {updated_sweep_mult}")
                
                # Set back to original value
                logger.info(f"Setting sweep multiplier back to: {sweep_mult}")
                self.vv.SweepMultiplier(sweep_mult)
                restored_sweep_mult = self.vv.SweepMultiplier()
                assert abs(sweep_mult - restored_sweep_mult) < 0.0001  # Compare with tolerance
                logger.info(f"Sweep multiplier successfully restored to: {restored_sweep_mult}")
                
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_sweep_multiplier: {error_info}")
            pytest.fail(f"Error in test_sweep_multiplier: {error_info}")
    
    @pytest.mark.sine
    def test_demand_multiplier(self):
        """Test demand multiplier getter and setter"""
        # First ensure we have a sine test
        try:
            self.test_load_sine_test()
            
            # Start test if not running
            if not self.vv.IsRunning():
                logger.info("Starting test for demand multiplier test")
                self.vv.StartTest()
                
                # Wait for test to enter running state
                running = self.wait_for_condition(self.vv.IsRunning)
                if not running:
                    logger.warning("Test did not enter running state, skipping demand multiplier test")
                    pytest.skip("Test did not enter running state")
            
            # Get demand multiplier
            demand_mult = self.vv.DemandMultiplier()
            assert demand_mult is not None
            logger.info(f"Demand multiplier: {demand_mult} dB")

            # Set demand multiplier 
            if demand_mult is not None:
                # Save original value to restore later
                original_demand_mult = demand_mult
                
                # Set to test value
                new_demand_mult = 1.0  # dB
                logger.info(f"Setting demand multiplier to: {new_demand_mult} dB")
                self.vv.DemandMultiplier(new_demand_mult)
                updated_demand_mult = self.vv.DemandMultiplier()
                assert updated_demand_mult is not None
                assert abs(new_demand_mult - updated_demand_mult) < 0.0001  # Compare with tolerance
                logger.info(f"Demand multiplier successfully set to: {updated_demand_mult} dB")
                
                # Set back to original value
                logger.info(f"Setting demand multiplier back to: {original_demand_mult} dB")
                self.vv.DemandMultiplier(original_demand_mult)
                restored_demand_mult = self.vv.DemandMultiplier()
                assert abs(original_demand_mult - restored_demand_mult) < 0.0001  # Compare with tolerance
                logger.info(f"Demand multiplier successfully restored to: {restored_demand_mult} dB")
                
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_demand_multiplier: {error_info}")
            pytest.fail(f"Error in test_demand_multiplier: {error_info}")
    
    @pytest.mark.sine
    def test_sweep_commands(self):
        """Test sine sweep commands"""
        # First ensure we have a sine test
        try:
            self.test_load_sine_test()
            
            # Start test if not running
            if not self.vv.IsRunning():
                logger.info("Starting test for sweep commands test")
                self.vv.StartTest()
                
                # Wait for test to enter running state
                running = self.wait_for_condition(self.vv.IsRunning)
                if not running:
                    logger.warning("Test did not enter running state, skipping sweep commands test")
                    pytest.skip("Test did not enter running state")
            
            # Test sweep commands
            logger.info("Test is running, testing sweep commands")
            
            logger.info("Testing SweepHold command")
            self.vv.SweepHold()
            time.sleep(1)  # Give time for command to take effect
            
            logger.info("Testing SweepUp command")
            self.vv.SweepUp()
            time.sleep(1)  # Give time for command to take effect
            
            logger.info("Testing SweepDown command")
            self.vv.SweepDown()
            time.sleep(1)  # Give time for command to take effect
            
            logger.info("Testing SweepStepUp command")
            self.vv.SweepStepUp()
            time.sleep(1)  # Give time for command to take effect
            
            logger.info("Testing SweepStepDown command")
            self.vv.SweepStepDown()
            time.sleep(1)  # Give time for command to take effect
            
            logger.info("Testing SweepResonanceHold command")
            self.vv.SweepResonanceHold()
            time.sleep(1)  # Give time for command to take effect
            
            logger.info("All sweep commands executed successfully")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_sweep_commands: {error_info}")
            pytest.fail(f"Error in test_sweep_commands: {error_info}")
    
    @pytest.mark.sine
    def test_sine_additional_parameters(self):
        """Test additional sine parameters if available"""
        # First ensure we have a sine test
        try:
            self.test_load_sine_test()
            
            # Test various sine parameters if they exist
            
            # Test sweep rate
            if hasattr(self.vv, 'SweepRate'):
                sweep_rate = self.vv.SweepRate()
                assert sweep_rate is not None
                logger.info(f"Sweep rate: {sweep_rate} oct/min")
                
                # Test setting sweep rate
                new_sweep_rate = sweep_rate * 0.8
                logger.info(f"Setting sweep rate to: {new_sweep_rate} oct/min")
                self.vv.SweepRate(new_sweep_rate)
                updated_sweep_rate = self.vv.SweepRate()
                assert abs(new_sweep_rate - updated_sweep_rate) < 0.0001  # Compare with tolerance
                logger.info(f"Sweep rate successfully set to: {updated_sweep_rate} oct/min")
                
                # Restore original value
                self.vv.SweepRate(sweep_rate)
            
            # Test tone duration (if available)
            if hasattr(self.vv, 'ToneDuration'):
                tone_duration = self.vv.ToneDuration()
                assert tone_duration is not None
                logger.info(f"Tone duration: {tone_duration} sec")
            
            # Test sweep direction (if available)
            if hasattr(self.vv, 'SweepDirection'):
                sweep_direction = self.vv.SweepDirection()
                assert sweep_direction is not None
                logger.info(f"Sweep direction: {sweep_direction}")
            
            # Test tracking filter params (if available)
            if hasattr(self.vv, 'TrackingFilterBandwidth'):
                tracking_bw = self.vv.TrackingFilterBandwidth()
                assert tracking_bw is not None
                logger.info(f"Tracking filter bandwidth: {tracking_bw}")
            
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in test_sine_additional_parameters: {error_info}")
            pytest.fail(f"Error in test_sine_additional_parameters: {error_info}")
    
    def teardown_method(self):
        """Clean up after each test method"""
        # If test is running, stop it
        if hasattr(self, 'vv') and self.vv is not None and self.vv.IsRunning():
            logger.info("Stopping test after SINE tests")
            self.vv.StopTest()
            self.wait_for_not(self.vv.IsRunning)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("sine_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("="*80)
    print("VibrationVIEW Sine Tests")
    print("="*80)
    print("Run this file with pytest:")
    print("    pytest sine_tests.py -v")
    print("="*80)
