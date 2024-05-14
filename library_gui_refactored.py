import os
import numpy as np
import ast
import json
from abc import ABC, abstractmethod

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont

from library_misc import *
from CONSTANTS import *


class GUI:
    inputs = {}

    def __init__(self, root):
        self.root = root
        self.set_style()


    def set_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 12), padding=5, highlightthickness=0)
        style.configure('TButton', font=('Helvetica', 12), padding=5)
        style.configure('TCombobox', font=('Helvetica', 12), padding=5)
        style.map('TCombobox', fieldbackground=[('readonly', 'lightgrey')], selectbackground=[('readonly', 'lightgrey')], selectforeground=[('readonly', 'black')])
        style.map('TEntry', fieldbackground=[('!disabled', 'white'), ('disabled', 'grey')])
        self.root.configure(bg='light grey')


    def run_gui(self, entries, buttons):
        self.root.title("Parameter Input GUI")
        self.root.geometry("500x800")
        self.entries = entries
        self.buttons = buttons

        row = 0
        for entry in self.entries:
            entry.setup(row)
            entry.row = row
            row += entry.rows_occupied

        for button in self.buttons:
            button.setup(row)
            row += entry.rows_occupied
        
        self.root.mainloop()
        self.root.quit()


    def find_entry(self, param_name):
        for entry in self.entries:
            if entry.param_name == param_name:
                return entry
        raise Exception(f"Parameter {param_name} is not associated with an GUI_Input object")
        

    def clear_all(self):
        for entry in self.entries:
            entry.clear()
    

    def get_values(self):
        self.inputs = {}
        for entry in self.entries:

            if not(entry.is_valid()):
                tk.messagebox.showerror(title=None, message=f'Input for "{entry.param_desc}" is not valid!')
                return
            
            self.inputs[entry.param_name] = entry.get()


    def load(self, filename):
        with open(filename, "r") as f:
            json_obj = json.load(f)
        for entry in self.entries:
            entry.write(json_obj.get(entry.param_name, ""))




class GUI_input(ABC):
    rows_occupied = 1
    TEXT = 1
    COMBOBOX = 2

    def __init__(self, gui, param_name, param_desc, mandatory = True, hidden = False):
        self.gui = gui
        self.param_name = param_name
        self.param_desc = param_desc
        self.mandatory = mandatory
        self.hidden = hidden

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



# ====================== TEXT ======================


class GUI_input_text(GUI_input):
    entry_type = GUI_input.TEXT

    def setup(self, row):
        ttk.Label(self.gui.root, text=self.param_desc, background='light grey').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.entry_var = ttk.Entry(self.gui.root, width=50)
        self.entry_var.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    
    def is_valid(self):
        if self.entry_var.get() != "" or self.mandatory == False:
            return True
        else:
            return False

    def clear(self):
        self.entry_var.delete(0, tk.END)

    def write(self, content):
        self.clear()
        self.entry_var.insert(0, str(content))

    def print_value(self):
        print(self.entry_var.get())

    def get(self):
        return self.entry_var.get()



class GUI_input_text_field_sweep(GUI_input_text):

    def is_valid(self):
        if self.entry_var.get() != "" or self.mandatory == False:
            return True
        else:
            return False

    def get(self):
        field_sweep_str = self.entry_var.get()
        try:
            # Check if the input string uses range notation (e.g., "1:1:5")
            if ':' in field_sweep_str:
                # Split the string by ':' to get start, step, stop values
                start, step, stop = map(float, field_sweep_str.split(':'))
                # Use range to generate the list of numbers
                field_sweep_list = list(np.arange(start, stop + 0.00001, step))  # +0.00001 fa includere il numero finale, TODO trovare un modo migliore per includerlo
            else:
                # For comma-separated values, convert string to list of integers
                # Handle both with and without brackets
                if not field_sweep_str.startswith('['):
                    field_sweep_str = f'[{field_sweep_str}]'
                field_sweep_list = ast.literal_eval(field_sweep_str)
                # Ensure the result is a list of floats
                field_sweep_list = list(np.array(field_sweep_list).astype(float))
            
            for i in range(len(field_sweep_list)):
                field_sweep_list[i] = ( np.round(field_sweep_list[i] *10**10)/10**10 )
            
            return field_sweep_list
        except (ValueError, SyntaxError) as e:
            return None
    
        
class GUI_input_text_to_freq(GUI_input_text):
    def __init__(self, func=lambda string : float(string), *args, **kwargs):
        self.func = func
        super().__init__(*args, **kwargs)

    def write(self, content):
        self.clear()
        self.entry_var.insert(0, content/10**9)

    def get(self):
        return self.func(self.entry_var.get())
    

class GUI_input_text_to_number(GUI_input_text):
    def __init__(self, func=lambda string : float(string), *args, **kwargs):
        self.func = func
        super().__init__(*args, **kwargs)

    def get(self):
        return self.func(self.entry_var.get())


