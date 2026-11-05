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
