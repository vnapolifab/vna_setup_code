from matplotlib import pyplot as plt
import numpy as np
import os

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # Import the messagebox module

from library_analysis import *
from library_gui import *
from library_vna import *
from library_power_supply import *



def analysis(user_folder: str, sample_folder: str, measure_folder: str) -> None:
    settings = load_metadata(user_folder, sample_folder, measure_folder)
    freq, fields, amplitudes, phases = load_measurement(user_folder, sample_folder, measure_folder)

    [traces, Us] = analysisSW(freq, fields, amplitudes, phases, user_folder, sample_folder, measure_folder, s_parameter=settings["s_parameter"], show_plots=True)  # Plots imag(U), real(U), trasmission
    # [peak_freq, Ms_fit] = analysisKittel(freq, traces, fields)  # Plots Kittel function and fit
    # # The conversion factor between current and field was measured to be 53.2, yet its uniformity might play a role (ranges between 51-57)
    
    plt.show()


if __name__ == "__main__":
    print("*** LOG SCREEN ***")

    measurement_path = gui_analysis_startup()
    if measurement_path != None:
        analysis(measurement_path)
