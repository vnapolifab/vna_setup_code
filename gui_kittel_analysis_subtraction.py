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
    [traces, Us] = analysisFMR_subtraction(freq, fields, amplitudes, phases, measurement_path, show_plots=True)  # Plots imag(U), real(U), trasmission

    return(traces, freq, fields)



if __name__ == "__main__":
    print("*** LOG SCREEN ***")

    measurement_path1 = gui_analysis_startup()
    measurement_path2 = gui_analysis_startup()
    [trace1,freq,fields] = analysis(measurement_path1)
    [trace2,freq,fields] = analysis(measurement_path2)


traces = trace1 - trace2
plt.figure()
plt.title("Imag(U)")

for i in range(len(fields)): 
    
    plt.plot(freq[0:], traces[i,0:])
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Imag(U) [arb. u.]")
    plt.legend([f"{f} mT" for f in fields])

plt.show()

