import os
import numpy as np
import ast
import json
from abc import ABC, abstractmethod

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont

from library_misc import * # Custom library imports
import CONSTANTS as c # Import constants from a separate file


# Custom exception for handling cases where a GUI input entry is not found
class EntryNotFound(Exception):
    pass



# GUI Class which handles the graphical user interface functionality
class GUI:
    inputs = {} # Dictionary to store input values from the user

    def __init__(self, root, size, title):
        # Initializes the GUI with the root window, size, and title
        self.root = root
        self.size = size
        self.title = title
        self.set_style() # Set style for widgets


    def set_style(self):
        # Sets style for different widgets used in the GUI
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 12), padding=5, highlightthickness=0)
        style.configure('TButton', font=('Helvetica', 12), padding=5)
        style.configure('TCombobox', font=('Helvetica', 12), padding=5)
        style.map('TCombobox', fieldbackground=[('readonly', 'lightgrey')], selectbackground=[('readonly', 'lightgrey')], selectforeground=[('readonly', 'black')])
        style.map('TEntry', fieldbackground=[('!disabled', 'white'), ('disabled', 'grey')])
        self.root.configure(bg='light grey') # Set background color


    def run_gui(self, entries, buttons):
        # This function runs the GUI and sets up entries and buttons
        self.root.title(self.title)
        self.root.geometry(self.size)
        self.entries = entries
        self.buttons = buttons

        row = 0
        for entry in self.entries:
            entry.setup(row) # Setup entry widgets
            entry.row = row
            row += entry.rows_occupied

        for button in self.buttons:
            button.setup(row) # Setup buttons
            row += entry.rows_occupied
        
        self.root.mainloop() # Starts the Tkinter main loop
        self.root.quit() # Exits the Tkinter main loop


    def find_entry(self, param_name):
        # Searches for an entry by its parameter name
        for entry in self.entries:
            if entry.param_name == param_name:
                return entry
        raise EntryNotFound(f"Parameter {param_name} is not associated with an GUI_Input object")
        

    def clear_all(self):
        # Clears all input fields
        for entry in self.entries:
            entry.clear()
    

    def get_value(self, param):
        # Retrieves the value for a specific parameter
        return self.find_entry(param).get()


    def submit_values(self):
        # Collects and validates the user inputs before submission
        self.inputs = {}
        for entry in self.entries:

            valid, custom_error = entry.is_valid()
            if not(valid):
                message = custom_error if custom_error else f'Input for "{entry.param_desc}" is not valid!'
                tk.messagebox.showerror(title=None, message=message) # Display error message
                return
            
            self.inputs[entry.param_name] = entry.get()
        self.root.destroy() # Close the window after successful submission


    def load(self, filename):
        # Loads settings from a JSON file into the GUI
        with open(filename, "r") as f:
            json_obj = json.load(f)
        for entry in self.entries:
            entry.write(json_obj.get(entry.param_name, "")) # Populate each entry with the value from the file


# Abstract base class for all types of GUI inputs
class GUI_input(ABC):
    rows_occupied = 1
    TEXT = 1
    COMBOBOX = 2

    def __init__(self, gui, param_name, param_desc, mandatory = True, hidden = False):
        self.gui = gui
        self.param_name = param_name
        self.param_desc = param_desc
        self.mandatory = mandatory # Whether the input is mandatory or optional
        self.hidden = hidden # Whether the input is hidden

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def is_valid(self):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def get(self):
        pass



# ====================== TEXT INPUT CLASSES ======================


class GUI_input_text(GUI_input):
    entry_type = GUI_input.TEXT

    def setup(self, row):
        # Creates a label and text entry field in the GUI
        ttk.Label(self.gui.root, text=self.param_desc, background='light grey').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.entry_var = ttk.Entry(self.gui.root, width=50)
        self.entry_var.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    
    def is_valid(self):
        # Validates the input field (checks if it's empty or if it meets conditions)
        custom_error_message = None
        if self.entry_var.get() != "" or self.mandatory == False:
            return True, custom_error_message
        else:
            return False, custom_error_message

    def clear(self):
        # Clears the text input field
        self.entry_var.delete(0, tk.END)

    def write(self, content):
        # Writes the provided content to the text input field
        self.clear()
        self.entry_var.insert(0, content)

    def print_value(self):
        # Prints the value from the text entry field
        print(self.entry_var.get().strip())

    def get(self):
        # Returns the value from the text input field (stripped of leading/trailing spaces)
        return self.entry_var.get().strip()


