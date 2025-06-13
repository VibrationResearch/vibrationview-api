"""
VibrationVIEW Python API - Thread-Safe Version

This module provides a thread-safe Python interface to VibrationVIEW software 
through COM automation, suitable for multi-threaded applications like Flask.
"""

import win32com.client
import pythoncom
import time
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

from .vv_enums import vvVector, vvTestType
from .comhelper import ExtractComErrorInfo

from typing import List, Union, Optional, Any


class COMThreadManager:
    """Manages COM initialization and cleanup for multiple threads"""
    
    def __init__(self):
        self._thread_data = threading.local()
        self._active_threads = weakref.WeakSet()
        self._lock = threading.RLock()
    
    def initialize_com(self) -> bool:
        """Initialize COM for the current thread if not already initialized"""
        if not hasattr(self._thread_data, 'initialized'):
            try:
                # Try to initialize COM - handle the case where it might already be initialized
                try:
                    pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
                except pythoncom.com_error as e:
                    # If already initialized, that's fine
                    if e.hresult == -2147221006:  # RPC_E_CHANGED_MODE
                        # Try with different threading model
                        try:
                            pythoncom.CoInitialize()
                        except:
                            # COM might already be initialized, which is OK
                            pass
                    elif e.hresult == -2147220991:  # S_FALSE - already initialized
                        pass
                    else:
                        raise e
                
                self._thread_data.initialized = True
                self._thread_data.thread_id = threading.get_ident()
                
                with self._lock:
                    self._active_threads.add(threading.current_thread())
                
                return True
            except Exception as e:
                print(f"Failed to initialize COM: {e}")
                return False
        return True
    
    def uninitialize_com(self):
        """Uninitialize COM for the current thread"""
        if hasattr(self._thread_data, 'initialized') and self._thread_data.initialized:
            try:
                pythoncom.CoUninitialize()
                self._thread_data.initialized = False
            except Exception as e:
                print(f"Error uninitializing COM: {e}")
    
    def is_com_initialized(self) -> bool:
        """Check if COM is initialized for the current thread"""
        return hasattr(self._thread_data, 'initialized') and self._thread_data.initialized


