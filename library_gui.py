import os
import numpy as np
import ast
import json
from abc import ABC, abstractmethod
# from icecream import ic

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont

from library_misc import *
import CONSTANTS as c

import httpx

url = "https://test.fair.labdb.eu.org"
import dataclasses
from typing import Optional, Any
import copy


@dataclasses.dataclass
class User:
    email: str
    userid: int


@dataclasses.dataclass
class UserTeams:
    name: str
    id: int


class EntryNotFound(Exception):
    pass


class GUI:
    inputs = {}

    def __init__(self, root, size, title):
        self.root = root
        self.size = size
        self.title = title
        self.set_style()

    def set_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 12), padding=5, highlightthickness=0)
        style.configure('TButton', font=('Helvetica', 12), padding=5)
        style.configure('TCombobox', font=('Helvetica', 12), padding=5)
        style.map('TCombobox', fieldbackground=[('readonly', 'lightgrey')],
                  selectbackground=[('readonly', 'lightgrey')], selectforeground=[('readonly', 'black')])
        style.map('TEntry', fieldbackground=[('!disabled', 'white'), ('disabled', 'grey')])
        self.root.configure(bg='light grey')

    def run_gui(self, entries, buttons):
        self.root.title(self.title)
        self.root.geometry(self.size)
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

    def find_entry(self, param_name):
        for entry in self.entries:
            if entry.param_name == param_name:
                return entry
        raise EntryNotFound(f"Parameter {param_name} is not associated with an GUI_Input object")

    def clear_all(self):
        for entry in self.entries:
            entry.clear()

    def get_value(self, param):
        return self.find_entry(param).get()

    def submit_values(self):
        self.inputs = {}
        for entry in self.entries:
            if entry.to_be_submitted:
                valid, custom_error = entry.is_valid()
                if not (valid):
                    message = custom_error if custom_error else f'Input for "{entry.param_desc}" is not valid!'
                    tk.messagebox.showerror(title=None, message=message)
                    return

                self.inputs[entry.param_name] = entry.get()
        # self.root.destroy()

    def load(self, filename):
        with open(filename, "r") as f:
            json_obj = json.load(f)
        for entry in self.entries:
            entry.write(json_obj.get(entry.param_name, ""))


class GUI_input(ABC):
    rows_occupied = 1
    to_be_submitted: bool = True
    TEXT = 1
    COMBOBOX = 2

    def __init__(self, gui, param_name, param_desc, mandatory=True, hidden=False):
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
        ttk.Label(self.gui.root, text=self.param_desc, background='light grey').grid(row=row, column=0, sticky="w",
                                                                                     padx=5, pady=5)
        self.entry_var = ttk.Entry(self.gui.root, width=10)
        self.entry_var.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

    def is_valid(self):
        custom_error_message = None
        if self.entry_var.get() != "" or self.mandatory == False:
            return True, custom_error_message
        else:
            return False, custom_error_message

    def clear(self):
        self.entry_var.delete(0, tk.END)

    def write(self, content):
        self.clear()
        self.entry_var.insert(0, content)

    def print_value(self):
        print(self.entry_var.get().strip())

    def get(self):
        return self.entry_var.get().strip()


class GUI_input_text_measurement_name(GUI_input_text):
    def is_valid(self):
        custom_error_message = None
        if self.entry_var.get() == "" and self.mandatory == True:
            return False, custom_error_message

        path = os.path.join(c.DATA_FOLDER_NAME, self.gui.get_value("user_name"), self.gui.get_value("sample_name"),
                            self.get())
        print(path)
        if not (os.path.exists(path)):
            return True, None
        else:
            return False, "This sample has already a measurement with this name!"


class GUI_input_text_field_sweep(GUI_input_text):

    def is_valid(self):
        custom_error_message = None
        if self.entry_var.get() != "" or self.mandatory == False:
            return True, custom_error_message
        else:
            return False, custom_error_message

    def get(self):
        field_sweep_str = self.entry_var.get()
        try:
            # Check if the input string uses range notation (e.g., "1:1:5")
            if ':' in field_sweep_str:
                # Split the string by ':' to get start, step, stop values
                start, step, stop = map(float, field_sweep_str.split(':'))
                # Use range to generate the list of numbers
                field_sweep_list = list(np.arange(start, stop + 0.00001,
                                                  step))  # +0.00001 fa includere il numero finale, TODO trovare un modo migliore per includerlo
            else:
                # For comma-separated values, convert string to list of integers
                # Handle both with and without brackets
                if not field_sweep_str.startswith('['):
                    field_sweep_str = f'[{field_sweep_str}]'
                field_sweep_list = ast.literal_eval(field_sweep_str)
                # Ensure the result is a list of floats
                field_sweep_list = list(np.array(field_sweep_list).astype(float))

            for i in range(len(field_sweep_list)):
                field_sweep_list[i] = (np.round(field_sweep_list[i] * 10 ** 10) / 10 ** 10)

            return field_sweep_list
        except (ValueError, SyntaxError) as e:
            return None

    def write(self, content):
        self.clear()
        self.entry_var.insert(0, str(list(np.array(content)[1:])))


