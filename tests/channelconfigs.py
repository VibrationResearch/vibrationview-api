from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

@dataclass
class TedsConfig:
    """TEDS data configuration for a channel"""
    manufacturer: str
    model_number: str
    version_letter: str
    version_number: str
    serial_no: str
    sensitivity: str
    high_pass_cutoff: str
    sensitivity_direction: str
    weight: str
    polarity: str
    low_pass_cutoff: str
    resonance_frequency: str
    quality_factor: str
    amplitude_slope: str
    temperature_coefficient: str
    reference_frequency: str
    reference_temperature: str
    calibration_date: str
    calibration_initials: str
    calibration_period: str
    measurement_position_id: str
    
    def as_tuples(self) -> List[Tuple[str, str]]:
        """Convert to list of tuples in the format expected by tests"""
        return [
            ('Manufacturer', self.manufacturer),
            ('Model number', self.model_number),
            ('Version letter', self.version_letter),
            ('Version number', self.version_number),
            ('Serial no.', self.serial_no),
            ('Sensitivity @ ref. cond. (S ref)', self.sensitivity),
            ('High pass cut-off frequency (F hp)', self.high_pass_cutoff),
            ('Sensitivity direction (x,y,z, n/a)', self.sensitivity_direction),
            ('Transducer weight', self.weight),
            ('Polarity (Sign)', self.polarity),
            ('Low pass cut-off frequency (F lp)', self.low_pass_cutoff),
            ('Resonance frequency (F res)', self.resonance_frequency),
            ('Quality factor @ F res (Q)', self.quality_factor),
            ('Amplitude slope (a)', self.amplitude_slope),
            ('Temperature coefficient (b)', self.temperature_coefficient),
            ('Reference frequency (F ref)', self.reference_frequency),
            ('Reference temperature (T ref)', self.reference_temperature),
            ('Calibration date', self.calibration_date),
            ('Calibration initials', self.calibration_initials),
            ('Calibration Period', self.calibration_period),
            ('Measurement position ID', self.measurement_position_id)
        ]

@dataclass
class ChannelConfig:
    """Configuration for a single channel"""
    sensitivity: float
    unit: str
    label: str
    cap_coupled: bool
    accel_power: bool
    differential: bool
    serial: str
    cal_date: str
    teds: Optional[TedsConfig] = None

# Define TEDS data for channel 1
CHANNEL1_TEDS = TedsConfig(
    manufacturer="Dytran Instruments",
    model_number="3055",
    version_letter="B",
    version_number="1",
    serial_no="5065",
    sensitivity="10.41 mV/G",
    high_pass_cutoff="0.313 Hz",
    sensitivity_direction="X",
    weight="7.95 gm",
    polarity="+1",
    low_pass_cutoff="33 kHz",
    resonance_frequency="31.8 kHz",
    quality_factor="56.5 ",
    amplitude_slope="-2.3 %/decade",
    temperature_coefficient="0.1 %/°C",
    reference_frequency="98.7 Hz",
    reference_temperature="22.0 °C",
    calibration_date="2008-03-12T17:00:00Z",
    calibration_initials="ED ",
    calibration_period="365 days",
    measurement_position_id="0"
)

# Default configuration for most channels
DEFAULT_CHANNEL = ChannelConfig(
    sensitivity=10.0,
    unit="g",
    label="Acceleration",
    cap_coupled=False,
    accel_power=False,
    differential=False,
    serial="",
    cal_date="",
    teds=None  # Most channels don't have TEDS data
)

# Channel-specific configurations
channel_specific = {
    0: ChannelConfig(  # Channel 1 (index 0) has specific settings
        sensitivity=10.409000396728516,
        unit="g",
        label="Acceleration",
        cap_coupled=False,
        accel_power=True,
        differential=False,
        serial="5065",
        cal_date="Mar 12, 2008",
        teds=CHANNEL1_TEDS
    ),
    1: ChannelConfig(  # Channel 2 (index 1) has specific settings
        sensitivity=10.0,
        unit="g",
        label="Acceleration",
        cap_coupled=False,
        accel_power=True,
        differential=False,
        serial="",
        cal_date="",
        teds=None
    )
}

def get_channel_config(channel_index: int) -> ChannelConfig:
    """Get configuration for a specific channel index"""
    if channel_index in channel_specific:
        return channel_specific[channel_index]
    return DEFAULT_CHANNEL

# For backward compatibility with existing code:
channel_configs = {
    "sensitivities": [get_channel_config(i).sensitivity for i in range(16)],
    "units": [get_channel_config(i).unit for i in range(16)],
    "labels": [get_channel_config(i).label for i in range(16)],
    "cap_coupled": [get_channel_config(i).cap_coupled for i in range(16)],
    "accel_power": [get_channel_config(i).accel_power for i in range(16)],
    "differential": [get_channel_config(i).differential for i in range(16)],
    "serials": [get_channel_config(i).serial for i in range(16)],
    "cal_dates": [get_channel_config(i).cal_date for i in range(16)],
}