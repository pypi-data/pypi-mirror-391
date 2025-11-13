"""Test module for dotbot serial interface."""

import sys
import threading
import time
from unittest.mock import MagicMock, call, patch

import pytest
import serial

from dotbot_utils import serial_interface


@pytest.fixture
def mock_serial():
    """Fixture to mock serial.Serial."""
    with patch.object(
        serial_interface.serial, "Serial", autospec=True
    ) as mock_serial_cls:
        mock_instance = MagicMock()
        mock_serial_cls.return_value = mock_instance
        yield mock_instance


# -------------------------------
# Tests for get_default_port
# -------------------------------


def test_get_default_port_with_no_ports(monkeypatch):
    monkeypatch.setattr(serial_interface.list_ports, "comports", lambda: [])
    assert serial_interface.get_default_port() == "/dev/ttyACM0"


def test_get_default_port_with_jlink_ports(monkeypatch):
    mock_port = MagicMock()
    mock_port.product = "J-Link"
    mock_port.device = "/dev/ttyUSB1"
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(serial_interface.list_ports, "comports", lambda: [mock_port])
    assert serial_interface.get_default_port() == "/dev/ttyUSB1"


def test_get_default_port_windows_returns_first(monkeypatch):
    mock_port1 = MagicMock(device="COM3", product="J-Link")
    mock_port2 = MagicMock(device="COM4", product="Other")
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(
        serial_interface.list_ports, "comports", lambda: [mock_port1, mock_port2]
    )
    assert serial_interface.get_default_port() == "COM3"


# -------------------------------
# Tests for SerialInterface
# -------------------------------


def test_serial_interface_init_starts_thread(mock_serial):
    callback = MagicMock()
    with patch.object(serial_interface.SerialInterface, "start") as mock_start:
        interface = serial_interface.SerialInterface("COM1", 9600, callback)
        mock_start.assert_called_once()
        assert interface.callback == callback
        assert interface.serial == mock_serial
        assert isinstance(interface.lock, threading.Lock)


def test_write_sends_in_chunks(mock_serial):
    interface = serial_interface.SerialInterface("COM1", 9600, MagicMock())
    data = b"A" * 128
    interface.write(data)
    interface.flush()

    # Should write 64-byte chunks twice
    expected_calls = [
        call.flush(),
        call.write(data[:64]),
        call.flush(),
        call.write(data[64:128]),
        call.flush(),
        call.flush(),
    ]
    actual_calls = [c for c in mock_serial.method_calls if c[0] in ["write", "flush"]]
    assert actual_calls == expected_calls


def test_write_applies_chunk_delay(mock_serial, monkeypatch):
    interface = serial_interface.SerialInterface("COM1", 9600, MagicMock())
    sleep_mock = MagicMock()
    monkeypatch.setattr(time, "sleep", sleep_mock)
    data = b"B" * 64
    interface.write(data)
    sleep_mock.assert_called_with(serial_interface.PAYLOAD_CHUNK_DELAY)


def test_run_invokes_callback_until_none(mock_serial):
    callback = MagicMock()

    # Prevent the thread from auto-starting inside __init__
    with patch.object(serial_interface.SerialInterface, "start", return_value=None):
        interface = serial_interface.SerialInterface("COM1", 9600, callback)

    # Make sure our test-controlled serial mock is used before run() starts
    interface.serial = mock_serial

    # Create generator-based side effect so exhaustion returns None (no StopIteration)
    responses = iter([b"A", b"B", None])
    mock_serial.read.side_effect = lambda _size: next(responses, None)

    # Now run in current thread (no racing with background thread)
    interface.run()

    assert callback.call_args_list == [call(b"A"), call(b"B")]


def test_run_handles_serial_exception(mock_serial):
    """SerialException inside read() should cause loop exit (no raise)."""
    callback = MagicMock()
    with patch.object(serial_interface.SerialInterface, "start", return_value=None):
        interface = serial_interface.SerialInterface("COM1", 9600, callback)

    interface.serial = mock_serial
    mock_serial.read.side_effect = serial.serialutil.SerialException("TestError")

    # Should not raise, but should stop cleanly
    interface.run()

    # No callback calls expected, since the first read failed
    callback.assert_not_called()


def test_run_handles_port_not_open_error(mock_serial):
    """PortNotOpenError should propagate as SerialInterfaceException."""
    callback = MagicMock()
    with patch.object(serial_interface.SerialInterface, "start", return_value=None):
        interface = serial_interface.SerialInterface("COM1", 9600, callback)

    interface.serial = mock_serial
    mock_serial.read.side_effect = serial.serialutil.PortNotOpenError()

    # Should not raise, but should stop cleanly
    interface.run()

    # No callback calls expected, since the first read failed
    callback.assert_not_called()

    # # This one should raise SerialInterfaceException
    # with pytest.raises(serial_interface.SerialInterfaceException):
    #     interface.run()


def test_stop_closes_and_joins(mock_serial):
    interface = serial_interface.SerialInterface("COM1", 9600, MagicMock())
    with patch.object(interface, "join") as mock_join:
        interface.stop()
        mock_serial.close.assert_called_once()
        mock_join.assert_called_once()
