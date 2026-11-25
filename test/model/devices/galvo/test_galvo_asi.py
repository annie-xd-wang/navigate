# Copyright (c) 2021-2026  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only (subject to the
# limitations in the disclaimer below) provided that the following conditions are met:

#      * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.

#      * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.

#      * Neither the name of the copyright holders nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.

# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import importlib
import sys
import types
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


MODULE_PATH = "navigate.model.devices.galvo.asi"
TIGER_MODULE_PATH = "navigate.model.devices.APIs.asi.asi_tiger_controller"


class _ImportTigerController:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self._open = False

    def connect_to_serial(self):
        self._open = True

    def is_open(self):
        return self._open


@pytest.fixture
def asi_module(monkeypatch):
    tiger_module = types.ModuleType(TIGER_MODULE_PATH)
    tiger_module.TigerController = _ImportTigerController

    monkeypatch.setitem(sys.modules, TIGER_MODULE_PATH, tiger_module)

    sys.modules.pop(MODULE_PATH, None)
    module = importlib.import_module(MODULE_PATH)
    module = importlib.reload(module)
    return module


def build_asi_configuration(
    *,
    waveform="sawtooth",
    galvo_factor="none",
    amplitude="1.0",
    offset="0.0",
    frequency="2.0",
    rising_ramp="50",
    channel_1_selected=True,
    channel_2_selected=True,
    channel_overrides=None,
    laser_overrides=None,
):
    galvo_parameters = {
        "amplitude": amplitude,
        "offset": offset,
        "rising_ramp": rising_ramp,
        "frequency": frequency,
    }
    if channel_overrides:
        galvo_parameters.update(channel_overrides)
    if laser_overrides:
        galvo_parameters.update(laser_overrides)

    return {
        "configuration": {
            "microscopes": {
                "TestScope": {
                    "galvo": [
                        {
                            "hardware": {
                                "max": 5.0,
                                "min": -5.0,
                                "channel": "Dev1/ao0",
                                "axis": "B",
                            },
                            "waveform": waveform,
                            "phase": 0.25,
                        }
                    ],
                    "daq": {
                        "sample_rate": 100,
                        "trigger_source": "/Dev1/PFI0",
                    },
                }
            }
        },
        "experiment": {
            "MicroscopeState": {
                "microscope_name": "TestScope",
                "zoom": "1x",
                "channels": {
                    "channel_1": {"is_selected": channel_1_selected, "laser": "488"},
                    "channel_2": {"is_selected": channel_2_selected, "laser": "561"},
                },
            }
        },
        "waveform_constants": {
            "other_constants": {
                "camera_delay": "0",
                "galvo_factor": galvo_factor,
            },
            "galvo_constants": {
                "Galvo 0": {
                    "TestScope": {
                        "1x": galvo_parameters,
                    }
                },
            },
        },
    }


def build_asi_galvo(module, configuration=None, controller=None):
    if configuration is None:
        configuration = build_asi_configuration()
    if controller is None:
        controller = MagicMock(name="TigerController")
        controller.is_open.return_value = True
        controller.waveforms = {}
    galvo = module.ASIGalvo("TestScope", controller, configuration, device_id=0)
    return galvo, controller


def default_timing():
    exposure_times = {"channel_1": 0.2, "channel_2": 0.2}
    sweep_times = {"channel_1": 0.2, "channel_2": 0.2}
    return exposure_times, sweep_times


def test_init_and_str(asi_module):
    galvo, controller = build_asi_galvo(asi_module)

    assert str(galvo) == "GalvoASI"
    assert galvo.galvo is controller
    assert galvo.axis == "B"

    galvo.close = lambda: None


def test_connect_success(asi_module):
    tiger = MagicMock(name="TigerController")
    tiger.is_open.return_value = True

    with patch.object(asi_module, "TigerController", return_value=tiger) as tiger_cls:
        result = asi_module.ASIGalvo.connect("COM7", baudrate=57600, timeout=0.1)

    assert result is tiger
    tiger_cls.assert_called_once_with("COM7", 57600)
    tiger.connect_to_serial.assert_called_once_with()


def test_connect_failure_raises(asi_module):
    tiger = MagicMock(name="TigerController")
    tiger.is_open.return_value = False

    with patch.object(asi_module, "TigerController", return_value=tiger):
        with patch.object(asi_module.logger, "error") as mock_error:
            with pytest.raises(Exception, match="ASI stage connection failed"):
                asi_module.ASIGalvo.connect("COM8")

    mock_error.assert_called_once_with("ASI stage connection failed.")


