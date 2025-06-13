"""
VibrationVIEW Python API

A thread-safe Python interface to VibrationVIEW software through COM automation,
suitable for multi-threaded applications like Flask.
xample usage:
    Basic usage:
        from vibrationviewapi import VibrationVIEW
        
        vv = VibrationVIEW()
        version = vv.GetSoftwareVersion()
        vv.close()
    
    Context manager (recommended):
        from vibrationviewapi import VibrationVIEWContext
        
        with VibrationVIEWContext() as vv:
            version = vv.GetSoftwareVersion()
            channels = vv.GetHardwareInputChannels()
    
    Flask application:
        from vibrationviewapi import VibrationVIEWContext
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        
        @app.route('/status')
        def status():
            with VibrationVIEWContext() as vv:
                return jsonify({'version': vv.GetSoftwareVersion()})
"""

__version__ = "0.1.4"
__author__ = "Dan VanBaren"
__email__ = "support@vibrationresearch.com"

# Import main classes and functions to make them available at the package level
from .vibrationviewapi import VibrationVIEW, vvVector, vvTestType
from .vibrationviewcommandline import (
    GenerateReportFromVV,
    GenerateTXTFromVV,
    GenerateUFFFromVV
)
# Import enums
from .vv_enums import vvVector, vvTestType

# Import helper functions
from .comhelper import ExtractComErrorInfo

__version__ = "0.1.4"
__all__ = [
    "VibrationVIEW",
    "VibrationVIEWContext", 
    "VibrationVIEWPool",
    "get_vibrationview",
    "return_vibrationview",
    "vvVector",
    "vvTestType",
    "ExtractComErrorInfo",
    'GenerateReportFromVV',
    'GenerateTXTFromVV',
    'GenerateUFFFromVV'
]
