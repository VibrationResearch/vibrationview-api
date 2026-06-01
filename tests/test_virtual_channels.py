#!/usr/bin/env python
"""
Tests for Virtual Channel functions in VibrationVIEW API

Tests ImportVirtualChannels and RemoveAllVirtualChannels functions.
"""

import os
import sys
import logging
import pytest
from .conftest import VV_COM_AVAILABLE

pytestmark = pytest.mark.skipif(not VV_COM_AVAILABLE, reason="Requires VibrationVIEW COM server")

# Configure logger
logger = logging.getLogger(__name__)

# Get the absolute path of the current file's directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Construct the path to the sibling 'src' directory
src_dir = os.path.join(current_dir, '..', 'src')

# Add the 'src' directory to sys.path at the beginning to ensure it takes priority
sys.path.insert(0, src_dir)

try:
    from vibrationviewapi import VibrationVIEW, ExtractComErrorInfo
except ImportError:
    pytest.skip("Could not import VibrationVIEW API.", allow_module_level=True)


class TestVirtualChannels:
    """Test class for virtual channel functions"""

    @pytest.mark.vchan
    def test_remove_all_virtual_channels(self):
        """Test RemoveAllVirtualChannels function"""
        # First, find and import a .vchan file so we have something to remove
        inputconfig_folder = os.path.join(current_dir, '..', 'inputconfig')
        vchan_file = None

        if os.path.exists(inputconfig_folder):
            for file in os.listdir(inputconfig_folder):
                if file.lower().endswith('.vchan'):
                    vchan_file = os.path.normpath(os.path.join(inputconfig_folder, file))
                    break

        if vchan_file is None:
            pytest.skip("No .vchan file found for testing RemoveAllVirtualChannels")

        try:
            # Import virtual channels first
            import_result = self.vv.ImportVirtualChannels(vchan_file)
            assert import_result is True, f"ImportVirtualChannels returned {import_result}"
            logger.info(f"ImportVirtualChannels({vchan_file}) returned: {import_result}")

            # Now remove all virtual channels
            result = self.vv.RemoveAllVirtualChannels()
            assert result is True, f"RemoveAllVirtualChannels returned {result}"
            logger.info(f"RemoveAllVirtualChannels returned: {result}")

            # Verify that all virtual channels were actually removed
            vchan_status = self.vv.ReportField("VirtualChannels")
            assert vchan_status == "none", f"Expected 'none' but got '{vchan_status}'"
            logger.info(f"Verified VirtualChannels = '{vchan_status}'")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in RemoveAllVirtualChannels: {error_info}")
            pytest.fail(f"RemoveAllVirtualChannels failed: {error_info}")

    @pytest.mark.vchan
    def test_import_virtual_channels_nonexistent_file(self):
        """Test ImportVirtualChannels with non-existent file"""
        try:
            # Attempt to import a non-existent file - should fail or return False
            result = self.vv.ImportVirtualChannels("nonexistent_file.vchan")
            # The function may return False or raise an exception for invalid file
            logger.info(f"ImportVirtualChannels with non-existent file returned: {result}")
        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.info(f"ImportVirtualChannels correctly rejected non-existent file: {error_info}")
            # This is expected behavior - failing on invalid file is acceptable

    @pytest.mark.vchan
    def test_import_virtual_channels_with_valid_file(self):
        """Test ImportVirtualChannels with a valid VCHAN file if available"""
        # Look for a .vchan file in the inputconfig folder
        inputconfig_folder = os.path.join(current_dir, '..', 'inputconfig')
        vchan_file = None

        if os.path.exists(inputconfig_folder):
            for file in os.listdir(inputconfig_folder):
                if file.lower().endswith('.vchan'):
                    vchan_file = os.path.normpath(os.path.join(inputconfig_folder, file))
                    break

        if vchan_file is None:
            pytest.skip("No .vchan file found for testing ImportVirtualChannels")

        try:
            # Import the virtual channels
            result = self.vv.ImportVirtualChannels(vchan_file)
            assert result is True, f"ImportVirtualChannels returned {result}"
            logger.info(f"ImportVirtualChannels({vchan_file}) returned: {result}")

            # Verify that virtual channels were actually imported
            vchan_status = self.vv.ReportField("VirtualChannels")
            assert vchan_status != "none", f"Expected virtual channels but got '{vchan_status}'"
            logger.info(f"Verified VirtualChannels = '{vchan_status}'")

            # Clean up - remove the imported virtual channels
            cleanup_result = self.vv.RemoveAllVirtualChannels()
            logger.info(f"Cleanup RemoveAllVirtualChannels returned: {cleanup_result}")

        except Exception as e:
            error_info = ExtractComErrorInfo(e)
            logger.error(f"Error in ImportVirtualChannels: {error_info}")
            pytest.fail(f"ImportVirtualChannels failed: {error_info}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)8s] %(message)s",
        handlers=[
            logging.FileHandler("virtual_channels_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    print("=" * 80)
    print("VibrationVIEW Virtual Channels Test")
    print("=" * 80)
    print("Run with: pytest test_virtual_channels.py -v")
    print("=" * 80)
