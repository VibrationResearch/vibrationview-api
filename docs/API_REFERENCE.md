
# VibrationVIEW API Reference

Complete API documentation for the VibrationVIEW Python API.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Classes](#classes)
  - [VibrationVIEW](#vibrationview)
  - [VibrationVIEWContext](#vibrationviewcontext)
  - [VibrationVIEWPool](#vibrationviewpool)
- [Enumerations](#enumerations)
  - [vvVector](#vvvector)
  - [vvTestType](#vvtesttype)
- [Methods Reference](#methods-reference)
  - [Connection & Lifecycle](#connection--lifecycle)
  - [Test Control](#test-control)
  - [Test Status](#test-status)
  - [Data Acquisition](#data-acquisition)
  - [Vector Operations](#vector-operations)
  - [Channel Information](#channel-information)
  - [Report Functions](#report-functions)
  - [Hardware Information](#hardware-information)
  - [Input Configuration](#input-configuration)
  - [TEDS Support](#teds-support)
  - [Transducer Database](#transducer-database)
  - [Sine Test Control](#sine-test-control)
  - [System Check](#system-check)
  - [Recording](#recording)
  - [Window Control](#window-control)
  - [Virtual Channels](#virtual-channels)
- [Command Line Utilities](#command-line-utilities)
- [Helper Functions](#helper-functions)
- [Thread Safety](#thread-safety)

---

## Installation

### Installing Python

1. **Download Python** from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Run the installer
3. **Important:** On the first screen, check the box **"Add python.exe to PATH"** at the bottom
4. Click **"Install Now"**
5. Verify installation by opening Command Prompt and typing:
   ```bash
   python --version
   ```

### Installing the VibrationVIEW API

Once Python is installed, open Command Prompt and run:

```bash
pip install vibrationview-api
```

### Requirements

- Windows 10 or Windows 11
- VibrationVIEW software installed
- VibrationVIEW automation option (VR9604) or Simulation mode
- Python 3.7+

---

## Quick Start

### Installing VibrationVIEW

1. **Download VibrationVIEW** from: [https://vibrationresearch.com/download-demo/](https://vibrationresearch.com/download-demo/)
2. Run the installer and follow the prompts
3. Launch VibrationVIEW
4. **If you have VR hardware:** The Automation option (VR9604) is required to use the API
5. **If you don't have VR hardware:** You can run in **Simulation mode**:
   - Go to **Hardware > Select Hardware**
   - Choose **Simulated Hardware**
   - Select the number of input/output channels to simulate

### Basic Usage

```python
from vibrationviewapi import VibrationVIEW

vv = VibrationVIEW()
version = vv.GetSoftwareVersion()
print(f"VibrationVIEW version: {version}")
vv.close()
```

### Context Manager (Recommended)

```python
from vibrationviewapi import VibrationVIEWContext

with VibrationVIEWContext() as vv:
    version = vv.GetSoftwareVersion()
    channels = vv.GetHardwareInputChannels()
```

### Flask Application

```python
from vibrationviewapi import VibrationVIEWContext
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/status')
def status():
    with VibrationVIEWContext() as vv:
        return jsonify({'version': vv.GetSoftwareVersion()})
```

---

## COM Interfaces

VibrationVIEW exposes three COM interfaces. The Python API wraps the recommended interface:

| Interface | Description |
|-----------|-------------|
| **VibrationVIEWLib.IVibrationVIEW** | Recommended interface for VB/VBA/Python. All data types are directly supported. This is what the Python API uses. |
| VibrationVIEWLib.IVibrationVIEWControl | Control-only interface (start, stop, save, etc.) |
| VibrationVIEWLib.IVibrationVIEWData | Data retrieval interface (vectors, channels, etc.) |

> **Note:** The Python `VibrationVIEW` class uses `IVibrationVIEW` which combines both control and data functionality in a single interface.

---

## Classes

### VibrationVIEW

Thread-safe VibrationVIEW COM interface for multi-threaded applications.

```python
class VibrationVIEW(connection_timeout: float = 10.0, retry_attempts: int = 5)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `connection_timeout` | float | 10.0 | Maximum time to wait for VibrationVIEW connection (seconds) |
| `retry_attempts` | int | 5 | Number of connection retry attempts |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `vv` | COM Object | The underlying COM object for the current thread |

---

### VibrationVIEWContext

Context manager for VibrationVIEW instances. Automatically handles resource cleanup.

```python
from vibrationviewapi import VibrationVIEWContext

with VibrationVIEWContext() as vv:
    # Use vv here
    pass
# Resources automatically cleaned up
```

---

### VibrationVIEWPool

Thread-safe pool manager for VibrationVIEW instances in web applications.

```python
class VibrationVIEWPool(max_instances: int = 5)
```

#### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_instance()` | VibrationVIEW | Get an instance for the current thread |
| `return_instance(instance)` | None | Return an instance to the pool |

---

## Enumerations

### vvVector

Vector enumeration for data access. Import from `vibrationviewapi`.

```python
from vibrationviewapi import vvVector
```

| Category | Values | Range |
|----------|--------|-------|
| Waveform Axis | `WAVEFORMAXIS` | 0 |
| Waveform Channels | `WAVEFORM1` - `WAVEFORM64` | 1-64 |
| Waveform Demand/Control | `WAVEFORMDEMAND`, `WAVEFORMCONTROL`, etc. | 90-97 |
| Frequency Axis | `FREQUENCYAXIS` | 100 |
| Frequency Channels | `FREQUENCY1` - `FREQUENCY64` | 101-164 |
| Frequency Drive/Response | `FREQUENCYDRIVE`, `FREQUENCYRESPONSE`, etc. | 180-187 |
| Frequency Demand/Control | `FREQUENCYDEMAND`, `FREQUENCYCONTROL`, etc. | 190-197 |
| Time History Axis | `TIMEHISTORYAXIS` | 200 |
| Time History Channels | `TIMEHISTORY1` - `TIMEHISTORY64` | 201-264 |
| Rear Input History | `REARINPUTHISTORY1` - `REARINPUTHISTORY32` | 301-332 |

#### Example

```python
from vibrationviewapi import VibrationVIEW, vvVector

vv = VibrationVIEW()
length = vv.VectorLength(vvVector.FREQUENCYAXIS)
data = vv.Vector(vvVector.FREQUENCYAXIS, columns=1)
```

---

### vvTestType

Test type enumeration.

```python
from vibrationviewapi import vvTestType
```

| Name | Value | Description |
|------|-------|-------------|
| `TEST_SYSCHECK` | 0 | System Check |
| `TEST_SINE` | 1 | Sine Test |
| `TEST_RANDOM` | 2 | Random Test |
| `TEST_SHOCK` | 4 | Shock Test |
| `TEST_TRANSIENT` | 5 | Transient Test |
| `TEST_REPLAY` | 6 | Field Data Replay |

#### Class Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_name(value)` | str | Get human-readable name for test type |

#### Example

```python
from vibrationviewapi import VibrationVIEW, vvTestType

vv = VibrationVIEW()
test_type = vv.TestType()
if test_type == vvTestType.TEST_SINE:
    print("Running a sine test")
print(f"Test type: {vvTestType.get_name(test_type)}")
```

---

## Methods Reference

### Connection & Lifecycle

#### `close()`

Explicitly release COM resources for current thread.

```python
vv.close()
```

**Returns:** None

---

### Test Control

#### `RunTest(testName: str) -> bool`

Run VibrationVIEW test with the given filename.

| Parameter | Type | Description |
|-----------|------|-------------|
| `testName` | str | Full path to the test profile file |

**Returns:** `bool` - True if successful

```python
vv.RunTest("C:\\VibrationVIEW\\Profiles\\sine_sweep.vsp")
```

---

#### `OpenTest(testName: str) -> bool`

Open VibrationVIEW test without starting it.

| Parameter | Type | Description |
|-----------|------|-------------|
| `testName` | str | Full path to the test profile file |

**Returns:** `bool` - True if successful

```python
vv.OpenTest("C:\\VibrationVIEW\\Profiles\\sine_sweep.vsp")
```

---

#### `EditTest(testName: str) -> bool`

Open VibrationVIEW test in edit mode.

| Parameter | Type | Description |
|-----------|------|-------------|
| `testName` | str | Full path to the test profile file |

**Returns:** `bool` - True if successful

---

#### `StartTest() -> bool`

Start the currently loaded VibrationVIEW test.

**Returns:** `bool` - True if successful

```python
vv.OpenTest("C:\\VibrationVIEW\\Profiles\\test.vsp")
vv.StartTest()
```

---

#### `StopTest() -> bool`

Stop the currently running test.

**Returns:** `bool` - True if successful

---

#### `ResumeTest() -> bool`

Resume a paused test.

**Returns:** `bool` - True if successful

---

#### `AbortEdit() -> bool`

Abort any open edit session.

**Returns:** `bool` - True if successful

---

#### `SaveData(filename: str) -> bool`

Save test data to the specified filename.

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | str | Full path for the output data file |

**Returns:** `bool` - True if successful

```python
vv.SaveData("C:\\Data\\test_data.vsd")
```

---

#### `CloseTest(profile_name: str) -> bool`

Close test profile by name.

| Parameter | Type | Description |
|-----------|------|-------------|
| `profile_name` | str | Name of the test profile to close |

**Returns:** `bool` - True if test was closed

---

#### `CloseTab(tab_index: int) -> bool`

Close test tab by index.

| Parameter | Type | Description |
|-----------|------|-------------|
| `tab_index` | int | Index of the tab to close |

**Returns:** `bool` - True if tab was closed

---

#### `ListOpenTests() -> List[str]`

List all open test profiles.

**Returns:** `List[str]` - List of open test profile names

```python
open_tests = vv.ListOpenTests()
for test in open_tests:
    print(test)
```

---

### Test Status

#### `Status() -> dict`

Get VibrationVIEW status.

**Returns:** `dict` with keys:
- `stop_code`: Stop code string
- `stop_code_index`: Stop code index

```python
status = vv.Status()
print(f"Stop code: {status['stop_code']}")
```

---

#### `IsRunning() -> bool`

Check if test is running (the output is live).

**Returns:** `bool` - True if test is running

---

#### `IsStarting() -> bool`

Check if test is starting but not yet at level.

**Returns:** `bool` - True if test is starting

---

#### `IsChangingLevel() -> bool`

Check if test schedule is changing levels.

**Returns:** `bool` - True if changing level

---

#### `IsHoldLevel() -> bool`

Check if schedule timer is in hold.

**Returns:** `bool` - True if in hold

---

#### `IsOpenLoop() -> bool`

Check if test is in open loop mode.

**Returns:** `bool` - True if open loop

---

#### `IsAborted() -> bool`

Check if test has been aborted (any red stop code).

**Returns:** `bool` - True if aborted

---

#### `CanResumeTest() -> bool`

Check if test may be resumed.

**Returns:** `bool` - True if test can be resumed

---

#### `IsReady() -> bool`

Check if VR Box is running and ready to accept commands.

**Returns:** `bool` - True if ready

```python
while not vv.IsReady():
    time.sleep(0.5)
print("VibrationVIEW is ready")
```

---

#### `TestType(value: Optional[int] = None) -> int`

Get or set the test type (0=System Check, 1=Sine, 2=Random, 4=Shock, 5=Transient, 6=FDR).

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | int or vvTestType, optional | Test type to set |

**Returns:** `int` - Current test type

```python
# Get current test type
test_type = vv.TestType()

# Check test type
if test_type == vvTestType.TEST_SINE:
    print("This is a sine test")
```

---

### Data Acquisition

#### `Channel() -> List[float]`

Get the current channel values for all input channels.

**Returns:** `List[float]` - Channel values

```python
channel_data = vv.Channel()
for i, value in enumerate(channel_data):
    print(f"Channel {i+1}: {value}")
```

---

#### `Demand() -> List[float]`

Get the demand values for each control loop.

**Returns:** `List[float]` - Demand values

---

#### `Control() -> List[float]`

Get the control values for each control loop.

**Returns:** `List[float]` - Control values

---

#### `Output() -> List[float]`

Get the output values for each control loop.

**Returns:** `List[float]` - Output values

---

#### `RearInput() -> List[float]`

Get the input readings from the rear inputs (up to 8 channels).

**Returns:** `List[float]` - Rear input values

---

### Vector Operations

> **Note:** For VibrationVIEW 2024.4 and later, `ReportVector` and `ReportVectorHeader` have replaced these deprecated functions. See [Report Functions](#report-functions) for the recommended approach.

#### `Vector(vectorEnum: Union[int, vvVector], columns: int = 1) -> List[List[float]]`

Get raw data vector.

| Parameter | Type | Description |
|-----------|------|-------------|
| `vectorEnum` | int or vvVector | Vector identifier |
| `columns` | int | Number of columns in the data array (default: 1) |

**Returns:** `List[List[float]]` - 2D array of vector data

```python
from vibrationviewapi import vvVector

# Get frequency axis data
freq_data = vv.Vector(vvVector.FREQUENCYAXIS, columns=1)

# Get multiple channel waveforms
num_channels = vv.GetHardwareInputChannels()
waveform = vv.Vector(vvVector.WAVEFORMAXIS, columns=num_channels + 1)
```

---

#### `VectorLength(vectorEnum: Union[int, vvVector]) -> int`

Get required array length for a raw data vector.

| Parameter | Type | Description |
|-----------|------|-------------|
| `vectorEnum` | int or vvVector | Vector identifier |

**Returns:** `int` - Number of rows in the vector

---

#### `VectorUnit(vectorEnum: Union[int, vvVector]) -> str`

Get units for a raw data vector.

| Parameter | Type | Description |
|-----------|------|-------------|
| `vectorEnum` | int or vvVector | Vector identifier |

**Returns:** `str` - Unit string (e.g., "Hz", "g")

---

#### `VectorLabel(vectorEnum: Union[int, vvVector]) -> str`

Get label for a raw data vector.

| Parameter | Type | Description |
|-----------|------|-------------|
| `vectorEnum` | int or vvVector | Vector identifier |

**Returns:** `str` - Label string

---

### Channel Information

#### `ChannelLabel(channelNum: int) -> str`

Get the label for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channelNum` | int | Channel number (0-based) |

**Returns:** `str` - Channel label

---

#### `ChannelUnit(channelNum: int) -> str`

Get the unit for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channelNum` | int | Channel number (0-based) |

**Returns:** `str` - Channel unit (e.g., "g", "m/s")

---

#### `ControlLabel(loopNum: int) -> str`

Get the control label for a loop.

| Parameter | Type | Description |
|-----------|------|-------------|
| `loopNum` | int | Loop number (0-based) |

**Returns:** `str` - Control label

---

#### `ControlUnit(loopNum: int) -> str`

Get the control unit for a loop.

| Parameter | Type | Description |
|-----------|------|-------------|
| `loopNum` | int | Loop number (0-based) |

**Returns:** `str` - Control unit

---

#### `RearInputLabel(channel: int) -> str`

Get label for a rear input channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `str` - Rear input label

---

#### `RearInputUnit(channel: int) -> str`

Get unit for a rear input channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `str` - Rear input unit

---

### Report Functions

#### `ReportField(fieldName: str) -> Any`

Get a single report field value.

| Parameter | Type | Description |
|-----------|------|-------------|
| `fieldName` | str | Name of the report field |

**Returns:** Field value (type varies by field)

```python
stop_code = vv.ReportField("StopCode")
test_type = vv.ReportField("TestType")
```

---

#### `ReportFields(fields: str, array_out: Optional[List] = None) -> List`

Get multiple report field names and values as a 2D array.

> **Note:** Available field names are documented in VibrationVIEW menu **View > Report Parameters**.

| Parameter | Type | Description |
|-----------|------|-------------|
| `fields` | str | Comma-separated list of field names |
| `array_out` | List, optional | Pre-allocated array |

**Returns:** `List` - 2D array of (parameter, value) pairs

```python
fields = vv.ReportFields("ChName1,ChSensitivity1,StopCode,TestType", None)
for field in fields:
    print(f"{field[0]}: {field[1]}")
```

---

#### `ReportFieldsHistory(fields: str, array_out: Optional[List] = None) -> List`

Get report field values from history files.

| Parameter | Type | Description |
|-----------|------|-------------|
| `fields` | str | Comma-separated list of field names |
| `array_out` | List, optional | Pre-allocated array |

**Returns:** `List` - 2D array of (parameter, value1, value2, ...) rows

---

#### `FormFields() -> List`

Get all form field values as a 2D array.

**Returns:** `List` - 2D array of (parameter, value) pairs containing all form fields

```python
# Get all form fields
fields = vv.FormFields()
for field in fields:
    print(f"{field[0]}: {field[1]}")
```

---

#### `PostFormFields(fields: List) -> bool`

Post form field values from a 2D array, merging with existing form fields.

| Parameter | Type | Description |
|-----------|------|-------------|
| `fields` | List | 2D array of (parameter, value) pairs to post |

**Returns:** `bool` - True if successful

```python
# Post form field values
form_data = [
    ["Operator", "John Smith"],
    ["Notes", "Test run #1"]
]
vv.PostFormFields(form_data)
```

---

#### `ReportVector(vectors: str, array_out: Optional[List] = None) -> List`

Get report vector data.

> **Note:** Available vector names are documented in the VibrationVIEW help file under the "Report Vectors" section.

| Parameter | Type | Description |
|-----------|------|-------------|
| `vectors` | str | Comma-separated list of vector names |
| `array_out` | List, optional | Pre-allocated array |

**Returns:** `List` - Vector data array

```python
vectors = vv.ReportVector("Index,Frequency,Demand,Control", None)
```

---

#### `ReportVectorHeader(vectors: str, array_out: Optional[List] = None) -> List`

Get report vector headers (column names and units).

| Parameter | Type | Description |
|-----------|------|-------------|
| `vectors` | str | Comma-separated list of vector names |
| `array_out` | List, optional | Pre-allocated array |

**Returns:** `List` - Array where first row is column names, second row is units

```python
headers = vv.ReportVectorHeader("Index,Frequency,Demand,Control", None)
column_names = headers[0]
units = headers[1]
```

---

#### `ReportVectorHistory(vectors: str, array_out: Optional[List] = None, header_out: Optional[List] = None) -> tuple`

Get report vector data from history files.

| Parameter | Type | Description |
|-----------|------|-------------|
| `vectors` | str | Comma-separated list of vector names |
| `array_out` | List, optional | Pre-allocated data array |
| `header_out` | List, optional | Pre-allocated header array |

**Returns:** `tuple` - (array_out, header_out)

---

### Hardware Information

#### `GetHardwareInputChannels() -> int`

Get the number of hardware input channels.

**Returns:** `int` - Number of input channels (typically 4, 8, 12, or 16)

```python
num_channels = vv.GetHardwareInputChannels()
print(f"System has {num_channels} input channels")
```

---

#### `GetHardwareOutputChannels() -> int`

Get the number of hardware output channels.

**Returns:** `int` - Number of output channels (typically 1-4)

---

#### `GetHardwareSerialNumber() -> str`

Get the hardware serial number.

**Returns:** `str` - Serial number (0xFFFFFF indicates demo mode)

```python
serial = vv.GetHardwareSerialNumber()
if serial == 0xffffff:
    print("Running in demo mode")
```

---

#### `GetSoftwareVersion() -> str`

Get the VibrationVIEW software version.

**Returns:** `str` - Version string

---

#### `HardwareSupportsCapacitorCoupled(channel: int) -> bool`

Check if hardware supports capacitor coupled input for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `bool` - True if supported

---

#### `HardwareSupportsAccelPowerSource(channel: int) -> bool`

Check if hardware supports accelerometer power source for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `bool` - True if supported

---

#### `HardwareSupportsDifferential(channel: int) -> bool`

Check if hardware supports differential input for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `bool` - True if supported

---

### Input Configuration

#### `InputSensitivity(channel: int) -> float`

Get input sensitivity for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `float` - Sensitivity in mV/unit

---

#### `InputEngineeringScale(channel: int) -> float`

Get input engineering scale for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `float` - Engineering scale value

---

#### `InputSerialNumber(channel: int) -> str`

Get input transducer serial number for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `str` - Serial number

---

#### `InputCalDate(channel: int) -> str`

Get input calibration date for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `str` - Calibration date string

---

#### `InputCapacitorCoupled(channel: int, value: Optional[bool] = None) -> bool`

Get or set input capacitor coupled setting for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |
| `value` | bool, optional | Value to set |

**Returns:** `bool` - Current setting

```python
# Get current setting
is_coupled = vv.InputCapacitorCoupled(0)

# Set value
vv.InputCapacitorCoupled(0, True)
```

---

#### `InputAccelPowerSource(channel: int, value: Optional[bool] = None) -> bool`

Get or set input accelerometer power source (ICP/IEPE) for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |
| `value` | bool, optional | Value to set |

**Returns:** `bool` - Current setting

---

#### `InputDifferential(channel: int, value: Optional[bool] = None) -> bool`

Get or set input differential mode for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |
| `value` | bool, optional | Value to set |

**Returns:** `bool` - Current setting

---

#### `InputMode(channel: int, powerSource: bool, capCoupled: bool, differential: bool) -> bool`

Set all input mode parameters for a channel at once.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |
| `powerSource` | bool | Enable accelerometer power source |
| `capCoupled` | bool | Enable capacitor coupling |
| `differential` | bool | Enable differential mode |

**Returns:** `bool` - True if successful

---

#### `InputCalibration(channel: int, sensitivity: float, serialNumber: str, calDate: str) -> bool`

Set input calibration parameters for a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |
| `sensitivity` | float | Sensitivity in mV/unit |
| `serialNumber` | str | Transducer serial number |
| `calDate` | str | Calibration date string |

**Returns:** `bool` - True if successful

```python
vv.InputCalibration(0, 10.0, "SN12345", "Jan 15, 2025")
```

---

#### `SetInputConfigurationFile(configName: str) -> bool`

Load input configuration from a .vic file.

| Parameter | Type | Description |
|-----------|------|-------------|
| `configName` | str | Path to the .vic configuration file |

**Returns:** `bool` - True if successful

```python
vv.SetInputConfigurationFile("C:\\VibrationVIEW\\InputConfig\\my_config.vic")
```

---

### TEDS Support

#### `Teds(channel: Optional[int] = None) -> List[dict]`

Get TEDS (Transducer Electronic Data Sheet) data for channel(s).

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int, optional | Channel number (0-based). If None, gets all channels. |

**Returns:** `List[dict]` - List of dictionaries containing:
- `Channel`: Channel number (1-based)
- `Teds`: List of (key, value) tuples with TEDS data
- `Error`: Error message if TEDS read failed

```python
# Get TEDS for channel 1
teds = vv.Teds(0)
if "Teds" in teds[0]:
    for key, value in teds[0]["Teds"]:
        print(f"{key}: {value}")

# Get TEDS for all channels
all_teds = vv.Teds()
```

---

#### `TedsRead() -> List[str]`

Get TEDS URNs (Unique Registration Numbers) for all channels.

**Returns:** `List[str]` - Array of URN strings, one per channel

---

#### `TedsReadAndApply() -> List[str]`

Read TEDS URNs from hardware and apply to live mode.

**Returns:** `List[str]` - Array of URN strings after application

---

#### `TedsVerifyAndApply(urn_array: List[str]) -> List[str]`

Verify TEDS data against hardware and apply if matching.

| Parameter | Type | Description |
|-----------|------|-------------|
| `urn_array` | List[str] | Array of URN strings, one per channel |

**Returns:** `List[str]` - URN array after verification and application

---

#### `TedsVerifyStringAndApply(urn_string: str) -> List[str]`

Verify TEDS data from a single URN string and apply if matching.

| Parameter | Type | Description |
|-----------|------|-------------|
| `urn_string` | str | Single URN string |

**Returns:** `List[str]` - URN array after verification and application

---

#### `TedsFromURN(urn: str) -> List[str]`

Lookup and decode TEDS transducer by URN.

| Parameter | Type | Description |
|-----------|------|-------------|
| `urn` | str | Unique Registration Number |

**Returns:** `List[str]` - Array of TEDS data strings

---

### Transducer Database

#### `ChannelDatabaseIDs(channel: int) -> List[str]`

Get database GUIDs associated with a channel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `List[str]` - Array of GUID strings

---

#### `TransducerDatabaseRecord(guid: str) -> List[str]`

Get all database fields for a transducer GUID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `guid` | str | Transducer database GUID |

**Returns:** `List[str]` - Array of database field strings

---

#### `IsChannelDifferentThanDatabase(channel: int) -> bool`

Check if channel configuration differs from database.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `bool` - True if channel differs from database

---

#### `UpdateChannelConfigFromDatabase(channel: int) -> bool`

Read database values and apply to channel configuration.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel` | int | Channel number (0-based) |

**Returns:** `bool` - True if successful

---

### Sine Test Control

These methods are specific to sine tests.

#### `SineFrequency(value: Optional[float] = None) -> float`

Get or set the current sine frequency. (Sine ONLY)

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | float, optional | Frequency to set (Hz) |

**Returns:** `float` - Current frequency (Hz)

```python
# Get current frequency
freq = vv.SineFrequency()

# Set frequency
vv.SineFrequency(100.0)  # Set to 100 Hz
```

---

#### `SweepUp() -> bool`

Change sweep direction to up. (Sine ONLY)

**Returns:** `bool` - True if successful

---

#### `SweepDown() -> bool`

Change sweep direction to down. (Sine ONLY)

**Returns:** `bool` - True if successful

---

#### `SweepStepUp() -> bool`

Step the sine frequency up in 1Hz steps. (Sine ONLY)

**Returns:** `bool` - True if successful

---

#### `SweepStepDown() -> bool`

Step the sine frequency down in 1Hz steps. (Sine ONLY)

**Returns:** `bool` - True if successful

---

#### `SweepHold() -> bool`

Stop sweep and hold at current frequency. (Sine ONLY)

**Returns:** `bool` - True if successful

---

#### `SweepResonanceHold() -> bool`

Stop sweep and hold on resonance. (Sine ONLY)

**Returns:** `bool` - True if successful

---

#### `SweepMultiplier(value: Optional[float] = None) -> float`

Get or set the sweep rate multiplier (0.1x to 10x). (Sine ONLY)

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | float, optional | Multiplier value (0.1 to 10.0, linear) |

**Returns:** `float` - Current multiplier

```python
# Get current multiplier
mult = vv.SweepMultiplier()

# Set to half speed
vv.SweepMultiplier(0.5)
```

---

#### `DemandMultiplier(value: Optional[float] = None) -> float`

Get or set the demand output multiplier in dB. (Sine ONLY)

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | float, optional | Multiplier value (+/- dB) |

**Returns:** `float` - Current multiplier (dB)

---

### System Check

#### `SystemCheckFrequency(value: Optional[float] = None) -> float`

Get or set the system check frequency. (System Check ONLY)

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | float, optional | Frequency to set (Hz) |

**Returns:** `float` - Current frequency (Hz)

---

#### `SystemCheckOutputVoltage(value: Optional[float] = None) -> float`

Get or set the system check output voltage level. (System Check ONLY)

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | float, optional | Voltage to set |

**Returns:** `float` - Current voltage level

---

### Recording

#### `RecordStart() -> bool`

Start recording data.

**Returns:** `bool` - True if successful

---

#### `RecordStop() -> bool`

Stop recording data.

**Returns:** `bool` - True if successful

---

#### `RecordPause() -> bool`

Pause recording data.

**Returns:** `bool` - True if successful

---

#### `RecordGetFilename() -> str`

Get the filename of the last recording.

**Returns:** `str` - Path to the recording file

```python
vv.RecordStart()
time.sleep(30)
vv.RecordStop()
filename = vv.RecordGetFilename()
print(f"Recording saved to: {filename}")
```

---

### Window Control

#### `Minimize() -> bool`

Minimize the VibrationVIEW window.

**Returns:** `bool` - True if successful

---

#### `Maximize() -> bool`

Maximize the VibrationVIEW window.

**Returns:** `bool` - True if successful

---

#### `Restore() -> bool`

Restore the VibrationVIEW window.

**Returns:** `bool` - True if successful

---

#### `Activate() -> bool`

Activate (bring to front) the VibrationVIEW window.

**Returns:** `bool` - True if successful

---

#### `MenuCommand(id: int) -> bool`

Send a menu command to VibrationVIEW.

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | int | Menu command ID |

**Returns:** `bool` - True if successful

---

### Virtual Channels

#### `ImportVirtualChannels(file_path: str) -> bool`

Import virtual channel definitions from a VCHAN file.

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | str | Path to the .vchan file |

**Returns:** `bool` - True if successful

```python
vv.ImportVirtualChannels("C:\\VibrationVIEW\\VirtualChannels\\my_channels.vchan")
```

---

#### `RemoveAllVirtualChannels() -> bool`

Remove all virtual channel definitions.

**Returns:** `bool` - True if successful

---

## Command Line Utilities

These functions generate files using the VibrationVIEW command line interface.

### `GenerateReportFromVV(filePath: str, templateName: str, outputName: str) -> str`

Generate a report from a VibrationVIEW data file.

| Parameter | Type | Description |
|-----------|------|-------------|
| `filePath` | str | Path to the VV data file |
| `templateName` | str | Name of the report template |
| `outputName` | str | Desired output filename |

**Returns:** `str` - Path to the generated report

```python
from vibrationviewapi import GenerateReportFromVV

report_path = GenerateReportFromVV(
    "C:\\Data\\test.vsd",
    "Standard Report",
    "C:\\Reports\\test_report.pdf"
)
```

---

### `GenerateTXTFromVV(filePath: str, outputName: str) -> str`

Convert a VibrationVIEW data file to text format.

| Parameter | Type | Description |
|-----------|------|-------------|
| `filePath` | str | Path to the VV data file |
| `outputName` | str | Desired output filename |

**Returns:** `str` - Path to the generated text file

---

### `GenerateUFFFromVV(filePath: str, outputName: str) -> str`

Convert a VibrationVIEW data file to UFF (Universal File Format).

| Parameter | Type | Description |
|-----------|------|-------------|
| `filePath` | str | Path to the VV data file |
| `outputName` | str | Desired output filename |

**Returns:** `str` - Path to the generated UFF file

---

## Helper Functions

### `ExtractComErrorInfo(exception) -> str`

Extract detailed error information from a COM exception.

```python
from vibrationviewapi import ExtractComErrorInfo

try:
    vv.SomeMethod()
except Exception as e:
    error_msg = ExtractComErrorInfo(e)
    print(f"COM Error: {error_msg}")
```

---

### `get_vibrationview() -> VibrationVIEW`

Get a thread-safe VibrationVIEW instance from the global pool.

**Returns:** `VibrationVIEW` - Instance for the current thread

---

### `return_vibrationview(instance: VibrationVIEW)`

Return a VibrationVIEW instance to the global pool.

| Parameter | Type | Description |
|-----------|------|-------------|
| `instance` | VibrationVIEW | Instance to return |

---

## Thread Safety

The VibrationVIEW API is designed for thread-safe operation in multi-threaded applications.

### Key Features

1. **Thread-local COM objects**: Each thread gets its own COM object
2. **Automatic COM initialization**: COM is initialized per-thread as needed
3. **Connection pooling**: `VibrationVIEWPool` manages instances for web applications
4. **Context manager**: `VibrationVIEWContext` ensures proper cleanup

### Best Practices

```python
# For Flask/web applications, use the context manager
@app.route('/api/status')
def get_status():
    with VibrationVIEWContext() as vv:
        return jsonify({
            'running': vv.IsRunning(),
            'version': vv.GetSoftwareVersion()
        })

# For long-running scripts, create one instance
vv = VibrationVIEW()
try:
    # ... use vv ...
finally:
    vv.close()
```

### COM Threading Notes

- The API uses apartment-threaded COM (COINIT_APARTMENTTHREADED)
- Each thread must have its own COM object
- The `@com_method` decorator handles COM initialization automatically
- If COM errors occur, the API attempts automatic recovery

---

## Version History

| Version | VibrationVIEW Support |
|---------|----------------------|
| 0.1.6 | VibrationVIEW 2018-2025 |
| 0.1.7+ | VibrationVIEW 2026+ |

---

## Support

- **Documentation**: [VibrationVIEW Help File](https://vibrationresearch.com/software-update-files/)
- **Issues**: [GitHub Issues](https://github.com/vibrationresearch/vibrationview-api/issues)
- **Email**: support@vibrationresearch.com
