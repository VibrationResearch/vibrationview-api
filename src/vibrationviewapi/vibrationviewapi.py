"""
VibrationVIEW Python API - Thread-Safe Version

This module provides a thread-safe Python interface to VibrationVIEW software
through COM automation, suitable for multi-threaded applications like Flask.

All COM calls are marshaled to a single dedicated worker thread that owns
the COM object, ensuring correct COM apartment threading behavior.
"""

import win32com.client
import pythoncom
import time
import threading

from .vv_enums import vvVector, vvTestType
from .comhelper import ExtractComErrorInfo
from .comworker import _com_worker, _ensure_worker, com_method

from typing import List, Union, Optional, Any


class VibrationVIEW:
    """Thread-safe VibrationVIEW COM interface.

    All COM calls are marshaled to a dedicated worker thread, so this
    class can be used safely from any thread.
    """

    def __init__(self, connection_timeout: float = 10.0, retry_attempts: int = 5):
        """
        Initialize VibrationVIEW interface

        Args:
            connection_timeout: Maximum time to wait for VibrationVIEW connection
            retry_attempts: Number of connection retry attempts
        """
        self._connection_timeout = connection_timeout
        self._retry_attempts = retry_attempts
        self._vv_object = None
        self._lock = threading.Lock()

        _ensure_worker()
        self._create_com_object()

    def _create_com_object(self, skip_ready_check: bool = False):
        """Create the COM object on the worker thread."""
        with self._lock:
            self._vv_object = None
            timeout = self._connection_timeout
            retries = self._retry_attempts

            def _do_create():
                print('Creating VibrationVIEW object on COM worker thread')
                vv = win32com.client.Dispatch('VibrationVIEW.TestControl')
                print('VibrationVIEW object created')

                if skip_ready_check:
                    return vv

                # Wait for VibrationVIEW to be ready with timeout
                start_time = time.time()
                wait_time = 0.5

                for attempt in range(1, retries + 1):
                    try:
                        if vv and vv.IsReady:
                            print('VibrationVIEW key is now valid')
                            return vv
                    except Exception as e:
                        print(f'Attempt {attempt} failed: {e}')
                        if time.time() - start_time > timeout:
                            raise TimeoutError(f"Connection timeout after {timeout} seconds")

                        if attempt == retries:
                            raise RuntimeError('Failed to connect after multiple attempts')

                    print(f'Waiting {wait_time} seconds...')
                    time.sleep(wait_time)
                    wait_time = min(wait_time * 1.5, 2.0)

                # Loop completed without IsReady becoming True; assign the
                # object anyway so callers can poll IsReady() themselves.
                print(f'VibrationVIEW not ready after {retries} attempts, assigning object anyway')
                return vv

            try:
                future = _com_worker.submit(_do_create)
                self._vv_object = future.result()
            except Exception as e:
                error_msg = f'Failed to connect to VibrationVIEW: {ExtractComErrorInfo(e)}'
                print(error_msg)
                self._vv_object = None
                raise RuntimeError(error_msg)

    @property
    def vv(self):
        """Get the COM object (for use on the worker thread only)."""
        if self._vv_object is None:
            self._create_com_object()
        return self._vv_object

    def __del__(self):
        """Clean up COM resources"""
        self.close()

    def close(self):
        """Explicitly release COM resources."""
        try:
            if self._vv_object is not None:
                self._vv_object = None
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
        """Check if VR Box is running and ready to accept commands"""
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
        """Get the input readings from the rear inputs - this can work for more than 8 channels"""
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
    def ReportVector(self, vectors: str, array_out: Optional[List] = None) -> List:
        """
        Get report vector specified by sVector.

        Args:
            vectors: String specifying which vector(s) to retrieve
            array_out: Optional pre-allocated array. If properly sized, it will be filled;
                      otherwise a new array is allocated

        Returns:
            Array containing the requested vector data
        """
        result = self.vv.ReportVector(vectors, array_out)
        return result

    @com_method
    def ReportVectorHeader(self, vectors: str, array_out: Optional[List] = None) -> List:
        """
        Get report vector headers specified by sVector.

        Args:
            vectors: String specifying which vector header(s) to retrieve
            array_out: Optional pre-allocated array. If properly sized, it will be filled;
                      otherwise a new array is allocated

        Returns:
            Array containing the requested vector header data
        """
        result = self.vv.ReportVectorHeader(vectors, array_out)
        return result

    @com_method
    def ReportVectorHistory(self, vectors: str, array_out: Optional[List] = None, header_out: Optional[List] = None) -> tuple:
        """
        Get report vector data from history files.

        Args:
            vectors: String specifying which vector(s) to retrieve
            array_out: Optional pre-allocated array. If properly sized, it will be filled;
                      otherwise a new array is allocated
            header_out: Optional pre-allocated array for headers. If properly sized, it will be filled;
                       otherwise a new array is allocated

        Returns:
            Tuple of (array_out, header_out) containing the requested vector data and headers
        """
        result = self.vv.ReportVectorHistory(vectors, array_out, header_out)
        return result

    @com_method
    def ReportFields(self, fields: str, array_out: Optional[List] = None) -> List:
        """
        Get report field names and values as 2D array (param, value).

        Args:
            fields: String specifying which field(s) to retrieve
            array_out: Optional pre-allocated array. If properly sized, it will be filled;
                      otherwise a new array is allocated

        Returns:
            2D array containing the requested field data as (parameter, value) pairs
        """
        result = self.vv.ReportFields(fields, array_out)
        return result

    @com_method
    def ReportFieldsHistory(self, fields: str, array_out: Optional[List] = None) -> List:
        """
        Get report field names and values from history files as 2D array (param, value1, value2, ...).

        Args:
            fields: String specifying which field(s) to retrieve
            array_out: Optional pre-allocated array. If properly sized, it will be filled;
                      otherwise a new array is allocated

        Returns:
            2D array containing the requested field data as (parameter, value1, value2, ...) rows
        """
        result = self.vv.ReportFieldsHistory(fields, array_out)
        return result

    @com_method
    def FormFields(self) -> List:
        """
        Get all form field values as 2D array (param, value).

        Returns:
            2D array containing all form field data as (parameter, value) pairs
        """
        result = self.vv.FormFields()
        return result

    @com_method
    def PostFormFields(self, fields: List) -> bool:
        """
        Post form field values from 2D array (param, value), merging with existing form fields.

        Args:
            fields: 2D array of (parameter, value) pairs to post

        Returns:
            True if successful
        """
        self.vv.PostFormFields(fields)
        return True

    @com_method
    def RearInputUnit(self, channel: int) -> str:
        """Get units for the rear input channel"""
        return self.vv.RearInputUnit(channel)

    @com_method
    def RearInputLabel(self, channel: int) -> str:
        """Get label for the rear input channel"""
        return self.vv.RearInputLabel(channel)

    @com_method
    def TedsRead(self) -> List[str]:
        """
        Get TEDS URNs for all channels.
        Returns a 1D array of URN strings, one per channel.
        """
        tedsInfo = self.vv.TedsRead()
        return tedsInfo

    @com_method
    def TedsVerifyAndApply(self, urn_array: List[str]) -> List[str]:
        """
        Verify TEDS data against hardware and apply to livemode if matching.

        Args:
            urn_array: 1D array of URN strings, one per channel

        Returns:
            1D array of URN strings after verification and application
        """
        result = self.vv.TedsVerifyAndApply(urn_array)
        return result

    @com_method
    def TedsVerifyStringAndApply(self, urn_string: str) -> List[str]:
        """
        Verify TEDS data from a single URN string and apply to livemode if matching.

        Args:
            urn_string: Single URN string

        Returns:
            1D array of URN strings after verification and application
        """
        result = self.vv.TedsVerifyStringAndApply(urn_string)
        return result

    @com_method
    def TedsReadAndApply(self) -> List[str]:
        """
        Read TEDS URNs from hardware and apply to livemode.
        Returns a 1D array of URN strings, one per channel.
        """
        tedsInfo = self.vv.TedsReadAndApply()
        return tedsInfo

    @com_method
    def TedsFromURN(self, urn: str) -> List[str]:
        """
        Lookup and decode TEDS transducer by Unique Registration Number (URN).

        Args:
            urn: Unique Registration Number string

        Returns:
            Array of TEDS data strings
        """
        result = self.vv.TedsFromURN(urn)
        return result

    @com_method
    def Teds(self, channel: Optional[int] = None) -> List[dict]:
        """Get TEDs value for requested channel(s)"""
        allTedsData = []
        try:
            numChannels = self.GetHardwareInputChannels()
            """ descriptor, value, unit for up to 32 TEDS fields """
            allocatedStringArray = [[''] * 3 for _ in range(32)]

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

    # -- Database methods --
    @com_method
    def UpdateChannelConfigFromDatabase(self, channel: int) -> bool:
        """
        Read database values and apply differences to document for the specified channel.

        Args:
            channel: Channel number (0-based)

        Returns:
            True if successful, False otherwise
        """
        return self.vv.UpdateChannelConfigFromDatabase(channel)

    @com_method
    def IsChannelDifferentThanDatabase(self, channel: int) -> bool:
        """
        Check if channel configuration differs from database.

        Args:
            channel: Channel number (0-based)

        Returns:
            True if channel differs from database, False otherwise
        """
        return bool(self.vv.IsChannelDifferentThanDatabase(channel))

    @com_method
    def ChannelDatabaseIDs(self, channel: int) -> List[str]:
        """
        Get database GUIDs for a channel.

        Args:
            channel: Channel number (0-based)

        Returns:
            Array of GUID strings associated with the channel
        """
        result = self.vv.ChannelDatabaseIDs(channel)
        return result

    @com_method
    def TransducerDatabaseRecord(self, guid: str) -> List[str]:
        """
        Get all database fields for a given GUID.

        Args:
            guid: Transducer database GUID

        Returns:
            Array of strings containing all database fields for the transducer
        """
        result = self.vv.TransducerDatabaseRecord(guid)
        return result

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
            return self.vv.TestType

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
            return bool(self.vv.InputCapacitorCoupled(channel))
        else:
            # Use direct COM property assignment for indexed property
            # Property ID 50 from COM interface, DISPATCH_PROPERTYPUT
            self.vv._oleobj_.Invoke(50, 0, pythoncom.DISPATCH_PROPERTYPUT, 0, channel, int(bool(value)))
            return bool(value)

    @com_method
    def InputAccelPowerSource(self, channel: int, value: Optional[bool] = None) -> bool:
        """Get/Set input accelerometer power source setting for a channel"""
        if value is None:
            return bool(self.vv.InputAccelPowerSource(channel))
        else:
            # Use direct COM property assignment for indexed property

            # Property ID 51 from COM interface, DISPATCH_PROPERTYPUT
            # For indexed properties with propput, pass arguments in correct order
            self.vv._oleobj_.Invoke(51, 0, pythoncom.DISPATCH_PROPERTYPUT, 0, channel, int(bool(value)))
            return bool(value)

    @com_method
    def InputDifferential(self, channel: int, value: Optional[bool] = None) -> bool:
        """Get/Set input differential setting for a channel"""
        if value is None:
            return bool(self.vv.InputDifferential(channel))
        else:
            # Use direct COM property assignment for indexed property
            # Property ID 52 from COM interface (assuming next ID after 51), DISPATCH_PROPERTYPUT
            self.vv._oleobj_.Invoke(52, 0, pythoncom.DISPATCH_PROPERTYPUT, 0, channel, int(bool(value)))
            return bool(value)

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
        return bool(self.vv.HardwareSupportsCapacitorCoupled(channel))

    @com_method
    def HardwareSupportsAccelPowerSource(self, channel: int) -> bool:
        """Check if hardware supports accelerometer power source for a channel"""
        return bool(self.vv.HardwareSupportsAccelPowerSource(channel))

    @com_method
    def HardwareSupportsDifferential(self, channel: int) -> bool:
        """Check if hardware supports differential for a channel"""
        return bool(self.vv.HardwareSupportsDifferential(channel))

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

    @com_method
    def CloseTest(self, profile_name: str) -> bool:
        """
        Close test profile by name.

        Args:
            profile_name: Name of the test profile to close

        Returns:
            True if test was closed, False otherwise
        """
        return bool(self.vv.CloseTest(profile_name))

    @com_method
    def CloseTab(self, tab_index: int) -> bool:
        """
        Close test tab by index.

        Args:
            tab_index: Index of the tab to close

        Returns:
            True if tab was closed, False otherwise
        """
        return bool(self.vv.CloseTab(tab_index))

    @com_method
    def ListOpenTests(self) -> List[str]:
        """
        List all open test profiles.

        Returns:
            List of open test profile names
        """
        result = self.vv.ListOpenTests()
        return result if result else []

    @com_method
    def ImportVirtualChannels(self, file_path: str) -> bool:
        """
        Import virtual channel definitions from a VCHAN file.

        Args:
            file_path: Path to the VCHAN file to import

        Returns:
            True if successful, False otherwise
        """
        self.vv.ImportVirtualChannels(file_path)
        return True

    @com_method
    def RemoveAllVirtualChannels(self) -> bool:
        """
        Remove all virtual channel definitions.

        Returns:
            True if successful, False otherwise
        """
        self.vv.RemoveAllVirtualChannels()
        return True