class GUI_input_text_to_freq(GUI_input_text):

    def write(self, content):
        self.clear()
        self.entry_var.insert(0, content / 10 ** 9)

    def is_valid(self):
        try:
            float(self.entry_var.get())
            return True, None
        except:
            return False, None

    def get(self):
        return float(self.entry_var.get()) * 10 ** 9


class GUI_input_text_to_number(GUI_input_text):
    def __init__(self, func=lambda string: float(string), *args, **kwargs):
        self.func = func
        super().__init__(*args, **kwargs)

    def get(self):
        return self.func(self.entry_var.get())


# ====================== COMBOBOX ======================


class GUI_input_combobox(GUI_input):
    entry_type = GUI_input.COMBOBOX

    def __init__(self, values: Optional[list[str]], **kwargs):
        self.values = values
        super().__init__(**kwargs)

    def setup(self, row):
        ttk.Label(self.gui.root, text=self.param_desc, background='light grey').grid(row=row, column=0, sticky="w",
                                                                                     padx=5, pady=5)
        self.entry_var = ttk.Combobox(self.gui.root, state="readonly", values=self.values, width=50)
        self.entry_var.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        self.entry_var.bind('<<ComboboxSelected>>', self.on_change)

    def is_valid(self):
        custom_error_message = None
        if self.entry_var.get() != "":
            return True, custom_error_message
        else:
            return False, custom_error_message

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
        self.entry_var_text = ttk.Entry(self.gui.root, width=10)
        super().setup(*args, **kwargs)

    def get(self):
        combobox_input = super().get()
        return combobox_input if combobox_input != self.NEW_USER else self.entry_var_text.get()

    def on_change(self, event):
        if self.entry_var.get() == self.NEW_USER:
            self.entry_var_text.grid(row=self.row + 1, column=1, sticky="ew", padx=5, pady=5)
            self.gui.find_entry("sample_name").entry_var["values"] = [GUI_input_combobox_sample_name.NEW_SAMPLE]
        else:
            self.entry_var_text.grid_remove()
            self.gui.find_entry("sample_name").entry_var["values"] = [
                                                                         GUI_input_combobox_sample_name.NEW_SAMPLE] + find_subfolder(
                os.path.join(c.DATA_FOLDER_NAME, self.get()))


class GUI_input_combobox_sample_name(GUI_input_combobox):
    rows_occupied = 2
    NEW_SAMPLE = "---New Sample---"

    def setup(self, *args, **kwargs):
        self.entry_var_text = ttk.Entry(self.gui.root, width=10)
        super().setup(*args, **kwargs)

    def get(self):
        combobox_input = super().get()
        return combobox_input if combobox_input != self.NEW_SAMPLE else self.entry_var_text.get()

    def on_change(self, event):
        if self.entry_var.get() == self.NEW_SAMPLE:
            self.entry_var_text.grid(row=self.row + 1, column=1, sticky="ew", padx=5, pady=5)
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
        self.gui.find_entry("sample_name").entry_var["values"] = find_subfolder(
            os.path.join(c.DATA_FOLDER_NAME, self.get()))


class GUI_input_combobox_sample_name_for_analysis(GUI_input_combobox):
    def on_change(self, event):
        self.gui.find_entry("measurement_name").entry_var["values"] = find_subfolder(
            os.path.join(c.DATA_FOLDER_NAME, self.gui.find_entry("user_name").get(), self.get()))


# ====================== BUTTONS ======================


class GUI_button(ABC):
    rows_occupied = 1

    def __init__(self, gui, button_name):
        self.gui = gui
        self.button_name = button_name

    def setup(self, row):
        self.entry_var = ttk.Button(self.gui.root, text=self.button_name, command=self.on_press, width=20)
        self.entry_var.grid(row=row, column=0, columnspan=2, padx=10, pady=10)

    @abstractmethod
    def on_press(self):
        pass


class GUI_button_submit(GUI_button):
    def on_press(self):
        self.gui.submit_values()


class GUI_button_clear(GUI_button):
    def on_press(self):
        self.gui.clear_all()


class GUI_button_load_last_settings(GUI_button):
    def on_press(self):
        self.gui.load("last_settings.json")


