"""
ASLM data acquisition card communication classes.

Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted for academic and research use only (subject to the limitations in the disclaimer below)
provided that the following conditions are met:

     * Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

     * Neither the name of the copyright holders nor the names of its
     contributors may be used to endorse or promote products derived from this
     software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

# Standard Imports
import logging

# Third Party Imports

# Local Imports
from aslm.model.aslm_model_waveforms import tunable_lens_ramp, sawtooth, camera_exposure

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class DAQBase:
    def __init__(self, model, experiment, etl_constants, verbose=False):
        self.model = model
        self.experiment = experiment
        self.etl_constants = etl_constants
        self.verbose = verbose

        # Initialize Variables
        self.sample_rate = self.model.DAQParameters['sample_rate']
        self.sweep_time = self.model.DAQParameters['sweep_time']
        self.samples = int(self.sample_rate * self.sweep_time)

        # New DAQ Attempt
        self.etl_delay = self.model.RemoteFocusParameters['remote_focus_l_delay_percent']
        self.etl_ramp_rising = self.model.RemoteFocusParameters['remote_focus_l_ramp_rising_percent']
        self.etl_ramp_falling = self.model.RemoteFocusParameters['remote_focus_l_ramp_falling_percent']

        # ETL Parameters
        self.etl_l_waveform = None
        self.etl_l_delay = self.model.RemoteFocusParameters['remote_focus_l_delay_percent']
        self.etl_l_ramp_rising = self.model.RemoteFocusParameters['remote_focus_l_ramp_rising_percent']
        self.etl_l_ramp_falling = self.model.RemoteFocusParameters['remote_focus_l_ramp_falling_percent']
        self.etl_l_amplitude = self.model.RemoteFocusParameters['remote_focus_l_amplitude']
        self.etl_l_offset = self.model.RemoteFocusParameters['remote_focus_l_offset']
        self.etl_l_min_ao = self.model.RemoteFocusParameters['remote_focus_l_min_ao']
        self.etl_l_max_ao = self.model.RemoteFocusParameters['remote_focus_l_max_ao']

        # Remote Focus Parameters
        self.etl_r_waveform = None
        self.etl_r_delay = self.model.RemoteFocusParameters['remote_focus_r_delay_percent']
        self.etl_r_ramp_rising = self.model.RemoteFocusParameters['remote_focus_r_ramp_rising_percent']
        self.etl_r_ramp_falling = self.model.RemoteFocusParameters['remote_focus_r_ramp_falling_percent']
        self.etl_r_amplitude = self.model.RemoteFocusParameters['remote_focus_r_amplitude']
        self.etl_r_offset = self.model.RemoteFocusParameters['remote_focus_r_offset']
        self.etl_r_min_ao = self.model.RemoteFocusParameters['remote_focus_r_min_ao']
        self.etl_r_max_ao = self.model.RemoteFocusParameters['remote_focus_r_max_ao']

        # ETL history parameters
        self.prev_etl_r_amplitude = self.etl_r_amplitude
        self.prev_etl_r_offset = self.etl_r_offset
        self.prev_etl_l_amplitude = self.etl_l_amplitude
        self.prev_etl_l_offset = self.etl_l_offset

        # Bundled Waveform
        self.galvo_and_etl_waveforms = None

        # Left Galvo Parameters
        self.galvo_l_waveform = None
        self.galvo_l_frequency = self.model.GalvoParameters['galvo_l_frequency']
        self.galvo_l_amplitude = self.model.GalvoParameters['galvo_l_amplitude']
        self.galvo_l_offset = self.model.GalvoParameters['galvo_l_offset']
        self.galvo_l_duty_cycle = self.model.GalvoParameters['galvo_l_duty_cycle']
        self.galvo_l_phase = self.model.GalvoParameters['galvo_l_phase']
        self.galvo_l_min_ao = self.model.GalvoParameters['galvo_l_min_ao']
        self.galvo_l_max_ao = self.model.GalvoParameters['galvo_l_max_ao']

        # Right Galvo Parameters
        self.galvo_r_waveform = None
        self.galvo_r_frequency = None
        self.galvo_r_amplitude = self.model.GalvoParameters['galvo_r_amplitude']
        self.galvo_r_offset = None
        self.galvo_r_duty_cycle = None
        self.galvo_r_phase = None
        self.galvo_r_max_ao = self.model.GalvoParameters['galvo_r_max_ao']
        self.galvo_r_min_ao = self.model.GalvoParameters['galvo_r_min_ao']

        # Camera Parameters
        self.camera_delay_percent = self.model.CameraParameters['delay_percent']
        self.camera_pulse_percent = self.model.CameraParameters['pulse_percent']
        self.camera_high_time = self.camera_pulse_percent * 0.01 * self.sweep_time
        self.camera_delay = self.camera_delay_percent * 0.01 * self.sweep_time

        # Laser Parameters
        self.laser_ao_waveforms = None
        self.laser_do_waveforms = None
        self.number_of_lasers = self.model.LaserParameters['number_of_lasers']
        self.laser_l_delay = self.model.LaserParameters['laser_l_delay_percent']
        self.laser_l_pulse = self.model.LaserParameters['laser_l_pulse_percent']

        self.laser_power = 0
        self.laser_idx = 0
        self.imaging_mode = None

        self.waveform_dict = {
            'channel_1':
                {'etl_waveform': None,
                 'galvo_waveform': None,
                 'camera_waveform': None},
            'channel_2':
                {'etl_waveform': None,
                 'galvo_waveform': None,
                 'camera_waveform': None},
            'channel_3':
                {'etl_waveform': None,
                 'galvo_waveform': None,
                 'camera_waveform': None},
            'channel_4':
                {'etl_waveform': None,
                 'galvo_waveform': None,
                 'camera_waveform': None},
            'channel_5':
                {'etl_waveform': None,
                 'galvo_waveform': None,
                 'camera_waveform': None}
        }

    def calculate_all_waveforms(self, microscope_state, etl_constants, galvo_parameters, readout_time):
        r"""
        Pre-calculates all waveforms necessary for the acquisition and organizes in a dictionary format.

        Parameters
        ----------
        microscope_state : dict
            Dictionary of experiment MicroscopeState parameters (see config/experiment.yml)
        etl_constants : dict
            Dictionary of ETL parameters (see config/etl_constants.yml)
        galvo_parameters : dict
            Dictionary of experiment GalvoParameters parameters (see config/experiment.yml)
        readout_time : float
            Readout time of the camera (seconds) if we are operating the camera in Normal mode, otherwise -1.

        Returns
        -------
        self.waveform_dict : dict
            Dictionary of waveforms to pass to galvo and ETL, plus a camera waveform for display purposes.
        """

        # Imaging Mode = 'high' or 'low'
        self.imaging_mode = microscope_state['resolution_mode']

        focus_prefix = 'r' if self.imaging_mode == 'high' else 'l'

        # Zoom = 'N/A' in high resolution mode, or '0.63x', '1x', '2x'... in low-resolution mode.
        zoom = microscope_state['zoom']

        # Iterate through the dictionary.
        for channel_key in microscope_state['channels']:
            # channel includes 'is_selected', 'laser', 'filter', 'camera_exposure'...
            channel = microscope_state['channels'][channel_key]

            # Only proceed if it is enabled in the GUI
            if channel['is_selected'] is True:

                # Get the Waveform Parameters - Assumes ETL Delay < Camera Delay.  Should Assert.
                laser = channel['laser']
                exposure_time = channel['camera_exposure_time'] / 1000
                self.sweep_time = exposure_time + exposure_time * ((self.camera_delay_percent + self.etl_ramp_falling) / 100)
                if readout_time > 0:
                    # This addresses the dovetail nature of the camera readout in normal mode. The camera reads middle
                    # out, and the delay in start of the last lines compared to the first lines causes the exposure
                    # to be net longer than exposure_time. This helps the galvo keep sweeping for the full camera
                    # exposure time.
                    self.sweep_time += readout_time

                # ETL Parameters
                etl_amplitude = float(etl_constants.ETLConstants[self.imaging_mode][zoom][laser]['amplitude'])
                etl_offset = float(etl_constants.ETLConstants[self.imaging_mode][zoom][laser]['offset'])

                # Galvo Parameters
                galvo_amplitude = float(galvo_parameters[f'galvo_{focus_prefix}_amplitude'])
                galvo_offset = float(galvo_parameters[f'galvo_{focus_prefix}_offset'])

                # We need the camera to experience N sweeps of the galvo. As such,
                # frequency should divide evenly into exposure_time
                galvo_frequency = float(galvo_parameters[f'galvo_{focus_prefix}_frequency'])/exposure_time  # 100.5/exposure_time

                # Calculate the Waveforms
                self.waveform_dict[channel_key]['etl_waveform'] = tunable_lens_ramp(sample_rate=self.sample_rate,
                                                                                       exposure_time=exposure_time,
                                                                                       sweep_time=self.sweep_time,
                                                                                       etl_delay=self.etl_delay,
                                                                                       camera_delay=self.camera_delay_percent,
                                                                                       fall=self.etl_ramp_falling,
                                                                                       amplitude=etl_amplitude,
                                                                                       offset=etl_offset)

                self.waveform_dict[channel_key]['galvo_waveform'] = sawtooth(sample_rate=self.sample_rate,
                                                                             sweep_time=self.sweep_time,
                                                                             frequency=galvo_frequency,
                                                                             amplitude=galvo_amplitude,
                                                                             offset=galvo_offset,
                                                                             phase=(self.camera_delay_percent/100)*exposure_time)

                self.waveform_dict[channel_key]['camera_waveform'] = camera_exposure(sample_rate=self.sample_rate,
                                                                                     sweep_time=self.sweep_time,
                                                                                     exposure=exposure_time,
                                                                                     camera_delay=self.camera_delay_percent)

                # Confirm that the values are between the minimum and maximum voltages.
                max_etl_voltage = getattr(self, f"etl_{focus_prefix}_max_ao")
                min_etl_voltage = getattr(self, f"etl_{focus_prefix}_min_ao")
                max_galvo_voltage = getattr(self, f"galvo_{focus_prefix}_max_ao")
                min_galvo_voltage = getattr(self, f"galvo_{focus_prefix}_min_ao")

                # Clip waveforms with min and max.
                self.waveform_dict[channel_key]['etl_waveform'][self.waveform_dict[channel_key]['etl_waveform'] >
                                                                max_etl_voltage] = max_etl_voltage
                self.waveform_dict[channel_key]['etl_waveform'][self.waveform_dict[channel_key]['etl_waveform'] <
                                                                min_etl_voltage] = min_etl_voltage
                self.waveform_dict[channel_key]['galvo_waveform'][self.waveform_dict[channel_key]['galvo_waveform'] >
                                                                max_galvo_voltage] = max_galvo_voltage
                self.waveform_dict[channel_key]['galvo_waveform'][self.waveform_dict[channel_key]['galvo_waveform'] <
                                                                min_galvo_voltage] = min_galvo_voltage

        return self.waveform_dict

    def calculate_samples(self):
        """
        # Calculate the number of samples for the waveforms.
        # Product of the sampling frequency and the duration of the waveform/exposure time.
        # sweep_time units originally seconds.
        """
        self.samples = int(self.sample_rate * self.sweep_time)

    def update_etl_parameters(self, microscope_state, channel, galvo_parameters, readout_time):
        """
        # Update the ETL parameters according to the zoom and excitation wavelength.
        """
        laser = channel['laser']
        resolution_mode = microscope_state['resolution_mode']

        if resolution_mode == 'high':
            # zoom = 'one'
            zoom = microscope_state['zoom']
            self.etl_r_amplitude = float(self.etl_constants.ETLConstants[resolution_mode][zoom][laser]['amplitude'])
            self.etl_r_offset = float(self.etl_constants.ETLConstants[resolution_mode][zoom][laser]['offset'])
            if self.verbose:
                print("High Resolution Mode.  Amp/Off:", self.etl_r_amplitude, self.etl_r_offset)
                logger.debug(f"High Resolution Mode.  Amp/Off:, {self.etl_r_amplitude}, {self.etl_r_offset})")

        elif resolution_mode == 'low':
            zoom = microscope_state['zoom']
            self.etl_l_amplitude = float(self.etl_constants.ETLConstants[resolution_mode][zoom][laser]['amplitude'])
            self.etl_l_offset = float(self.etl_constants.ETLConstants[resolution_mode][zoom][laser]['offset'])
            if self.verbose:
                print("Low Resolution Mode.  Amp/Off:", self.etl_l_amplitude, self.etl_l_offset)
            logger.debug(f"Low Resolution Mode.  Amp/Off:, {self.etl_l_amplitude}, {self.etl_l_offset})")

        else:
            print("ETL setting not pulled properly.")
            logger.info("ETL setting not pulled properly")

        update_waveforms = (self.prev_etl_l_amplitude != self.etl_l_amplitude) \
                           or (self.prev_etl_l_offset != self.etl_l_offset) \
                           or (self.prev_etl_r_amplitude != self.etl_r_amplitude) \
                           or (self.prev_etl_r_offset != self.etl_r_offset)

        if update_waveforms:
            self.calculate_all_waveforms(microscope_state, self.etl_constants, galvo_parameters, readout_time)
            self.calculate_samples()
            self.prev_etl_r_amplitude = self.etl_r_amplitude
            self.prev_etl_r_offset = self.etl_r_offset
            self.prev_etl_l_amplitude = self.etl_l_amplitude
            self.prev_etl_l_offset = self.etl_l_offset
