"""Stateful mock COM object for CI testing without VibrationVIEW installed.

Values are based on recorded interactions with VibrationVIEW 2025.
"""


_REPORT_FIELDS = {
    "BoxSerialNumber1": "Demonstration",
}

_VECTOR_UNITS = {
    "Index": "",
    "Frequency": "Hz",
    "Drive": "Volts",
    "DriveHigh": "Volts",
    "ChannelPhase1": "rad",
    "ChannelPhase2": "rad",
}

_TEDS_DATA = {
    "3C00000186B96114": [
        ["Channel", "1", ""],
        ["Manufacturer", "Dytran Instruments", ""],
        ["Model number", "3056", ""],
        ["Version letter", "B", ""],
        ["Version number", "2", ""],
        ["Serial no.", "999998", ""],
        ["Sensitivity @ ref. cond. (S ref)", "102.0", "mV/G"],
        ["High pass cut-off frequency (F hp)", "0.313", "Hz"],
        ["Sensitivity direction (x,y,z, n/a)", "X", ""],
        ["Transducer weight", "7.95", "gm"],
        ["Polarity (Sign)", "+1", ""],
        ["Low pass cut-off frequency (F lp)", "33", "kHz"],
        ["Resonance frequency (F res)", "31.8", "kHz"],
        ["Quality factor @ F res (Q)", "56.5", ""],
        ["Amplitude slope (a)", "-2.3", "%/decade"],
        ["Temperature coefficient (b)", "0.1", "%/\u00b0C"],
        ["Reference frequency (F ref)", "98.7", "Hz"],
        ["Reference temperature (T ref)", "27.0", "\u00b0C"],
        ["Calibration date", "2012-07-10T17:00:00Z", ""],
        ["Calibration initials", "FC", ""],
        ["Calibration Period", "365", "days"],
        ["Measurement position ID", "0", ""],
        ["User data (ascii 7-bit)", "", ""],
    ],
    "8200000C7A09F42D": [
        ["Unique Registration Number (URN)", "8200000C7A09F42D", ""],
        ["Manufacturer", "Dytran Instruments", ""],
        ["Model number", "3055", ""],
        ["Version letter", "B", ""],
        ["Version number", "1", ""],
        ["Serial no.", "999999", ""],
        ["Sensitivity @ ref. cond. (S ref)", "10.41", "mV/G"],
        ["High pass cut-off frequency (F hp)", "0.313", "Hz"],
        ["Sensitivity direction (x,y,z, n/a)", "X", ""],
        ["Transducer weight", "7.95", "gm"],
        ["Polarity (Sign)", "+1", ""],
        ["Low pass cut-off frequency (F lp)", "33", "kHz"],
        ["Resonance frequency (F res)", "31.8", "kHz"],
        ["Quality factor @ F res (Q)", "56.5", ""],
        ["Amplitude slope (a)", "-2.3", "%/decade"],
        ["Temperature coefficient (b)", "0.1", "%/\u00b0C"],
        ["Reference frequency (F ref)", "98.7", "Hz"],
        ["Reference temperature (T ref)", "22.0", "\u00b0C"],
        ["Calibration date", "2025-01-15T17:00:00Z", ""],
        ["Calibration initials", "DVB", ""],
        ["Calibration Period", "365", "days"],
        ["Measurement position ID", "0", ""],
        ["User data (ascii 7-bit)", "", ""],
    ],
    "010203040506072D": [
        ["Unique Registration Number (URN)", "010203040506072D", ""],
        ["Manufacturer", "PCB Piezotronics, Inc.", ""],
        ["Model number", "356", ""],
        ["Version letter", "A", ""],
        ["Version number", "2", ""],
        ["Serial no.", "999923", ""],
        ["Calibration date", "2025-06-09T17:00:00Z", ""],
        ["Sensitivity @ Fref", "10.001", "mV/G"],
        ["Fref", "99", "Hz"],
        ["F hp electrical", "1.000", "Hz"],
        ["Phase inversion (0: 0\u00b0, 1: 180\u00b0)", "0", ""],
        ["Sensitivity direction (x,y,z, n/a)", "X", ""],
        ["Meas. position ID", "0", ""],
        ["User data (ascii)", "", ""],
    ],
    "020203040506072D": [
        ["Unique Registration Number (URN)", "020203040506072D", ""],
        ["Manufacturer", "PCB Piezotronics, Inc.", ""],
        ["Model number", "356", ""],
        ["Version letter", "A", ""],
        ["Version number", "2", ""],
        ["Serial no.", "999923", ""],
        ["Calibration date", "2025-06-09T17:00:00Z", ""],
        ["Sensitivity @ Fref", "10.001", "mV/G"],
        ["Fref", "99", "Hz"],
        ["F hp electrical", "1.000", "Hz"],
        ["Phase inversion (0: 0\u00b0, 1: 180\u00b0)", "0", ""],
        ["Sensitivity direction (x,y,z, n/a)", "Y", ""],
        ["Meas. position ID", "0", ""],
        ["User data (ascii)", "", ""],
    ],
    "030203040506072D": [
        ["Unique Registration Number (URN)", "030203040506072D", ""],
        ["Manufacturer", "PCB Piezotronics, Inc.", ""],
        ["Model number", "356", ""],
        ["Version letter", "A", ""],
        ["Version number", "2", ""],
        ["Serial no.", "999923", ""],
        ["Calibration date", "2025-06-09T17:00:00Z", ""],
        ["Sensitivity @ Fref", "10.001", "mV/G"],
        ["Fref", "99", "Hz"],
        ["F hp electrical", "7.738", "Hz"],
        ["Phase inversion (0: 0\u00b0, 1: 180\u00b0)", "0", ""],
        ["Sensitivity direction (x,y,z, n/a)", "Z", ""],
        ["Meas. position ID", "0", ""],
        ["User data (ascii)", "", ""],
    ],
    "040203040506072D": [
        ["Unique Registration Number (URN)", "040203040506072D", ""],
        ["Manufacturer", "Bruel & Kjaer", ""],
        ["Model number", "11119", ""],
        ["Version letter", "A", ""],
        ["Version number", "1", ""],
        ["Serial no.", "10009", ""],
        ["Sensitivity @ reference condition", "9.9995", "mV/Pa"],
        ["Reference frequency (F ref)", "0.35", "Hz"],
        ["Pol. Voltage: 0=Prepolar., 1=28V, 2=200V", "1", ""],
        ["Mic. Type: 0=Free., 1=Press., 2=Random, 3=Other", "1", ""],
        ["Mic. Size: 0=1'', 1=1/2'', 2=1/4'', 3=1/8''", "2", ""],
        ["Equivalent microphone volume", "0", "mm\u00b3"],
        ["Polarity (Sign)", "+1", ""],
        ["Calibration date", "2025-02-14T17:00:00Z", ""],
        ["Calibration initials", "", ""],
        ["Calibration Period", "365", "days"],
        ["Measurement position ID", "0", ""],
        ["User data (ascii 7-bit)", "user", ""],
    ],
}


