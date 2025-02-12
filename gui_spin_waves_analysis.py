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
    settings = load_metadata(measurement_path)
    freq, fields, amplitudes1, phases1, amplitudes2, phases2, amplitudes3, phases3, amplitudes4, phases4 = load_measurement(measurement_path, Ports = settings["ports"])

    analysisSW(freq, fields, amplitudes1, phases1, amplitudes2, phases2, amplitudes3, phases3, amplitudes4, phases4, measurement_path, Ports = settings["ports"], show_plots=True)  # Plots imag(U), real(U), trasmission
    
    plt.show()


if __name__ == "__main__":
    print("*** LOG SCREEN ***")

    measurement_path = gui_analysis_startup()
    if measurement_path != None:
        analysis(measurement_path)
