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


def sawtooth(
    period: float = 10,
    amplitude: float = 1,
    offset: float = 0,
    duty_cycle: float = 100,
) -> tuple[int, int, float, float, int]:
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

    Returns
    -------
    tuple[int, int, float, float, int]
        The waveform parameters for the tiger controller.
    """

    # Converts period to ms and amplitude and offset to mV
    period = int(round(period * 1000))
    amplitude *= 1000
    offset *= 1000

    if duty_cycle < 25:
        # Negative amplitude reverses the polarity of the waveform
        amplitude = amplitude * -1
        # Sawtooth waveform that is triggered on TTL input
        return (4, 128, amplitude, offset, period)

    if duty_cycle > 75:
        # Sawtooth waveform that is triggered on TTL input
        return (4, 128, amplitude, offset, period)

    # Adjusts the period for a triangle waveform
    period = 2 * round(period / 2)
    # Triangle waveform that is triggered on TTL input
    return (4, 129, amplitude, offset, period)


def sine_wave(
    period: float = 10.0, amplitude: float = 1.0, offset: float = 0.0
) -> tuple[int, int, float, float, int]:
    """Sends the tiger controller commands to initiate the sine wave.

    Parameters
    ----------
    period : Float
        Unit - milliseconds
    amplitude : Float
        Unit - Volts
    offset : Float
        Unit - Volts

    Returns
    -------
    tuple[int, int, float, float, int]
        The waveform parameters for the tiger controller.
    """

    # Converts period to ms and amplitude and offset to mV
    period = int(round(period * 1000))
    amplitude *= 1000
    offset *= 1000

    # Sine wave that is triggered on TTL input
    return (4, 131, amplitude, offset, period)


def triangle(
    sweep_time: float = 0.24,
    amplitude: float = 1,
    offset: float = 0,
) -> tuple[int, int, float, float, int]:
    """Sends the tiger controller commands to initiate the triangle wave.

    The waveform starts at the offset and immediately rises linearly to 2x amplitude
    (amplitude here refers to 1/2 peak-to-peak) and immediately falls linearly back
    to the offset. The waveform is a periodic waveform with no delay periods between
    cycles.

    Parameters
    ----------
    sweep_time : Float
        Unit - Seconds
    amplitude : Float
        Unit - Volts
    offset : Float
        Unit - Volts

    Returns
    -------
    tuple[int, int, float, float, int]
        The waveform parameters for the tiger controller.
    """

    # Converts sweep_time to ms and amplitude and offset to mV
    period = int(round(sweep_time * 1000))
    amplitude *= 1000
    offset *= 1000

    # Triangle waveform
    return (4, 129, amplitude, offset, period)


def ramp(
    exposure_time: float = 0.2,
    flyback_time: float = 20,
    amplitude: float = 1,
    offset: float = 0.5,
) -> tuple[int, int, float, float, float, int]:
    """Sends the tiger controller commands to initiate the ramp wave.

    The waveform starts at offset and immediately rises linearly to 2x amplitude
    (amplitude here refers to 1/2 peak-to-peak) and then immediately drops back
    down to the offset voltage during the fall period.

    There is a delay period after each cycle that comes from the PLC, which is
    not included in this function.

    Parameters
    ----------
    exposure_time : Float
        Unit - Seconds
    flyback_time : Float
        Unit - milliseconds
    amplitude : Float
        Unit - Volts
    offset : Float
        Unit - Volts
    Returns
    -------
    tuple[int, int, float, float, float, int]
        The waveform parameters for the tiger controller.
    """

    # Converts exposure_time to ms and amplitude and offset to mV
    amplitude *= 1000
    offset *= 1000
    exposure_time = int(round(exposure_time * 1000))

    return (
        2,
        132,
        amplitude,
        offset,
        exposure_time + flyback_time,
        exposure_time,
    )
