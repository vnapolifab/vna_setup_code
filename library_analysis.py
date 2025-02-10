import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import curve_fit 
import json
from itertools import cycle

from library_misc import *
from library_file_management import *
from CONSTANTS import *

"""
This library containsfunctions used for the analysis of measurement results.
In this file functions are modified to be compatible with the gui.
"""

def analysisSW(freq: np.ndarray, fields: np.ndarray, amplitudes: np.ndarray, phases: np.ndarray, measurement_path: str, s_parameter: str, ref_n = 0, show_plots=True) -> tuple[np.ndarray, np.ndarray]:
    """
    This function takes as input the frequencies, fields, amplitudes and phases and plots relevant data for FMR resonance.
    ref_n is the index number for the reference measurement, default is zero.
    """

    n_traces = len(amplitudes[:,0])
    n_points = len(freq)

    # init
    traces_no_background_real = np.zeros((n_traces, n_points))
    traces_no_background_imag = np.zeros((n_traces, n_points))
    traces_no_background_complex = np.zeros((n_traces, n_points), dtype = 'complex_')
    amplitudes_no_background = np.zeros((n_traces, n_points))
    phase_sub = np.zeros((n_traces, n_points))
    
    amp_ref, phase_ref = amplitudes[ref_n], phases[ref_n]
    #phase_ref = unwrap_phase(phase_ref)
    phase_ref = np.unwrap(phase_ref)

    # Signal processing
    for i in range(n_traces):
        amp, phase = amplitudes[i,:], phases[i,:]
        #phase = unwrap_phase(phase)
        phase = np.unwrap(phase)

        traces_no_background_complex[i,:] = (amp * np.exp(1j * phase))-(amp_ref * np.exp(1j * phase_ref))
        phase_sub[i,:] = np.angle(traces_no_background_complex[i,:])
 
        traces_no_background_real[i,:] = np.real(traces_no_background_complex[i,:])
        traces_no_background_imag[i,:] = np.imag(traces_no_background_complex[i,:])
        amplitudes_no_background[i,:] = amplitudes[i,:] - amp_ref

    # Init
    amplitudes_dB = np.zeros((n_traces, n_points))

    for i in range(n_traces):
        amplitudes_dB[i,:] = 20*np.log10(amplitudes[i,:])


    # Plotting
    if show_plots:

        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title("Imaginary part (no background)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, traces_no_background_imag[i,0:], marker=MARKER, markersize=MARKER_SIZE,linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel(f"Imag({s_parameter}) [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, "imag.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title("Real part (no background)")
        for i in range(len(traces_no_background_real)): 
            plt.plot(freq[0:]/10**9, traces_no_background_real[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel(f"Re({s_parameter}) [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, "real.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title("Transmission coefficient")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("T", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, "t_coeff.png")
        

        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title("Phase")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, np.unwrap(phases[i,0:]), linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, "phase.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title("Phase of the subtracted parameter")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, np.unwrap(phase_sub[i,0:]), linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, "phase.png")

        
        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title("Transmission coefficient (dB)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes_dB[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("t (dB)", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, "trasmission_dB.png")

    return [traces_no_background_imag, traces_no_background_complex]









