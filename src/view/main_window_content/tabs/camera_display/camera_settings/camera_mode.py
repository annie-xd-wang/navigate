from cProfile import label
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from turtle import st

from view.custom_widgets.LabelInputWidgetFactory import LabelInput

class camera_mode(ttk.LabelFrame):
    '''
    # This class generates the camera mode label frame. 
    Widgets can be adjusted below. Dropdown values need to be set in the controller.
    The function widget.set_values(values) allows this. It can be found in the LabelInput class.
    The widgets can be found in the dictionary by using the first word in the label, after using get_widgets
    The variables tied to each widget can be accessed via the widget directly or with the dictionary generated by get_variables.
    '''
    def __init__(self, settings_tab, *args, **kwargs):

        #Init Frame
        text_label = 'Camera Modes'
        ttk.Labelframe.__init__(self, settings_tab, text=text_label, *args, **kwargs)

        #Holds dropdowns, this is done in case more widgets are to be added in a different frame, these can be grouped together
        content_frame = ttk.Frame(self)
        content_frame.grid(row=0, column=0, sticky=(NSEW))
        

        #Dictionary for all the variables, this will be used by the controller
        self.inputs = {}
        
        #Readout Direction Dropdown
        self.inputs['Readout'] = LabelInput(parent=content_frame,
                                            label='Readout Direction',
                                            input_class=ttk.Combobox,
                                            input_var=tk.StringVar()
                                            )
        self.inputs['Readout'].state(['readonly'])                                 
        self.inputs['Readout'].grid(row=0, column=0, pady=1)

        #Sensor Mode Dropdown
        self.inputs['Sensor'] = LabelInput(parent=content_frame,
                                           label='Sensor Mode',
                                           input_class=ttk.Combobox,
                                           input_var=tk.StringVar()
                                           )
        self.inputs['Sensor'].state(['readonly'])
        self.inputs['Sensor'].grid(row=1, column=0, pady=1)

        #Dual View Modes
        self.inputs['Dual'] = LabelInput(parent=content_frame,
                                         label='Dual View Modes',
                                         input_class=ttk.Combobox,
                                         input_var=tk.StringVar()
                                         )
        self.inputs['Dual'].state(['readonly'])                                 
        self.inputs['Dual'].grid(row=2, column=0, pady=1)

        #Split Pixel Number
        self.inputs['Split'] = LabelInput(parent=content_frame,
                                          label='Split Pixel Number',
                                          input_class=ttk.Combobox,
                                          input_var=tk.StringVar()
                                          )
        self.inputs['Split'].state(['readonly'])                                  
        self.inputs['Split'].grid(row=3, column=0, pady=1)


    def get_variables(self):
        '''
        # This function returns a dictionary of all the variables that are tied to each widget name.
        The key is the widget name, value is the variable associated.
        '''
        variables = {}
        for key, widget in self.inputs.items():
            variables[key] = widget.get()
        return variables
    
    def get_widgets(self):
        '''
        # This function returns the dictionary that holds the widgets.
        The key is the widget name, value is the LabelInput class that has all the data.
        '''
        return self.inputs



if __name__ == '__main__':
    root = tk.Tk()
    camera_mode(root).grid(row=0, column=0, sticky=(NSEW))
    root.mainloop()












# class camera_mode_label_frame(ttk.Labelframe):
#     def __init__(self, settings_tab, *args, **kwargs):

#         #Init Frame
#         text_label = 'Camera Modes'
#         ttk.Labelframe.__init__(self, settings_tab, text=text_label, *args, **kwargs)

#         #Mode Label Frame (Vertically oriented)
#         self.mode_label_frame = ttk.Frame(self)
#         self.mode_label_frame = ttk.Label(self.mode_label_frame, text='Readout Mode')
#         self.mode_label_frame.grid(row=0, column=0, sticky=(S))

#         #Mode Dropdown Menu
#         self.camera_mode = StringVar()
#         self.camera_mode_pull_down = ttk.Combobox(self)
#         self.camera_mode_pull_down['values'] = ['Normal Mode', 'Light-Sheet Mode']
#         self.camera_mode_pull_down.current(0)
#         self.camera_mode_pull_down.grid(row=1, column=0, sticky=(N))
#         #TODO: Have it save the parameters to session.

