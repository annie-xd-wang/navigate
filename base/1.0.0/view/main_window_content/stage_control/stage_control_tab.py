# Standard Imports
from tkinter import *
from tkinter import ttk
from tkinter.font import Font

# Local Imports
from view.main_window_content.stage_control.tabs.other_axis_frame import other_axis_frame
from view.main_window_content.stage_control.tabs.position_frame import position_frame
from view.main_window_content.stage_control.tabs.x_y_frame import x_y_frame
from view.main_window_content.stage_control.tabs.goto_frame import goto_frame

class stage_control_tab(ttk.Frame):
    def __init__(stage_control_tab, note3, *args, **kwargs):

        #Init Frame
        ttk.Frame.__init__(stage_control_tab, note3, *args, **kwargs)

        #Building out stage control elements, frame by frame

        #Position Frame
        stage_control_tab.position_frame = position_frame(stage_control_tab)

        #XY Frame
        stage_control_tab.x_y_frame = x_y_frame(stage_control_tab)

        #Z Frame
        stage_control_tab.z_frame = other_axis_frame(stage_control_tab, 'Z')

        #Theta Frame
        stage_control_tab.theta_frame = other_axis_frame(stage_control_tab, 'Theta')

        #Focus Frame
        stage_control_tab.focus_frame = other_axis_frame(stage_control_tab, 'Focus')

        #GoTo Frame
        stage_control_tab.goto_frame = goto_frame(stage_control_tab)
        stage_control_tab.goto_frame_label = ttk.Label(stage_control_tab.goto_frame, text="Goto Frame")
        stage_control_tab.goto_frame_label.pack() #For visual mockup purposes


        '''
        Grid for frames
                1   2   3   4   5
                6   7   8   9   10 

        Position frame is 1-5
        xy is 6
        z is 7
        theta is 8
        focus is 9
        goto is 10
        '''

        #Gridding out frames
        stage_control_tab.position_frame.grid(row=0, column=0, columnspan=5, sticky=(NSEW))
        stage_control_tab.x_y_frame.grid(row=1, column=0, sticky=(NSEW))
        stage_control_tab.z_frame.grid(row=1, column=1, sticky=(NSEW))
        stage_control_tab.theta_frame.grid(row=1, column=2, sticky=(NSEW))
        stage_control_tab.focus_frame.grid(row=1, column=3, sticky=(NSEW))
        stage_control_tab.goto_frame.grid(row=1, column=4, sticky=(NSEW))