# ELABFTW
class GUIButtonSaveToElabFTW(GUI_button):
    def __init__(self, gui, button_name, elab_user, equipment_templates):
        self.elab_user: GuiInputComboboxElabUsers = elab_user
        self.equipment_templates: GUIEquipmentTemplates = equipment_templates
        super().__init__(gui, button_name)

    def setup(self, row):
        self.entry_var = ttk.Button(self.gui.root, text=self.button_name, command=self.on_press, width=20)
        self.entry_var.grid(row=row, column=20, columnspan=2, padx=10, pady=10)

    def on_press(self):

        mod_template = copy.deepcopy(self.equipment_templates.saved_template)
        for parameter in self.equipment_templates.saved_template["metadata"]["extra_fields"]:
            if parameter in self.gui.inputs.keys():
                mod_template["metadata"]["extra_fields"][parameter]["value"] = str(self.gui.inputs[parameter])
        experiment = {
            "title": self.gui.inputs["measurement_name"],
            "category_id": self.equipment_templates.saved_experiment_id,
            "metadata": mod_template["metadata"],
            "userid": self.elab_user.saved_user_id,
            "team_name": self.elab_user.saved_team_name
        }
        response = httpx.post(
            f"{url}/experiments",
            json=experiment,
            verify=False
        )

        if response.status_code == 200:
            print("Experiment successfully Created!")
        else:
            print("Doh!")


def find_subfolder(folder_path):
    try:
        subfolders = next(os.walk(folder_path))[1]
    except FileNotFoundError:
        messagebox.showerror("Folder Not Found", f"The '{folder_path}' folder does not exist.")
        subfolders = []
    return subfolders


def save_users() -> list[User]:
    user_list: list[User] = [User(email=user["email"], userid=user["userid"]) for user in
                             httpx.get(f"{url}/users", verify=False).json()]
    return user_list


class GuiInputComboboxElabUsers(GUI_input_combobox):
    entry_type = GUI_input.COMBOBOX
    to_be_submitted = False

    def __init__(self, values: list[User], **kwargs):
        self.user_list: list[User] = values
        self.values = [user.email for user in values]
        self.user_teams: Optional[list[UserTeams]] = None
        self.saved_team_name: Optional[int] = None
        self.saved_user_id: Optional[int] = None
        super().__init__(values=self.values, **kwargs)

    def setup(self, row):
        ttk.Label(self.gui.root, text=self.param_desc, background='light grey').grid(row=row, column=15, sticky="w",
                                                                                     padx=5, pady=5)
        self.entry_var = ttk.Combobox(self.gui.root, state="readonly", values=self.values,
                                      width=50)
        self.entry_var.grid(row=row, column=20, sticky="ew", padx=5, pady=5)
        self.entry_var.bind('<<ComboboxSelected>>', self.on_change)
        # userteams
        ttk.Label(self.gui.root, text="User Teams", background='light grey').grid(row=row + 2, column=15,
                                                                                  sticky="w",
                                                                                  padx=5, pady=5)
        self.user_teams_combobox = ttk.Combobox(self.gui.root, state="readonly", width=50)
        self.user_teams_combobox.grid(row=row + 2, column=20, sticky="ew", padx=5, pady=5)
        self.user_teams_combobox.bind('<<ComboboxSelected>>', self.save_teams_id)

    def on_change(self, event):
        self.saved_user_id: int = [user.userid for user in self.user_list if user.email == self.entry_var.get()][0]
        self.user_teams = [UserTeams(id=team["id"], name=team["name"]) for team in
                           httpx.get(f"{url}/users/{self.saved_user_id}", verify=False).json()]
        self.user_teams_combobox["values"] = [team.name for team in self.user_teams]

    def save_teams_id(self, event):
        self.saved_team_name = [team.name for team in self.user_teams if team.name == self.user_teams_combobox.get()][0]


class GUIEquipmentTemplates(GUI_input_combobox):
    entry_type = GUI_input.COMBOBOX
    to_be_submitted = False

    def __init__(self, **kwargs):
        self.saved_experiment_id: Optional[int] = None
        self.experiments_templates = httpx.get(f"{url}/equipment/radio_frequency_station", verify=False).json()
        self.values = list(self.experiments_templates.keys())
        self.saved_template: Optional[dict[str, Any]] = None
        super().__init__(self.values, **kwargs)

    def setup(self, row):
        # userteams
        ttk.Label(self.gui.root, text=self.param_desc, background='light grey').grid(row=4, column=15,
                                                                                     sticky="w",
                                                                                     padx=5, pady=5)
        self.entry_var = ttk.Combobox(self.gui.root, state="readonly", width=50, values=self.values)
        self.entry_var.grid(row=4, column=20, sticky="ew", padx=5, pady=5)
        self.entry_var.bind('<<ComboboxSelected>>', self.on_change)

    def on_change(self, event):
        self.saved_experiment_id: int = self.experiments_templates[self.entry_var.get()][
            "id"]
        self.saved_template = self.experiments_templates[self.entry_var.get()]


