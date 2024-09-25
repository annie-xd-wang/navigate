# Copyright (c) 2021-2024  The University of Texas Southwestern Medical Center.
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
#

# Standard Library Imports
import pytest
import random

# Third Party Imports
from pipython import GCSError

# Local Imports
from navigate.model.devices.stages.pi import PIStage


class MockPIStage:
    def __init__(self):
        self.axes = [1, 2, 3, 4, 5]

        for axis in self.axes:
            setattr(self, f"{axis}_abs", 0)

    def MOV(self, pos_dict):
        for axis in pos_dict:
            if axis not in self.axes:
                continue
            setattr(self, f"{axis}_abs", pos_dict[axis])

    def qPOS(self, axes):
        pos = {}
        for axis in axes:
            if axis not in self.axes:
                raise GCSError
            pos[str(axis)] = getattr(self, f"{axis}_abs")
        return pos

    def STP(self, noraise=True):
        pass

    def waitontarget(self, pi_device, timeout=5.0):
        pass


class TestStagePI:
    """Unit Test for PI Stage Class"""

    @pytest.fixture(autouse=True)
    def setup_class(
        self, stage_configuration, random_single_axis_test, random_multiple_axes_test
    ):
        self.microscope_name = "Mesoscale"
        self.configuration = {
            "configuration": {
                "microscopes": {self.microscope_name: stage_configuration}
            }
        }
        self.stage_configuration = stage_configuration
        self.stage_configuration["stage"]["hardware"]["type"] = "PI"
        self.random_single_axis_test = random_single_axis_test
        self.random_multiple_axes_test = random_multiple_axes_test

    def test_stage_attributes(self):
        stage = PIStage(self.microscope_name, None, self.configuration)

        # Methods
        assert hasattr(stage, "get_position_dict") and callable(
            getattr(stage, "get_position_dict")
        )
        assert hasattr(stage, "report_position") and callable(
            getattr(stage, "report_position")
        )
        assert hasattr(stage, "move_axis_absolute") and callable(
            getattr(stage, "move_axis_absolute")
        )
        assert hasattr(stage, "move_absolute") and callable(
            getattr(stage, "move_absolute")
        )
        assert hasattr(stage, "stop") and callable(getattr(stage, "stop"))
        assert hasattr(stage, "get_abs_position") and callable(
            getattr(stage, "get_abs_position")
        )

    @pytest.mark.parametrize(
        "axes, axes_mapping",
        [
            (["x"], None),
            (["y"], None),
            (["x", "z"], None),
            (["f", "z"], None),
            (["x", "y", "z"], None),
            (["x", "y", "z", "f"], None),
            (["x", "y", "z", "f", "theta"], None),
            (["x"], [1]),
            (["y"], [2]),
            (["x", "z"], [1, 3]),
            (["f", "z"], [2, 3]),
            (["x", "y", "z"], [1, 2, 3]),
            (["x", "y", "z", "f"], [1, 3, 2, 4]),
            (["x", "y", "z", "f", "theta"], [3, 5, 2, 1, 4]),
        ],
    )
    def test_initialize_stage(self, axes, axes_mapping):
        self.stage_configuration["stage"]["hardware"]["axes"] = axes
        self.stage_configuration["stage"]["hardware"]["axes_mapping"] = axes_mapping
        stage = PIStage(self.microscope_name, None, self.configuration)

        # Attributes
        for axis in axes:
            assert hasattr(stage, f"{axis}_pos")
            assert hasattr(stage, f"{axis}_min")
            assert hasattr(stage, f"{axis}_max")
            assert getattr(stage, f"{axis}_pos") == 0
            assert (
                getattr(stage, f"{axis}_min")
                == self.stage_configuration["stage"][f"{axis}_min"]
            )
            assert (
                getattr(stage, f"{axis}_max")
                == self.stage_configuration["stage"][f"{axis}_max"]
            )

        if axes_mapping is None:
            # using default mapping which is hard coded in pi.py
            default_mapping = {"x": 1, "y": 2, "z": 3, "f": 5, "theta": 4}
            for axis, device_axis in stage.axes_mapping.items():
                assert default_mapping[axis] == device_axis
            assert len(stage.axes_mapping) <= len(stage.axes)
        else:
            for i, axis in enumerate(axes):
                assert stage.axes_mapping[axis] == axes_mapping[i]

        assert stage.stage_limits is True

    @pytest.mark.parametrize(
        "axes, axes_mapping",
        [
            (["x"], None),
            (["y"], None),
            (["x", "z"], None),
            (["f", "z"], None),
            (["x", "y", "z"], None),
            (["x", "y", "z", "f"], None),
            (["x", "y", "z", "f", "theta"], None),
            (["x"], [1]),
            (["y"], [2]),
            (["x", "z"], [1, 3]),
            (["f", "z"], [2, 3]),
            (["x", "y", "z"], [1, 2, 3]),
            (["x", "y", "z", "f"], [1, 3, 2, 4]),
            (["x", "y", "z", "f", "theta"], [3, 5, 2, 1, 4]),
        ],
    )
    def test_report_position(self, axes, axes_mapping):
        PI_device = MockPIStage()
        device_connection = {"pi_tools": PI_device, "pi_device": PI_device}
        self.stage_configuration["stage"]["hardware"]["axes"] = axes
        self.stage_configuration["stage"]["hardware"]["axes_mapping"] = axes_mapping
        stage = PIStage(self.microscope_name, device_connection, self.configuration)

        for _ in range(10):
            pos_dict = {}
            for axis in axes:
                pos = random.randrange(-100, 500)
                pos_dict[f"{axis}_pos"] = float(pos)
                if axis != "theta":
                    setattr(PI_device, f"{stage.axes_mapping[axis]}_abs", pos / 1000)
                else:
                    setattr(PI_device, f"{stage.axes_mapping[axis]}_abs", float(pos))
            temp_pos = stage.report_position()
            assert pos_dict == temp_pos

    @pytest.mark.parametrize(
        "axes, axes_mapping",
        [
            (["x"], None),
            (["y"], None),
            (["x", "z"], None),
            (["f", "z"], None),
            (["x", "y", "z"], None),
            (["x", "y", "z", "f"], None),
            (["x", "y", "z", "f", "theta"], None),
            (["x"], [1]),
            (["y"], [2]),
            (["x", "z"], [1, 3]),
            (["f", "z"], [2, 3]),
            (["x", "y", "z"], [1, 2, 3]),
            (["x", "y", "z", "f"], [1, 3, 2, 4]),
            (["x", "y", "z", "f", "theta"], [3, 5, 2, 1, 4]),
        ],
    )
    def test_move_axis_absolute(self, axes, axes_mapping):
        PI_device = MockPIStage()
        device_connection = {"pi_tools": PI_device, "pi_device": PI_device}
        self.stage_configuration["stage"]["hardware"]["axes"] = axes
        self.stage_configuration["stage"]["hardware"]["axes_mapping"] = axes_mapping
        stage = PIStage(self.microscope_name, device_connection, self.configuration)
        self.random_single_axis_test(stage)
        stage.stage_limits = False
        self.random_single_axis_test(stage)

    @pytest.mark.parametrize(
        "axes, axes_mapping",
        [
            (["x"], None),
            (["y"], None),
            (["x", "z"], None),
            (["f", "z"], None),
            (["x", "y", "z"], None),
            (["x", "y", "z", "f"], None),
            (["x", "y", "z", "f", "theta"], None),
            (["x"], [1]),
            (["y"], [2]),
            (["x", "z"], [1, 3]),
            (["f", "z"], [2, 3]),
            (["x", "y", "z"], [1, 2, 3]),
            (["x", "y", "z", "f"], [1, 3, 2, 4]),
            (["x", "y", "z", "f", "theta"], [3, 5, 2, 1, 4]),
        ],
    )
    def test_move_absolute(self, axes, axes_mapping):
        PI_device = MockPIStage()
        device_connection = {"pi_tools": PI_device, "pi_device": PI_device}
        self.stage_configuration["stage"]["hardware"]["axes"] = axes
        self.stage_configuration["stage"]["hardware"]["axes_mapping"] = axes_mapping
        stage = PIStage(self.microscope_name, device_connection, self.configuration)
        self.random_multiple_axes_test(stage)
        stage.stage_limits = False
        self.random_multiple_axes_test(stage)