@pytest.mark.parametrize(
    "waveform,duty_cycle,expected",
    [
        ("sawtooth", "0", (4, 128, -2000.0, 500.0, 11)),
        ("sawtooth", "50", (4, 129, 2000.0, 500.0, 12)),
        ("sawtooth", "100", (4, 128, 2000.0, 500.0, 11)),
        ("sine", "50", (4, 131, 2000.0, 500.0, 11)),
    ],
)
def test_adjust_stores_parameters_and_returns_waveforms(
    asi_module, waveform: str, duty_cycle: str, expected: tuple
) -> None:
    configuration = build_asi_configuration(
        waveform=waveform,
        amplitude="2.0",
        offset="0.5",
        frequency="1",
        rising_ramp=duty_cycle,
        channel_2_selected=False,
    )
    galvo, controller = build_asi_galvo(asi_module, configuration=configuration)
    # Changing the rate after initialization must affect the sampled waveform.
    configuration["configuration"]["microscopes"]["TestScope"]["daq"][
        "sample_rate"
    ] = 10000
    controller.waveforms = {"A": {"channel_1": (4, 131, 1000, 0, 100)}}
    other_axis = controller.waveforms["A"].copy()

    waveforms = galvo.adjust({"channel_1": 0.011}, {"channel_1": 0.022})

    assert waveforms is galvo.waveform_dict
    assert set(waveforms) == {"channel_1"}
    assert controller.waveforms["B"] == {"channel_1": expected}
    assert controller.waveforms["A"] == other_axis
    samples = waveforms["channel_1"]
    assert isinstance(samples, np.ndarray)
    assert samples.size == 220
    assert np.isfinite(samples).all()
    assert samples.min() == pytest.approx(-1.5, abs=0.02)
    assert samples.max() == pytest.approx(2.5, abs=0.02)
    # Check shape and frequency using known points in the first cycle.
    assert samples[0] == pytest.approx(
        0.5 if waveform == "sine" else 2.5 if duty_cycle == "0" else -1.5
    )
    if waveform == "sine":
        assert samples[27] == pytest.approx(2.5, abs=0.01)
        assert samples[82] == pytest.approx(-1.5, abs=0.01)
    elif duty_cycle == "50":
        assert samples[55] == pytest.approx(2.5, abs=0.02)
    else:
        assert samples[55] == pytest.approx(0.5, abs=0.02)
    controller.single_axis_waveform.assert_not_called()
    controller.single_axis_mode.assert_not_called()
    galvo.close = lambda: None


@pytest.mark.parametrize("rising_ramp,corrected", [("12", 0), ("63", 50), ("88", 100)])
def test_adjust_sawtooth_rounds_invalid_duty_cycle(
    asi_module, rising_ramp: str, corrected: int
) -> None:
    configuration = build_asi_configuration(
        rising_ramp=rising_ramp, channel_2_selected=False
    )
    galvo, controller = build_asi_galvo(asi_module, configuration=configuration)

    waveforms = galvo.adjust(*default_timing())

    assert set(waveforms) == {"channel_1"}
    assert controller.waveforms["B"]["channel_1"] == (
        4,
        129 if corrected == 50 else 128,
        -1000.0 if corrected == 0 else 1000.0,
        0.0,
        100,
    )
    assert (
        configuration["waveform_constants"]["galvo_constants"]["Galvo 0"]["TestScope"][
            "1x"
        ]["rising ramp"]
        == corrected
    )
    galvo.close = lambda: None


@pytest.mark.parametrize("waveform", ["sine", "sawtooth"])
@pytest.mark.parametrize("factor", ["channel", "laser"])
def test_adjust_keeps_channel_parameters_independent(
    asi_module, waveform: str, factor: str
) -> None:
    overrides = {
        "Channel 1" if factor == "channel" else "488": {
            "amplitude": "2.0",
            "offset": "0.5",
        },
        "Channel 2" if factor == "channel" else "561": {
            "amplitude": "3.0",
            "offset": "-0.2",
        },
    }
    configuration = build_asi_configuration(
        waveform=waveform, galvo_factor=factor, channel_overrides=overrides
    )
    galvo, controller = build_asi_galvo(asi_module, configuration=configuration)
    exposure_times = {"channel_1": 0.2, "channel_2": 0.4}
    sweep_times = {"channel_1": 0.2, "channel_2": 0.3}

    waveforms = galvo.adjust(exposure_times, sweep_times)

    waveform_id = 131 if waveform == "sine" else 129
    assert controller.waveforms["B"] == {
        "channel_1": (4, waveform_id, 2000.0, 500.0, 100),
        "channel_2": (4, waveform_id, 3000.0, -200.0, 200),
    }
    assert {key: value.size for key, value in waveforms.items()} == {
        "channel_1": 20,
        "channel_2": 30,
    }
    assert waveforms["channel_1"][0] == pytest.approx(
        0.5 if waveform == "sine" else -1.5
    )
    assert waveforms["channel_2"][0] == pytest.approx(
        -0.2 if waveform == "sine" else -3.2
    )

    configuration["experiment"]["MicroscopeState"]["channels"]["channel_1"][
        "is_selected"
    ] = False
    waveforms = galvo.adjust(exposure_times, sweep_times)
    assert set(waveforms) == {"channel_2"}
    assert set(controller.waveforms["B"]) == {"channel_2"}
    galvo.close = lambda: None


