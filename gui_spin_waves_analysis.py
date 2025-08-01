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



# Import necessary modules
from matplotlib import pyplot as plt  # For plotting measurement data
import numpy as np  # For numerical operations
import os  # For handling file system operations

# Import GUI-related modules from Tkinter
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # Import messagebox for displaying alerts

# Import custom libraries for analysis, GUI interaction, VNA, and power supply handling
from library_analysis import *  
from library_gui import *  
from library_vna import *  
from library_power_supply import *  

def analysis(measurement_path: str) -> None:
    """
    Performs analysis on measurement data stored at the given path.

    Parameters:
    measurement_path (str): Path to the measurement data folder.
    """

    # Load measurement metadata (e.g., settings and configurations)
    settings = load_metadata(measurement_path)

    # Load measurement data including frequency, field values, amplitudes, and phases
    freq, fields, amplitudes1, phases1, amplitudes2, phases2, amplitudes3, phases3, amplitudes4, phases4 = load_measurement(
        measurement_path, Ports=settings["ports"]
    )

    # Perform data analysis and visualization
    # This function likely processes S-parameters and visualizes the real & imaginary parts
    analysisSW(
        freq, fields, amplitudes1, phases1, amplitudes2, phases2,
        amplitudes3, phases3, amplitudes4, phases4,
        measurement_path, Ports=settings["ports"], show_plots=True
    )

    # Display all generated plots
    plt.show()


if __name__ == "__main__":
    """
    Main script execution: 
    - Displays a log message
    - Opens GUI for user to select a measurement file
    - If a valid file is selected, it proceeds with analysis
    """

    print("*** LOG SCREEN ***")  # Display log screen message

    # Open GUI dialog for selecting a measurement path
    measurement_path = gui_analysis_startup()

    # If the user selects a measurement file, perform analysis
    if measurement_path is not None:
        analysis(measurement_path)
