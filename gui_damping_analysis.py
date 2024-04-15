import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # Import the messagebox module

from library_analysis import *
from library_gui import *
from library_vna import *
from library_power_supply import *

from matplotlib import pyplot as plt
import numpy as np


def analysis(user_folder: str, sample_folder: str, measure_folder: str) -> None:
    settings = load_metadata(user_folder, sample_folder, measure_folder)
    freq, fields, amplitudes, phases = load_measurement(user_folder, sample_folder, measure_folder)
    
    [traces, Us] = analysisFMR(freq, fields, amplitudes, phases, user_folder, sample_folder, measure_folder, show_plots=False)
    alpha = analysisDamping(freq, fields, traces, user_folder, sample_folder, measure_folder)

    plt.show()



if __name__ == "__main__":
    print("*** LOG SCREEN ***")
    print("results and actions are reported here:\n")

    user_folder, sample_folder, measure_folder = gui_folder_selection(func_on_submit = analysis)