# Class for handling specific text input for measurement name
class GUI_input_text_measurement_name(GUI_input_text):
    def is_valid(self):
        # Checks if the measurement name is valid (checks if a folder exists)
        custom_error_message = None
        if self.entry_var.get() == "" and self.mandatory == True:
            return False, custom_error_message
        
        path = os.path.join(c.DATA_FOLDER_NAME, self.gui.get_value("user_name"), self.gui.get_value("sample_name"), self.get())
        print(path)
        if not(os.path.exists(path)):
            return True, None
        else: 
            return False, "This sample has already a measurement with this name!"


# Class for handling field sweep input in the form of a range or list
class GUI_input_text_field_sweep(GUI_input_text):

    def is_valid(self):
        custom_error_message = None
        if self.entry_var.get() != "" or self.mandatory == False:
            return True, custom_error_message
        else:
            return False, custom_error_message

    def get(self):
        # Processes the field sweep input and returns it as a list of numbers
        field_sweep_str = self.entry_var.get()
        try:
            # Check if the input string uses range notation (e.g., "1:1:5")
            if ':' in field_sweep_str:
                # Split the string by ':' to get start, step, stop values
                start, step, stop = map(float, field_sweep_str.split(':'))
                # Use range to generate the list of numbers
                field_sweep_list = list(np.arange(start, stop + 0.00001, step))  # +0.00001 fa includere il numero finale, TODO trovare un modo migliore per includerlo
            else:
                # Handle input as a list of comma-separated values
                # For comma-separated values, convert string to list of integers
                # Handle both with and without brackets
                if not field_sweep_str.startswith('['):
                    field_sweep_str = f'[{field_sweep_str}]'
                field_sweep_list = ast.literal_eval(field_sweep_str)
                # Ensure the result is a list of floats
                field_sweep_list = list(np.array(field_sweep_list).astype(float))
            
            # Round values to avoid floating-point inaccuracies
            for i in range(len(field_sweep_list)):
                field_sweep_list[i] = ( np.round(field_sweep_list[i] *10**10)/10**10 )
            
            return field_sweep_list
        except (ValueError, SyntaxError) as e:
            return None
        
    def write(self, content):
        # Writes the content to the input field (as a list)
        self.clear()
        self.entry_var.insert(0, str(list((content)[1:])))
    

# Class for converting text input to frequency in Hz (from GHz received as input)
class GUI_input_text_to_freq(GUI_input_text):

    def write(self, content):
        # Converts and writes the frequency in GHz as input (the settings are in Hz, when you load the last settings you need to convert them to GHz to write them in the GUI)
        self.clear()
        self.entry_var.insert(0, content/10**9)

    def is_valid(self):
        # Tries to convert the input to a float
        try:
            float(self.entry_var.get())
            return True, None
        except:
            return False, None

    def get(self):
            # Retrieves and converts the frequency back to Hz
            return float(self.entry_var.get())*10**9
        

    

class GUI_input_text_to_number(GUI_input_text):
    def __init__(self, func=lambda string : float(string), *args, **kwargs):
        self.func = func
        super().__init__(*args, **kwargs)

    def get(self):
        return self.func(self.entry_var.get())


# ====================== COMBOBOX INPUT CLASSES======================

# Abstract class for combobox inputs
class GUI_input_combobox(GUI_input):
    entry_type = GUI_input.COMBOBOX

    def __init__(self, values, **kwargs):
        self.values = values
        super().__init__(**kwargs)

    def setup(self, row):
        # Creates a label and combobox input field in the GUI
        ttk.Label(self.gui.root, text=self.param_desc, background='light grey').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.entry_var = ttk.Combobox(self.gui.root, state="readonly", values=self.values, width=50)
        self.entry_var.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        self.entry_var.bind('<<ComboboxSelected>>', self.on_change)

    def is_valid(self):
        # Checks if a valid selection is made
        custom_error_message = None
        if self.entry_var.get() != "":
            return True, custom_error_message
        else:
            return False, custom_error_message

    def clear(self):
        # Clears the combobox input
        self.entry_var.set("")

    def write(self, content):
        # Sets a specific value in the combobox
        self.entry_var.set(content)

    def get(self):
        # Retrieves the selected value from the combobox
        return self.entry_var.get()

    def on_change(self, event):
        pass