# Input configuration profiles: maps config name patterns to active TEDS channel count
# Each profile defines which TEDS URNs are enabled (from _TEDS_DATA keys)
_CONFIG_PROFILES = {
    "6-channels-TEDS": {
        "urns": [
            "3C00000186B96114",
            "8200000C7A09F42D",
            "010203040506072D",
            "020203040506072D",
            "030203040506072D",
            "040203040506072D",
        ],
    },
    "channel 1 TEDS": {
        "urns": [
            "3C00000186B96114",
        ],
    },
    "8 -channel-TEDS": {
        "urns": [
            "3C00000186B96114",
            "8200000C7A09F42D",
            "010203040506072D",
            "020203040506072D",
            "030203040506072D",
            "040203040506072D",
            "3C00000186B96114",
            "8200000C7A09F42D",
        ],
    },
}

# TEDS sensitivity values: URN -> sensitivity from TEDS data
_TEDS_SENSITIVITY = {
    "3C00000186B96114": 102.0,   # from Sensitivity @ ref. cond. (S ref)
    "8200000C7A09F42D": 10.41,
    "010203040506072D": 10.001,
    "020203040506072D": 10.001,
    "030203040506072D": 10.001,
    "040203040506072D": 9.9995,
}


class MockCOMObject:
    """Simulates VibrationVIEW.TestControl COM object with state tracking."""

    NUM_CHANNELS = 16

    def __init__(self):
        # State
        self._running = False
        self._starting = False
        self._recording = False
        self._test_loaded = False
        self._aborted = False
        self._open_tests = []
        self._running_ticks = 0  # auto-stop after many polls

        # Settable properties
        self._test_type = 0
        self._demand_multipler = 0.0
        self._sweep_multiplier = 1.0
        self._system_check_frequency = 100.0
        self._system_check_output_voltage = 0.1
        self._sine_frequency = 100.0
        self._record_filename = ""
        self._record_counter = 0

        # Active TEDS configuration (default: 6-channels-TEDS)
        self._active_config = "6-channels-TEDS"
        self._teds_applied = False

        # Per-channel state (0-indexed)
        self._cap_coupled = [False] * self.NUM_CHANNELS
        self._accel_power = [False] * self.NUM_CHANNELS
        self._differential = [False] * self.NUM_CHANNELS
        self._sensitivity = [10.0] * self.NUM_CHANNELS
        self._serial_number = [""] * self.NUM_CHANNELS
        self._cal_date = [""] * self.NUM_CHANNELS

        # Form fields state
        self._form_fields = {}

        # Virtual channels state
        self._virtual_channels = "none"

        # _oleobj_ for indexed property access
        self._oleobj_ = _MockOleObj(self)

    # --- Simple properties (read-only) ---

    @property
    def IsReady(self):
        return 1

    @property
    def Running(self):
        if self._running:
            self._running_ticks += 1
            # Auto-stop after 100 polls to simulate a test
            if self._running_ticks > 100:
                self._running = False
                self._starting = False
                self._running_ticks = 0
                return 0
            return 1
        return 0

    @property
    def Starting(self):
        return 1 if self._starting else 0

    @property
    def ChangingLevel(self):
        return 0

    @property
    def HoldLevel(self):
        return 0

    @property
    def OpenLoop(self):
        return 0

    @property
    def Aborted(self):
        return 1 if self._aborted else 0

    @property
    def CanResumeTest(self):
        return 1 if self._aborted else 0

    @property
    def HardwareInputChannels(self):
        return self.NUM_CHANNELS

    @property
    def HardwareOutputChannels(self):
        return 3

    @property
    def HardwareSerialNumber(self):
        return 16777215

    @property
    def SoftwareVersion(self):
        return 2025.0404

    @property
    def RecordGetFilename(self):
        return self._record_filename

    # --- Settable properties ---

    @property
    def TestType(self):
        return self._test_type

    @TestType.setter
    def TestType(self, value):
        self._test_type = int(value)

    @property
    def DemandMultipler(self):
        return self._demand_multipler

    @DemandMultipler.setter
    def DemandMultipler(self, value):
        self._demand_multipler = value

    @property
    def SweepMultiplier(self):
        return self._sweep_multiplier

    @SweepMultiplier.setter
    def SweepMultiplier(self, value):
        self._sweep_multiplier = value

    @property
    def SystemCheckFrequency(self):
        return self._system_check_frequency

    @SystemCheckFrequency.setter
    def SystemCheckFrequency(self, value):
        self._system_check_frequency = value

    @property
    def SystemCheckOutputVoltage(self):
        return self._system_check_output_voltage

    @SystemCheckOutputVoltage.setter
    def SystemCheckOutputVoltage(self, value):
        self._system_check_output_voltage = value

    @property
    def SineFrequency(self):
        return self._sine_frequency

    @SineFrequency.setter
    def SineFrequency(self, value):
        self._sine_frequency = value

    # --- Test control methods ---

    def StartTest(self):
        self._starting = True
        self._running = True
        self._aborted = False
        self._running_ticks = 0
        return None

    def StopTest(self):
        if self._running:
            self._aborted = True
        self._running = False
        self._starting = False
        return None

    def ResumeTest(self):
        if self._aborted:
            self._running = True
            self._starting = True
            self._aborted = False
        return None

    def RunTest(self, test_name):
        self._test_loaded = True
        self._open_tests = [["1", test_name]]
        self._starting = True
        self._running = True
        return None

    def OpenTest(self, test_name):
        self._test_loaded = True
        self._open_tests = [["1", test_name]]
        # Profiles with embedded input configs change the TEDS state
        import os
        base = os.path.splitext(os.path.basename(test_name))[0].lower()
        if "named config" in base:
            # sine-named config.vsp has a named config with only channel 1 TEDS
            self._active_config = "channel 1 TEDS"
            self._teds_applied = False
            self._sensitivity = [10.0] * self.NUM_CHANNELS
        elif "input_configuration_teds" in base:
            # sine_with_Input_configuration_TEDS.vsp uses 6-channel TEDS
            self._active_config = "6-channels-TEDS"
            self._teds_applied = False
            self._sensitivity = [10.0] * self.NUM_CHANNELS
        return None

    def EditTest(self, test_name):
        return None

    def AbortEdit(self):
        return None

    def CloseTest(self, profile_name=None):
        self._test_loaded = False
        self._open_tests = []
        return None

    def CloseTab(self, tab_index=None):
        return None

    # --- Status ---

    def Status(self):
        if self._running:
            return ("Running", 0)
        return ("Remote Stop", 4365)

    # --- Recording ---

    def RecordStart(self):
        self._recording = True
        self._record_counter += 1
        import os
        import tempfile
        self._record_filename = os.path.join(
            tempfile.gettempdir(),
            f"mock_recording_{self._record_counter}.vrd",
        )
        return None

    def RecordStop(self):
        self._recording = False
        return None

    def RecordPause(self):
        return None

    # --- Window control ---

    def Minimize(self):
        return None

    def Restore(self):
        return None

    def Maximize(self):
        return None

    def Activate(self):
        return None

    def MenuCommand(self, cmd_id):
        return None

    # --- Sweep control ---

    def SweepUp(self):
        return None

    def SweepDown(self):
        return None

    def SweepStepUp(self):
        return None

    def SweepStepDown(self):
        return None

    def SweepHold(self):
        return None

    def SweepResonanceHold(self):
        return None

    # --- Data methods ---

    def SaveData(self, filename):
        return None

    def Demand(self, arr):
        return arr

    def Control(self, arr):
        return arr

    def Channel(self, arr):
        return arr

    def Output(self, arr):
        return arr

    def RearInput(self, arr):
        return arr

    def VectorLength(self, vector_enum):
        return 4096

    def Vector(self, data_array, vector_enum):
        return data_array

    # --- Channel info methods ---

    def VectorUnit(self, vector_enum):
        return "G"

    def VectorLabel(self, vector_enum):
        return "Acceleration"

    def ChannelUnit(self, channel):
        return "G"

    def ChannelLabel(self, channel):
        return "Acceleration"

    def ControlUnit(self, loop_num):
        return "G"

    def ControlLabel(self, loop_num):
        return "Control"

    def RearInputUnit(self, channel):
        return "\u00b0C"

    def RearInputLabel(self, channel):
        return "User Analog 1"

    def InputSerialNumber(self, channel):
        return self._serial_number[channel]

    def InputCalDate(self, channel):
        return self._cal_date[channel]

    def InputSensitivity(self, channel):
        return self._sensitivity[channel]

    def InputEngineeringScale(self, channel):
        return 10.0

    def InputCapacitorCoupled(self, channel):
        return 1 if self._cap_coupled[channel] else 0

    def InputAccelPowerSource(self, channel):
        return 1 if self._accel_power[channel] else 0

    def InputDifferential(self, channel):
        return 1 if self._differential[channel] else 0

    def HardwareSupportsCapacitorCoupled(self, channel):
        return 1

    def HardwareSupportsAccelPowerSource(self, channel):
        return 1

    def HardwareSupportsDifferential(self, channel):
        return 1

    def IsChannelDifferentThanDatabase(self, channel):
        return 0

    def InputMode(self, channel, power_source, cap_coupled, differential):
        self._accel_power[channel] = bool(power_source)
        self._cap_coupled[channel] = bool(cap_coupled)
        self._differential[channel] = bool(differential)
        return None

    def InputCalibration(self, channel, sensitivity, serial_number, cal_date):
        self._sensitivity[channel] = sensitivity
        self._serial_number[channel] = serial_number
        self._cal_date[channel] = cal_date
        return None

    def UpdateChannelConfigFromDatabase(self, channel):
        return None

    # --- Input configuration ---

    def set_InputConfigurationFile(self, config_name):
        if self._running:
            _raise_com_error("Test is already running")
        if self._recording:
            _raise_com_error("Recording is active")
        # Match config name to a known profile
        import os
        base = os.path.splitext(os.path.basename(config_name))[0]
        for profile_key in _CONFIG_PROFILES:
            if profile_key.lower() in base.lower():
                self._active_config = profile_key
                self._teds_applied = False
                # Reset sensitivities to default when config changes
                self._sensitivity = [10.0] * self.NUM_CHANNELS
                return None
        # Unknown config — reset to no TEDS
        self._active_config = None
        self._teds_applied = False
        self._sensitivity = [10.0] * self.NUM_CHANNELS
        return None

    # --- Report methods ---

    def ReportField(self, field_name):
        if field_name == "VirtualChannels":
            return self._virtual_channels
        if field_name == "OutputVoltage%g":
            # Simulate output voltage based on channel 1 sensitivity
            # Formula: 1G demand * sensitivity(mV/G) / 1000 = Volts
            sens = self._sensitivity[0]
            return str(sens / 1000.0)
        return _REPORT_FIELDS.get(field_name, "0")

    def ReportVector(self, vectors, array_out):
        cols = vectors.split(",")
        return [[0.0] * len(cols)]

    def ReportVectorHeader(self, vectors, array_out):
        cols = vectors.split(",")
        names = []
        units = []
        for col in cols:
            name = col.strip()
            names.append(name)
            units.append(_VECTOR_UNITS.get(name, "G"))
        return [names, units]

    def ReportVectorHistory(self, vectors, array_out, header_out):
        if self._running:
            _raise_com_error("Test is running")
        cols = vectors.split(",")
        names = [col.strip() for col in cols]
        units = [_VECTOR_UNITS.get(n, "G") for n in names]
        data = [[0.0] * len(cols)]
        return (data, [names, units])

    def ReportFields(self, fields, array_out):
        field_list = fields.split(",")
        return [[f.strip(), "0"] for f in field_list]

    def ReportFieldsHistory(self, fields, array_out):
        if self._running:
            _raise_com_error("Test is running")
        field_list = fields.split(",")
        return [[f.strip(), "0"] for f in field_list]

    # --- Form methods ---

    def PostFormFields(self, fields):
        for row in fields:
            if len(row) >= 2:
                self._form_fields[row[0]] = row[1]
        return None

    def FormFields(self):
        if not self._form_fields:
            _raise_com_error("No data available")
        return [[k, v] for k, v in self._form_fields.items()]

    # --- TEDS methods ---

    def _teds_urns(self):
        """Return 16-element list of TEDS URNs based on active config."""
        if self._active_config and self._active_config in _CONFIG_PROFILES:
            urns = list(_CONFIG_PROFILES[self._active_config]["urns"])
        else:
            urns = []
        urns.extend(["Disabled"] * (self.NUM_CHANNELS - len(urns)))
        return urns

    def _apply_teds_sensitivity(self, urns):
        """Apply TEDS sensitivity values to channels based on URNs."""
        self._teds_applied = True
        for i, urn in enumerate(urns):
            if i < self.NUM_CHANNELS and urn != "Disabled" and urn in _TEDS_SENSITIVITY:
                self._sensitivity[i] = _TEDS_SENSITIVITY[urn]

    def TedsRead(self):
        return self._teds_urns()

    def TedsVerifyAndApply(self, urn_array):
        expected = self._teds_urns()
        for i, urn in enumerate(urn_array):
            exp = expected[i] if i < len(expected) else "Disabled"
            urn_str = urn if isinstance(urn, str) else str(urn)
            exp_str = exp if isinstance(exp, str) else str(exp)
            if exp_str == "Disabled":
                if urn_str.strip() and urn_str.lower() != "disabled":
                    _raise_com_error("URN on disabled channel")
            else:
                if not urn_str.strip():
                    _raise_com_error("Missing URN on enabled channel")
                if urn_str != exp_str:
                    _raise_com_error("URN mismatch")
        urns = self._teds_urns()
        self._apply_teds_sensitivity(urns)
        return urns

    def TedsVerifyStringAndApply(self, urn_string):
        urns = urn_string.split(",")
        expected = self._teds_urns()
        for i, urn in enumerate(urns):
            exp = expected[i] if i < len(expected) else "Disabled"
            urn = urn.strip()
            exp_str = exp if isinstance(exp, str) else str(exp)
            if exp_str == "Disabled":
                if urn and urn.lower() != "disabled":
                    _raise_com_error("URN on disabled channel")
            else:
                if urn and urn != exp_str:
                    _raise_com_error("URN mismatch")
        return self._teds_urns()

    def TedsReadAndApply(self):
        # Profiles with forced/named input configs reject TedsReadAndApply
        if self._open_tests:
            import os
            test_name = self._open_tests[0][1] if self._open_tests[0] else ""
            base = os.path.splitext(os.path.basename(test_name))[0].lower()
            if "named config" in base:
                _raise_com_error("Input configuration is forced by test profile")
        urns = self._teds_urns()
        self._apply_teds_sensitivity(urns)
        return urns

    def TedsFromURN(self, urn):
        if urn in _TEDS_DATA:
            return _TEDS_DATA[urn]
        return []

    def Teds(self, channel, allocated_array):
        # Return TEDS data for channels that have TEDS URNs
        urns = self._teds_urns()
        if channel < len(urns) and urns[channel] != "Disabled":
            urn = urns[channel]
            if urn in _TEDS_DATA:
                rows = _TEDS_DATA[urn]
                for i, row in enumerate(rows):
                    if i < len(allocated_array):
                        for j, val in enumerate(row):
                            if j < len(allocated_array[i]):
                                allocated_array[i][j] = val
        return allocated_array

    # --- Database methods ---

    def ChannelDatabaseIDs(self, channel):
        return ["GUID-001"]

    def TransducerDatabaseRecord(self, guid):
        return ["Record1"]

    # --- List methods ---

    def ListOpenTests(self):
        return self._open_tests

    # --- Virtual channels ---

    def ImportVirtualChannels(self, file_path):
        import os
        if not os.path.exists(file_path):
            _raise_com_error("Passed an invalid parameter value")
        self._virtual_channels = "imported"
        return True

    def RemoveAllVirtualChannels(self):
        self._virtual_channels = "none"
        return True


