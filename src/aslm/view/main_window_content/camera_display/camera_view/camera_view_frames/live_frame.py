# Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only (subject to the limitations in the disclaimer below)
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

# Standard Library Imports
import logging
import tkinter as tk
from tkinter import *
from tkinter import ttk

# Third Party Imports

# Local Imports
from aslm.view.custom_widgets.LabelInputWidgetFactory import LabelInput

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class live_frame(ttk.Labelframe):
    def __init__(self, cam_view, *args, **kwargs):

        # Init Frame
        text_label = "Image Display"
        ttk.Labelframe.__init__(self, cam_view, text=text_label, *args, **kwargs)

        # Formatting
        Grid.columnconfigure(self, "all", weight=1)
        Grid.rowconfigure(self, "all", weight=1)

        self.live_var = StringVar()
        self.live = ttk.Combobox(
            self, textvariable=self.live_var, state="readonly", width=6
        )
        self.live["values"] = (
            "Live",
            "XY Slice",
            "YZ Slice",
            "ZY Slice",
            "XY MIP",
            "YZ MIP",
            "ZY MIP",
        )
        self.live.set("Live")
        self.live.grid(row=0, column=0)
        self.live.state = "readonly"

    def get_variables(self):
        """
        # This function returns a dictionary of all the variables that are tied to each widget name.
        The key is the widget name, value is the variable associated.
        """
        variables = {}
        for key, widget in self.inputs.items():
            variables[key] = widget.get()
        return variables

    def get_widgets(self):
        """
        # This function returns the dictionary that holds the widgets.
        The key is the widget name, value is the LabelInput class that has all the data.
        """
        return self.inputs
