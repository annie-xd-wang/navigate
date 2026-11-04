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
#

#  Standard Library Imports
import logging
from typing import Any

# Local Imports
from navigate.model.devices.galvo.base import GalvoBase
from navigate.config.configuration_schema import SettingSpec
from navigate.model.devices.device_types import SerialDevice
from navigate.model.devices.APIs.asi.asi_tiger_controller import TigerController
from navigate.tools.decorators import log_initialization

# # Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


@log_initialization
class ASIGalvo(GalvoBase, SerialDevice):
    """GalvoASI Class - ASI DAQ Control of Galvanometers"""

    configuration_schema = {
        "hardware/axis": SettingSpec(
            str,
            default="B",
            label="Axis",
            help_text="ASI controller axis assigned to this galvo.",
            required=True,
        ),
    }

    def __init__(
        self,
        microscope_name: str,
        device_connection: Any,
        configuration: dict[str, Any],
        device_id: int = 0,
    ) -> None:
        """Initialize the GalvoASI class.

        Parameters
        ----------
        microscope_name : str
            Name of the microscope.
        device_connection : Any
            Connection to the NI DAQ device.
        configuration : dict[str, Any]
            Dictionary of configuration parameters.
        device_id : int
            Galvo ID. Default is 0.
        """
        super().__init__(microscope_name, device_connection, configuration, device_id)

        #: Any: Device connection.
        self.galvo = device_connection

        #: str: Galvo Axis
        self.axis = self.device_config["hardware"]["axis"]  # .get("axis","B")
        logger.debug(f"galvo axis: {self.axis}")

    def __str__(self) -> str:
        """Return string representation of the GalvoASI."""
        return "GalvoASI"

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
        self, exposure_times: dict[str, float], sweep_times: dict[str, float]
    ) -> dict[str, Any]:
        """Adjust the galvo waveform to account for the camera readout time.

        Parameters
        ----------
        exposure_times : dict
            Dictionary of camera exposure time in seconds on a per-channel basis.
            e.g., exposure_times = {"channel_1": 0.1, "channel_2": 0.2}
        sweep_times : dict
            Dictionary of acquisition sweep time in seconds on a per-channel basis.
            e.g., sweep_times = {"channel_1": 0.1, "channel_2": 0.2}

        Returns
        -------
        waveform_dict : dict
            Dictionary that includes the galvo waveforms on a per-channel basis.
        """

        waveform_dict = super().adjust(exposure_times, sweep_times)

        waveform_params = {}
        microscope_state = self.configuration["experiment"]["MicroscopeState"]
        microscope_name = microscope_state["microscope_name"]
        zoom_value = microscope_state["zoom"]
        galvo_factor = self.configuration["waveform_constants"]["other_constants"].get(
            "galvo_factor", "none"
        )
        galvo_parameters = self.configuration["waveform_constants"]["galvo_constants"][
            self.galvo_name
        ][microscope_name][zoom_value]

        for channel_key in microscope_state["channels"].keys():
            channel = microscope_state["channels"][channel_key]
            if channel["is_selected"] is True:
                exposure_time = exposure_times[channel_key]
                self.sweep_time = sweep_times[channel_key]

                # galvo Parameters
                try:
                    galvo_amplitude = float(galvo_parameters.get("amplitude", 0))
                    galvo_offset = float(galvo_parameters.get("offset", 0))
                    galvo_rising_ramp = float(galvo_parameters.get("rising_ramp", 50))
                    galvo_frequency = (
                        float(galvo_parameters.get("frequency", 0)) / exposure_time
                    )
                    factor_name = None
                    if galvo_factor == "channel":
                        factor_name = (
                            f"Channel {channel_key[channel_key.index('_') + 1 :]}"
                        )
                    elif galvo_factor == "laser":
                        factor_name = channel["laser"]
                    if factor_name and factor_name in galvo_parameters.keys():
                        galvo_amplitude = float(
                            galvo_parameters[factor_name].get("amplitude", 0)
                        )
                        galvo_offset = float(
                            galvo_parameters[factor_name].get("offset", 0)
                        )

                except ValueError as e:
                    logger.debug(
                        f"{e} waveform constants.yml doesn't have parameter "
                        f"amplitude/offset/frequency for {self.galvo_name}"
                    )
                    return

                waveform_params[channel_key] = {
                    "sweep_time": self.sweep_time,
                    "exposure_time": exposure_time,
                    "galvo_amplitude": galvo_amplitude,
                    "galvo_offset": galvo_offset,
                    "galvo_rising_ramp": galvo_rising_ramp,
                    "galvo_frequency": galvo_frequency,
                }

        self.daq.analog_outputs[self.axis] = {
            "waveform": waveform_params,
        }

        return waveform_dict

    def sawtooth(
        self,
        period: float = 10,
        amplitude: float = 1,
        offset: float = 0,
        duty_cycle: float = 100,
    ) -> None:
        """
        Sends the tiger controller commands to initiate the sawtooth wave.

        If the duty cycle given is 50, a triangle wave will be initiated.

        Parameters
        ----------
        period : Float
            Unit - milliseconds
        amplitude : Float
            Unit - Volts
        offset : Float
            Unit - Volts
        duty_cycle : Float
            Unit - Percent
        """

        # Converts period to ms and amplitude and offset to mV
        period = int(round(period * 1000))
        amplitude *= 1000
        offset *= 1000

        if duty_cycle == 0:
            # Negative amplitude reverses the polarity of the waveform
            amplitude = amplitude * -1
            # Sawtooth waveform that is triggered on TTL input
            self.galvo.single_axis_waveform(self.axis, 128, amplitude, offset, period)

        if duty_cycle == 50:
            # Adjusts the period for a triangle waveform
            period = 2 * round(period / 2)
            # Triangle waveform that is triggered on TTL input
            self.galvo.single_axis_waveform(self.axis, 129, amplitude, offset, period)

        if duty_cycle == 100:
            # Sawtooth waveform that is triggered on TTL input
            self.galvo.single_axis_waveform(self.axis, 128, amplitude, offset, period)

        # Waveform is free running after TTL input
        self.galvo.single_axis_mode(self.axis, 4)

    def sine_wave(
        self, period: float = 10.0, amplitude: float = 1.0, offset: float = 0.0
    ) -> None:
        """Sends the tiger controller commands to initiate the sine wave.

        Parameters
        ----------
        period : Float
            Unit - milliseconds
        amplitude : Float
            Unit - Volts
        offset : Float
            Unit - Volts

        """

        # Converts period to ms and amplitude and offset to mV
        period = int(round(period * 1000))
        amplitude *= 1000
        offset *= 1000

        # Sine wave that is triggered on TTL input
        self.galvo.single_axis_waveform(self.axis, 131, amplitude, offset, period)
        # Waveform is free running after it is triggered
        self.galvo.single_axis_mode(self.axis, 4)

    def turn_off(self) -> None:
        """Stops the galvo waveform"""
        self.galvo.single_axis_mode(self.axis, 0)

    def close(self) -> None:
        """Close the ASI galvo serial port.

        Stops the remote focus waveform and then closes the port.
        """
        if self.galvo.is_open():
            self.turn_off()
            logger.debug("ASI Remote Focus - Closing Device.")
            self.galvo.disconnect_from_serial()

    def __del__(self) -> None:
        """Destructor for the ASIGalvo class."""
        self.close()
