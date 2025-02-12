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

def analysisSW(freq: np.ndarray, fields: np.ndarray, amplitudes1: np.ndarray, phases1: np.ndarray, amplitudes2: np.ndarray, phases2: np.ndarray, amplitudes3: np.ndarray, phases3: np.ndarray, amplitudes4: np.ndarray, phases4: np.ndarray, measurement_path: str, Ports: str, ref_n = 0, show_plots=False) -> tuple[np.ndarray, np.ndarray]:
    """
    This function takes as input the frequencies, fields, amplitudes and phases and plots relevant data for FMR resonance.
    ref_n is the index number for the reference measurement, default is zero.
    """

    n_traces = len(amplitudes1[:,0])
    n_points = len(freq)

    # init
    traces_no_background_real1 = np.zeros((n_traces, n_points))
    traces_no_background_imag1 = np.zeros((n_traces, n_points))
    traces_no_background_complex1 = np.zeros((n_traces, n_points), dtype = 'complex')
    amplitudes_no_background1 = np.zeros((n_traces, n_points))
    phase_sub1 = np.zeros((n_traces, n_points))

    traces_no_background_real2 = np.zeros((n_traces, n_points))
    traces_no_background_imag2 = np.zeros((n_traces, n_points))
    traces_no_background_complex2 = np.zeros((n_traces, n_points), dtype = 'complex')
    amplitudes_no_background2 = np.zeros((n_traces, n_points))
    phase_sub2 = np.zeros((n_traces, n_points))

    traces_no_background_real3 = np.zeros((n_traces, n_points))
    traces_no_background_imag3 = np.zeros((n_traces, n_points))
    traces_no_background_complex3 = np.zeros((n_traces, n_points), dtype = 'complex')
    amplitudes_no_background3 = np.zeros((n_traces, n_points))
    phase_sub3 = np.zeros((n_traces, n_points))

    traces_no_background_real4 = np.zeros((n_traces, n_points))
    traces_no_background_imag4 = np.zeros((n_traces, n_points))
    traces_no_background_complex4 = np.zeros((n_traces, n_points), dtype = 'complex')
    amplitudes_no_background4 = np.zeros((n_traces, n_points))
    phase_sub4 = np.zeros((n_traces, n_points))
    
    amp_ref1, phase_ref1 = amplitudes1[ref_n], phases1[ref_n]
    phase_ref1 = np.unwrap(phase_ref1)
    amp_ref2, phase_ref2 = amplitudes2[ref_n], phases2[ref_n]
    phase_ref2 = np.unwrap(phase_ref2)
    amp_ref3, phase_ref3 = amplitudes3[ref_n], phases3[ref_n]
    phase_ref3 = np.unwrap(phase_ref3)
    amp_ref4, phase_ref4 = amplitudes4[ref_n], phases4[ref_n]
    phase_ref4 = np.unwrap(phase_ref4)


    # Signal processing
    for i in range(n_traces):
        amp1, phase1 = amplitudes1[i,:], phases1[i,:]
        phase1 = np.unwrap(phase1)
        amp2, phase2 = amplitudes2[i,:], phases2[i,:]
        phase2 = np.unwrap(phase2)
        amp3, phase3 = amplitudes3[i,:], phases3[i,:]
        phase3 = np.unwrap(phase3)
        amp4, phase4 = amplitudes4[i,:], phases4[i,:]
        phase4 = np.unwrap(phase4)

        #1
        traces_no_background_complex1[i,:] = (amp1 * np.exp(1j * phase1))-(amp_ref1 * np.exp(1j * phase_ref1))
        phase_sub1[i,:] = np.angle(traces_no_background_complex1[i,:])
 
        traces_no_background_real1[i,:] = np.real(traces_no_background_complex1[i,:])
        traces_no_background_imag1[i,:] = np.imag(traces_no_background_complex1[i,:])
        amplitudes_no_background1[i,:] = amplitudes1[i,:] - amp_ref1

        #2
        traces_no_background_complex2[i,:] = (amp2 * np.exp(1j * phase2))-(amp_ref2 * np.exp(1j * phase_ref2))
        phase_sub2[i,:] = np.angle(traces_no_background_complex2[i,:])
 
        traces_no_background_real2[i,:] = np.real(traces_no_background_complex2[i,:])
        traces_no_background_imag2[i,:] = np.imag(traces_no_background_complex2[i,:])
        amplitudes_no_background2[i,:] = amplitudes2[i,:] - amp_ref2

        #3
        traces_no_background_complex3[i,:] = (amp3 * np.exp(1j * phase3))-(amp_ref3 * np.exp(1j * phase_ref3))
        phase_sub3[i,:] = np.angle(traces_no_background_complex3[i,:])
 
        traces_no_background_real3[i,:] = np.real(traces_no_background_complex3[i,:])
        traces_no_background_imag3[i,:] = np.imag(traces_no_background_complex3[i,:])
        amplitudes_no_background3[i,:] = amplitudes3[i,:] - amp_ref3

        #4
        traces_no_background_complex4[i,:] = (amp4 * np.exp(1j * phase4))-(amp_ref4 * np.exp(1j * phase_ref4))
        phase_sub4[i,:] = np.angle(traces_no_background_complex4[i,:])
 
        traces_no_background_real4[i,:] = np.real(traces_no_background_complex4[i,:])
        traces_no_background_imag4[i,:] = np.imag(traces_no_background_complex4[i,:])
        amplitudes_no_background4[i,:] = amplitudes4[i,:] - amp_ref4



    # Init
    amplitudes_dB1 = np.zeros((n_traces, n_points))
    amplitudes_dB2 = np.zeros((n_traces, n_points))
    amplitudes_dB3 = np.zeros((n_traces, n_points))
    amplitudes_dB4 = np.zeros((n_traces, n_points))

    for i in range(n_traces):
        amplitudes_dB1[i,:] = 20*np.log10(amplitudes1[i,:])
        amplitudes_dB2[i,:] = 20*np.log10(amplitudes2[i,:])
        amplitudes_dB3[i,:] = 20*np.log10(amplitudes3[i,:])
        amplitudes_dB4[i,:] = 20*np.log10(amplitudes4[i,:])


    # Plotting
    if (Ports == '12'):
        S1 = 'S11'
        S2 = 'S21'
        S3 = 'S12'
        S4 = 'S22'

    if (Ports == '13'):
        S1 = 'S11'
        S2 = 'S31'
        S3 = 'S13'
        S4 = 'S33'

    if (Ports == '14'):
        S1 = 'S11'
        S2 = 'S41'
        S3 = 'S14'
        S4 = 'S44'

    if (Ports == '23'):
        S1 = 'S22'
        S2 = 'S32'
        S3 = 'S23'
        S4 = 'S33'

    if (Ports == '24'):
        S1 = 'S22'
        S2 = 'S42'
        S3 = 'S24'
        S4 = 'S44'

    if (Ports == '34'):
        S1 = 'S33'
        S2 = 'S43'
        S3 = 'S34'
        S4 = 'S44'


    if show_plots:

        #1
        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title(f"Imaginary part {S1} (subtracted)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, traces_no_background_imag1[i,0:], marker=MARKER, markersize=MARKER_SIZE,linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel(f"Imag() [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"imag_{S1}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Real part {S1} (subtracted)")
        for i in range(len(traces_no_background_real1)): 
            plt.plot(freq[0:]/10**9, traces_no_background_real1[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel(f"Re() [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"real_{S1}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title(f"Amplitude {S1} (lin mag)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes1[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("T", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"amplitude_{S1}.png")
        

        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Unwrapped phase {S1} (RAW)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, np.unwrap(phases1[i,0:]), linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"phase_{S1}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Unwrapped phase {S1} (subtracted)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, np.unwrap(phase_sub1[i,0:]), linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"phase_{S1}.png")

        
        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Amplitude {S1} (dB)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes_dB1[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("t (dB)", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"amplitude_dB_{S1}.png")


        #2
        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title(f"Imaginary part {S2} (subtracted)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, traces_no_background_imag2[i,0:], marker=MARKER, markersize=MARKER_SIZE,linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel(f"Imag() [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"imag_{S2}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Real part {S2} (subtracted)")
        for i in range(len(traces_no_background_real2)): 
            plt.plot(freq[0:]/10**9, traces_no_background_real2[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel(f"Re() [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"real_{S2}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title(f"Amplitude {S2} (lin mag)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes2[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("T", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"amplitude_{S2}.png")
        

        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Unwrapped phase {S2} (RAW)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, np.unwrap(phases2[i,0:]), linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"phase_{S2}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Unwrapped phase {S2} (subtracted)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, np.unwrap(phase_sub2[i,0:]), linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"phase_{S2}.png")

        
        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Amplitude {S2} (dB)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes_dB2[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("t (dB)", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"amplitude_dB_{S2}.png")



        #3
        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title(f"Imaginary part {S3} (subtracted)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, traces_no_background_imag3[i,0:], marker=MARKER, markersize=MARKER_SIZE,linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel(f"Imag() [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"imag_{S3}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Real part {S3} (subtracted)")
        for i in range(len(traces_no_background_real3)): 
            plt.plot(freq[0:]/10**9, traces_no_background_real3[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel(f"Re() [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"real_{S3}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title(f"Amplitude {S3} (lin mag)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes3[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("T", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"amplitude_{S3}.png")
        

        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Unwrapped phase {S3} (RAW)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, np.unwrap(phases3[i,0:]), linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"phase_{S3}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Unwrapped phase {S3} (subtracted)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, np.unwrap(phase_sub3[i,0:]), linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"phase_{S3}.png")

        
        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Amplitude {S3} (dB)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes_dB3[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("t (dB)", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"amplitude_dB_{S3}.png")



        #4
        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title(f"Imaginary part {S4} (subtracted)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, traces_no_background_imag4[i,0:], marker=MARKER, markersize=MARKER_SIZE,linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel(f"Imag() [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"imag_{S4}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Real part {S4} (subtracted)")
        for i in range(len(traces_no_background_real4)): 
            plt.plot(freq[0:]/10**9, traces_no_background_real4[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel(f"Re() [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"real_{S4}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title(f"Amplitude {S4} (lin mag)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes4[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("T", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"amplitude_{S4}.png")
        

        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Unwrapped phase {S4} (RAW)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, np.unwrap(phases4[i,0:]), linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"phase_{S4}.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Unwrapped phase {S4} (subtracted)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, np.unwrap(phase_sub4[i,0:]), linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"phase_{S4}.png")

        
        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title(f"Amplitude {S4} (dB)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes_dB4[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("t (dB)", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        save_plot(measurement_path, f"amplitude_dB_{S4}.png")

    return 









