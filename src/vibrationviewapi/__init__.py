"""
VibrationVIEW API: Python interface for VibrationVIEW vibration testing software.

This package provides an interface to VibrationVIEW software through COM automation,
allowing for programmatic control of vibration tests and data acquisition.
"""

__version__ = "0.1.0"
__author__ = "Dan VanBaren"
__email__ = "support@vibrationresearch.com"

# Import main classes and functions to make them available at the package level
from .vibrationviewAPI import VibrationVIEW, vvVector, vvTestType
from .vibrationviewCommandLine import (
    GenerateReportFromVV,
    GenerateTXTFromVV,
    GenerateUFFFromVV
)

# Define what should be available when using "from vibrationviewapi import *"
__all__ = [
    'VibrationVIEW',
    'vvVector',
    'vvTestType',
    'GenerateReportFromVV',
    'GenerateTXTFromVV',
    'GenerateUFFFromVV'
]