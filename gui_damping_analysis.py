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


def analysis(user_folder, sample_folder, measure_folder):
    settings = load_metadata(user_folder, sample_folder, measure_folder)
    freq, fields, amplitudes, phases = load_measurement(user_folder, sample_folder, measure_folder)
    
    [traces, Us] = analysisFMR(freq, fields, amplitudes, phases, user_folder, sample_folder, measure_folder, show_plots=False)
    alpha = analysisDamping(freq, fields, traces, user_folder, sample_folder, measure_folder)

    plt.show()




print("*** LOG SCREEN ***")
print("results and actions are reported here:\n")

# Call the function
user_folder, sample_folder, measure_folder = gui_folder_selection(func_on_submit = analysis)
# if user_folder and measure_folder:
#     print(f"User folder: {user_folder}")
#     print(f"Measure folder: {measure_folder}")
# else:
#     print("Submission was incomplete.")