@pytest.mark.parametrize("waveform", ["sine", "sawtooth"])
def test_adjust_with_no_selected_channels_clears_stale_waveforms(
    asi_module, waveform: str
) -> None:
    galvo, controller = build_asi_galvo(
        asi_module, build_asi_configuration(waveform=waveform)
    )
    galvo.adjust(*default_timing())
    for channel in galvo.configuration["experiment"]["MicroscopeState"][
        "channels"
    ].values():
        channel["is_selected"] = False

    assert galvo.adjust({}, {}) == {}
    assert controller.waveforms["B"] == {}
    galvo.close = lambda: None


def test_adjust_initializes_controller_waveform_storage(asi_module) -> None:
    controller = MagicMock(spec=["is_open", "single_axis_waveform", "single_axis_mode"])
    controller.is_open.return_value = False
    galvo, _ = build_asi_galvo(asi_module, controller=controller)

    galvo.adjust(*default_timing())

    assert isinstance(controller.waveforms, dict)
    assert set(controller.waveforms["B"]) == {"channel_1", "channel_2"}
    galvo.close = lambda: None


def test_adjust_sine_zero_frequency_uses_exposure_period(asi_module) -> None:
    galvo, controller = build_asi_galvo(
        asi_module,
        build_asi_configuration(waveform="sine", frequency="0", offset="-0.2"),
    )

    waveforms = galvo.adjust(*default_timing())

    for channel in ("channel_1", "channel_2"):
        assert controller.waveforms["B"][channel] == (4, 131, 1000.0, -200.0, 200)
        np.testing.assert_allclose(waveforms[channel], np.full(20, -0.2))
    galvo.close = lambda: None


@pytest.mark.parametrize("waveform", ["sine", "sawtooth"])
def test_adjust_applies_camera_delay_to_sampled_waveform(
    asi_module, waveform: str
) -> None:
    configuration = build_asi_configuration(waveform=waveform, channel_2_selected=False)
    galvo, controller = build_asi_galvo(asi_module, configuration)
    before = galvo.adjust(*default_timing())["channel_1"].copy()
    parameters = controller.waveforms["B"]["channel_1"]
    configuration["waveform_constants"]["other_constants"]["camera_delay"] = "25"

    after = galvo.adjust(*default_timing())["channel_1"]

    assert not np.allclose(before, after)
    assert after[0] == pytest.approx(-np.sin(0.025) if waveform == "sine" else 0.0)
    assert controller.waveforms["B"]["channel_1"] == parameters
    galvo.close = lambda: None


def test_adjust_unknown_waveform_prints_message(asi_module) -> None:
    configuration = build_asi_configuration(waveform="banana", channel_2_selected=False)
    galvo, controller = build_asi_galvo(asi_module, configuration=configuration)

    with patch("builtins.print") as mock_print:
        result = galvo.adjust(*default_timing())

    assert result == {}
    assert controller.waveforms["B"] == {}
    controller.single_axis_waveform.assert_not_called()
    controller.single_axis_mode.assert_not_called()
    mock_print.assert_called_with(
        "Unknown Galvo waveform specified in configuration file."
    )
    galvo.close = lambda: None


@pytest.mark.parametrize(
    "parameter", ["amplitude", "offset", "frequency", "rising_ramp"]
)
@pytest.mark.parametrize("invalid", ["not-a-number", "-", "."])
def test_adjust_returns_none_on_invalid_waveform_constants(
    asi_module, parameter: str, invalid: str
) -> None:
    configuration = build_asi_configuration(
        channel_2_selected=False, **{parameter: invalid}
    )
    galvo, controller = build_asi_galvo(asi_module, configuration=configuration)

    with patch.object(asi_module.logger, "debug") as mock_debug:
        result = galvo.adjust(*default_timing())

    assert result is None
    assert controller.waveforms["B"] == {}
    mock_debug.assert_called_once()
    controller.single_axis_waveform.assert_not_called()
    controller.single_axis_mode.assert_not_called()
    galvo.close = lambda: None


def test_turn_off_sets_single_axis_mode_zero(asi_module):
    galvo, controller = build_asi_galvo(asi_module)

    galvo.turn_off()

    controller.single_axis_mode.assert_called_once_with("B", 0)

    galvo.close = lambda: None


def test_close_turns_off_and_disconnects_when_open(asi_module):
    galvo, controller = build_asi_galvo(asi_module)
    controller.is_open.return_value = True

    with patch.object(galvo, "turn_off") as mock_turn_off:
        galvo.close()

    mock_turn_off.assert_called_once_with()
    controller.disconnect_from_serial.assert_called_once_with()

    galvo.close = lambda: None


def test_close_is_noop_when_controller_not_open(asi_module):
    galvo, controller = build_asi_galvo(asi_module)
    controller.is_open.return_value = False

    with patch.object(galvo, "turn_off") as mock_turn_off:
        galvo.close()

    mock_turn_off.assert_not_called()
    controller.disconnect_from_serial.assert_not_called()

    galvo.close = lambda: None


def test_del_calls_close(asi_module):
    galvo, _ = build_asi_galvo(asi_module)

    with patch.object(galvo, "close") as mock_close:
        galvo.__del__()

    mock_close.assert_called_once_with()

    galvo.close = lambda: None
