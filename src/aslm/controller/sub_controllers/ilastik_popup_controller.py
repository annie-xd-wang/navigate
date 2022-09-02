"""
ASLM sub-controller ETL popup window.

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
from tkinter import filedialog, messagebox, Checkbutton, Label
import traceback

from aslm.controller.sub_controllers.gui_controller import GUI_Controller
from aslm.controller.aslm_controller_functions import combine_funcs
from aslm.model.model_features.aslm_restful_features import prepare_service

import logging

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class Ilastik_Popup_Controller(GUI_Controller):

    def __init__(self, view, parent_controller, service_url):
        super().__init__(view, parent_controller)

        self.service_url = service_url
        self.project_filename = None

        # add saving function to the function closing the window
        self.exit_func = combine_funcs(self.view.popup.dismiss,
                                  lambda: delattr(self.parent_controller, 'ilastik_controller'))
        self.view.popup.protocol("WM_DELETE_WINDOW", self.exit_func)
        buttons = self.view.get_buttons()
        buttons['load'].configure(command=self.load_project)
        buttons['confirm'].configure(command=self.confirm_setting)

        self.project_filename_var = self.view.get_variables()['project_name']
        self.label_frame = self.view.get_widgets()['label_frame']

    def load_project(self):
        filename = filedialog.askopenfilename(defaultextension='.ilp',
                                               filetypes=[('Ilastik Project File', '*.ilp')])
        try:
            r = prepare_service(self.service_url, project_file=filename)
            message='There is something wrong when loading the ilastik project file, please make sure the file exists and is correct!'
        except Exception as e:
            r = None
            message = 'Please make sure the aslm_server for ilastik is running!'
            logger.debug(e)
            logger.debug(traceback.format_exc())

        # destroy current labels
        for child in self.label_frame.winfo_children():
            child.destroy()

        if not r:
            self.project_filename_var.set("Please select an ilastik pixelclassification project file!")
            messagebox.showerror(title='Ilastik Error', 
                                 message=message)
        else:
            self.update_project(filename, r)

    def update_project(self, filename, label_dict):
        self.project_filename_var.set(filename)
        logger.info(f"{filename} is loaded successfully!")

        # redraw new labels
        for i, label_name in enumerate(label_dict['names']):
            label_widget = Checkbutton(self.label_frame, text=label_name)
            label_widget.grid(row=1+i, column=0, pady=(0, 10), padx=(20, 5), sticky="W")
            color_block = Label(self.label_frame, background=label_dict['label_colors'][i], width=3, height=1)
            color_block.grid(row=1+i, column=1, pady=(0, 10), padx=(0, 10))

    def confirm_setting(self):
        """confirm setting

        tell the model which labels will be used
        activate features containing ilastik
        """
        # add saving function to the function closing the window
        self.exit_func()

    def showup(self):
        """show the popup window

        this function will let the popup window show in front
        """
        self.view.popup.deiconify()
        self.view.popup.attributes("-topmost", 1)