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
    def __init__(self, root, entries):
        self.root = root
        self.set_style()
        self.setup_gui(entries)
        self.root.mainloop()
        self.root.quit()


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


    def setup_gui(self, entries):
        self.root.title("Parameter Input GUI")
        self.root.geometry("750x800")

        for i, entry in enumerate(entries.values()):
            entry.setup(self, i)




class GUI_entry(ABC):
    TEXT = 1
    COMBOBOX = 2
    BUTTON = 3
    # value = tk.StringVar()

    def __init__(self, param_name, param_desc, is_valid_func=lambda x:True):
        self.param_name = param_name
        self.param_desc = param_desc

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def is_valid():
        pass

    @abstractmethod
    def clear():
        pass

    @abstractmethod
    def write():
        pass



class GUI_entry_standard_text(GUI_entry):
    entry_type = GUI_entry.TEXT

    def __init__(self, param_name, param_desc):
        super().__init__(param_name, param_desc)

    def setup(self, gui, row):
        ttk.Label(gui.root, text=self.param_desc, background='light grey').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.entry = ttk.Entry(gui.root, width=50)
        self.entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    
    def is_valid(self):
        if self.entry.get() != "":
            return True
        else:
            return False

    def clear(self):
        self.entry.delete(0, tk.END)

    def write(self):
        pass

    def print_value(self):
        print(self.entry.get())



class GUI_entry_combobox(GUI_entry):
    entry_type = GUI_entry.COMBOBOX

    def __init__(self, param_name, param_desc, values):
        self.values = values
        super().__init__(param_name, param_desc)

    def setup(self, gui, row):
        ttk.Label(gui.root, text=self.param_name, background='light grey').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.entry = ttk.Combobox(gui.root, state="readonly", values=self.values, width=50)
        self.entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        self.entry.bind('<<ComboboxSelected>>', self.print_value)

    def is_valid(self):
        if self.entry.get() != "":
            return True
        else:
            return False

    def clear(self):
        pass

    def write(self):
        pass

    def print_value(self, event):
        print(self.entry.get())



class GUI_entry_submit_button(GUI_entry):
    entry_type = GUI_entry.BUTTON

    def __init__(self, param_name, param_desc):
        super().__init__(param_name, param_desc)

    def setup(self, gui, row):
        self.entry = ttk.Button(gui.root, text=self.param_desc, command=self.on_press, width=20)
        self.entry.grid(row=row, column=1, columnspan=1, padx=10, pady=10)

    def on_press(self):
        print(f"{"Parameter":20} | {"Validity":20}")
        print("-"*30)
        for key, val in zip(entries.keys(), entries.values()):
            print(f"{key:20} | {val.is_valid()}")

    def is_valid(self):
        return True

    def clear(self):
        pass

    def write(self):
        pass



class GUI_entry_clear_button(GUI_entry):
    entry_type = GUI_entry.BUTTON

    def __init__(self, param_name, param_desc):
        super().__init__(param_name, param_desc)

    def setup(self, gui, row):
        self.entry = ttk.Button(gui.root, text=self.param_desc, command=self.on_press, width=20)
        self.entry.grid(row=row, column=1, columnspan=1, padx=10, pady=10)

    def on_press(self):
        for name, entry in zip(entries.keys(), entries.values()):
            if entry.entry_type == GUI_entry.TEXT:
                entry.clear()

    def is_valid(self):
        return True

    def clear(self):
        pass

    def write(self):
        pass





if __name__ == "__main__":
    root = tk.Tk()

    entries = {
        
        "user_name" : GUI_entry_combobox(param_name="user_name", param_desc="User", values=[1,2,3]),
        
        "sample_name" : GUI_entry_combobox(param_name="sample_name", param_desc="Sample", values=[1,2,3]),
        
        "measurement_name" : GUI_entry_standard_text(param_name="measurement_name", param_desc="Measurement name"),

        "description" : GUI_entry_standard_text(param_name="description", param_desc="Description"),

        "dipole_mode" : GUI_entry_combobox(param_name="dipole_mode", param_desc="Dipole mode", values=[1,2,3]),

        "s_parameter" : GUI_entry_standard_text(param_name="s_parameter", param_desc="Field sweep [mT]"),

        "field_sweep" : GUI_entry_standard_text(param_name="field_sweep", param_desc="Field sweep [mT]"),

        "angle" : GUI_entry_standard_text(param_name="angle", param_desc="Angle [deg]"),

        "start_frequency" : GUI_entry_standard_text(param_name="start_frequency", param_desc="Start frequency [GHz]"),

        "stop_frequency" : GUI_entry_standard_text(param_name="stop_frequency", param_desc="Stop frequency [GHz]"),
        
        "number_of_points" : GUI_entry_standard_text(param_name="number_of_points", param_desc="Number of points"),
        
        "bandwith" : GUI_entry_standard_text(param_name="bandwidth", param_desc="Bandwidth [Hz]"),

        "power" : GUI_entry_standard_text(param_name="power", param_desc="Power [dBm]"),
        
        "ref_field" : GUI_entry_standard_text(param_name="ref_field", param_desc="Ref field [mT]"),

        "submit" : GUI_entry_submit_button(param_name="submit", param_desc="Submit"),

        "clear" : GUI_entry_clear_button(param_name="clear", param_desc="Clear")
    }

    GUI(root, entries=entries)