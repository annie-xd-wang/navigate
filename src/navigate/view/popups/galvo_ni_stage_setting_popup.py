# Copyright (c) 2021-2026  The University of Texas Southwestern Medical Center.
# All rights reserved.

"""Popup for configuring the calibration of NI-controlled galvo stages."""

import tkinter as tk
from tkinter import ttk

from navigate.view.custom_widgets.LabelInputWidgetFactory import LabelInput
from navigate.view.custom_widgets.popup import PopUp
from navigate.view.custom_widgets.validation import ValidatedCombobox
from navigate.view.theme import get_theme_space_px


class GalvoNIStageSettingPopup:
    """Create the Galvo (NI) Stage Setting popup window."""

    def __init__(self, root, *args, **kwargs):
        self.popup = PopUp(
            root,
            name="Galvo (NI) Stage Setting",
            size="430x230+320+180",
            top=False,
            transient=False,
        )
        self.popup.resizable(tk.FALSE, tk.FALSE)
        self.frame = self.popup.content_frame
        self.frame.grid_columnconfigure(0, weight=1)

        self.microscope = LabelInput(
            self.frame,
            label="Microscope",
            input_class=ValidatedCombobox,
            input_var=tk.StringVar(),
            label_args={"style": "Title.TLabel"},
            input_args={"state": "readonly"},
        )
        self.stage_axis = LabelInput(
            self.frame,
            label="Stage Axis",
            input_class=ValidatedCombobox,
            input_var=tk.StringVar(),
            input_args={"state": "readonly"},
        )
        self.volts_per_micron = LabelInput(
            self.frame,
            label="Volts Per Micron",
            input_class=ValidatedCombobox,
            input_var=tk.StringVar(),
            input_args={"state": "readonly"},
        )
        self.other_volts_per_micron = LabelInput(
            self.frame,
            label="Other",
            input_var=tk.StringVar(),
            input_args={"state": "disabled"},
        )
        self.save_button = ttk.Button(self.frame, text="Save")
        self.clear_button = ttk.Button(self.frame, text="Clear")

        for row, widget in enumerate(
            (
                self.microscope,
                self.stage_axis,
                self.volts_per_micron,
                self.other_volts_per_micron,
            )
        ):
            widget.grid(
                row=row,
                column=0,
                padx=get_theme_space_px(8),
                pady=get_theme_space_px(5),
                sticky="ew",
            )

        # Make each setting easy to read while allowing the dropdown to expand.
        for setting in (
            self.microscope,
            self.stage_axis,
            self.volts_per_micron,
            self.other_volts_per_micron,
        ):
            setting.widget.configure(width=28)

        self.save_button.grid(
            row=4,
            column=0,
            padx=get_theme_space_px(8),
            pady=get_theme_space_px(8),
            sticky="e",
        )
        self.clear_button.grid(
            row=4,
            column=0,
            padx=get_theme_space_px(8),
            pady=get_theme_space_px(8),
            sticky="w",
        )