class _MockOleObj:
    """Mock for _oleobj_ to handle indexed property puts."""

    # Property IDs from the COM interface
    PROP_CAP_COUPLED = 50
    PROP_ACCEL_POWER = 51
    PROP_DIFFERENTIAL = 52

    def __init__(self, mock):
        self._mock = mock

    def Invoke(self, prop_id, lcid, wflags, result_flag, channel, value):
        # wflags == 4 is DISPATCH_PROPERTYPUT
        if self._mock._running:
            _raise_com_error("Cannot change input configuration while test is running")

        if prop_id == self.PROP_CAP_COUPLED:
            self._mock._cap_coupled[channel] = bool(value)
        elif prop_id == self.PROP_ACCEL_POWER:
            self._mock._accel_power[channel] = bool(value)
        elif prop_id == self.PROP_DIFFERENTIAL:
            self._mock._differential[channel] = bool(value)
        return None


def _raise_com_error(message):
    """Raise a pywintypes.com_error or fallback Exception."""
    try:
        import pywintypes
        raise pywintypes.com_error(
            -2147352567,
            "Exception occurred.",
            (0, "VibrationVIEW", message, None, 0, -2147220992),
            None,
        )
    except ImportError:
        raise Exception(message)


def create_mock_com_object():
    """Create a stateful mock COM object that simulates VibrationVIEW.TestControl."""
    return MockCOMObject()
