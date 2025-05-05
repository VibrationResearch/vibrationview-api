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