#         #Mode Readout Direction Label Frame (Vertically oriented)
#         self.mode_readout_label_frame = ttk.Frame(self)
#         self.mode_readout_label = ttk.Label(self.mode_readout_label_frame, text='Readout Direction')
#         self.mode_readout_label.grid(row=0, column=0, sticky=(S))

#         #Mode Readout Direction Dropdown Menu
#         self.readout_mode = StringVar()
#         self.readout_mode_pull_down = ttk.Combobox(self)
#         self.readout_mode_pull_down['values'] = ['Top to Bottom', 'Bottom to Top', 'Bidirectional']
#         self.readout_mode_pull_down.current(0)
#         self.readout_mode_pull_down.grid(row=1, column=0, sticky=(N))
#         #TODO: Have it save the parameters to session.



#         self.mode_label_frame.grid(row=0, column=0, sticky=(NSEW))
#         self.mode_readout_label_frame.grid(row=0, column=1, sticky=(NSEW))

'''
        
        self.start_pos_spinval = StringVar()
        # set default start value to 0 nm
        if self.start_pos_spinval.get() == '':
            self.start_pos_spinval.set('0')
        self.start_pos_spinbox = ttk.Spinbox(
            self.mode_readout_label_frame,
            from_=0,
            to=500.0,
            textvariable=self.start_pos_spinval, #this holds the data in the entry
            increment=0.5,
            width=14
            #TODO command= function from connector
        )
        self.start_pos_spinbox.grid(row=1, column=0, sticky=(N))

        #End Pos Frame (Vertically oriented)
        self.end_pos_frame = ttk.Frame(self)
        self.end_pos_label = ttk.Label(self.end_pos_frame, text='End Pos')
        self.end_pos_label.grid(row=0, column=0, sticky=(S))
        self.end_pos_spinval = StringVar()
        # Set default end position to 200 microns
        if self.end_pos_spinval.get() == '':
            self.end_pos_spinval.set('200')
        self.end_pos_spinbox = ttk.Spinbox(
            self.end_pos_frame,
            from_=0,
            to=500.0,
            textvariable=self.end_pos_spinval, #this holds the data in the entry
            increment=0.5,
            width=14
            #command=calculate_number_of_steps(self)
            #function from connector
        )
        self.end_pos_spinbox.state(['disabled']) #Starts it disabled
        self.end_pos_spinbox.grid(row=1, column=0, sticky=(N))

        # Calculate number of steps for slice frame
        #TODO: Make it update upon changing the values.
        def calculate_number_of_steps(self):
            #Calculate number of steps
            start_position = np.float(self.start_pos_spinval.get())
            end_position = np.float(self.end_pos_spinval.get())
            step_size = np.float(self.step_size_spinval.get())
            number_of_steps = np.floor((end_position - start_position)/step_size)
            print("number of steps", number_of_steps)
            return number_of_steps

        #Slice Frame (Vertically oriented)
        self.slice_frame = ttk.Frame(self)
        self.slice_label = ttk.Label(self.slice_frame, text='Slice')
        self.slice_label.grid(row=0, column=0, sticky=(S))
        self.slice_spinval = StringVar() #Attempts to get slice value with
        self.slice_spinval.set(calculate_number_of_steps(self)) #calculate_number_of_steps(self)
        self.slice_spinbox = ttk.Spinbox(
            self.slice_frame,
            from_=0,
            to=500.0,
            textvariable=self.slice_spinval, #this holds the data in the entry
            increment=0.5,
            width=14
            #TODO command= function from connector
        )
        self.slice_spinbox.state(['disabled']) #Starts it disabled
        self.slice_spinbox.grid(row=1, column=0, sticky=(N))

        #Gridding Each Holder Frame
        self.mode_label_frame.grid(row=0, column=0, sticky=(NSEW))
        self.mode_readout_label_frame.grid(row=0, column=1, sticky=(NSEW))
        self.end_pos_frame.grid(row=0, column=2, sticky=(NSEW))
        self.slice_frame.grid(row=0, column=3, sticky=(NSEW))
        '''