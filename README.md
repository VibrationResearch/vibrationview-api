# VibrationVIEW Python API

A Python API wrapper for interfacing with Vibration Research Corporation's VibrationVIEW software.

**Source Code:** [https://github.com/vibrationresearch/vibrationview-api](https://github.com/vibrationresearch/vibrationview-api)

## Overview

This package provides a thread-safe Python interface to VibrationVIEW, allowing for:

- Test automation and control (start, stop, pause, resume)
- Data acquisition and analysis (vectors, report fields, time history)
- Window management
- Channel configuration and calibration
- Input/output monitoring
- TEDS (Transducer Electronic Data Sheet) support
- Transducer database integration
- Virtual channel management
- Recording control
- Specialized test controls (e.g., sine sweep functions)
- Multi-threaded application support (Flask, web services)

The API wraps the COM interface provided by VibrationVIEW to enable seamless integration with Python scripts and applications.

## Installation

```bash
pip install vibrationview-api
```

> **Note:**
> - Version 0.1.6 supports VibrationVIEW 2018-2025
> - Version 0.1.7+ includes VibrationVIEW 2026 functionality

### Requirements

- Windows operating system (compatible with Windows 10 and Windows 11)
- VibrationVIEW software installed
- VibrationVIEW automation option (VR9604) - OR - VibrationVIEW may be run in Simulation mode without any additional hardware or software
- Python 3.7 or higher
- pywin32 (automatically installed as a dependency)

## Quick Start

```python
from vibrationviewapi import VibrationVIEW

# Test basic functionality
try:
    # Connect to VibrationVIEW
    vv = VibrationVIEW()
    
    # Print connection status
    if vv.vv is None:
        print("Failed to connect to VibrationVIEW")
    else:
        print("Connected to VibrationVIEW")
        
        # Get software version
        version = vv.GetSoftwareVersion()
        print(f"VibrationVIEW version: {version}")
        
        # Get hardware info
        input_channels = vv.GetHardwareInputChannels()
        output_channels = vv.GetHardwareOutputChannels()
        print(f"Hardware: {input_channels} input channels, {output_channels} output channels")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    # Clean up resources
    if 'vv' in locals() and vv is not None:
        vv.close()
        print("Connection closed")
```

## Key Features

### Test Control
- Open, start, stop, pause, and resume tests
- Run and edit tests from specified file paths
- Monitor test status (running, starting, changing level, hold, open loop, aborted)
- Close tests by name or tab index
- List all open tests

### Data Acquisition
- Retrieve vector data (time history, frequency, waveform)
- Get channel, control, demand, and output readings
- Access vector properties (units, labels, length)
- Report fields and vectors with history support
- Rear input monitoring

### Window Management
- Minimize, maximize, restore, and activate application windows
- Send menu commands programmatically

### Channel Configuration
- Read and configure channel settings
- Input calibration (sensitivity, serial number, calibration date)
- Configure input modes (power source, capacitor coupled, differential)
- Hardware capability queries
- Load input configuration files

### TEDS Support
- Read TEDS data from hardware
- Verify and apply TEDS data
- Lookup transducers by URN (Unique Registration Number)

### Transducer Database
- Query channel database IDs
- Retrieve transducer database records
- Check and update channel configuration from database

### Virtual Channels
- Import virtual channel definitions from VCHAN files
- Remove all virtual channels

### Recording
- Start, stop, and pause recordings
- Retrieve recording filenames

### Sine-Specific Functions
- Control sweep direction (up/down, step up/down)
- Hold at current frequency or resonance
- Control sweep rate multiplier and amplitude multiplier
- Get/set sine frequency

### System Check
- Configure system check frequency
- Set system check output voltage

### Thread Safety
- Thread-safe COM object management
- Connection pooling for web applications
- Context manager support for easy resource cleanup

## API Documentation

For detailed documentation of all available methods, refer to the VibrationVIEW help file included with the software. The latest version of VibrationVIEW can be downloaded from:
[VibrationVIEW Software Updates](https://vibrationresearch.com/software-update-files/)

## Examples

### Running a Sine Test and Recording Data

```python
from vibrationviewapi import VibrationVIEW
import time

# Connect to VibrationVIEW
vv = VibrationVIEW()

# Wait for VibrationVIEW to be ready
while not vv.IsReady():
    time.sleep(0.5)

# Open a sine test
vv.OpenTest("C:\\VibrationVIEW\\Profiles\\sine_sweep.vsp")

# Start the test
vv.StartTest()

# Start recording
vv.RecordStart()

# Let test run for 30 seconds
time.sleep(30)

# Stop recording
vv.RecordStop()

# Get the recording filename
recording_file = vv.RecordGetFilename()
print(f"Recording saved to: {recording_file}")

# Stop the test
vv.StopTest()
```

### Accessing Channel Information

```python
from vibrationviewapi import VibrationVIEW
import time

# Connect to VibrationVIEW
vv = VibrationVIEW()

# Wait for VibrationVIEW to be ready
while not vv.IsReady():
    time.sleep(0.5)

# Get number of hardware channels
num_channels = vv.GetHardwareInputChannels()
print(f"Hardware has {num_channels} input channels")

# Print information for each channel
for i in range(num_channels):
    channel_num = i + 1  # 1-based for display
    label = vv.ChannelLabel(i)
    unit = vv.ChannelUnit(i)
    sensitivity = vv.InputSensitivity(i)
    
    print(f"Channel {channel_num}:")
    print(f"  Label: {label}")
    print(f"  Unit: {unit}")
    print(f"  Sensitivity: {sensitivity}")
    
    # Try to get TEDS information if available
    teds_info = vv.Teds(i)
    if teds_info and len(teds_info) > 0 and isinstance(teds_info[0], dict) and "Teds" in teds_info[0]:
        print(f"  TEDS data available: {len(teds_info[0]['Teds'])} entries")
```

### Retrieving Report Fields

```python
from vibrationviewapi import VibrationVIEW
import time

# Connect to VibrationVIEW
vv = VibrationVIEW()

# Wait for VibrationVIEW to be ready
while not vv.IsReady():
    time.sleep(0.5)

# Open a test file
vv.OpenTest("C:\\VibrationVIEW\\Profiles\\sine_sweep.vsp")

# Get report fields - returns 2D array of (parameter, value) pairs
field_names = "ChName1,ChAcp1,ChSensitivity1,StopCode,TestType"
fields = vv.ReportFields(field_names, None)

# Print each field
for field in fields:
    print(f"{field[0]}: {field[1]}")
```

### Retrieving Report Vectors

```python
from vibrationviewapi import VibrationVIEW
import time

# Connect to VibrationVIEW
vv = VibrationVIEW()

# Wait for VibrationVIEW to be ready
while not vv.IsReady():
    time.sleep(0.5)

# Open a test file
vv.OpenTest("C:\\VibrationVIEW\\Profiles\\sine_sweep.vsp")

# Start and run the test to generate data
vv.StartTest()
time.sleep(5)
vv.StopTest()

# Get report vectors - comma-separated list of vector names
vector_names = "Index,Frequency,Demand,Control,Drive,Channel1,Channel2"
vectors = vv.ReportVector(vector_names, None)

# Get vector headers (column names and units)
headers = vv.ReportVectorHeader(vector_names, None)
column_names = headers[0]  # First row contains column names
units = headers[1]         # Second row contains units

# Print headers
for i, name in enumerate(column_names):
    print(f"{name} ({units[i]})")

# Print first few data rows
for row in vectors[:5]:
    print(row)
```

