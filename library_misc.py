import os
import numpy as np
import json
import matplotlib.pyplot as plt

from logger import logger  # Importing logger for logging purposes
import CONSTANTS as c  # Importing constants from a custom module

"""
This library contains general functions that are used throughout the program and are not related to a specific instrument or procedure.
"""

# Function to set default styling for all plots created using Matplotlib
def set_default_pyplot_style_settings():
    plt.rcParams["font.size"] = 16  # Set font size for all text in plots
    plt.rcParams["figure.figsize"] = c.FULLSCREEN_SIZE  # Set figure size using a constant from the CONSTANTS module
    plt.rcParams["axes.grid"] = True  # Enable grid for all plots
    plt.rcParams["lines.linewidth"] = 2  # Set default linewidth for all plot lines
    plt.rcParams["lines.marker"] = '.'  # Set the marker style for plot lines
    plt.rcParams["lines.markersize"] = 4  # Set default size for plot markers

# Function to display a warning message to the user
def sendWarning(s: str):
    # Function used for user interface
    print("WARNING: " + s)

# Function to display an error message to the user
def sendError(s: str):
    # Function used for user interface
    print("ERROR: " + s)

# Function to log a message for general logging purposes
def sendLog(s: str):  
    # Function used for user interface
    print("LOG: " + s)

# Function to update a log file with new measurement details
def update_log(settings: object):
    with open("log.txt", "r") as f:  # Open the log file in read mode
        text = f.read()  # Read all the content of the file

    new_text = f"""
    Date-time: {settings["datetime"]}
    User: {settings["user_name"]}
    File name: {settings["measurement_name"]}
    Description: {settings["description"]}


    """  # Create a new log entry with relevant measurement information

    file_content = text + new_text  # Append new log entry to existing content
    with open("log.txt", "w") as f:  # Open the log file in write mode
        f.write(file_content)  # Write the updated content back to the log file



    
