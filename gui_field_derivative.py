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



def analysis(measurement_path: str) -> None:
    freq, fields, amplitudes, phases = load_measurement(measurement_path)

    set_default_pyplot_style_settings()
    [traces, Us] = analysisFMR_derivative(freq, fields, amplitudes, phases, measurement_path, show_plots=True)  # Plots imag(U), real(U), trasmission
    [q] = analysis_field_derivative(freq, traces, fields, measurement_path)  # Plots Kittel function and fit
    
    plt.show()



if __name__ == "__main__":
    print("*** LOG SCREEN ***")

    measurement_path = gui_analysis_startup()
    if measurement_path != None:
        analysis(measurement_path)

