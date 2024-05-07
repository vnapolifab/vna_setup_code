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
        self.root.geometry("500x700")
        self.entries = entries
        self.buttons = buttons

        for i, entry in enumerate(self.entries.values()):
            entry.setup(self, i)

        for j, button in enumerate(self.buttons.values()):
            button.setup(self, i+j+1)
        
        self.root.mainloop()
        self.root.quit()
        

    def clear_all(self):
        for name, entry in zip(self.entries.keys(), self.entries.values()):
            entry.clear()
    

    def get_values(self):
        self.inputs = {}
        for name, entry in zip(self.entries.keys(), self.entries.values()):
            if entry.entry_type == GUI_input.BUTTON: 
                continue

            if not(entry.is_valid()):
                tk.messagebox.showerror(title=None, message=f'Input for "{entry.param_desc.lower()}" is not valid!')
                return
            
            self.inputs[entry.param_name] = entry.get()

        self.root.quit()


    def load(self, filename):
        with open(filename, "r") as f:
            json_obj = json.load(f)
        for param, val  in zip(json_obj.keys(), json_obj.values()):
            if param in self.entries.keys():
                self.entries[param].write(val)




class GUI_input(ABC):
    TEXT = 1
    COMBOBOX = 2
    BUTTON = 3

    def __init__(self, gui, param_name, param_desc):
        self.gui = gui
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

    @abstractmethod
    def get():
        pass




class GUI_input_standard_text(GUI_input):
    entry_type = GUI_input.TEXT

    def __init__(self, gui, param_name, param_desc):
        super().__init__(gui, param_name, param_desc)

    def setup(self, gui, row):
        ttk.Label(gui.root, text=self.param_desc, background='light grey').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.entry_var = ttk.Entry(gui.root, width=50)
        self.entry_var.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    
    def is_valid(self):
        if self.entry_var.get() != "":
            return True
        else:
            return False

    def clear(self):
        self.entry_var.delete(0, tk.END)

    def write(self, content):
        self.clear()
        self.entry_var.insert(0, content)

    def print_value(self):
        print(self.entry_var.get())

    def get(self):
        return self.entry_var.get()


class GUI_input_combobox(GUI_input):
    entry_type = GUI_input.COMBOBOX

    def __init__(self, gui, param_name, param_desc, values):
        self.values = values
        super().__init__(gui, param_name, param_desc)

    def setup(self, gui, row):
        ttk.Label(gui.root, text=self.param_name, background='light grey').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.entry_var = ttk.Combobox(gui.root, state="readonly", values=self.values, width=50)
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

    def on_change(self, event):
        print("Changed value")

    def get(self):
        return self.entry_var.get()




class GUI_button(ABC):
    def __init__(self, gui, button_name):
        self.gui = gui
        self.button_name = button_name

    def setup(self, gui, row):
        self.entry_var = ttk.Button(gui.root, text=self.button_name, command=self.on_press, width=20)
        self.entry_var.grid(row=row, column=1, columnspan=1, padx=10, pady=10)

    @abstractmethod
    def on_press(self):
        pass


class GUI_button_submit(GUI_button):
    def __init__(self, gui, button_name):
        super().__init__(gui, button_name)

    def on_press(self):
        gui.get_values()


class GUI_button_clear(GUI_button):
    entry_type = GUI_input.BUTTON

    def __init__(self, gui, button_name):
        super().__init__(gui, button_name)

    def on_press(self):
        gui.clear_all()


class GUI_button_load_last_settings(GUI_button):
    entry_type = GUI_input.BUTTON

    def __init__(self, gui, button_name):
        super().__init__(gui, button_name)

    def on_press(self):
        gui.load("last_settings.json")





def gui_startup():
    global gui
    gui = GUI(root=tk.Tk())

    entries = {
        
        "user_name" : GUI_input_combobox(gui=gui, param_name="user_name", param_desc="User", values=[1,2,3]),
        
        "sample_name" : GUI_input_combobox(gui=gui, param_name="sample_name", param_desc="Sample", values=[1,2,3]),
        
        "measurement_name" : GUI_input_standard_text(gui=gui, param_name="measurement_name", param_desc="Measurement name"),

        "description" : GUI_input_standard_text(gui=gui, param_name="description", param_desc="Description"),

        "dipole_mode" : GUI_input_combobox(gui=gui, param_name="dipole_mode", param_desc="Dipole mode", values=[1,2,3]),

        "s_parameter" : GUI_input_standard_text(gui=gui, param_name="s_parameter", param_desc="Field sweep [mT]"),

        "field_sweep" : GUI_input_standard_text(gui=gui, param_name="field_sweep", param_desc="Field sweep [mT]"),

        "angle" : GUI_input_standard_text(gui=gui, param_name="angle", param_desc="Angle [deg]"),

        "start_frequency" : GUI_input_standard_text(gui=gui, param_name="start_frequency", param_desc="Start frequency [GHz]"),

        "stop_frequency" : GUI_input_standard_text(gui=gui, param_name="stop_frequency", param_desc="Stop frequency [GHz]"),
        
        "number_of_points" : GUI_input_standard_text(gui=gui, param_name="number_of_points", param_desc="Number of points"),
        
        "bandwith" : GUI_input_standard_text(gui=gui, param_name="bandwidth", param_desc="Bandwidth [Hz]"),

        "power" : GUI_input_standard_text(gui=gui, param_name="power", param_desc="Power [dBm]"),
        
        "ref_field" : GUI_input_standard_text(gui=gui, param_name="ref_field", param_desc="Ref field [mT]"),

    }


    buttons = {
        "submit" : GUI_button_submit(gui=gui, button_name="Submit"),
        "clear" : GUI_button_clear(gui=gui, button_name="Clear"),
        "load"  : GUI_button_load_last_settings(gui=gui, button_name="Load last settings")
    }



    gui.run_gui(entries=entries, buttons=buttons)

    return gui.inputs if gui.inputs else None



if __name__ == "__main__":
    ans = gui_startup()    

    print(ans)

    