def com_method(func):
    """Decorator to ensure COM is initialized before calling COM methods"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Ensure COM is initialized for this thread
        if not self._com_manager.initialize_com():
            raise RuntimeError("Failed to initialize COM for current thread")
        
        # Ensure we have a valid COM object for this thread
        if not hasattr(self._thread_local, 'vv_object') or self._thread_local.vv_object is None:
            self._create_com_object_for_thread()
        
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            error_str = str(e)
            # If COM error, try to recreate the object once
            if any(keyword in error_str.lower() for keyword in ["com", "rpc", "coinitialize", "invalid"]):
                try:
                    print(f"COM error detected, recreating object for thread {threading.get_ident()}")
                    # Force COM reinitialization
                    self._com_manager.uninitialize_com()
                    if not self._com_manager.initialize_com():
                        raise RuntimeError("Failed to reinitialize COM")
                    self._create_com_object_for_thread()
                    return func(self, *args, **kwargs)
                except Exception as retry_error:
                    print(f"Retry failed: {retry_error}")
                    raise e
            raise e
    
    return wrapper


class VibrationVIEW:
    """Thread-safe VibrationVIEW COM interface for multi-threaded applications"""
    
    # Class-level COM manager shared across all instances
    _com_manager = COMThreadManager()
    
    def __init__(self, connection_timeout: float = 10.0, retry_attempts: int = 5):
        """
        Initialize VibrationVIEW interface
        
        Args:
            connection_timeout: Maximum time to wait for VibrationVIEW connection
            retry_attempts: Number of connection retry attempts
        """
        self._thread_local = threading.local()
        self._connection_timeout = connection_timeout
        self._retry_attempts = retry_attempts
        self._lock = threading.RLock()
        
        # Initialize COM for the current thread
        if not self._com_manager.initialize_com():
            raise RuntimeError("Failed to initialize COM")
        
        # Create initial COM object
        self._create_com_object_for_thread()
    
    def _create_com_object_for_thread(self):
        """Create a new COM object for the current thread"""
        thread_id = threading.get_ident()
        
        # Clear any existing object for this thread
        if hasattr(self._thread_local, 'vv_object'):
            self._thread_local.vv_object = None
        
        try:
            # Ensure COM is initialized for this thread
            if not self._com_manager.initialize_com():
                raise RuntimeError("Failed to initialize COM for thread")
            
            # Create new COM object for this thread
            print(f'Creating VibrationVIEW object for thread {thread_id}')
            vv = win32com.client.Dispatch('VibrationVIEW.TestControl')
            print(f'VibrationVIEW object created for thread {thread_id}')
            
            # Wait for VibrationVIEW to be ready with timeout
            start_time = time.time()
            wait_time = 0.5
            
            for attempt in range(1, self._retry_attempts + 1):
                try:
                    if vv and vv.IsReady:
                        print(f'VibrationVIEW key is now valid for thread {thread_id}')
                        self._thread_local.vv_object = vv
                        return
                except Exception as e:
                    print(f'Thread {thread_id}, Attempt {attempt} failed: {e}')
                    if time.time() - start_time > self._connection_timeout:
                        raise TimeoutError(f"Connection timeout after {self._connection_timeout} seconds")
                    
                    if attempt == self._retry_attempts:
                        raise RuntimeError('Failed to connect after multiple attempts')
                
                print(f'Thread {thread_id}, waiting {wait_time} seconds...')
                time.sleep(wait_time)
                wait_time = min(wait_time * 1.5, 2.0)  # Exponential backoff with cap
                
        except Exception as e:
            error_msg = f'Failed to connect to VibrationVIEW on thread {thread_id}: {ExtractComErrorInfo(e)}'
            print(error_msg)
            self._thread_local.vv_object = None
            raise RuntimeError(error_msg)
    
    @property
    def vv(self):
        """Get the COM object for the current thread"""
        if not hasattr(self._thread_local, 'vv_object') or self._thread_local.vv_object is None:
            self._create_com_object_for_thread()
        return self._thread_local.vv_object
    
    def __del__(self):
        """Clean up COM resources"""
        self.close()
    
    def close(self):
        """Explicitly release COM resources for current thread"""
        try:
            if hasattr(self._thread_local, 'vv_object') and self._thread_local.vv_object is not None:
                self._thread_local.vv_object = None
            
            # Only uninitialize if we're in a thread that has COM initialized
            if self._com_manager.is_com_initialized():
                self._com_manager.uninitialize_com()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    # -- Basic control methods (IVibrationVIEW Interface) --
    @com_method
    def RunTest(self, testName: str) -> bool:
        """Run VibrationVIEW Test with the given name"""
        return self.vv.RunTest(testName)

    @com_method
    def OpenTest(self, testName: str) -> bool:
        """Open VibrationVIEW Test with the given name"""
        return self.vv.OpenTest(testName)

    @com_method
    def EditTest(self, testName: str) -> bool:
        """Edit VibrationVIEW Test with the given name"""
        return self.vv.EditTest(testName)

    @com_method
    def StartTest(self) -> bool:
        """Start Currently Loaded VibrationVIEW Test"""
        return self.vv.StartTest()

    @com_method
    def StopTest(self) -> bool:
        """Stop Test"""
        return self.vv.StopTest()

    @com_method
    def AbortEdit(self) -> bool:
        """Abort any open Edit session"""
        return self.vv.AbortEdit()

    @com_method
    def SaveData(self, filename: str) -> bool:
        """Save data to the specified filename"""
        return self.vv.SaveData(filename)

    @com_method
    def Minimize(self) -> bool:
        """Minimize VibrationVIEW"""
        return self.vv.Minimize()

    @com_method
    def Restore(self) -> bool:
        """Restore VibrationVIEW"""
        return self.vv.Restore()

    @com_method
    def Maximize(self) -> bool:
        """Maximize VibrationVIEW"""
        return self.vv.Maximize()

    @com_method
    def Activate(self) -> bool:
        """Activate VibrationVIEW"""
        return self.vv.Activate()

    @com_method
    def MenuCommand(self, id: int) -> bool:
        """Send menu command to VibrationVIEW"""
        return self.vv.MenuCommand(id)

    # -- Status and properties --
    @com_method
    def Status(self) -> dict:
        """Get VibrationVIEW Status"""
        stop_code, stop_code_index = self.vv.Status()
        return {'stop_code': stop_code, 'stop_code_index': stop_code_index}

    @com_method
    def IsRunning(self) -> bool:
        """Check if test is running"""
        return bool(self.vv.Running)

    @com_method
    def IsStarting(self) -> bool:
        """Check if test is starting but not at level"""
        return bool(self.vv.Starting)

    @com_method
    def IsChangingLevel(self) -> bool:
        """Check if test schedule is changing levels"""
        return bool(self.vv.ChangingLevel)

    @com_method
    def IsHoldLevel(self) -> bool:
        """Check if schedule timer is in hold"""
        return bool(self.vv.HoldLevel)

    @com_method
    def IsOpenLoop(self) -> bool:
        """Check if test is open loop"""
        return bool(self.vv.OpenLoop)

    @com_method
    def IsAborted(self) -> bool:
        """Check if test has aborted"""
        return bool(self.vv.Aborted)

    @com_method
    def CanResumeTest(self) -> bool:
        """Check if test may be resumed"""
        return bool(self.vv.CanResumeTest)

    @com_method
    def IsReady(self) -> bool:
        """Check if Ethernet Box is running"""
        return bool(self.vv.IsReady)

    @com_method
    def ResumeTest(self) -> bool:
        """Resume Active Test"""
        return self.vv.ResumeTest()

    # -- Data retrieval methods --
    @com_method
    def Demand(self) -> List[float]:
        """Get the demand values for each loop"""
        num_outputs = self.GetHardwareOutputChannels()
        arr = [0.0] * num_outputs
        arr = self.vv.Demand(arr)
        return arr

    @com_method
    def Control(self) -> List[float]:
        """Get the control values for each loop"""
        num_outputs = self.GetHardwareOutputChannels()
        arr = [0.0] * num_outputs
        self.vv.Control(arr)
        return arr

    @com_method
    def Channel(self) -> List[float]:
        """Get the channel values"""
        try:
            num_channels = self.GetHardwareInputChannels()
            arr = [0.0] * num_channels
            arr = self.vv.Channel(arr)
            return arr
        except Exception as e:
            print(f"Error getting channel data: {e}")
            return []

    @com_method
    def Output(self) -> List[float]:
        """Get the output values for each loop"""
        num_outputs = self.GetHardwareOutputChannels()
        arr = [0.0] * num_outputs
        self.vv.Output(arr)
        return arr

    @com_method
    def Vector(self, vectorEnum: Union[int, vvVector], columns: int = 1) -> List[List[float]]:
        """
        Get raw data vector

        Args:
            vectorEnum: Either a vvVector enum value or integer corresponding to the vector
            columns: The number of columns in the data array. Default is 1.

        Returns:
            List of lists representing the raw data for the requested vector.
        """
        try:
            rows = self.vv.VectorLength(vectorEnum)
            dataArray = [[0.0 for _ in range(columns)] for _ in range(rows)]
            arr = self.vv.Vector(dataArray, int(vectorEnum))
            return arr
        except Exception as e:
            print(f"Error retrieving data for vector {vectorEnum}: {str(e)}")
            return [[0.0 for _ in range(columns)] for _ in range(1)]

    @com_method
    def RearInput(self) -> List[float]:
        """Get the input readings from the rear inputs"""
        num_inputs = 8
        arr = [0.0] * num_inputs
        self.vv.RearInput(arr)
        return arr

    # -- Properties for raw data vectors --
    @com_method
    def VectorUnit(self, vectorEnum: Union[int, vvVector]) -> str:
        """Get units for raw data vector"""
        return self.vv.VectorUnit(int(vectorEnum))

    @com_method
    def VectorLabel(self, vectorEnum: Union[int, vvVector]) -> str:
        """Get label for raw data vector"""
        return self.vv.VectorLabel(int(vectorEnum))

    @com_method
    def VectorLength(self, vectorEnum: Union[int, vvVector]) -> int:
        """Get required array length for Raw Data Vector Array"""
        return self.vv.VectorLength(int(vectorEnum))

    @com_method
    def ControlUnit(self, loopNum: int) -> str:
        """Get the channel unit associated with loop number"""
        return self.vv.ControlUnit(loopNum)

    @com_method
    def ControlLabel(self, loopNum: int) -> str:
        """Get the control unit label associated with loop number"""
        return self.vv.ControlLabel(loopNum)

    @com_method
    def ChannelUnit(self, channelNum: int) -> str:
        """Get the channel unit associated with channel number"""
        return self.vv.ChannelUnit(channelNum)

    @com_method
    def ChannelLabel(self, channelNum: int) -> str:
        """Get the channel unit label associated with channel number"""
        return self.vv.ChannelLabel(channelNum)

    @com_method
    def ReportField(self, fieldName: str) -> Any:
        """Get report value specified by field name"""
        return self.vv.ReportField(fieldName)

    @com_method
    def RearInputUnit(self, channel: int) -> str:
        """Get units for the rear input channel"""
        return self.vv.RearInputUnit(channel)

    @com_method
    def RearInputLabel(self, channel: int) -> str:
        """Get label for the rear input channel"""
        return self.vv.RearInputLabel(channel)

    @com_method
    def Teds(self, channel: Optional[int] = None) -> List[dict]:
        """Get TEDs value for requested channel(s)"""
        allTedsData = []
        try:
            numChannels = self.GetHardwareInputChannels()
            allocatedStringArray = [[''] * 2 for _ in range(32)]

            channelsToCheck = [channel] if channel is not None else range(numChannels)
            
            for ch in channelsToCheck:
                try:
                    tedsInfo = self.vv.Teds(ch, allocatedStringArray)
                    teds_info_clean = [item for item in tedsInfo if item[0] and item[1]]
                    
                    tedsData = {
                        "Channel": ch + 1,
                        "Teds": teds_info_clean
                    }
                    allTedsData.append(tedsData)

                except Exception as e:
                    comErr = ExtractComErrorInfo(e)
                    tedsError = {
                        "Channel": ch + 1,
                        "Error": comErr,
                    }
                    allTedsData.append(tedsError)

            return allTedsData
        except Exception as e:
            print(f"Error getting TEDS data: {e}")
            return []

    # -- Test control methods --
    @com_method
    def SweepUp(self) -> bool:
        """Sine Sweep up Sine test"""
        return self.vv.SweepUp()

    @com_method
    def SweepDown(self) -> bool:
        """Sine Sweep down Sine test"""
        return self.vv.SweepDown()

    @com_method
    def SweepStepUp(self) -> bool:
        """Sine Sweep Up to next integer frequency"""
        return self.vv.SweepStepUp()

    @com_method
    def SweepStepDown(self) -> bool:
        """Sine Sweep Down to next integer frequency"""
        return self.vv.SweepStepDown()

    @com_method
    def SweepHold(self) -> bool:
        """Sine Hold Sweep frequency"""
        return self.vv.SweepHold()

    @com_method
    def SweepResonanceHold(self) -> bool:
        """Sine Hold Resonance"""
        return self.vv.SweepResonanceHold()

    @com_method
    def DemandMultiplier(self, value: Optional[float] = None) -> float:
        """Get/Set multiplier for Demand output (dB)"""
        if value is None:
            return self.vv.DemandMultipler
        else:
            self.vv.DemandMultipler = value
            return value

    @com_method
    def SweepMultiplier(self, value: Optional[float] = None) -> float:
        """Get/Set multiplier for Sine Sweep (linear)"""
        if value is None:
            return self.vv.SweepMultiplier
        else:
            self.vv.SweepMultiplier = value
            return value

    @com_method
    def TestType(self, value: Optional[Union[int, vvTestType]] = None) -> int:
        """Get/Set Test Type"""
        if value is None:
            return self.vv.TestType
        else:
            self.vv.TestType = int(value)
            return int(value)

    @com_method
    def SystemCheckFrequency(self, value: Optional[float] = None) -> float:
        """Get/Set System Check Frequency"""
        if value is None:
            return self.vv.SystemCheckFrequency
        else:
            self.vv.SystemCheckFrequency = value
            return value

    @com_method
    def SystemCheckOutputVoltage(self, value: Optional[float] = None) -> float:
        """Get/Set System Check output level"""
        if value is None:
            return self.vv.SystemCheckOutputVoltage
        else:
            self.vv.SystemCheckOutputVoltage = value
            return value

    @com_method
    def SineFrequency(self, value: Optional[float] = None) -> float:
        """Get/Set Sine Frequency"""
        if value is None:
            return self.vv.SineFrequency
        else:
            self.vv.SineFrequency = value
            return value

    # -- Hardware and Input configuration methods --
    @com_method
    def GetHardwareInputChannels(self) -> int:
        """Get number of hardware input channels"""
        return self.vv.HardwareInputChannels

    @com_method
    def GetHardwareOutputChannels(self) -> int:
        """Get number of hardware output channels"""
        return self.vv.HardwareOutputChannels

    @com_method
    def GetHardwareSerialNumber(self) -> str:
        """Get hardware serial number"""
        return self.vv.HardwareSerialNumber

    @com_method
    def GetSoftwareVersion(self) -> str:
        """Get software version"""
        return self.vv.SoftwareVersion

    @com_method
    def InputCalDate(self, channel: int) -> str:
        """Get input calibration date for a channel"""
        return self.vv.InputCalDate(channel)

    @com_method
    def InputSerialNumber(self, channel: int) -> str:
        """Get input serial number for a channel"""
        return self.vv.InputSerialNumber(channel)

    @com_method
    def InputCapacitorCoupled(self, channel: int, value: Optional[bool] = None) -> bool:
        """Get/Set input capacitor coupled setting for a channel"""
        if value is None:
            return self.vv.InputCapacitorCoupled(channel)
        else:
            self.vv.InputCapacitorCoupled(channel, value)
            return value

    @com_method
    def InputAccelPowerSource(self, channel: int, value: Optional[bool] = None) -> bool:
        """Get/Set input accelerometer power source setting for a channel"""
        if value is None:
            return self.vv.InputAccelPowerSource(channel)
        else:
            self.vv.InputAccelPowerSource(channel, value)
            return value

    @com_method
    def InputDifferential(self, channel: int, value: Optional[bool] = None) -> bool:
        """Get/Set input differential setting for a channel"""
        if value is None:
            return self.vv.InputDifferential(channel)
        else:
            self.vv.InputDifferential(channel, value)
            return value

    @com_method
    def InputSensitivity(self, channel: int) -> float:
        """Get input sensitivity for a channel"""
        return self.vv.InputSensitivity(channel)

    @com_method
    def InputEngineeringScale(self, channel: int) -> float:
        """Get input engineering scale for a channel"""
        return self.vv.InputEngineeringScale(channel)

    @com_method
    def InputMode(self, channel: int, powerSource: bool, capCoupled: bool, differential: bool) -> bool:
        """Set input mode for a channel"""
        return self.vv.InputMode(channel, powerSource, capCoupled, differential)

    @com_method
    def InputCalibration(self, channel: int, sensitivity: float, serialNumber: str, calDate: str) -> bool:
        """Set input calibration for a channel"""
        return self.vv.InputCalibration(channel, sensitivity, serialNumber, calDate)

    @com_method
    def HardwareSupportsCapacitorCoupled(self, channel: int) -> bool:
        """Check if hardware supports capacitor coupled for a channel"""
        return self.vv.HardwareSupportsCapacitorCoupled(channel)

    @com_method
    def HardwareSupportsAccelPowerSource(self, channel: int) -> bool:
        """Check if hardware supports accelerometer power source for a channel"""
        return self.vv.HardwareSupportsAccelPowerSource(channel)

    @com_method
    def HardwareSupportsDifferential(self, channel: int) -> bool:
        """Check if hardware supports differential for a channel"""
        return self.vv.HardwareSupportsDifferential(channel)

    # -- V8/V11 Methods --
    @com_method
    def GetActiveTest(self) -> Any:
        """Get the active test object"""
        return self.vv.ActiveTest

    @com_method
    def RecordStart(self) -> bool:
        """Start recording data"""
        return self.vv.RecordStart()
    
    @com_method
    def RecordStop(self) -> bool:
        """Stop recording data"""
        return self.vv.RecordStop()
    
    @com_method
    def RecordPause(self) -> bool:
        """Pause recording data"""
        return self.vv.RecordPause()
    
    @com_method
    def RecordGetFilename(self) -> str:
        """Get the last recording's filename"""
        return self.vv.RecordGetFilename
    
    @com_method
    def SetInputConfigurationFile(self, configName: str) -> bool:
        """Load input configuration file"""
        return self.vv.set_InputConfigurationFile(configName)


