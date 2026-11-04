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


#  Standard Library Imports
import logging
from typing import Any, Optional

# Third Party Imports

# Local Imports
from navigate.model.devices.remote_focus.base import RemoteFocusBase
from navigate.model.devices.device_types import SerialDevice
from navigate.config.configuration_schema import SettingSpec
from navigate.model.devices.APIs.asi.asi_tiger_controller import TigerController
from navigate.tools.decorators import log_initialization

# # Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


@log_initialization
class ASIRemoteFocus(RemoteFocusBase, SerialDevice):
    configuration_schema = {
        "hardware/axis": SettingSpec(
            str,
            default="B",
            label="Axis",
            help_text="ASI controller axis assigned to the remote-focus device.",
            required=True,
        )
    }
    """ASIRemoteFocus Class - Analog control of the remote focus device."""

    def __init__(
        self,
        microscope_name: str,
        device_connection: Any,
        configuration: dict[str, Any],
        *args,
        **kwargs,
    ) -> None:
        """Initialize the ASIRemoteFocus class.

        Parameters
        ----------
        microscope_name : str
            The microscope name.
        device_connection : Any
            The device connection object.
        configuration : Dict[str, Any]
            The configuration dictionary.

        """

        super().__init__(microscope_name, device_connection, configuration)

        #: Any: Device connection object.
        self.remote_focus = device_connection

        #: str: Output axis on Tiger Controller
        self.axis = self.device_config["hardware"]["axis"]

    @classmethod
    def connect(
        cls, port: str, baudrate: int = 115200, timeout: float = 0.25
    ) -> TigerController:
        """Build ASILaser Serial Port connection

        Parameters
        ----------
        port : str
            Port for communicating with the filter wheel, e.g., COM1.
        baudrate : int
            Baud rate for communicating with the filter wheel, default is 115200.
        timeout : float
            Timeout for communicating with the filter wheel, default is 0.25.

        Returns
        -------
        tiger_controller : TigerController
            ASI Tiger Controller object.
        """
        # wait until ASI device is ready
        tiger_controller = TigerController(port, baudrate)
        tiger_controller.connect_to_serial()
        if not tiger_controller.is_open():
            logger.error("ASI stage connection failed.")
            raise Exception("ASI stage connection failed.")
        return tiger_controller

    def adjust(
        self,
        exposure_times: dict[str, float],
        sweep_times: dict[str, float],
        offset: Optional[float] = None,
    ) -> dict[str, Any]:
        """Adjust the waveform.

        This method adjusts the waveform parameters.
        Based on the sensor mode and readout direction, either the triangle or ramp function will be called.

        Parameters
        ----------
        exposure_times : dict
            Dictionary of exposure times for each selected channel
        sweep_times : dict
            Dictionary of sweep times for each selected channel
        offset : float, optional
            Offset value for the remote focus waveform, by default None
        """

        waveform_dict = super().adjust(exposure_times, sweep_times, offset)

        waveform_params = {}
        # to determine if the waveform has to be triangular
        sensor_mode = self.configuration["experiment"]["CameraParameters"][
            self.microscope_name
        ]["sensor_mode"]
        readout_direction = self.configuration["experiment"]["CameraParameters"][
            self.microscope_name
        ]["readout_direction"]
        if sensor_mode == "Light-Sheet" and (
            readout_direction == "Bidirectional"
            or readout_direction == "Rev. Bidirectional"
        ):
            waveform_shape = "triangle"
        else:
            waveform_shape = "ramp"
        microscope_state = self.configuration["experiment"]["MicroscopeState"]
        waveform_constants = self.configuration["waveform_constants"]
        imaging_mode = microscope_state["microscope_name"]
        zoom = microscope_state["zoom"]
        remote_focus_ramp_falling = (
            float(waveform_constants["other_constants"]["remote_focus_ramp_falling"])
            / 1000
        )
        remote_focus_delay = (
            float(waveform_constants["other_constants"]["remote_focus_delay"]) / 1000
        )
        percent_smoothing = float(
            waveform_constants["other_constants"]["percent_smoothing"]
        )
        for channel_key in microscope_state["channels"].keys():
            # channel includes 'is_selected', 'laser', 'filter', 'camera_exposure'...
            channel = microscope_state["channels"][channel_key]

            # Only proceed if it is enabled in the GUI
            if channel["is_selected"] is True:

                # Get the Waveform Parameters - Assumes ETL Delay < Camera Delay.
                # Should Assert.
                laser = channel["laser"]
                exposure_time = exposure_times[channel_key]
                self.sweep_time = sweep_times[channel_key]

                # Remote Focus Parameters
                temp = waveform_constants["remote_focus_constants"][imaging_mode][zoom][
                    laser
                ]["amplitude"]
                if temp == "-" or temp == ".":
                    waveform_constants["remote_focus_constants"][imaging_mode][zoom][
                        laser
                    ]["amplitude"] = "0"

                remote_focus_amplitude = float(
                    waveform_constants["remote_focus_constants"][imaging_mode][zoom][
                        laser
                    ]["amplitude"]
                )

                # Validation for when user puts a '-' in spinbox
                temp = waveform_constants["remote_focus_constants"][imaging_mode][zoom][
                    laser
                ]["offset"]
                if temp == "-" or temp == ".":
                    waveform_constants["remote_focus_constants"][imaging_mode][zoom][
                        laser
                    ]["offset"] = "0"

                remote_focus_offset = float(
                    waveform_constants["remote_focus_constants"][imaging_mode][zoom][
                        laser
                    ]["offset"]
                )
                if offset is not None:
                    remote_focus_offset += offset

                waveform_params[channel_key] = {
                    "amplitude": remote_focus_amplitude,
                    "offset": remote_focus_offset,
                    "sweep_time": self.sweep_time,
                    "exposure_time": exposure_time,
                    "remote_focus_ramp_falling": remote_focus_ramp_falling,
                    "remote_focus_delay": remote_focus_delay,
                    "percent_smoothing": percent_smoothing,
                    "shape": waveform_shape,
                }

        self.daq.analog_outputs[self.axis] = {
            "trigger_source": self.axis,
            "waveform": waveform_params,
        }

        return waveform_dict

    def move(
        self,
        exposure_times: dict[str, float],
        sweep_times: dict[str, float],
        offset: Optional[float] = None,
    ) -> None:
        """Move the remote focus.

        This method moves the remote focus.

        Parameters
        ----------
        exposure_times : dict
            Dictionary of exposure times for each selected channel
        sweep_times : dict
            Dictionary of sweep times for each selected channel
        offset : float
            The offset of the signal in volts.
        """

        self.adjust(exposure_times, sweep_times, offset)
        # TODO: update axis setting

    def turn_off(self):
        """Stops the remote focus waveform"""
        self.remote_focus.single_axis_mode(self.axis, 0)

    def close(self):
        """Close the ASI remote_focus serial port.

        Stops the remote focus waveform and then closes the port.
        """
        if self.remote_focus.is_open():
            self.turn_off()
            logger.debug("ASI Remote Focus - Closing Device.")
            self.remote_focus.disconnect_from_serial()

    def __del__(self):
        """Destructor for the ASIRemoteFocus class."""
        self.close()