class GUI_input_combobox_user_name(GUI_input_combobox):
    rows_occupied = 2
    NEW_USER = "---New User---"

    def setup(self, *args, **kwargs):
        self.entry_var_text = ttk.Entry(self.gui.root, width=50)
        super().setup(*args, **kwargs)

    def get(self):
        combobox_input = super().get()
        return combobox_input if combobox_input != self.NEW_USER else self.entry_var_text.get()

    def on_change(self, event):
        if self.entry_var.get() == self.NEW_USER:
            self.entry_var_text.grid(row=self.row+1, column=1, sticky="ew", padx=5, pady=5)
            self.gui.find_entry("sample_name").entry_var["values"] = [GUI_input_combobox_sample_name.NEW_SAMPLE]
        else:
            self.entry_var_text.grid_remove()
            self.gui.find_entry("sample_name").entry_var["values"] = [GUI_input_combobox_sample_name.NEW_SAMPLE] + find_subfolder( os.path.join(c.DATA_FOLDER_NAME, self.get()) )



class GUI_input_combobox_sample_name(GUI_input_combobox):
    rows_occupied = 2
    NEW_SAMPLE = "---New Sample---"

    def setup(self, *args, **kwargs):
        self.entry_var_text = ttk.Entry(self.gui.root, width=50)
        super().setup(*args, **kwargs)

    def get(self):
        combobox_input = super().get()
        return combobox_input if combobox_input != self.NEW_SAMPLE else self.entry_var_text.get()

    def on_change(self, event):
        if self.entry_var.get() == self.NEW_SAMPLE:
            self.entry_var_text.grid(row=self.row+1, column=1, sticky="ew", padx=5, pady=5)
        else:
            self.entry_var_text.grid_remove()



class GUI_input_combobox_dipole_mode(GUI_input_combobox):
    rows_occupied = 2
    NEW_SAMPLE = "---New Sample---"

    def get(self):
        combobox_input = super().get()
        return int(combobox_input)


class GUI_input_combobox_user_name_for_analysis(GUI_input_combobox):
    def on_change(self, event):
        self.gui.find_entry("sample_name").entry_var["values"] = find_subfolder( os.path.join(c.DATA_FOLDER_NAME, self.get()) )

class GUI_input_combobox_sample_name_for_analysis(GUI_input_combobox):
    def on_change(self, event):
        self.gui.find_entry("measurement_name").entry_var["values"] = find_subfolder( os.path.join(c.DATA_FOLDER_NAME, self.gui.find_entry("user_name").get(), self.get()) )


# ====================== BUTTONS CLASSES ======================


class GUI_button(ABC):
    rows_occupied = 1

    def __init__(self, gui, button_name):
        self.gui = gui
        self.button_name = button_name

    def setup(self, row):
        # Creates a button in the GUI
        self.entry_var = ttk.Button(self.gui.root, text=self.button_name, command=self.on_press, width=20)
        self.entry_var.grid(row=row, column=0, columnspan=2, padx=10, pady=10)

    @abstractmethod
    def on_press(self):
        pass


# Classes for specific button actions
class GUI_button_submit(GUI_button):
    def on_press(self):
        # Submits the entered values
        self.gui.submit_values()


class GUI_button_clear(GUI_button):
    def on_press(self):
        # Clears all inputs
        self.gui.clear_all()


class GUI_button_load_last_settings(GUI_button):
    def on_press(self):
        # Loads settings from the last saved configuration
        self.gui.load("last_settings.json")



def find_subfolder(folder_path):
    # Helper function to find subfolders inside a directory
    try:
        subfolders = next(os.walk(folder_path))[1]
    except FileNotFoundError:
        messagebox.showerror("Folder Not Found", f"The '{folder_path}' folder does not exist.")
        subfolders = []
    return subfolders