class VibrationVIEWPool:
    """Kept for backward compatibility. Returns the same VibrationVIEW instance
    since all COM calls are now serialized through a single worker thread."""

    def __init__(self, max_instances: int = 5):
        self._instance = None
        self._lock = threading.Lock()

    def get_instance(self) -> VibrationVIEW:
        """Get a VibrationVIEW instance."""
        with self._lock:
            if self._instance is None:
                self._instance = VibrationVIEW()
            return self._instance

    def return_instance(self, instance: VibrationVIEW):
        """No-op; the instance is shared."""
        pass


# Global pool instance for Flask applications
_vv_pool = None
_vv_pool_lock = threading.Lock()

def _get_pool():
    global _vv_pool
    if _vv_pool is None:
        with _vv_pool_lock:
            if _vv_pool is None:
                _vv_pool = VibrationVIEWPool()
    return _vv_pool

def get_vibrationview() -> VibrationVIEW:
    """Get a thread-safe VibrationVIEW instance for Flask applications"""
    return _get_pool().get_instance()

def return_vibrationview(instance: VibrationVIEW):
    """Return a VibrationVIEW instance (no-op with worker thread model)"""
    _get_pool().return_instance(instance)


# Context manager for easy use in Flask routes
class VibrationVIEWContext:
    """Context manager for VibrationVIEW instances"""

    def __enter__(self) -> VibrationVIEW:
        self.instance = get_vibrationview()
        return self.instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        return_vibrationview(self.instance)
