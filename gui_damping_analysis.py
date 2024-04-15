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


# def analysis_old(user_folder, measure_folder):
#     """
#     Function triggered by button press.
#     Contains data analysis.
#     """

#     freq, fields, amplitudes, phases = load_measurement(user_folder, measure_folder)
#     [traces, Us] = analysisFMR(freq, fields, amplitudes, phases)
#     settings = load_metadata(user_folder, measure_folder)

#     traces_field = []
#     for i in range(settings["number_of_points"]):
#         traces_field.append(traces[1:,i])

#     traces_field=np.array(traces_field)

#     plt.figure()
#     for n in range(settings["number_of_points"]):
#         # plt.subplot(settings["number_of_points"],1,n+1)
#         plt.plot(fields[1:], traces_field[n,:])
#         # plt.title(str(n) + ") " + f"{freq[n]/10**9:.4}" + "GHz")

#     traces_field = np.array(traces_field)
#     field_peaks = []
#     for trace in traces_field:
#         max_ind = np.argmax(trace)
#         field_peaks.append(fields[max_ind])

#     # for trace in traces:
#     #U must be used or the fit won't work ----> la Lorentziana usata per fittare ha fondo nullo, se non normalizzi riportando il fondo a zero (come si fa nel calcolo di U) la curva non fitta
    
#     g = 1.7e11
#     mu0 = 4e-7 * np.pi
#     conversion = 795.7747 #the field needs to be transformed in A/m before being used
#     alpha = np.zeros((len(traces_field),1))
#     field_width = np.zeros((len(traces_field),1))

#     plt.figure()
#     for i in range(1,len(traces_field),1):
#         # plt.subplot(settings["number_of_points"],1,i+1)
#         getFWHMFitted(fields[1:], traces_field[i,:], field_peaks[i])
#         # plt.title(str(i) + ") " + f"{freq[i]/10**9:.4}" + "GHz")

#         width = getFWHMFitted(fields[1:], traces_field[i,:], field_peaks[i])
#         width = np.array(width)
#         print(f"{i}) FWHM: \t" + str(width[0]), end = ",   ")

#         alpha[i] = conversion*(width*g*mu0)/(4*np.pi*freq[i])
#         #alpha[i] = (g*mu0*conversion*width)/(2*freq[i]/(2*np.pi)) 
#         print(f"{i}) Alpha: \t{alpha[i][0]}")

#     alpha_sum = 0

#     for i in range(len(traces_field)):
#         alpha_sum += alpha[i]

#     alpha_final = alpha_sum/len(traces_field)
#     print("Alpha averaged: {alpha_final}")



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