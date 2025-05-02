# Import the package with the correct name as shown in pip list
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