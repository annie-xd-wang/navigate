import copy
import importlib
import sys
import types
from unittest.mock import MagicMock, patch

import pytest


MODULE_PATH = "navigate.model.devices.remote_focus.asi"
TIGER_MODULE_PATH = "navigate.model.devices.APIs.asi.asi_tiger_controller"


class _FakeTigerController:
    default_is_open = True

    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.connect_calls = 0
        self.disconnect_calls = 0
        self._is_open = type(self).default_is_open

    def connect_to_serial(self):
        self.connect_calls += 1

    def is_open(self):
        return self._is_open

    def disconnect_from_serial(self):
        self.disconnect_calls += 1


@pytest.fixture
def asi_module(monkeypatch):
    _FakeTigerController.default_is_open = True

    fake_tiger_module = types.ModuleType(TIGER_MODULE_PATH)
    fake_tiger_module.TigerController = _FakeTigerController
    monkeypatch.setitem(sys.modules, TIGER_MODULE_PATH, fake_tiger_module)

    sys.modules.pop(MODULE_PATH, None)
    module = importlib.import_module(MODULE_PATH)
    return importlib.reload(module)


def _build_config(sensor_mode="Widefield", readout_direction="Top-to-Bottom"):
    return {
        "configuration": {
            "microscopes": {
                "TestScope": {
                    "remote_focus": {
                        "hardware": {
                            "axis": "B",
                            "max": 5.0,
                            "min": -5.0,
                            "channel": "Dev7/ao3",
                        }
                    },
                    "daq": {"sample_rate": 10, "trigger_source": "PFI1"},
                }
            }
        },
        "experiment": {
            "CameraParameters": {
                "TestScope": {
                    "sensor_mode": sensor_mode,
                    "readout_direction": readout_direction,
                }
            },
            "MicroscopeState": {
                "microscope_name": "test_mode",
                "zoom": "1x",
                "channels": {
                    "ch1": {"is_selected": True, "laser": "488"},
                    "ch2": {"is_selected": False, "laser": "561"},
                },
            },
        },
        "waveform_constants": {
            "other_constants": {
                "camera_delay": "5",
                "remote_focus_ramp_falling": "17.5",
                "remote_focus_delay": "0",
                "percent_smoothing": "0",
            },
            "remote_focus_constants": {
                "test_mode": {
                    "1x": {
                        "488": {"amplitude": "2.0", "offset": "0.1"},
                        "561": {"amplitude": "1.0", "offset": "0.0"},
                    }
                }
            },
        },
    }


def _new_rf(asi_module, config=None, remote_focus=None):
    if config is None:
        config = _build_config()
    if remote_focus is None:
        remote_focus = MagicMock()
        remote_focus.is_open.return_value = False
    return asi_module.ASIRemoteFocus("TestScope", remote_focus, copy.deepcopy(config))


def test_connect_success(asi_module):
    controller = asi_module.ASIRemoteFocus.connect(port="COM5", baudrate=9600)

    assert isinstance(controller, _FakeTigerController)
    assert controller.port == "COM5"
    assert controller.baudrate == 9600
    assert controller.connect_calls == 1


def test_connect_raises_when_not_open(asi_module):
    _FakeTigerController.default_is_open = False

    with patch.object(asi_module.logger, "error") as mock_error:
        with pytest.raises(Exception, match="ASI stage connection failed."):
            asi_module.ASIRemoteFocus.connect(port="COM5")

    mock_error.assert_called_once_with("ASI stage connection failed.")


def test_adjust_returns_base_waveforms_without_programming_hardware(asi_module):
    device = _new_rf(asi_module)
    waveforms = {"channel_1": object()}
    exposure_times = {"channel_1": 0.1}
    sweep_times = {"channel_1": 0.2}
    with patch.object(
        asi_module.RemoteFocusBase, "adjust", return_value=waveforms
    ) as adjust:
        result = device.adjust(exposure_times, sweep_times, offset=0.25)

    assert result is waveforms
    adjust.assert_called_once_with(exposure_times, sweep_times, 0.25)
    controller = device.remote_focus
    controller.single_axis_waveform.assert_not_called()
    controller.single_axis_mode.assert_not_called()
    controller.is_open.return_value = False


def test_move_delegates_to_adjust(asi_module):
    rf = _new_rf(asi_module)
    rf.adjust = MagicMock()

    exposure_times = {"ch1": 0.2}
    sweep_times = {"ch1": 0.3}
    rf.move(exposure_times, sweep_times, offset=-0.1)

    rf.adjust.assert_called_once_with(exposure_times, sweep_times, -0.1)
    rf.remote_focus.is_open.return_value = False


def test_close_turns_off_and_disconnects_when_open(asi_module):
    remote_focus = MagicMock()
    remote_focus.is_open.return_value = True
    rf = _new_rf(asi_module, remote_focus=remote_focus)

    rf.close()

    remote_focus.single_axis_mode.assert_called_once_with("B", 0)
    remote_focus.disconnect_from_serial.assert_called_once_with()
    remote_focus.is_open.return_value = False


def test_close_is_noop_when_not_open(asi_module):
    remote_focus = MagicMock()
    remote_focus.is_open.return_value = False
    rf = _new_rf(asi_module, remote_focus=remote_focus)

    rf.close()

    remote_focus.single_axis_mode.assert_not_called()
    remote_focus.disconnect_from_serial.assert_not_called()
    remote_focus.is_open.return_value = False


@pytest.mark.parametrize(
    "direction", ["Top-to-Bottom", "Bidirectional", "Rev. Bidirectional"]
)
def test_adjust_generates_sampled_remote_focus_waveforms(asi_module, direction):
    config = _build_config(sensor_mode="Light-Sheet", readout_direction=direction)
    config["configuration"]["microscopes"]["TestScope"]["daq"]["sample_rate"] = 1000
    device = _new_rf(asi_module, config=config)
    result = device.adjust({"ch1": 0.1}, {"ch1": 0.3}, offset=0.25)
    assert result is device.waveform_dict
    assert result["ch1"].size > 0
    assert "ch2" not in result
    assert result["ch1"].min() >= -5
    assert result["ch1"].max() <= 5
    device.remote_focus.single_axis_waveform.assert_not_called()
