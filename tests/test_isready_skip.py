"""Test that IsReady() skips the ready-wait loop in _create_com_object_for_thread().

When IsReady is called and no COM object exists yet, _create_com_object_for_thread
should assign the COM object immediately without polling IsReady in a retry loop.
"""

import os
import sys
import time
import pytest
from unittest.mock import patch, PropertyMock

# Ensure src/ is on the path
current_dir = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(current_dir, "..", "src")
sys.path.insert(0, src_dir)

from .mock_com import MockCOMObject


class TestIsReadySkipsWaitLoop:
    """Verify that IsReady() does not block waiting for itself."""

    def test_falsy_com_object_still_connects_when_ready(self):
        """Ready COM objects should be accepted even if they evaluate False."""
        mock = MockCOMObject()
        type(mock).IsReady = PropertyMock(return_value=1)
        type(mock).__bool__ = lambda self: False

        with patch("win32com.client.Dispatch", return_value=mock):
            from vibrationviewapi import VibrationVIEW

            vv = VibrationVIEW(connection_timeout=2, retry_attempts=1)

            assert vv.vv is mock
            assert vv.IsReady() is True

    def test_isready_returns_false_without_timeout(self):
        """IsReady() should return False immediately when COM reports not ready,
        rather than timing out inside _create_com_object_for_thread."""
        mock = MockCOMObject()
        # Make the underlying COM IsReady return 0 (not ready)
        type(mock).IsReady = PropertyMock(return_value=0)

        with patch("win32com.client.Dispatch", return_value=mock):
            from vibrationviewapi import VibrationVIEW

            # With skip_ready_check, construction should NOT block on IsReady.
            # Use a short timeout so the test fails fast if the skip is broken.
            start = time.monotonic()
            vv = VibrationVIEW(connection_timeout=2, retry_attempts=1)
            result = vv.IsReady()
            elapsed = time.monotonic() - start

            assert result is False
            # Should complete nearly instantly, not wait 2+ seconds
            assert elapsed < 1.0, f"IsReady() took {elapsed:.1f}s — ready-wait was not skipped"

    def test_isready_returns_true(self):
        """IsReady() should return True when COM reports ready."""
        mock = MockCOMObject()
        # Default mock already returns IsReady=1, but be explicit
        type(mock).IsReady = PropertyMock(return_value=1)

        with patch("win32com.client.Dispatch", return_value=mock):
            from vibrationviewapi import VibrationVIEW

            vv = VibrationVIEW(connection_timeout=2, retry_attempts=1)
            assert vv.IsReady() is True

    def test_other_methods_still_wait_for_ready(self):
        """Non-IsReady methods should still go through the ready-wait loop.
        When IsReady is False, the constructor retries and the COM object
        is not assigned, so subsequent method calls trigger another attempt."""
        mock = MockCOMObject()
        type(mock).IsReady = PropertyMock(return_value=0)

        with patch("win32com.client.Dispatch", return_value=mock):
            from vibrationviewapi import VibrationVIEW

            start = time.monotonic()
            vv = VibrationVIEW(connection_timeout=1, retry_attempts=2)
            elapsed = time.monotonic() - start

            # Constructor should have spent time in the retry/wait loop
            assert elapsed >= 0.4, f"Constructor returned too fast ({elapsed:.2f}s) — wait loop was skipped"
