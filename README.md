# VibrationVIEW Python API

A Python API wrapper for interfacing with Vibration Research Corporation's VibrationVIEW software.

[![PyPI version](https://img.shields.io/pypi/v/vibrationview-api.svg)](https://pypi.org/project/vibrationview-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This package provides a Python interface to VibrationVIEW, allowing for:

- Test automation and control (start, stop, pause)
- Data acquisition and analysis
- Window management
- Channel configuration
- Input/output monitoring
- File operations
- Specialized test controls (e.g., sine sweep functions)

The API wraps the COM interface provided by VibrationVIEW to enable seamless integration with Python scripts and applications.

## Installation

```bash
pip install vibrationview-api
```

### Requirements

- Windows operating system (compatible with Windows 10 and Windows 11)
- VibrationVIEW software installed (compatible with version 10.0 and above)
- Python 3.7 or higher
- pywin32 (automatically installed as a dependency)
- psutil (automatically installed as a dependency)

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

## Key Features

### Test Control
- Open, start, stop, and pause tests
- Run tests from specified file paths
- Monitor test status

### Data Acquisition
- Retrieve vector data (time, frequency, waveform)
- Get channel readings and control values
- Access vector properties (units, labels, length)

### Window Management
- Minimize, maximize, restore and activate application windows
- Control window state programmatically

### Channel Configuration
- Read and configure channel settings
- Access TEDS data
- Configure input properties (sensitivity, coupling, etc.)

### Sine-Specific Functions
- Control sweep direction and rate
- Adjust sweep and demand multipliers
- Hold at specific frequencies or resonances

### File Operations
- Save test data
- Export data to various formats using the command-line utilities

## API Documentation

For detailed documentation of all available methods, please visit:
[VibrationVIEW API Documentation](https://www.vibrationresearch.com/vibrationview-api/)

## Examples

### Running a Sine Test and Recording Data

```python
from vibrationviewapi import VibrationVIEW
import time
import os

# Connect to VibrationVIEW
vv = VibrationVIEW()

# Open a sine test
vv.OpenTest("C:\\VibrationVIEW\\Profiles\\sine_sweep.vsp")

# Start the test
vv.StartTest()

# Wait for test to enter running state
time.sleep(2)

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

# Connect to VibrationVIEW
vv = VibrationVIEW()

# Get number of hardware channels
num_channels = vv.GetHardwareInputChannels()
print(f"Hardware has {num_channels} input channels")

# Get TEDS information for all channels
teds_data = vv.Teds()  # This calls the Teds method without a channel parameter to get all channels

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
    
    # Find the corresponding TEDS data for this channel
    channel_teds = next((item for item in teds_data if item.get("Channel") == channel_num), None)
    
    if channel_teds and "Teds" in channel_teds:
        teds_entries = channel_teds["Teds"]
        print(f"  TEDS data available: {len(teds_entries)} entries")
        
        # List all TEDS entries
        print("  TEDS entries:")
        for key, value in teds_entries:
            print(f"    {key}: {value}")
    else:
        print("  No TEDS data available")
```

## Contributing

This is an official software distribution repository maintained by Vibration Research Corporation. It is not actively monitored for community contributions. If you encounter issues or have feature requests, please contact Vibration Research Corporation directly through our support channels.

For any questions or support regarding this API, please visit our website or contact our technical support team.


## License

This project is licensed under the MIT License with VibrationVIEW Attribution - see the LICENSE file for details.

## Acknowledgements

- VibrationVIEW is a registered trademark of Vibration Research Corporation.
- This API is developed and maintained by Vibration Research Corporation.
