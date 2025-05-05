"""
VibrationVIEW API: Python interface for VibrationVIEW vibration testing software.

This package provides an interface to VibrationVIEW software through COM automation,
allowing for programmatic control of vibration tests and data acquisition.
"""

__version__ = "0.1.0"
__author__ = "Dan VanBaren"
__email__ = "support@vibrationresearch.com"

# Import main classes and functions to make them available at the package level
from .vibrationviewapi import VibrationVIEW, vvVector, vvTestType
from .vibrationviewcommandline import (
    GenerateReportFromVV,
    GenerateTXTFromVV,
    GenerateUFFFromVV
)
from .comhelper import ExtractComErrorInfo

# Define what should be available when using "from vibrationviewapi import *"
__all__ = [
    'VibrationVIEW',
    'vvVector',
    'vvTestType',
    'ExtractComErrorInfo',
    'GenerateReportFromVV',
    'GenerateTXTFromVV',
    'GenerateUFFFromVV'
]