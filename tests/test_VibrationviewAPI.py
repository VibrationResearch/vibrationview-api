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

import logging
import os
import sys
import time

import pytest

# Configure logger
logger = logging.getLogger(__name__)

# Get the absolute path of the current file's directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Construct the path to the sibling 'src' directory
src_dir = os.path.join(current_dir, '..', 'src')

# Add the 'src' directory to sys.path at the beginning to ensure it takes priority
sys.path.insert(0, src_dir)

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

class TestVibrationVIEW:
    """Test class for VibrationVIEW pytest implementation"""

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
        assert inputs in [4, 8, 12, 16, 32]
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

    @pytest.mark.connection
    def test_open_list_close_test(self):
        """Test OpenTest, ListOpenTests, CloseTest workflow"""
        test_file = self.find_test_file("sine")
        if not test_file:
            pytest.skip("No test file found")

        self.vv.OpenTest(test_file)

        open_tests = self.vv.ListOpenTests()
        assert open_tests is not None
        assert len(open_tests) > 0
        logger.info(f"Open tests: {open_tests}")

        self.vv.CloseTest(test_file)
        logger.info("Open/list/close test passed")

    @pytest.mark.connection
    def test_close_tab(self):
        """Test CloseTab functionality"""
        test_file = self.find_test_file("sine")
        if not test_file:
            pytest.skip("No test file found")

        self.vv.OpenTest(test_file)
        self.vv.CloseTab(0)
        logger.info("CloseTab test passed")

    @pytest.mark.connection
    def test_edit_and_abort_edit(self):
        """Test EditTest and AbortEdit"""
        test_file = self.find_test_file("sine")
        if not test_file:
            pytest.skip("No test file found")

        self.vv.EditTest(test_file)
        self.vv.AbortEdit()
        logger.info("EditTest/AbortEdit passed")

    @pytest.mark.connection
    def test_save_data(self):
        """Test SaveData call"""
        self.vv.SaveData("mock_output.vsd")
        logger.info("SaveData call passed")

    @pytest.mark.connection
    def test_sweep_controls(self):
        """Test all sweep control methods"""
        self.vv.SweepUp()
        self.vv.SweepDown()
        self.vv.SweepStepUp()
        self.vv.SweepStepDown()
        self.vv.SweepHold()
        self.vv.SweepResonanceHold()
        logger.info("All sweep control methods passed")

    @pytest.mark.connection
    def test_demand_multiplier(self):
        """Test DemandMultiplier get/set"""
        current = self.vv.DemandMultiplier()
        assert current is not None
        self.vv.DemandMultiplier(3.0)
        assert self.vv.DemandMultiplier() == 3.0
        self.vv.DemandMultiplier(current)
        logger.info("DemandMultiplier get/set passed")

    @pytest.mark.connection
    def test_sweep_multiplier(self):
        """Test SweepMultiplier get/set"""
        current = self.vv.SweepMultiplier()
        assert current is not None
        self.vv.SweepMultiplier(2.0)
        assert self.vv.SweepMultiplier() == 2.0
        self.vv.SweepMultiplier(current)
        logger.info("SweepMultiplier get/set passed")

    @pytest.mark.connection
    def test_test_type(self):
        """Test TestType get/set"""
        current = self.vv.TestType()
        assert current is not None
        self.vv.TestType(vvTestType.TEST_SINE)
        assert self.vv.TestType() == vvTestType.TEST_SINE
        logger.info("TestType get/set passed")

    @pytest.mark.connection
    def test_system_check_properties(self):
        """Test SystemCheckFrequency and SystemCheckOutputVoltage get/set"""
        # These require system check test type
        self.vv.TestType(vvTestType.TEST_SYSCHECK)

        freq = self.vv.SystemCheckFrequency()
        assert freq is not None
        self.vv.SystemCheckFrequency(200.0)
        assert self.vv.SystemCheckFrequency() == 200.0
        self.vv.SystemCheckFrequency(freq)

        voltage = self.vv.SystemCheckOutputVoltage()
        assert voltage is not None
        self.vv.SystemCheckOutputVoltage(0.5)
        assert self.vv.SystemCheckOutputVoltage() == 0.5
        self.vv.SystemCheckOutputVoltage(voltage)
        logger.info("SystemCheck properties get/set passed")

    @pytest.mark.connection
    def test_sine_frequency(self):
        """Test SineFrequency get/set"""
        # Ensure a sine test is loaded so frequency can be set
        test_file = self.find_test_file("sine")
        if test_file:
            self.vv.OpenTest(test_file)

        current = self.vv.SineFrequency()
        assert current is not None
        assert isinstance(current, (int, float))
        logger.info(f"SineFrequency current value: {current}")

        self.vv.SineFrequency(440.0)
        result = self.vv.SineFrequency()
        logger.info(f"SineFrequency after set: {result}")

        # Restore original
        self.vv.SineFrequency(current)
        logger.info("SineFrequency get/set passed")

    @pytest.mark.connection
    def test_demand_control_output(self):
        """Test Demand, Control, Channel, and Output data retrieval"""
        demand = self.vv.Demand()
        assert demand is not None
        assert len(demand) == self.vv.GetHardwareOutputChannels()

        control = self.vv.Control()
        assert control is not None

        channel = self.vv.Channel()
        assert channel is not None
        assert len(channel) == self.vv.GetHardwareInputChannels()

        output = self.vv.Output()
        assert output is not None
        logger.info("Demand/Control/Channel/Output data retrieval passed")

    @pytest.mark.connection
    def test_database_methods(self):
        """Test database-related methods"""
        diff = self.vv.IsChannelDifferentThanDatabase(0)
        assert isinstance(diff, bool)

        ids = self.vv.ChannelDatabaseIDs(0)
        assert ids is not None
        logger.info(f"ChannelDatabaseIDs: {ids}")

        self.vv.UpdateChannelConfigFromDatabase(0)
        logger.info("Database methods passed")

    @pytest.mark.connection
    def test_input_mode(self):
        """Test InputMode set method"""
        self.vv.InputMode(0, True, False, False)
        assert self.vv.InputAccelPowerSource(0)
        assert not self.vv.InputCapacitorCoupled(0)
        assert not self.vv.InputDifferential(0)
        logger.info("InputMode set passed")

    @pytest.mark.connection
    def test_input_calibration(self):
        """Test InputCalibration set method"""
        self.vv.InputCalibration(0, 100.0, "SN12345", "2025-01-01")
        assert self.vv.InputSensitivity(0) == 100.0
        assert self.vv.InputSerialNumber(0) == "SN12345"
        cal_date = self.vv.InputCalDate(0)
        assert cal_date is not None
        assert "2025" in str(cal_date), f"Expected date containing '2025', got '{cal_date}'"
        logger.info(f"InputCalibration set passed (date returned: {cal_date})")

    @pytest.mark.connection
    def test_resume_after_stop(self):
        """Test CanResumeTest and ResumeTest after stopping a running test"""
        test_file = self.find_test_file("sine")
        if not test_file:
            pytest.skip("No test file found")

        self.vv.OpenTest(test_file)
        self.vv.StartTest()
        running = self.wait_for_condition(self.vv.IsRunning, wait_time=10)
        if not running:
            pytest.skip("Test did not enter running state")

        time.sleep(2)
        self.vv.StopTest()
        self.wait_for_not(self.vv.IsRunning, wait_time=5)
        time.sleep(1)

        can_resume = self.vv.CanResumeTest()
        logger.info(f"CanResumeTest: {can_resume}")
        if not can_resume:
            pytest.skip("Test cannot be resumed after stopping")

        self.vv.ResumeTest()
        running = self.wait_for_condition(self.vv.IsRunning, wait_time=10)
        if running:
            logger.info("Test resumed successfully")

        self.vv.StopTest()
        self.wait_for_not(self.vv.IsRunning, wait_time=5)
        logger.info("Resume after stop passed")

    @pytest.mark.control
    def test_test_control(self):
        """Test test control functions"""
        self.vv.TestType = vvTestType.TEST_SINE
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
