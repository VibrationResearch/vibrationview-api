#!/usr/bin/env python
"""
VibrationVIEW Test Application

This script tests all functions of the VibrationVIEW Python wrapper.
It attempts to exercise every method to verify functionality.

Prerequisites:
- VibrationVIEW software installed and running
- PyWin32 library installed (pip install pywin32)

Note: Some tests may be skipped if not applicable to the current setup.
"""

import os
import sys
import time
import traceback
from datetime import datetime

# Import the VibrationVIEW wrapper
# Assuming the wrapper is in a file called vibrationview_wrapper.py
# You may need to adjust the import path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
try:
    # Import main VibrationVIEW API
    from vibrationviewAPI import VibrationVIEW, vvVector, vvTestType, ExtractComErrorInfo
    
except ImportError:
    print("Error: Could not import VibrationVIEW API. Make sure they are in the same directory or in your Python path.")
    sys.exit(1)

class VibrationVIEWTester:
    """Test class for VibrationVIEW Python wrapper"""
    
    def __init__(self):
        self.vv = None
        self.results = []
        
        # Get the script directory and use it as base path
        self.script_dir = os.path.abspath(os.path.dirname(__file__))
        
        # Try to find VibrationVIEW test folder
        self.test_folder = os.path.join(self.script_dir, "Profiles")
        
        self.test_files = {
            "sine": "Sine.vsp",
            "random": "Random.vrp",
            "shock": "Shock.vkp",
            "transient": "Transient.vtp",
            "DataReplay": "FDR.vrp"
        }
        
        # Create output directory
        self.output_dir = os.path.join(self.script_dir, "output")
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
        except Exception as e:
            print(f"Warning: Could not create output directory: {e}")
            self.output_dir = self.script_dir
        
        # Create a log file for test results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.output_dir, f"vv_test_results_{timestamp}.txt")
        try:
            with open(self.log_file, "w") as f:
                f.write(f"VibrationVIEW Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 80 + "\n\n")
                f.write(f"Test folder: {self.test_folder}\n\n")
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
            self.log_file = None
       
    def log(self, message, success=None):
        """Log test result to console and file"""
        status = ""
        if success is not None:
            status = "[PASS]" if success else "[FAIL]"
        
        log_message = f"{status} {message}"
        print(log_message)
        
        if self.log_file:
            try:
                with open(self.log_file, "a") as f:
                    f.write(log_message + "\n")
            except Exception as e:
                print(f"Warning: Could not write to log file: {e}")
        
        self.results.append((message, success))
    
    def wait_for_condition(self, condition_func, wait_time=5, check_interval=0.1):
        """
        Wait up to wait_time seconds for condition_func to return True.
        
        Args:
            condition_func: Function that returns a boolean
            wait_time: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            Boolean indicating if condition was met
        """
        import time
        start_time = time.time()
        result = False
        
        while time.time() - start_time < wait_time:
            result = condition_func()
            if result:
                break
            time.sleep(check_interval)
            
        return result
    
    def wait_for_not(self, condition_func, wait_time=5, check_interval=0.1):
        """
        Wait up to wait_time seconds for condition_func to return False.
        
        Args:
            condition_func: Function that returns a boolean
            wait_time: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            Boolean indicating if condition became False (False if condition is now False)
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < wait_time:
            result = condition_func()
            if not result:
                return result
            time.sleep(check_interval)
            
        return True

    def run_test(self, test_name, test_func, *args, **kwargs):
        """Run a test function and log the result"""
        try:
            print(f"\nTesting: {test_name}")
            print("-" * 40)
            result = test_func(*args, **kwargs)
            self.log(f"{test_name} - Completed successfully", True)
            return result
        except Exception as e:
            self.log(f"{test_name} - Failed with error: {ExtractComErrorInfo(e)}", False)
            traceback.print_exc()
            return None
    
    def test_connection(self):
        """Test connection to VibrationVIEW"""
        self.vv = VibrationVIEW()
        if self.vv.vv is None:
            self.log("Connection to VibrationVIEW failed", False)
            return False
        
        self.log("Connected to VibrationVIEW successfully", True)

        return True
    
    def test_basic_properties(self):
        """Test basic property getters"""
        # Test hardware properties
        inputs = self.vv.GetHardwareInputChannels()
        self.log(f"Hardware input channels: {inputs}", (inputs is not None) and inputs in [4, 8, 12, 16])
      
        outputs = self.vv.GetHardwareOutputChannels()
        self.log(f"Hardware output channels: {outputs}", (outputs is not None) and outputs in [1, 2, 3, 4])
        
        serial = self.vv.GetHardwareSerialNumber()
        self.log(f"Hardware serial number: {serial:X}", serial is not None)
        self.log(f"Running demo mode: {serial:X}", (serial is not None) and (serial == 0xffffff))

        version = self.vv.GetSoftwareVersion()
        self.log(f"Software version: {version}", version is not None)
        
        is_ready = self.vv.IsReady()
        self.log(f"VibrationVIEW ready: {is_ready}", is_ready is True)
        
        return True
    
    def test_window_control(self):
        """Test window control functions"""
        # Maximize
        self.vv.Maximize()
        self.log("Window maximized", True)
        time.sleep(1)

        # Minimize
        self.vv.Minimize()
        self.log("Window minimized", True)
        time.sleep(1)
        
        # Restore
        self.vv.Restore()
        self.log("Window restored", True)
        time.sleep(1)
        
        # Restore (second time should drop the maximized)
        self.vv.Restore()
        self.log("Window restored Again", True)

        # Activate
        self.vv.Activate()
        self.log("Window activated", True)
        time.sleep(1)
        
        return True
    
    def find_test_file(self, test_type):
        """Find an appropriate test file for the specified test type"""
        if test_type in self.test_files:
            test_file = os.path.join(self.test_folder, self.test_files[test_type])
            if os.path.exists(test_file):
                return test_file
        
        # Try to find any test file with the appropriate extension
        if os.path.exists(self.test_folder):
            # Get the extension for the requested test type
            ext = None
            if test_type in self.test_files:
                ext = os.path.splitext(self.test_files[test_type])[1]
            
            # Search for files with that extension
            if ext:
                for file in os.listdir(self.test_folder):
                    if file.lower().endswith(ext.lower()):
                        return os.path.join(self.test_folder, file)
            
            # If no file with specific extension found, try any known extension
            for file in os.listdir(self.test_folder):
                for _, test_file in self.test_files.items():
                    if file.lower().endswith(os.path.splitext(test_file)[1].lower()):
                        return os.path.join(self.test_folder, file)
        
        # If no specific file found, return the first available one
        default_test = next(iter(self.test_files.values()), None)
        if default_test:
            return os.path.join(self.test_folder, default_test)
        
        return None
    
    def test_file_operations(self):
        """Test file operations (open, save)"""
        # Find a test file
        test_file = self.find_test_file("sine")
        if not test_file:
            self.log("No test file found for testing", False)
            return False
        
        # Open the test
        self.log(f"Attempting to open test file: {test_file}")
        try:
            self.vv.OpenTest(test_file)
            self.log(f"Test file opened: {test_file}", True)
        except Exception as e:
            self.log(f"Opening test file failed: {ExtractComErrorInfo(e)}", False)

        self.log(f"Attempting to open and run test file: {test_file}")
        try:
            self.vv.RunTest(test_file)
            self.log(f"Test file run: {test_file}", True)
        except Exception as e:
            self.log(f"Running test file failed: {ExtractComErrorInfo(e)}", False)
            return False
        
        # Get test type
        try:
            test_type = self.vv.TestType()
            test_type_name = vvTestType.get_name(test_type) if test_type is not None else "Unknown"
            self.log(f"Test type: {test_type_name}", test_type is not None)
        except Exception as e:
            self.log(f"Getting test type failed: {ExtractComErrorInfo(e)}", False)
        
        # Save data if possible
        try:
            # Create a data directory if it doesn't exist
            data_dir = os.path.join(self.script_dir, "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Get filename without path and create new path in data folder
            file_name = os.path.basename(test_file)
            base_name, ext = os.path.splitext(file_name)
            
            # Modify the extension for data files
            if len(ext) > 3:  # Ensure the extension is at least 3 characters
                new_ext = ext[:3] + 'd'  # .vrp becomes .vrd
            else:
                new_ext = ext  # If the extension is too short, don't change it
            
            # Construct the new save path in the data directory
            save_path = os.path.join(data_dir, base_name + new_ext)
            
            self.vv.SaveData(save_path)
            self.log(f"Test data saved to: {save_path}", True)
        except Exception as e:
            self.log(f"Saving data failed: {ExtractComErrorInfo(e)}", False)
        
        return True
    
    def test_channel_info(self):
        """Test channel information for all available channels"""
        try:
            num_channels = self.vv.GetHardwareInputChannels()
            if num_channels is None:
                self.log("Unable to get number of hardware input channels", False)
                return False
                
            self.log(f"Number of hardware input channels: {num_channels}", num_channels > 0)
            
            # Test all available channels
            for channel_index in range(num_channels):
                self.log(f"\n--- Testing Channel {channel_index+1} ---", True)
                
                # Get channel label
                try:
                    label = self.vv.ChannelLabel(channel_index)
                    self.log(f"Channel {channel_index+1} label: {label}", label is not None)
                except Exception as e:
                    self.log(f"Error getting channel label: {ExtractComErrorInfo(e)}", False)
                
                # Get channel unit
                try:
                    unit = self.vv.ChannelUnit(channel_index)
                    self.log(f"Channel {channel_index+1} unit: {unit}", unit is not None)
                except Exception as e:
                    self.log(f"Error getting channel unit: {ExtractComErrorInfo(e)}", False)
                
                # Try to get sensitivity
                try:
                    sensitivity = self.vv.InputSensitivity(channel_index)
                    self.log(f"Channel {channel_index+1} sensitivity: {sensitivity}", sensitivity is not None)
                except Exception as e:
                    self.log(f"Channel {channel_index+1} sensitivity: {ExtractComErrorInfo(e)}", False)
                
                # Try to get TEDS data
                try:
                    # Create an array to receive the TEDS data
                    teds_array = self.vv.Teds(channel_index)
                    self.log(f"Channel {channel_index+1} TEDS data retrieved", teds_array is not None)
                    if teds_array:
                        teds_str = str(teds_array)
                        self.log(f"TEDS data: {teds_str[:200]}..." if len(teds_str) > 200 
                                else f"TEDS data: {teds_str}", True)
                except Exception as e:
                    self.log(f"Channel {channel_index+1} TEDS data: {ExtractComErrorInfo(e)}", False)
                
                # Try to get hardware capabilities
                try:
                    cap_coupled = self.vv.HardwareSupportsCapacitorCoupled(channel_index)
                    self.log(f"Channel {channel_index+1} supports capacitor coupled: {cap_coupled}", 
                            cap_coupled is not None)
                    
                    accel_power = self.vv.HardwareSupportsAccelPowerSource(channel_index)
                    self.log(f"Channel {channel_index+1} supports accel power source: {accel_power}", 
                            accel_power is not None)
                    
                    differential = self.vv.HardwareSupportsDifferential(channel_index)
                    self.log(f"Channel {channel_index+1} supports differential: {differential}", 
                            differential is not None)
                except Exception as e:
                    self.log(f"Error getting hardware capabilities: {ExtractComErrorInfo(e)}", False)
                    
                # Get additional channel information if available
                try:
                    # Try to get serial number
                    serial = self.vv.InputSerialNumber(channel_index)
                    self.log(f"Channel {channel_index+1} serial number: {serial}", serial is not None)
                    
                    # Try to get calibration date
                    cal_date = self.vv.InputCalDate(channel_index)
                    self.log(f"Channel {channel_index+1} calibration date: {cal_date}", cal_date is not None)
                    
                    # Try to get capacitor coupled status
                    cap_status = self.vv.InputCapacitorCoupled(channel_index)
                    self.log(f"Channel {channel_index+1} capacitor coupled status: {cap_status}", cap_status is not None)
                    
                    # Try to get power source status
                    power_status = self.vv.InputAccelPowerSource(channel_index)
                    self.log(f"Channel {channel_index+1} accel power source status: {power_status}", power_status is not None)
                    
                    # Try to get differential status
                    diff_status = self.vv.InputDifferential(channel_index)
                    self.log(f"Channel {channel_index+1} differential status: {diff_status}", diff_status is not None)
                    
                    # Try to get engineering scale
                    eng_scale = self.vv.InputEngineeringScale(channel_index)
                    self.log(f"Channel {channel_index+1} engineering scale: {eng_scale}", eng_scale is not None)
                except Exception as e:
                    self.log(f"Error getting additional channel information: {ExtractComErrorInfo(e)}", False)
                    
        except Exception as e:
            self.log(f"Error in test_channel_info: {ExtractComErrorInfo(e)}", False)
            return False
        
        return True
    
    def test_data_acquisition(self):
        """Test data acquisition functions"""
        # Test vector acquisition
        try:
            sine_test = self.find_test_file("sine")
            if sine_test:
                try:
                    self.vv.RunTest(sine_test)
                    test_type = self.vv.TestType()
                    if test_type != vvTestType.TEST_SINE:
                        self.log("Could not run a sine test, vectors will have unexpected results", None)
                except:
                    self.log("Could not run a sine test, vectors will have unexpected results", None)
                    return True
                
                # Wait up to 5 seconds for IsRunning
                running = self.wait_for_condition(self.vv.IsRunning)
                if running:
                    self.vv.SweepHold()
                    self.log("Sweep hold command sent", True)

            for vector_name in ["WAVEFORMAXIS", "FREQUENCYAXIS", "TIMEHISTORYAXIS"]:
                vector_enum = getattr(vvVector, vector_name)
                try:
                    # Get vector length
                    length = self.vv.VectorLength(vector_enum)
                    self.log(f"{vector_name} length: {length}", length is not None)
                    
                    # Get vector data
                    inputs = self.vv.GetHardwareInputChannels()
                    data = self.vv.Vector(vector_enum, inputs + 1) # X-Axis, Y-axis values for each channel
                    data_len = len(data) if data else 0
                    num_columns = len(data[0]) if data and data[0] else 0  # Get the number of columns (assuming non-empty data)
    
                    self.log(f"{vector_name} data retrieved, length: {data_len}, columns: {num_columns}", data is not None)
                    
                    for column_index in range(num_columns):
                        # Get vector unit
                        unit = self.vv.VectorUnit(vector_enum + column_index)
                        self.log(f"{vector_name} Channel:{column_index} unit: {unit}", unit is not None)
                    
                        # Get vector label
                        label = self.vv.VectorLabel(vector_enum + column_index)
                        self.log(f"{vector_name} Channel:{column_index} label: {label}", label is not None)
                    
                except Exception as e:
                    self.log(f"Error with {vector_name}: {ExtractComErrorInfo(e)}", False)
        except Exception as e:
            self.log(f"Error in vector acquisition tests: {ExtractComErrorInfo(e)}", False)
        
        # Test other data acquisition methods
        try:
            # Channel data
            channel_data = self.vv.Channel()
            self.log(f"Channel data retrieved, length: {len(channel_data) if channel_data else 0}", channel_data is not None)
            
            # Demand data
            demand_data = self.vv.Demand()
            self.log(f"Demand data retrieved, length: {len(demand_data) if demand_data else 0}", demand_data is not None)
            
            # Control data
            control_data = self.vv.Control()
            self.log(f"Control data retrieved, length: {len(control_data) if control_data else 0}", control_data is not None)
            
            # Output data
            output_data = self.vv.Output()
            self.log(f"Output data retrieved, length: {len(output_data) if output_data else 0}", output_data is not None)
            
            # Rear input data
            try:
                rear_input_data = self.vv.RearInput()
                self.log(f"Rear input data retrieved, length: {len(rear_input_data) if rear_input_data else 0}", rear_input_data is not None)
            except Exception as e:
                self.log(f"Rear input data retrieval failed: {ExtractComErrorInfo(e)}", False)
        except Exception as e:
            self.log(f"Error in data acquisition tests: {ExtractComErrorInfo(e)}", False)
            return False
        
        return True
    
    def test_test_control(self):
        """Test test control functions"""
        # Get current status
        try:
            status = self.vv.Status()
            self.log(f"Test status: {status}", status is not None)
            
            running = self.vv.IsRunning()
            self.log(f"Test running: {running}", running is not None)
            
            starting = self.vv.IsStarting()
            self.log(f"Test starting: {starting}", starting is not None)
            
            changing_level = self.vv.IsChangingLevel()
            self.log(f"Test changing level: {changing_level}", changing_level is not None)
            
            hold_level = self.vv.IsHoldLevel()
            self.log(f"Test hold level: {hold_level}", hold_level is not None)
            
            open_loop = self.vv.IsOpenLoop()
            self.log(f"Test open loop: {open_loop}", open_loop is not None)
            
            aborted = self.vv.IsAborted()
            self.log(f"Test aborted: {aborted}", aborted is not None)
        except Exception as e:
            self.log(f"Error getting test status: {ExtractComErrorInfo(e)}", False)
        
        self.vv.StopTest()

        # Test starting and stopping if not already running
        running = self.wait_for_not(self.vv.IsRunning)
        time.sleep(1)
        if not running:
            try:
                # Start test
                self.vv.StartTest()
                self.log("Test started", True)
                
                # Check if starting
                starting = self.wait_for_condition(self.vv.IsStarting)
                self.log(f"Test starting after start: {starting}", starting is True)

                # Wait up to 5 seconds for IsRunning
                running = self.wait_for_condition(self.vv.IsRunning)

                # Check if running
                running = self.vv.IsRunning()
                self.log(f"Test running after start: {running}", running is True)
                
                # Stop test
                self.vv.StopTest()
                self.log("Test stopped", True)
                
                # Check if stopped
                running = self.wait_for_not(self.vv.IsRunning)
                self.log(f"Test running after stop: {running}", running is False)
            except Exception as e:
                self.log(f"Error in test start/stop: {ExtractComErrorInfo(e)}", False)
        else:
            self.log("Test already running, skipping start/stop test", None)
        
        self.vv.StopTest()

        return True
    
    def test_sine_specific(self):
        """Test sine-specific functions"""
        # First check if we have a sine test
        try:
            test_type = self.vv.TestType()
            if test_type != vvTestType.TEST_SINE:
                # Try to open a sine test
                sine_test = self.find_test_file("sine")
                if sine_test:
                    try:
                        self.vv.OpenTest(sine_test)
                        test_type = self.vv.TestType()
                        if test_type != vvTestType.TEST_SINE:
                            self.log("Could not open a sine test, skipping sine-specific tests", None)
                            return True
                    except:
                        self.log("Could not open a sine test, skipping sine-specific tests", None)
                        return True
                else:
                    self.log("No sine test available, skipping sine-specific tests", None)
                    return True
            else:
                self.vv.StartTest()
                
        except Exception as e:
            self.log(f"Error checking test type: {ExtractComErrorInfo(e)}", False)
            return False
        
        # Test sine sweep functions
        try:
            # Get sine frequency
            freq = self.vv.SineFrequency()
            self.log(f"Sine frequency: {freq}", freq is not None)
            
            # Get sweep multiplier
            sweep_mult = self.vv.SweepMultiplier()
            self.log(f"Sweep multiplier: {sweep_mult}", sweep_mult is not None)
            
            # Set sweep multiplier 
            if sweep_mult is not None:
                new_sweep_mult = sweep_mult * 0.5
                self.vv.SweepMultiplier(new_sweep_mult)  # Set to same value to test setter
                self.log(f"Set sweep multiplier to: {new_sweep_mult}", True)
                sweep_mult = self.vv.SweepMultiplier()
                self.log(f"Verified sweep multiplier set to: {sweep_mult}", (sweep_mult is not None) and (new_sweep_mult == sweep_mult))


            # Test sweep commands (if test is running)
            running = self.wait_for_condition(self.vv.IsRunning)
            if running:
                try:
                    # Get demand multiplier
                    demand_mult = self.vv.DemandMultiplier()
                    self.log(f"Demand multiplier: {demand_mult}", demand_mult is not None)

                    # Set demand multiplier 
                    if demand_mult is not None:
                        new_demand_mult = 1 # dB
                        self.vv.DemandMultiplier(new_demand_mult)  # Set to test setter
                        self.log(f"Set demand multiplier to: {new_demand_mult}", True)
                        demand_mult = self.vv.DemandMultiplier()
                        self.log(f"Verified demand multiplier set to: {demand_mult}", (demand_mult is not None) and (new_demand_mult == demand_mult))
                    self.vv.SweepHold()
                    self.log("Sweep hold command sent", True)
                    time.sleep(1)
                    
                    self.vv.SweepUp()
                    self.log("Sweep up command sent", True)
                    time.sleep(1)
                    
                    self.vv.SweepDown()
                    self.log("Sweep down command sent", True)
                    time.sleep(1)
                    
                    self.vv.SweepStepUp()
                    self.log("Sweep step up command sent", True)
                    time.sleep(1)
                    
                    self.vv.SweepStepDown()
                    self.log("Sweep step down command sent", True)
                    time.sleep(1)
                    
                    self.vv.SweepResonanceHold()
                    self.log("Sweep resonance hold command sent", True)
                except Exception as e:
                    self.log(f"Error in sweep commands: {ExtractComErrorInfo(e)}", False)
            else:
                self.log("Test not running, skipping sweep commands", None)
        except Exception as e:
            self.log(f"Error in sine-specific tests: {ExtractComErrorInfo(e)}", False)
            return False

        if self.vv.IsRunning:
            self.vv.StopTest()

        return True
   
    def test_input_configuration_file(self):
        """Test SetInputConfigurationFile method for all channels at once"""
        try:
            # Channel configuration options for testing
            channel_configs = {
                # Input sensitivities (mV/unit)
                "sensitivities": [10.409000396728516, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
                
                # Units - all should be "g"
                "units": ["g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g", "g"],
                
                # Channel labels
                "labels": ["Acceleration", "Acceleration", "Acceleration", "Acceleration", "Acceleration", "Acceleration", "Acceleration", "Acceleration", 
                        "Acceleration", "Acceleration", "Acceleration", "Acceleration", "Acceleration", "Acceleration", "Acceleration", "Acceleration"],
                
                # Capacitor coupled options (boolean)
                "cap_coupled": [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
                
                # Accel power source options (boolean)
                "accel_power": [True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
                
                # Differential options (boolean)
                "differential": [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
                
                # Serial numbers - only channel 1 has a value
                "serials": ["5065", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                
                # Calibration dates - only channel 1 has a value
                "cal_dates": ["Mar 12, 2008", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
            }
            
            num_channels = self.vv.GetHardwareInputChannels()
            if num_channels is None or num_channels <= 0:
                self.log("Unable to get number of hardware input channels", False)
                return False
                    
            self.log(f"Testing SetInputConfigurationFile for {num_channels} channels")
            
            # Create config file path in a subfolder of the script directory
            config_subfolder = "InputConfig"
            config_folder = os.path.join(self.script_dir, config_subfolder)
            
            # Ensure the directory exists
            if not os.path.exists(config_folder):
                self.log(f"Configuration folder not found: {config_folder}", False)
                return False
            
            # Use the specific .vic file
            config_file = os.path.join(config_folder, "channel 1 TEDS.vic")
            
            if not os.path.exists(config_file):
                self.log(f"Configuration file not found: {config_file}", False)
                return False
            
            # Apply the configuration file once (it will change all channels)
            try:
                self.vv.SetInputConfigurationFile(config_file)
                self.log(f"\nApplied configuration file: {config_file} to all channels", True)
                
                # Check all channels after configuration
                self.log("\n--- Getting settings for all channels after configuration ---", True)
                for channel_index in range(min(num_channels, 16)):
                    try:
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
            
                        # Log the actual configurations retrieved from self.vv
                        self.log(f"Channel {channel_index+1} settings after config:", True)
                        self.log(f"  - Label: {label}", label is not None)
                        self.log(f"  - Unit: {unit}", unit is not None)
                        self.log(f"  - Sensitivity: {sensitivity}", sensitivity is not None)
                        self.log(f"  - Engineering Scale: {eng_scale}", eng_scale is not None)
                        self.log(f"  - Capacitor Coupled: {cap_coupled}", cap_coupled is not None)
                        self.log(f"  - Accel Power Source: {accel_power}", accel_power is not None)
                        self.log(f"  - Differential: {differential}", differential is not None)
                        self.log(f"  - Serial Number: {serial}", serial is not None)
                        self.log(f"  - Calibration Date: {cal_date}", cal_date is not None)
                        
                        # Test TEDS data using the improved method
                        teds_data = self.vv.Teds(channel_index)
                        
                        # Expected TEDS data for channel 1
                        expected_teds_channel1 = [
                            ('Manufacturer', 'Dytran Instruments'),
                            ('Model number', '3055'),
                            ('Version letter', 'B'),
                            ('Version number', '1'),
                            ('Serial no.', '5065'),
                            ('Sensitivity @ ref. cond. (S ref)', '10.41 mV/G'),
                            ('High pass cut-off frequency (F hp)', '0.313 Hz'),
                            ('Sensitivity direction (x,y,z, n/a)', 'X'),
                            ('Transducer weight', '7.95 gm'),
                            ('Polarity (Sign)', '+1'),
                            ('Low pass cut-off frequency (F lp)', '33 kHz'),
                            ('Resonance frequency (F res)', '31.8 kHz'),
                            ('Quality factor @ F res (Q)', '56.5 '),
                            ('Amplitude slope (a)', '-2.3 %/decade'),
                            ('Temperature coefficient (b)', '0.1 %/°C'),
                            ('Reference frequency (F ref)', '98.7 Hz'),
                            ('Reference temperature (T ref)', '22.0 °C'),
                            ('Calibration date', '2008-03-12T17:00:00Z'),
                            ('Calibration initials', 'ED '),
                            ('Calibration Period', '365 days'),
                            ('Measurement position ID', '0')
                        ]

                        # Process TEDS results
                        if teds_data:
                            # We should have just one channel in the result
                            channel_teds = teds_data[0]
                            
                            if "Error" in channel_teds:
                                # If there's an error for this channel
                                if channel_index == 0:
                                    # First channel should have TEDS
                                    self.log(f"  - TEDS Error: {channel_teds['Error']}", False)
                                else:
                                    # Other channels aren't expected to have TEDS
                                    self.log(f"  - No TEDS data (as expected for non-primary channel)", True)
                            else:
                                # There's TEDS data
                                teds_info = channel_teds.get("Teds", [])
                                if teds_info:
                                    # For Channel 1, check against expected values
                                    if channel_index == 0:
                                        self.log(f"  - TEDS Data: Found {len(teds_info)} items", True)
                                        
                                        # Check if all expected values are present
                                        matches = 0
                                        total_expected = len(expected_teds_channel1)
                                        for expected_key, expected_value in expected_teds_channel1:
                                            found = False
                                            for actual_key, actual_value in teds_info:
                                                if actual_key == expected_key and actual_value == expected_value:
                                                    found = True
                                                    matches += 1
                                                    break
                                            self.log(f"  - TEDS '{expected_key}': expected '{expected_value}', " + 
                                                    (f"found match" if found else f"not found or mismatched"), found)
                                        
                                        match_percentage = (matches / total_expected) * 100 if total_expected > 0 else 0
                                        self.log(f"  - TEDS Validation: {matches}/{total_expected} matches ({match_percentage:.1f}%)", 
                                                match_percentage >= 90)  # Consider >90% a success
                                        
                                    else:
                                        # Display info for non-primary channels
                                        display_count = min(3, len(teds_info))
                                        teds_preview = ", ".join([f"{item[0]}: {item[1]}" for item in teds_info[:display_count]])
                                        if len(teds_info) > display_count:
                                            teds_preview += f", ... ({len(teds_info)} items total)"
                                        self.log(f"  - Found TEDS data on non-primary channel: {teds_preview}", None)
                                else:
                                    if channel_index == 0:
                                        self.log("  - TEDS data structure found but empty", False)
                                    else:
                                        self.log("  - No TEDS data (as expected for non-TEDS channel)", True)
                        else:
                            if channel_index == 0:
                                self.log("  - No TEDS data returned", False)
                            else:
                                self.log("  - No TEDS data (as expected for non-TEDS channel)", True)

                       # Compare with expected values
                        expected_sensitivity = channel_configs["sensitivities"][channel_index]
                        expected_unit = channel_configs["units"][channel_index]
                        expected_label = channel_configs["labels"][channel_index]
                        expected_cap_coupled = channel_configs["cap_coupled"][channel_index]
                        expected_accel_power = channel_configs["accel_power"][channel_index]
                        expected_differential = channel_configs["differential"][channel_index]
                        expected_serial = channel_configs["serials"][channel_index]
                        expected_cal_date = channel_configs["cal_dates"][channel_index]
                        
                        # Log comparison results
                        self.log(f"Channel {channel_index+1} expected vs actual:", True)
                        if label is not None:
                            match = (expected_label.lower() in label.lower()) if label else False
                            self.log(f"  - Label: expected '{expected_label}', got '{label}'", match)
                        
                        if unit is not None:
                            match = (expected_unit.lower() in unit.lower()) if unit else False
                            self.log(f"  - Unit: expected '{expected_unit}', got '{unit}'", match)
                        
                        if sensitivity is not None:
                            match = abs(expected_sensitivity - sensitivity) < (expected_sensitivity * 0.001) if sensitivity is not None else False
                            self.log(f"  - Sensitivity: expected {expected_sensitivity}, got {sensitivity}", match)
                        
                        if cap_coupled is not None:
                            match = (expected_cap_coupled == cap_coupled)
                            self.log(f"  - Capacitor Coupled: expected {expected_cap_coupled}, got {cap_coupled}", match)
                        
                        if accel_power is not None:
                            match = (expected_accel_power == accel_power)
                            self.log(f"  - Accel Power Source: expected {expected_accel_power}, got {accel_power}", match)
                        
                        if differential is not None:
                            match = (expected_differential == differential)
                            self.log(f"  - Differential: expected {expected_differential}, got {differential}", match)
                            
                        if serial is not None and expected_serial:
                            match = (expected_serial == serial)
                            self.log(f"  - Serial Number: expected '{expected_serial}', got '{serial}'", match)
                            
                        if cal_date is not None and expected_cal_date:
                            match = (expected_cal_date in cal_date)
                            self.log(f"  - Calibration Date: expected '{expected_cal_date}', got '{cal_date}'", match)
                        
                    except Exception as e:
                        self.log(f"Error getting channel {channel_index+1} properties after config: {ExtractComErrorInfo(e)}", False)
                    
            except Exception as e:
                self.log(f"Error applying configuration file: {ExtractComErrorInfo(e)}", False)
                return False
            
            # At the end of the test, apply the 10mV per G.vic file
            try:
                final_config_file = os.path.join(config_folder, "10mV per G.vic")
                
                if os.path.exists(final_config_file):
                    self.vv.SetInputConfigurationFile(final_config_file)
                    self.log(f"\nTest completed - Applied final configuration file: {final_config_file}", True)
                else:
                    self.log(f"Final configuration file not found: {final_config_file}", False)
            except Exception as e:
                self.log(f"Error applying final configuration file: {ExtractComErrorInfo(e)}", False)
                        
        except Exception as e:
            self.log(f"Error in test_input_configuration_file: {ExtractComErrorInfo(e)}", False)
            return False
        
        return True
    
    def test_recording_functions(self):
        """Test recording functions (V11 interface)"""
        try:
            # Start recording
            self.vv.RecordStart()
            self.log("Recording started", True)
            
            # Wait a moment
            time.sleep(2)
            
            # Pause recording
            self.vv.RecordPause()
            self.log("Recording paused", True)
            
            # Wait a moment
            time.sleep(1)
            
            # Stop recording
            self.vv.RecordStop()
            self.log("Recording stopped", True)
            
            # Get recording filename
            try:
                filename = self.vv.RecordGetFilename()
                self.log(f"Recording filename: {filename}", filename is not None)
            except Exception as e:
                self.log(f"Error getting recording filename: {ExtractComErrorInfo(e)}", False)
        except Exception as e:
            self.log(f"Error in recording functions: {ExtractComErrorInfo(e)}", False)
            return False
        
        return True
    
    def summarize_results(self):
        """Summarize test results"""
        total = len(self.results)
        passed = sum(1 for _, success in self.results if success is True)
        failed = sum(1 for _, success in self.results if success is False)
        skipped = sum(1 for _, success in self.results if success is None)
        
        try:
            success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        except:
            success_rate = 0
        
        summary = f"""
Test Summary:
-------------
Total tests:  {total}
Passed:       {passed}
Failed:       {failed}
Skipped:      {skipped}
Success rate: {success_rate:.1f}% (excluding skipped tests)

"""
        if self.log_file:
            summary += f"Results saved to: {self.log_file}"
        
        print(summary)
        
        if self.log_file:
            try:
                with open(self.log_file, "a") as f:
                    f.write("\n" + summary)
            except Exception as e:
                print(f"Warning: Could not write summary to log file: {e}")
        
    def run_all_tests(self):
        """Run all tests"""
        # First test connection
        if not self.run_test("Connection test", self.test_connection):
            print("Connection failed, cannot continue tests")
            self.summarize_results()
            return False
        
        # Now run all other tests
        self.run_test("Basic properties", self.test_basic_properties)
        self.run_test("Window control", self.test_window_control)
        self.run_test("File operations", self.test_file_operations)
        self.run_test("Channel information", self.test_channel_info)
        self.run_test("Data acquisition", self.test_data_acquisition)
        self.run_test("Test control", self.test_test_control)
        self.run_test("Sine-specific functions", self.test_sine_specific)
        self.run_test("Input Configuration functions", self.test_input_configuration_file)
        self.run_test("Recording functions", self.test_recording_functions)
        
        # Summarize results
        self.summarize_results()
        
        return True

if __name__ == "__main__":
    print("="*80)
    print("VibrationVIEW Python Wrapper Test Application")
    print("="*80)
    
    tester = VibrationVIEWTester()
    tester.run_all_tests()