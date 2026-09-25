# Copyright (c) 2021-2026  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only
# (subject to the limitations in the disclaimer below)
# provided that the following conditions are met:

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

import math


def calculate_rotation(stage_center, current_position, rotation_angle):
    """Calculate the new position after rotation.

    Parameters
    ----------
    stage_center : tuple
        The center position of the stage.
    current_position : tuple
        The current position of the stage.
    rotation_angle : float
        The angle of rotation in degrees (-180 to 180). Negative values indicate clockwise rotation.

    Returns
    -------
    new_position : tuple
        The new position after rotation.
    """
    if rotation_angle == 0:
        return tuple(current_position)

    if rotation_angle < 0:
        rotation_angle = -rotation_angle
        x = (
            stage_center[0]
            + (current_position[0] - stage_center[0])
            * math.cos(math.radians(rotation_angle))
            + (current_position[1] - stage_center[1])
            * math.sin(math.radians(rotation_angle))
        )
        y = (
            stage_center[1]
            + (current_position[1] - stage_center[1])
            * math.cos(math.radians(rotation_angle))
            - (current_position[0] - stage_center[0])
            * math.sin(math.radians(rotation_angle))
        )
    else:
        x = (
            stage_center[0]
            + (current_position[0] - stage_center[0])
            * math.cos(math.radians(rotation_angle))
            - (current_position[1] - stage_center[1])
            * math.sin(math.radians(rotation_angle))
        )
        y = (
            stage_center[1]
            + (current_position[0] - stage_center[0])
            * math.sin(math.radians(rotation_angle))
            + (current_position[1] - stage_center[1])
            * math.cos(math.radians(rotation_angle))
        )

    return (round(x, 3), round(y, 3))
