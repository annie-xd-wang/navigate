# Copyright (c) 2021-2026  The University of Texas Southwestern Medical Center.
# All rights reserved.

"""Controller for the Galvo (NI) Stage Setting popup."""

from navigate.controller.configuration_controller import ConfigurationController
from navigate.tools.file_functions import write_to_yaml
from navigate.view.popups.galvo_ni_stage_setting_popup import GalvoNIStageSettingPopup


class GalvoNIStageSettingController:
    """Configure volts-per-micron formulas for NI-controlled stage axes."""

    PRESETS = {
        "25x: 0.0298*x": "0.0298*x",
        "40x: 0.043*x": "0.043*x",
        "60x: 0.0705*x": "0.0705*x",
    }
    OTHER = "Other"
    NI_STAGE_TYPES = {"NI", "NIStage", "GalvoNIStage"}

    def __init__(
        self, popup: GalvoNIStageSettingPopup, parent_controller, *args, **kwargs
    ):
        self.parent_controller = parent_controller
        self.view = popup
        self.local_config_controller = ConfigurationController(
            self.parent_controller.configuration
        )
        self.current_microscope = self.local_config_controller.microscope_name
        self.axis_hardware = {}

        self.view.microscope.set_values(self.local_config_controller.microscope_list)
        self.view.volts_per_micron.set_values([*self.PRESETS, self.OTHER])
        self.view.microscope.set(self.current_microscope)
        self.update_microscope()

        self.view.microscope.variable.trace_add("write", self.update_microscope)
        self.view.stage_axis.variable.trace_add("write", self.update_axis)
        self.view.volts_per_micron.variable.trace_add(
            "write", self.update_volts_per_micron_state
        )
        self.update_axis()
        self.view.save_button.configure(command=self.save_settings)
        self.view.clear_button.configure(command=self.clear_settings)
        self.view.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        self.view.popup.bind("<Escape>", lambda event: self.close_popup())

    def showup(self):
        """Bring the popup back to the front."""
        self.view.popup.showup()

    def _ni_stage_axes(self, microscope_name):
        """Return the NI stage axes and their hardware configuration entries."""
        stage = self.parent_controller.configuration["configuration"]["microscopes"][
            microscope_name
        ]["stage"]
        hardware = stage.get("hardware", [])
        if isinstance(hardware, dict):
            hardware = [hardware]

        axes = {}
        for device in hardware:
            if device.get("type") not in self.NI_STAGE_TYPES:
                continue
            for axis in device.get("axes", []):
                axes[axis] = device
        return axes

    def update_microscope(self, *args):
        """Show only stage axes belonging to an NI stage on the microscope."""
        self.current_microscope = self.view.microscope.get()
        self.axis_hardware = self._ni_stage_axes(self.current_microscope)
        axes = list(self.axis_hardware)
        self.view.stage_axis.set_values(axes)
        self.view.stage_axis.widget.configure(state="readonly" if axes else "disabled")
        if axes:
            self.view.stage_axis.set(axes[0])
        else:
            self.view.stage_axis.set("")
            self.view.volts_per_micron.set("")
            self.view.volts_per_micron.widget.configure(state="disabled")
            self.view.other_volts_per_micron.set("")
            self.view.other_volts_per_micron.widget.configure(state="disabled")

    def update_axis(self, *args):
        """Display the selected axis's configured calibration formula."""
        axis = self.view.stage_axis.get()
        device = self.axis_hardware.get(axis)
        if device is None:
            return

        self.view.volts_per_micron.widget.configure(state="readonly")
        stage_parameters = self.parent_controller.configuration["experiment"][
            "StageParameters"
        ]
        formula = str(
            stage_parameters.get(self.current_microscope, {}).get(
                f"{axis}_volts_per_micron", device.get("volts_per_micron") or ""
            )
        )
        preset = next(
            (label for label, value in self.PRESETS.items() if value == formula),
            self.OTHER,
        )
        self.view.volts_per_micron.set(preset)
        self.view.other_volts_per_micron.set("" if preset != self.OTHER else formula)
        self.update_volts_per_micron_state()

    def update_volts_per_micron_state(self, *args):
        """Enable a custom formula only when the Other preset is selected."""
        state = (
            "normal"
            if self.view.volts_per_micron.get() == self.OTHER
            else "disabled"
        )
        self.view.other_volts_per_micron.widget.configure(state=state)

    def save_settings(self):
        """Write the selected calibration formula to the experiment file."""
        axis = self.view.stage_axis.get()
        device = self.axis_hardware.get(axis)
        selection = self.view.volts_per_micron.get()
        if device is None or not selection:
            return

        formula = (
            self.view.other_volts_per_micron.get().strip()
            if selection == self.OTHER
            else self.PRESETS[selection]
        )
        if not formula:
            return
        self.parent_controller.configuration["experiment"]["StageParameters"][
            self.current_microscope
        ][f"{axis}_volts_per_micron"] = formula
        write_to_yaml(
            content_dict=self.parent_controller.configuration["experiment"],
            filename=self.parent_controller.experiment_path,
        )
        self.parent_controller.execute(
            "set_stage_volts_per_micron",
            self.current_microscope,
            axis,
            formula,
        )

    def clear_settings(self):
        """Remove every saved NI-stage calibration from the experiment file."""
        stage_parameters = self.parent_controller.configuration["experiment"][
            "StageParameters"
        ]
        for microscope_parameters in stage_parameters.values():
            if not hasattr(microscope_parameters, "keys"):
                continue
            for key in list(microscope_parameters.keys()):
                if key.endswith("_volts_per_micron"):
                    del microscope_parameters[key]
        write_to_yaml(
            content_dict=self.parent_controller.configuration["experiment"],
            filename=self.parent_controller.experiment_path,
        )
        self.update_axis()

    def close_popup(self):
        """Close the popup and remove its controller."""
        self.view.popup.destroy()
        if hasattr(self.parent_controller, "galvo_ni_stage_setting_controller"):
            del self.parent_controller.galvo_ni_stage_setting_controller
