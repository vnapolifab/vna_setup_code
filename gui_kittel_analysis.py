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
    freq, fields, amplitudes, phases = load_measurement(user_folder, sample_folder, measure_folder)

    [traces, Us] = analysisFMR(freq, fields, amplitudes, phases, user_folder, sample_folder, measure_folder, show_plots=True, for_notebook=False)  # Plots imag(U), real(U), trasmission
    [peak_freq, Ms_fit] = analysisKittel(freq, traces, fields, user_folder, sample_folder, measure_folder)  # Plots Kittel function and fit
    #The conversion factor between current and field was measured to be 53.2, yet its uniformity might play a role (ranges between 51-57)
    
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