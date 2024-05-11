from matplotlib import pyplot as plt
import numpy as np
import os

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # Import the messagebox module

from library_analysis import *
from library_gui import *
from library_gui_refactored import *
from library_vna import *
from library_power_supply import *



def analysis(measurement_path: str) -> None:
    freq, fields, amplitudes, phases = load_measurement(measurement_path)
    
    [traces, Us] = analysisFMR(freq, fields, amplitudes, phases, measurement_path, show_plots=False)
    alpha = analysisDamping(freq, fields, traces, measurement_path)

    plt.show()



if __name__ == "__main__":
    print("*** LOG SCREEN ***")

    measurement_path = gui_analysis_startup()
    if measurement_path != None:
        analysis(measurement_path)