def gui_measurement_startup():
    gui = GUI(root=tk.Tk(), size="1200x800", title="Parameter Input GUI")
    user_list: list[User] = save_users()
    entries = [
        GUI_input_combobox_user_name(gui=gui, param_name="user_name", param_desc="User",
                                     values=[GUI_input_combobox_user_name.NEW_USER] + find_subfolder(
                                         c.DATA_FOLDER_NAME)),
        GUI_input_combobox_sample_name(gui=gui, param_name="sample_name", param_desc="Sample", values=[]),
        GUI_input_text_measurement_name(gui=gui, param_name="measurement_name", param_desc="Measurement name"),
        GUI_input_text(gui=gui, param_name="description", param_desc="Description", mandatory=False),
        GUI_input_combobox_dipole_mode(gui=gui, param_name="dipole_mode", param_desc="Dipole mode", values=[1]),
        GUI_input_combobox(gui=gui, param_name="s_parameter", param_desc="S Parameter",
                           values=["S11", "S22", "S33", "S44", "S12", "S21", "S13", "S31", "S23", "S32", "S24", "S42",
                                   "S34", "S43", "S14", "S41"]),
        GUI_input_text_field_sweep(gui=gui, param_name="field_sweep", param_desc="Field sweep [mT]"),
        GUI_input_text(gui=gui, param_name="angle", param_desc="Angle [deg]", mandatory=False),
        # TODO chagne it so it si not mandatory only in osme dipole mode
        GUI_input_text_to_freq(gui=gui, param_name="start_frequency", param_desc="Start frequency [GHz]"),
        GUI_input_text_to_freq(gui=gui, param_name="stop_frequency", param_desc="Stop frequency [GHz]"),
        GUI_input_text_to_number(gui=gui, param_name="number_of_points", param_desc="Number of points",
                                 func=lambda x: int(x)),
        GUI_input_text_to_number(gui=gui, param_name="bandwidth", param_desc="Bandwidth [Hz]"),
        GUI_input_text_to_number(gui=gui, param_name="power", param_desc="Power [dBm]"),
        GUI_input_text_to_number(gui=gui, param_name="ref_field", param_desc="Ref field [mT]"),
        GUI_input_text(gui=gui, param_name="cal_file", param_desc="Calibration file", mandatory=False)
    ]
    # ELABFTW
    elab_user = GuiInputComboboxElabUsers(gui=gui, param_name="ELABFTW User Name", param_desc="ELABFTW User Name",
                                          values=user_list, mandatory=False)
    equipment_templates = GUIEquipmentTemplates(gui=gui, param_name="Experiments Templates",
                                                param_desc="Experiments Templates",
                                                mandatory=False)
    save_to_elab_button = GUIButtonSaveToElabFTW(gui=gui, elab_user=elab_user,
                                                 equipment_templates=equipment_templates, button_name="save_to_elab")
    buttons = [
        GUI_button_submit(gui=gui, button_name="Submit"),
        GUI_button_clear(gui=gui, button_name="Clear"),
        GUI_button_load_last_settings(gui=gui, button_name="Load last settings"),

    ]

    elab_user.setup(row=0)
    equipment_templates.setup(row=2)
    save_to_elab_button.setup(row=5)
    gui.run_gui(entries=entries, buttons=buttons)
    return gui.inputs if gui.inputs else None


def gui_analysis_startup():
    gui = GUI(root=tk.Tk(), size="500x200", title="Parameter Input GUI")

    entries = [
        GUI_input_combobox_user_name_for_analysis(gui=gui, param_name="user_name", param_desc="User",
                                                  values=find_subfolder(c.DATA_FOLDER_NAME)),
        GUI_input_combobox_sample_name_for_analysis(gui=gui, param_name="sample_name", param_desc="Sample", values=[]),
        GUI_input_combobox(gui=gui, param_name="measurement_name", param_desc="Measurement name", values=[]),
    ]

    buttons = [
        GUI_button_submit(gui=gui, button_name="Submit"),
    ]

    gui.run_gui(entries=entries, buttons=buttons)

    return os.path.join(c.DATA_FOLDER_NAME, gui.inputs["user_name"], gui.inputs["sample_name"],
                        gui.inputs["measurement_name"]) if gui.inputs else None


if __name__ == "__main__":
    # ans = gui_analysis_startup()
    ans = gui_measurement_startup()
    print(ans)
