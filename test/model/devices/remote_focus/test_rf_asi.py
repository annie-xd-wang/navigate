import copy
import importlib
import sys
import types
from unittest.mock import MagicMock, patch

import numpy as np
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
    remote_focus.waveforms = {}
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


@pytest.mark.parametrize(
    "sensor_mode,readout_direction,expected",
    [
        ("Light-Sheet", "Bidirectional", (4, 129, 2000.0, 300.0, 300)),
        ("Light-Sheet", "Rev. Bidirectional", (4, 129, 2000.0, 300.0, 300)),
        ("Widefield", "Bidirectional", (2, 132, 2000.0, 300.0, 117.5, 100)),
        ("Light-Sheet", "Top-to-Bottom", (2, 132, 2000.0, 300.0, 117.5, 100)),
    ],
)
def test_adjust_stores_parameters_and_returns_waveforms(
    asi_module, sensor_mode, readout_direction, expected
):
    rf = _new_rf(asi_module, _build_config(sensor_mode, readout_direction))
    # Use enough samples to check delay, voltage range, and waveform length.
    rf.configuration["configuration"]["microscopes"]["TestScope"]["daq"][
        "sample_rate"
    ] = 10000
    rf.remote_focus.waveforms = {"A": {"ch1": (4, 131, 1000, 0, 100)}}
    other_axis = copy.deepcopy(rf.remote_focus.waveforms["A"])

    waveforms = rf.adjust({"ch1": 0.1}, {"ch1": 0.3}, offset=0.2)

    assert set(waveforms) == {"ch1"}
    assert waveforms is rf.waveform_dict
    assert rf.remote_focus.waveforms["B"]["ch1"] == pytest.approx(expected)
    assert rf.remote_focus.waveforms["A"] == other_axis
    waveform = waveforms["ch1"]
    assert isinstance(waveform, np.ndarray)
    assert waveform.size == (6000 if expected[1] == 129 else 3000)
    assert waveform.min() == pytest.approx(-1.7)
    assert waveform.max() == pytest.approx(2.3)
    rf.remote_focus.single_axis_waveform.assert_not_called()
    rf.remote_focus.single_axis_mode.assert_not_called()


@pytest.mark.parametrize("invalid", ["-", "."])
def test_adjust_validates_incomplete_values(asi_module, invalid):
    config = _build_config()
    constants = config["waveform_constants"]["remote_focus_constants"]["test_mode"][
        "1x"
    ]["488"]
    constants.update(amplitude=invalid, offset=invalid)
    rf = _new_rf(asi_module, config)

    rf.adjust({"ch1": 0.1}, {"ch1": 0.3}, offset=0.5)

    assert rf.remote_focus.waveforms["B"]["ch1"] == (
        2,
        132,
        1000000.0,
        500.0,
        117.5,
        100,
    )


@pytest.mark.parametrize("readout_direction", ["Bidirectional", "Top-to-Bottom"])
def test_adjust_keeps_offset_independent_for_each_channel(
    asi_module, readout_direction
):
    rf = _new_rf(asi_module, _build_config("Light-Sheet", readout_direction))
    channels = rf.configuration["experiment"]["MicroscopeState"]["channels"]
    channels["ch2"]["is_selected"] = True
    exposure_times = {"ch1": 0.1, "ch2": 0.05}
    sweep_times = {"ch1": 0.3, "ch2": 0.2}

    waveforms = rf.adjust(exposure_times, sweep_times, offset=0.2)

    assert set(waveforms) == {"ch1", "ch2"}
    assert rf.remote_focus.waveforms["B"]["ch1"][3] == pytest.approx(300)
    assert rf.remote_focus.waveforms["B"]["ch2"][3] == pytest.approx(200)

    channels["ch1"]["is_selected"] = False
    waveforms = rf.adjust(exposure_times, sweep_times)
    assert set(waveforms) == {"ch2"}
    assert set(rf.remote_focus.waveforms["B"]) == {"ch2"}
    assert rf.remote_focus.waveforms["B"]["ch2"][3] == 0


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