# ====================== COMBOBOX ======================


class GUI_input_combobox(GUI_input):
    entry_type = GUI_input.COMBOBOX

    def __init__(self, values, **kwargs):
        self.values = values
        super().__init__(**kwargs)

    def setup(self, row):
        ttk.Label(self.gui.root, text=self.param_desc, background='light grey').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.entry_var = ttk.Combobox(self.gui.root, state="readonly", values=self.values, width=50)
        self.entry_var.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        self.entry_var.bind('<<ComboboxSelected>>', self.on_change)

    def is_valid(self):
        if self.entry_var.get() != "":
            return True
        else:
            return False

    def clear(self):
        self.entry_var.set("")

    def write(self, content):
        self.entry_var.set(content)

    def get(self):
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
            self.gui.find_entry("sample_name").entry_var["values"] = [GUI_input_combobox_sample_name.NEW_SAMPLE] + find_subfolder( os.path.join(DATA_FOLDER_NAME, self.get()) )


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


# ====================== BUTTONS ======================


class GUI_button(ABC):
    rows_occupied = 1

    def __init__(self, gui, button_name):
        self.gui = gui
        self.button_name = button_name

    def setup(self, row):
        self.entry_var = ttk.Button(self.gui.root, text=self.button_name, command=self.on_press, width=20)
        self.entry_var.grid(row=row, column=1, columnspan=1, padx=10, pady=10)

    @abstractmethod
    def on_press(self):
        pass


class GUI_button_submit(GUI_button):
    def on_press(self):
        self.gui.get_values()
        self.gui.root.quit()


class GUI_button_clear(GUI_button):
    def on_press(self):
        self.gui.clear_all()


class GUI_button_load_last_settings(GUI_button):
    def on_press(self):
        self.gui.load("last_settings.json")



def find_subfolder(folder_path):
    try:
        subfolders = next(os.walk(folder_path))[1]
    except FileNotFoundError:
        messagebox.showerror("Folder Not Found", f"The '{folder_path}' folder does not exist.")
        subfolders = []
    return subfolders



def gui_measurement_startup():
    gui = GUI(root=tk.Tk())

    entries = [
        GUI_input_combobox_user_name(   gui=gui,    param_name="user_name",            param_desc="User",                  values=[GUI_input_combobox_user_name.NEW_USER] + find_subfolder(DATA_FOLDER_NAME)),
        GUI_input_combobox_sample_name( gui=gui,    param_name="sample_name",          param_desc="Sample",                values=[]),
        GUI_input_text(                 gui=gui,    param_name="measurement_name",     param_desc="Measurement name"       ),
        GUI_input_text(                 gui=gui,    param_name="description",          param_desc="Description",           mandatory=False),
        GUI_input_combobox_dipole_mode( gui=gui,    param_name="dipole_mode",          param_desc="Dipole mode",           values=[1]),
        GUI_input_combobox(             gui=gui,    param_name="s_parameter",          param_desc="S Parameter",           values=["S13"]),
        GUI_input_text_field_sweep(     gui=gui,    param_name="field_sweep",          param_desc="Field sweep [mT]"       ),
        GUI_input_text(                 gui=gui,    param_name="angle",                param_desc="Angle [deg]",           mandatory=False), # TODO chagne it so it si not mandatory only in osme dipole mode
        GUI_input_text_to_freq(         gui=gui,    param_name="start_frequency",      param_desc="Start frequency [GHz]", func=lambda x : float(x)*10**9),
        GUI_input_text_to_freq(         gui=gui,    param_name="stop_frequency",       param_desc="Stop frequency [GHz]",  func=lambda x : float(x)*10**9),
        GUI_input_text_to_number(       gui=gui,    param_name="number_of_points",     param_desc="Number of points",      func=lambda x : int(x)),
        GUI_input_text_to_number(       gui=gui,    param_name="bandwidth",            param_desc="Bandwidth [Hz]"         ),
        GUI_input_text_to_number(       gui=gui,    param_name="power",                param_desc="Power [dBm]"            ),
        GUI_input_text_to_number(       gui=gui,    param_name="ref_field",            param_desc="Ref field [mT]"         ),
        GUI_input_text(                 gui=gui,    param_name="cal_file",             param_desc="Calibration file",      mandatory=False),
    ]



    buttons = [
        GUI_button_submit(              gui=gui,    button_name="Submit"            ),
        GUI_button_clear(               gui=gui,    button_name="Clear"             ),
        GUI_button_load_last_settings(  gui=gui,    button_name="Load last settings")
    ]


    gui.run_gui(entries=entries, buttons=buttons)

    return gui.inputs if gui.inputs else None



if __name__ == "__main__":
    ans = gui_measurement_startup()    
    print(ans)