# Singleton pattern for shared VibrationVIEW instance in web applications
class VibrationVIEWPool:
    """Thread-safe pool manager for VibrationVIEW instances"""
    
    def __init__(self, max_instances: int = 5):
        self._max_instances = max_instances
        self._instances = []
        self._lock = threading.RLock()
        self._thread_local = threading.local()
    
    def get_instance(self) -> VibrationVIEW:
        """Get a VibrationVIEW instance for the current thread"""
        # Check if current thread already has an instance
        if hasattr(self._thread_local, 'instance'):
            return self._thread_local.instance
        
        with self._lock:
            # Try to reuse an existing instance
            if self._instances:
                instance = self._instances.pop()
            else:
                # Create new instance if under limit
                instance = VibrationVIEW()
            
            self._thread_local.instance = instance
            return instance
    
    def return_instance(self, instance: VibrationVIEW):
        """Return an instance to the pool"""
        with self._lock:
            if len(self._instances) < self._max_instances:
                self._instances.append(instance)
            else:
                instance.close()
        
        # Clear thread local reference
        if hasattr(self._thread_local, 'instance'):
            delattr(self._thread_local, 'instance')


# Global pool instance for Flask applications
_vv_pool = VibrationVIEWPool()

def get_vibrationview() -> VibrationVIEW:
    """Get a thread-safe VibrationVIEW instance for Flask applications"""
    return _vv_pool.get_instance()

def return_vibrationview(instance: VibrationVIEW):
    """Return a VibrationVIEW instance to the pool"""
    _vv_pool.return_instance(instance)


# Context manager for easy use in Flask routes
class VibrationVIEWContext:
    """Context manager for VibrationVIEW instances"""
    
    def __enter__(self) -> VibrationVIEW:
        self.instance = get_vibrationview()
        return self.instance
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return_vibrationview(self.instance)