# GUI setup function for measurement parameters
def gui_measurement_startup():
     # Initializes the GUI with a set of entries and buttons for measurement
    gui = GUI(root=tk.Tk(), size="500x800", title="Parameter Input GUI")

    entries = [
        GUI_input_combobox_user_name(   gui=gui,    param_name="user_name",            param_desc="User",                  values=[GUI_input_combobox_user_name.NEW_USER] + find_subfolder(c.DATA_FOLDER_NAME)),
        GUI_input_combobox_sample_name( gui=gui,    param_name="sample_name",          param_desc="Sample",                values=[]),
        GUI_input_text_measurement_name(gui=gui,    param_name="measurement_name",     param_desc="Measurement name"       ),
        GUI_input_text(                 gui=gui,    param_name="description",          param_desc="Description",           mandatory=False),
        GUI_input_combobox_dipole_mode( gui=gui,    param_name="dipole_mode",          param_desc="Dipole mode",           values=[1, 2]),
        GUI_input_combobox(             gui=gui,    param_name="ports",                param_desc="Ports",                 values=["12", "13", "14", "23", "24", "34"]),
        GUI_input_text_field_sweep(     gui=gui,    param_name="field_sweep",          param_desc="Field sweep [mT]"       ),
        GUI_input_text_to_number(       gui=gui,    param_name="angle",                param_desc="Angle [deg]",           ), # TODO chagne it so it si not mandatory only in dipole mode, but it is in quadrypole
        GUI_input_text_to_freq(         gui=gui,    param_name="start_frequency",      param_desc="Start frequency [GHz]"  ),
        GUI_input_text_to_freq(         gui=gui,    param_name="stop_frequency",       param_desc="Stop frequency [GHz]"   ),
        GUI_input_text_to_number(       gui=gui,    param_name="number_of_points",     param_desc="Number of points",      func=lambda x : int(x)),
        GUI_input_text_to_number(       gui=gui,    param_name="bandwidth",            param_desc="Bandwidth [Hz]"         ),
        GUI_input_text_to_number(       gui=gui,    param_name="power",                param_desc="Power [dBm]"            ),
        GUI_input_text_to_number(       gui=gui,    param_name="ref_field",            param_desc="Ref field [mT]"         ),
        GUI_input_text(                 gui=gui,    param_name="cal_name",             param_desc="Calibration file",      mandatory=False),
        GUI_input_text(                 gui=gui,    param_name="avg_factor",           param_desc="Averaging factor",      ),
    ]



    buttons = [
        GUI_button_submit(              gui=gui,    button_name="Submit"            ),
        GUI_button_clear(               gui=gui,    button_name="Clear"             ),
        GUI_button_load_last_settings(  gui=gui,    button_name="Load last settings")
    ]


    gui.run_gui(entries=entries, buttons=buttons)

    return gui.inputs if gui.inputs else None



# GUI setup function for analysis parameters
def gui_analysis_startup():
    # Initializes the GUI for analysis-related parameters
    gui = GUI(root=tk.Tk(), size="500x200", title="Parameter Input GUI")

    entries = [
        GUI_input_combobox_user_name_for_analysis(  gui=gui, param_name="user_name",        param_desc="User",             values=find_subfolder(c.DATA_FOLDER_NAME)),
        GUI_input_combobox_sample_name_for_analysis(gui=gui, param_name="sample_name",      param_desc="Sample",           values=[]),
        GUI_input_combobox(                         gui=gui, param_name="measurement_name", param_desc="Measurement name", values=[]),
    ]

    buttons = [
        GUI_button_submit(              gui=gui,    button_name="Submit"            ),
    ]

    gui.run_gui(entries=entries, buttons=buttons)
    
    return os.path.join(c.DATA_FOLDER_NAME, gui.inputs["user_name"], gui.inputs["sample_name"], gui.inputs["measurement_name"]) if gui.inputs else None



# Test to see if the GUI works (will be deprecated)
if __name__ == "__main__":
    ans = gui_measurement_startup()
    print(ans)
