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

# Standard Library Imports

# Third Party Imports
import pytest

# Local Imports


@pytest.mark.hardware
def test_initialize_daq_ni():
    from navigate.model.devices.daq.ni import NIDAQ
    from test.model.dummy import DummyModel

    model = DummyModel()
    daq = NIDAQ(model.configuration)
    daq.camera_trigger_task = None


@pytest.mark.hardware
def test_daq_ni_functions():
    from navigate.model.devices.daq.ni import NIDAQ
    from test.model.dummy import DummyModel

    model = DummyModel()
    daq = NIDAQ(model.configuration)
    microscope_name = model.configuration["experiment"]["MicroscopeState"][
        "microscope_name"
    ]

    funcs = [
        "enable_microscope",
        "prepare_acquisition",
        "run_acquisition",
        "stop_acquisition",
    ]
    args = [
        [microscope_name],
        [list(daq.waveform_dict.keys())[0]],
        None,
        None,
    ]

    for f, a in zip(funcs, args):
        if a is not None:
            getattr(daq, f)(*a)
        else:
            getattr(daq, f)()
