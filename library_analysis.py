import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import curve_fit 
import json
from itertools import cycle

from library_misc import *
from CONSTANTS import *

"""
This library containsfunctions used for the analysis of measurement results.
In this file functions are modified to be compatible with the gui.
"""


def analysisFMR(freq: np.ndarray, fields: np.ndarray, amplitudes: np.ndarray, phases: np.ndarray, user_folder: str, sample_folder: str, measurement_folder: str, ref_n = 0, show_plots=True) -> tuple[np.ndarray, np.ndarray]:
    """
    This function takes as input the frequencies, fields, amplitudes and phases and plots relevant data for FMR resonance.
    ref_n is the index number for the reference measurement, default is zero.
    """

    n_traces = len(amplitudes[:,0])
    n_points = len(freq)
    
    amp_ref, phase_ref = amplitudes[ref_n], phases[ref_n]
    phase_ref = unwrap_phase(phase_ref)

    traces = np.zeros((n_traces, n_points))
    Ur = np.zeros((n_traces, n_points))

    # Calculate U
    for i in range(n_traces):
        amp, phase = amplitudes[i], phases[i]
        phase = unwrap_phase(phase)

        #U = 1j * (np.log((amp * np.exp(1j * phase*0)) / (amp_ref * np.exp(0))) / np.log(amp_ref * np.exp(0)))
        #U = 1j * (np.log((amp * np.exp(1j * phase)) / (amp_ref * np.exp(1j * phase_ref))) / np.log(amp_ref * np.exp(1j * phase_ref)))
        U = -1j * (((amp * np.exp(1j * phase)) - (amp_ref * np.exp(1j * phase_ref))) / (amp_ref * np.exp(1j * phase_ref)))
        #U = (((amp) - (amp_ref)) / (amp_ref ))
        # U[0] = 0  # First value explodes due to discontinuity
 
        Ur[i,:] = np.real(U)
        # amplitudes[i, :] = amp
        traces[i, :] = np.imag(U)
        phases[i, :] = phase

    Us = Ur+1j*traces

    # # post-processing   ( removed )
    # for i in range(n_traces):
    #     traces_postprocessing[i,:] = gaussian_filter1d(traces[i, :], 6)


    # Plottavamo [3:] per esclusdere i primi tre punti. Perchè? ora invece con [0:] funziona


    # Plotting
    if show_plots:

        plt.figure( figsize=(FULLSCREEN_SIZE) )
        plt.title("Imag(U)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, traces[i,0:],linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Imag(U) [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\imag_u.png")



        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title("Real(U)")
        for i in range(len(traces)): 
            plt.plot(freq[0:]/10**9, Ur[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Re(U) [arb. u.]", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\real_u.png")

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
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\t_coeff.png")
        

        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title("Phase")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, phases[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\phase.png")

    return traces, Us



def analysisKittel(freq: np.ndarray, traces: np.ndarray, fields: np.ndarray, user_folder: str, sample_folder: str, measurement_folder: object) -> tuple[np.ndarray, np.ndarray]:
    """
    This function takes as input traces and fields and estimates Ms from a fit of the Kittel function.
    Returns frequencies of the FMR peaks and the Ms.
    """

    f_max = []
    for trace in traces[1:]:  # excludes reference from peak finder
        index = np.argmax(trace)
        f_max.append( freq[index] )

    fields = fields[1:]  # drop reference field

    add_zero = False
    if add_zero:
        f_max = np.concatenate([[0], f_max])
        fields = np.concatenate([[0], fields])
        

    popt, pcov = curve_fit(FMR_tang, fields, f_max, 1e6)
    M_fit = popt[0]

    print("Fitted value for Ms: " + str(M_fit))

    plt.figure( figsize=(FULLSCREEN_SIZE) )
    
    plt.plot(fields, np.array(f_max)/10**9)
    plt.plot(fields, FMR_tang(fields, M_fit)/10**9)

    plt.xlabel("External Field (mT)", fontsize=AXIS_FONTSIZE);
    plt.ylabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE);
    plt.xticks(fontsize=AXIS_FONTSIZE);
    plt.yticks(fontsize=AXIS_FONTSIZE);

    plt.legend(["Measurement data", f"Fitted Kittel, Ms={M_fit/10**6:.3}e6 A/m"])
    plt.grid()
    plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\Fitted Kittel.png")

    return f_max, M_fit


def analysisDamping(freqs: np.ndarray, fields: np.ndarray, u_freq_sweep: np.ndarray, user_folder: str, sample_folder: str, measurement_folder: str, show_plots=True) -> None:
    fields_no_ref = fields[1:]
    n_freq_points = u_freq_sweep.shape[1] 

    # Defines u_field_sweep: rows are field dependent, columns frequency dependent
    u_field_sweep = np.transpose(u_freq_sweep[1:, :])  # [1:, :] to exclude first freq sweep (reference)
    n_field_points = u_field_sweep.shape[1]


    # Defines field_peaks: array with fields corrisponding to the maximum of u_field_sweep
    field_peaks = np.zeros(shape=(n_freq_points, ))
    for i in range(n_freq_points):
        field_peaks[i] = fields_no_ref[ np.argmax(u_field_sweep[i,:]) ]


    # U must be used or the fit won't work ----> la Lorentziana usata per fittare ha fondo nullo, se non normalizzi riportando il fondo a zero (come si fa nel calcolo di U) la curva non fitta
    g, mu0  = 1.76e11, 4e-7*np.pi
    conversion = 795.7747  # the field needs to be transformed in A/m before being used

    alpha, alpha_raw, FWHMs = np.zeros([n_freq_points,]), np.zeros([n_freq_points,]), np.zeros([n_freq_points,])

    colors = cycle([
        '#1f77b4',  # blue
        '#ff7f0e',  # orange
        '#2ca02c',  # green
        '#d62728',  # red
        '#9467bd',  # purple
        '#8c564b',  # brown
        '#e377c2',  # pink
        '#7f7f7f',  # gray
        '#bcbd22',  # lime green-yellow
        '#17becf'   # cyan-teal
    ])


    # Plot U as a function of H for fixed frequencies
    if show_plots:
        plt.figure( figsize=(FULLSCREEN_SIZE) )

        for n in range(n_freq_points):
            plt.plot(fields_no_ref, u_field_sweep[n,:], marker=MARKER, markersize=MARKER_SIZE)
        
        plt.legend([ f"{f/10**9:.2f} GHz" for f in freqs ])
        plt.title("Raw data")
        plt.xlabel("External Field (mT)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Suscettivity (arb. u.)", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\Raw data.png")



    # 
    # ===== CODE TO FIT DATA AND REMOVE BACKGROUND =====
    # 

    plt.figure( figsize=(FULLSCREEN_SIZE) )
    backgrounds = np.zeros([n_freq_points, n_field_points])
    center = np.zeros(n_freq_points)
    width = np.zeros(n_freq_points)
    peak = np.zeros(n_freq_points)


    #Useful to create the legend of the fitted spectra with the background present
    j = 0
    i = 0
    frequencies_tri = [0]*3*len(freqs)

    for i in range(n_freq_points):
        frequencies_tri[j] = freqs[i]
        frequencies_tri[j+1] = freqs[i]
        frequencies_tri[j+2] = freqs[i]
        j = j+3



    for i in range(n_freq_points):


        if DEBUG_MODE:
               
            center[i], width[i], peak[i], a, b, x1, x2, m = lorentzian_fit(fields_no_ref, u_field_sweep[i,:], [field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:])])
            x = fields_no_ref
            background = a*(x < x1) + b*(x > x2) + ((x >= x1) & (x < x2)) * (a +(b-a)* (x-(x1))/(x2-x1)) + m*x

            backgrounds[i,:] = background
            
            # # --- DOUBLE FIT (two fits, one for background subtraction and then a new lorentian fit without background)
            #center, width, peak, center2, width2, peak2,a, b, x1, x2 = multi_lorentzian_fit(fields_no_ref, u_field_sweep[i,:], [field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:]), 1.1*field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:])/2])





            # alpha_raw[i] = conversion*(width*g*mu0)/(4*np.pi*freqs[i])
            # print(f"{freqs[i]/10**9:.2f}) Alpha from raw data: {alpha_raw[i]:.5f}")
        
            # center, width, peak, a, b, x1, x2 = lorentzian_fit(fields_no_ref, u_field_sweep[i,:], [field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:])], remove_background=True)
            # trace_no_background = u_field_sweep[i,:] - getLinearBackground(fields_no_ref, a, b, x1, x2)
            # center, width, peak = lorentzian_fit(fields_no_ref, trace_no_background, [field_peaks[i], 0.1*field_peaks[i], np.max(trace_no_background)])
            # # ---


            # --- PEAK + SHOULDER FIT
            # center, width, peak= lorentzian_fit(fields_no_ref, u_field_sweep[i,:], [field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:])])
            # alpha_raw[i] = conversion*(width*g*mu0)/(4*np.pi*freqs[i])
            # print(f"{freqs[i]/10**9:.2f}) Alpha from raw data: {alpha_raw[i]:.5f}")
        
            # center, width, peak, center2, width2, peak2, a, b, x1, x2 = double_lorentzian_fit(fields_no_ref, u_field_sweep[i,:], [field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:]), 1.1*field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:])/2], remove_background=True)
            # trace_no_background = u_field_sweep[i,:] - getLinearBackground(fields_no_ref, a, b, x1, x2)
                
            # center, width, peak = lorentzian_fit(fields_no_ref, u_field_sweep[i,:], initial_guess = [field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:])])
            # alpha_raw[i] = conversion*(width*g*mu0)/(4*np.pi*freqs[i])
            # print(f"{freqs[i]/10**9:.2f}) Alpha from raw data: {alpha_raw[i]:.5f}")
        
            # center, width, peak, a, b, x1, x2 = lorentzian_fit(fields_no_ref, u_field_sweep[i,:], [field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:])], remove_background=True)
            # trace_no_background = u_field_sweep[i,:] - getLinearBackground(fields_no_ref, a, b, x1, x2)
            # center, width, peak, center2, width2, peak2 = double_lorentzian_fit(fields_no_ref, trace_no_background, [field_peaks[i], 0.1*field_peaks[i], np.max(trace_no_background), 1.1*field_peaks[i], 0.1*field_peaks[i], np.max(trace_no_background)/2])
            # # center, width, peak, a, b, x1, x2 = lorentzian_fit(fields_no_ref, u_field_sweep[i,:], [field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:])], remove_background=True)
            # # ---



            FWHMs[i] = width[i]
            alpha[i] = conversion*(width[i]*g*mu0)/(4*np.pi*freqs[i])
            
            print(f"Frequency: {freqs[i]/10**9:.2f}) Alpha: {alpha[i]:.5f}\n") 


            # # PLOTS
            c = next(colors)
            plt.plot(fields_no_ref, u_field_sweep[i,:], marker=MARKER, markersize=MARKER_SIZE, color=c)
            plt.plot(fields_no_ref, lorentzian_curve(fields_no_ref, center[i], width[i], peak[i], a, b, x1, x2, m), "-.", color=c)
            plt.plot(fields_no_ref, background, "--", color=c)
            

            #plt.plot(fields_no_ref, multi_lorentzian_curve(fields_no_ref, center, center2, width, width2, peak, peak2, a, b, x1, x2), "-.", color=c)
            # plt.plot(fields_no_ref, lorentzian_curve(fields_no_ref, center2, width2, peak2), "--", color=c)
            # plt.plot(fields_no_ref, lorentzian_curve(fields_no_ref, center, width, peak)+lorentzian_curve(fields_no_ref, center2, width2, peak2), "--", color=c)
           
            # da aggiungere la legenda
            plt.title("Fitted data (with background)")
            plt.legend([ f"{f/10**9:.2f} GHz" for f in frequencies_tri ])
            plt.xlabel("External Field (mT)", fontsize=AXIS_FONTSIZE)
            plt.ylabel("Suscettivity (arb. u.)", fontsize=AXIS_FONTSIZE)
            plt.xticks(fontsize=AXIS_FONTSIZE)
            plt.yticks(fontsize=AXIS_FONTSIZE)
            plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\Fitted data (with background).png")

    plt.grid()



    colors = cycle([
        '#1f77b4',  # blue
        '#ff7f0e',  # orange
        '#2ca02c',  # green
        '#d62728',  # red
        '#9467bd',  # purple
        '#8c564b',  # brown
        '#e377c2',  # pink
        '#7f7f7f',  # gray
        '#bcbd22',  # lime green-yellow
        '#17becf'   # cyan-teal
    ])

    # New figure with the background subtracted peaks 
    plt.figure( figsize=(FULLSCREEN_SIZE) )

    for i in range(n_freq_points):

        # center, width, peak, a, b, x1, x2, x = lorentzian_fit(fields_no_ref, u_field_sweep[i,:], [field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:])])
        # #center, width, peak, center2, width2, peak2,a, b, x1, x2 = multi_lorentzian_fit(fields_no_ref, u_field_sweep[i,:], [field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:]), 1.1*field_peaks[i], 0.1*field_peaks[i], np.max(u_field_sweep[i,:])/2])
        # x = fields_no_ref
        # background = a*(x < x1) + b*(x > x2) + ((x >= x1) & (x < x2)) * (a +(b-a)* (x-(x1))/(x2-x1)) + m*x

        c = next(colors)
        #plt.plot(fields_no_ref, multi_lorentzian_curve(fields_no_ref, center, center2, width, width2, peak, peak2, a, b, x1, x2)-background, "-", color=c)
        #plt.plot(fields_no_ref, lorentzian_curve(fields_no_ref, center[i], width[i], peak[i], a, b, x1, x2, m)-backgrounds[i,:], "--", color=c)
        plt.plot(fields_no_ref, u_field_sweep[i,:]-backgrounds[i,:], marker=MARKER, markersize=MARKER_SIZE, color=c)
        
        # da aggiungere la legenda
        plt.title("Fitted data (background removed)")
        plt.legend([ f"{f/10**9:.2f} GHz" for f in freqs ])
        plt.xlabel("External Field (mT)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Suscettivity (arb. u.)", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\Fitted data (background removed).png")
        plt.grid()


    # Other plots

    #Get alpha from linear fit of FWHMs vs f
    #TODO understand if it was implemented properely or not: differs in excess by a factor 2 with respect to the alpha obtained by Lorentzian fit
    [alpha_slope,inhomog] = linear_fit(freqs,FWHMs,[0,0])
    alpha_slope_array = np.zeros(len(freqs))
    print(f"Inhomogeneous broadening: {inhomog:.5f}\n") 

    # for i in range(len(freqs)):
    #     alpha_slope_array[i] = line_curve(freqs[i],alpha_slope,inhomog)*g/(2*np.pi*freqs[i]*conversion)
    #     print(f"Frequency: {freqs[i]/10**9:.2f}) Alpha from slope: {alpha_slope_array[i]:.5f}\n") 



    # plt.figure( figsize=(FULLSCREEN_SIZE) )
    # plt.plot(freqs/1e9, FWHMs, marker=MARKER, markersize=MARKER_SIZE)
    # plt.plot(freqs/1e9, line_curve(freqs,alpha_slope,inhomog), marker=MARKER, markersize=MARKER_SIZE)
    # plt.title("$\\Delta$H vs f")
    # plt.xlabel("f (GHz)", fontsize=AXIS_FONTSIZE)
    # plt.ylabel("$\\Delta$H (mT)", fontsize=AXIS_FONTSIZE)
    # plt.xticks(fontsize=AXIS_FONTSIZE)
    # plt.yticks(fontsize=AXIS_FONTSIZE)
    # plt.grid()
    # plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\Delta H vs f.png")


    plt.figure( figsize=(FULLSCREEN_SIZE) )
    plt.plot(field_peaks, FWHMs, marker=MARKER, markersize=MARKER_SIZE)
    plt.title("$\\Delta$H vs H")
    plt.xlabel("External Field (mT)", fontsize=AXIS_FONTSIZE)
    plt.ylabel("FWHM (mT)", fontsize=AXIS_FONTSIZE)
    plt.xticks(fontsize=AXIS_FONTSIZE)
    plt.yticks(fontsize=AXIS_FONTSIZE)
    plt.grid()
    plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\Delta H vs H.png")


    plt.figure( figsize=(FULLSCREEN_SIZE) )
    plt.plot(freqs/1e9, field_peaks, marker=MARKER, markersize=MARKER_SIZE)
    plt.title("Hr vs f")
    plt.xlabel("f (Hz)", fontsize=AXIS_FONTSIZE)
    plt.ylabel("Hr (mT)", fontsize=AXIS_FONTSIZE)
    plt.xticks(fontsize=AXIS_FONTSIZE)
    plt.yticks(fontsize=AXIS_FONTSIZE)
    plt.grid()
    plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\Hr vs f.png")


    # print("\n*** Averaged data: ***")
    # print(f"Alpha from raw data: {np.average(alpha_raw):.5f}")
    # print(f"Alpha from background removal: {np.average(alpha):.5f}")



# *******************



def analysisSW(freq: np.ndarray, fields: np.ndarray, amplitudes: np.ndarray, phases: np.ndarray, user_folder: str, sample_folder: str, measurement_folder: str, s_parameter: str, ref_n = 0, show_plots=True) -> tuple[np.ndarray, np.ndarray]:
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
    
    amp_ref, phase_ref = amplitudes[ref_n], phases[ref_n]
    phase_ref = unwrap_phase(phase_ref)

    # Signal processing
    for i in range(n_traces):
        amp, phase = amplitudes[i,:], phases[i,:]
        phase = unwrap_phase(phase)

        traces_no_background_complex[i,:] = amp * np.exp(1j * phase) - amp_ref * np.exp(1j * phase_ref)
 
        traces_no_background_real[i,:] = np.real(traces_no_background_complex[i,:])
        traces_no_background_imag[i,:] = np.imag(traces_no_background_complex[i,:])
        amplitudes_no_background[i,:] = amplitudes[i,:] - amp_ref

    # Init
    amplitudes_dB = np.zeros((n_traces, n_points))
    amplitudes_dB_no_background = np.zeros((n_traces, n_points))

    for i in range(n_traces):
        amplitudes_dB[i,:] = 20*np.log10(amplitudes[i,:])
        amplitudes_dB_no_background[i,:] = 20*np.log10(amplitudes_no_background[i,:])


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
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\imag.png")


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
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\real.png")


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
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\t_coeff.png")
        

        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title("Phase")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, phases[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("Phase", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\phase.png")

        
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
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\trasmission_dB.png")


        plt.figure( figsize=(FULLSCREEN_SIZE) ) 
        plt.title("Transmission coefficient no background (dB)")
        for i in range(n_traces): 
            plt.plot(freq[0:]/10**9, amplitudes_dB_no_background[i,0:], linewidth=1.5)
        plt.legend([f"{f} mT" for f in fields])
        plt.xlabel("Frequency (GHz)", fontsize=AXIS_FONTSIZE)
        plt.ylabel("t (dB)", fontsize=AXIS_FONTSIZE)
        plt.xticks(fontsize=AXIS_FONTSIZE)
        plt.yticks(fontsize=AXIS_FONTSIZE)
        plt.grid()
        plt.savefig(f"{DATA_FOLDER_NAME}\\{user_folder}\\{sample_folder}\\{measurement_folder}\\trasmission_dB_no_background.png")

    return [traces_no_background_imag, traces_no_background_complex]



# ********************



def unwrap_phase(phase):
    """
    Takes phase as input and removes jumps from +pi to -pi that are generated by default in the VNA data.
    """
    phase_unwrapped = np.zeros_like(phase)
    for i in range(1, len(phase)):
        phase_unwrapped[i] = phase[i]
        while phase_unwrapped[i] > phase_unwrapped[i - 1]:
            phase_unwrapped[i] -= 2 * np.pi
    return phase_unwrapped


def calculate_FWHM(freq, data):
    """
    Calulcates FWHM of a trace with no fit, just calculating the distance between midpoints. 
    """
    
    max_val = np.max(data)
    max_idx = np.argmax(data)

    half_max = max_val / 2

    ind1 = max_idx
    while data[ind1] > half_max:
        ind1 -= 1

    ind2 = max_idx
    while data[ind2] > data[max_idx] / 2:
        ind2 += 1

    fwhm = freq[ind2] - freq[ind1]
    return fwhm


def FMR_tang(H0, M):
    """
    Calculates the ideal Kittel relation.
    Takes as input the external field and the saturation magnetization.
    """

    g, mu0  = 1.76e11, 4e-7*np.pi
    H = H0 * 1e-3 / mu0
    FMR =  ((g * mu0)/(2*np.pi)) * np.sqrt(H * (H + M))
    return FMR


def lorentzian_curve(x, center, fwhm, peak_height, a=0, b=0, x1=0, x2=1, m=0):
    """
    Generates a Lorentzian curve.
    """

    A = np.pi*fwhm*peak_height/2
    lorentzian =  (A / np.pi) * (fwhm/2 / ((x - center)**2 + (fwhm/2)**2))  # Lorentzian formula 

    dx = fwhm/2 *3
    background = getLinearBackground(x, a, b, x1, x2)
    # a*(x < center-dx) + b*(x > center+dx) + ((x >= center-dx) & (x < center+dx)) * (a +(b-a)* (x-(center-dx))/(2*dx))  # TODO cancellare se il codice funziona

    return lorentzian + background + m*x


def multi_lorentzian_curve(x, center1, center2, fwhm1, fwhm2, peak_height1, peak_height2, a=0, b=0, x1=0, x2=1):
    """
    Generates a Lorentzian curve.
    """

    A1 = np.pi*fwhm1*peak_height1/2
    lorentzian1 =  (A1 / np.pi) * (fwhm1/2 / ((x - center1)**2 + (fwhm1/2)**2))  # Lorentzian formula 

    A2 = np.pi*fwhm2*peak_height2/2
    lorentzian2 =  (A2 / np.pi) * (fwhm2/2 / ((x - center2)**2 + (fwhm2/2)**2))  # Lorentzian formula 

    #dx = fwhm/2 *3
    background = getLinearBackground(x, a, b, x1, x2)
    # a*(x < center-dx) + b*(x > center+dx) + ((x >= center-dx) & (x < center+dx)) * (a +(b-a)* (x-(center-dx))/(2*dx))  # TODO cancellare se il codice funziona

    return lorentzian1 + lorentzian2 + background


def getLinearBackground(x, a, b, x1, x2):
    return a*(x < x1) + b*(x > x2) + ((x >= x1) & (x < x2)) * (a +(b-a)* (x-(x1))/(x2-x1))


def lorentzian_fit(x,y,initial_guess):
    """
    Fits data with a lorentian ,used for more accurate FWHM calculations.
    """

    # popt, pcov = curve_fit(lorentzian_curve, x,y, initial_guess, bounds=([0.75*initial_guess[0], 0, 0], [1.25*initial_guess[0],np.inf , np.inf]))
    try:
        popt, pcov = curve_fit(lorentzian_curve, x,y, initial_guess + [0, 0, initial_guess[0]-initial_guess[1], initial_guess[0]+initial_guess[1], 0], bounds = ([0,0,0,-np.inf,-np.inf,-np.inf,0,-np.inf], [np.inf,np.inf,np.inf,np.inf,np.inf,np.inf,np.inf, np.inf]))
        [center, fwhm, peak_height, a, b, x1, x2, m] = popt
        return center, fwhm, peak_height, a, b, x1, x2, m
        
    except:  # TODO specificare l'eccezione giusta, questo deve venire riportato se non trova la giusta interpolazione
        return float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan")
       

def multi_lorentzian_fit(x,y,initial_guess):
    """
    Fits data with a lorentian ,used for more accurate FWHM calculations.
    """

    # popt, pcov = curve_fit(lorentzian_curve, x,y, initial_guess, bounds=([0.75*initial_guess[0], 0, 0], [1.25*initial_guess[0],np.inf , np.inf]))
    try:
        popt, pcov = curve_fit(multi_lorentzian_curve, x,y, initial_guess + [0, 0, x[0], x[-1]])
        [center, fwhm, peak_height, center2, fwhm2, peak_height2] = popt
        return center, fwhm, peak_height, center2, fwhm2, peak_height2
        
    except:  # TODO specificare l'eccezione giusta, questo deve venire riportato se non trova la giusta interpolazione
        return float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan")
        


def double_lorentzian_fit(x,y,initial_guess, remove_background=False):
    """
    Fits data with two lorentians ,used for more accurate FWHM calculations.
    """

    # popt, pcov = curve_fit(lorentzian_curve, x,y, initial_guess, bounds=([0.75*initial_guess[0], 0, 0], [1.25*initial_guess[0],np.inf , np.inf]))
    

    try:
        if not(remove_background):
            popt, pcov = curve_fit(double_lorentzian_curve_no_background, x,y, initial_guess, bounds=(0, np.inf))
            [center, fwhm, peak_height, center2, fwhm2, peak_height2] = popt
            return center, fwhm, peak_height, center2, fwhm2, peak_height2
        else:
            popt, pcov = curve_fit(double_lorentzian_curve, x,y, initial_guess + [0, 0, x[0], x[-1]], bounds=(0, np.inf))
            [center, fwhm, peak_height, center2, fwhm2, peak_height2, a, b, x1, x2] = popt
            return center, fwhm, peak_height, center2, fwhm2, peak_height2, a, b, x1, x2
        

    except:  # TODO specificare l'eccezione giusta, questo deve venire riportato se non trova la giusta interpolazione
        if not(remove_background):
            return float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan")
        else:
            return float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"), float("nan")


def double_lorentzian_curve_no_background(x, center_1, fwhm_1, peak_height_1, center_2, fwhm_2, peak_height_2):
    """
    Generate a Lorentzian curve.

    Parameters:
    - x: NumPy array, x-axis values.
    - center: Center of the Lorentzian curve.
    - fwhm: Full Width at Half Maximum of the Lorentzian curve.
    - peak_height: Desired maximum value of the Lorentzian curve.

    Returns:
    - NumPy array representing the Lorentzian curve.
    """
    A_1 = np.pi*fwhm_1*peak_height_1/2
    lorentzian1 = (A_1 / np.pi) * (fwhm_1/2 / ((x - center_1)**2 + (fwhm_1/2)**2))  # Lorentzian formula
    
    A_2 = np.pi*fwhm_2*peak_height_2/2
    lorentzian2 = (A_2 / np.pi) * (fwhm_2/2 / ((x - center_2)**2 + (fwhm_2/2)**2))  # Lorentzian formula

    lorentzian = lorentzian1 + lorentzian2

    return lorentzian


def double_lorentzian_curve(x, center_1, fwhm_1, peak_height_1, center_2, fwhm_2, peak_height_2, a, b, x1, x2):
    """
    Generate a Lorentzian curve.

    Parameters:
    - x: NumPy array, x-axis values.
    - center: Center of the Lorentzian curve.
    - fwhm: Full Width at Half Maximum of the Lorentzian curve.
    - peak_height: Desired maximum value of the Lorentzian curve.

    Returns:
    - NumPy array representing the Lorentzian curve.
    """
    A_1 = np.pi*fwhm_1*peak_height_1/2
    lorentzian1 = (A_1 / np.pi) * (fwhm_1/2 / ((x - center_1)**2 + (fwhm_1/2)**2))  # Lorentzian formula
    
    A_2 = np.pi*fwhm_2*peak_height_2/2
    lorentzian2 = (A_2 / np.pi) * (fwhm_2/2 / ((x - center_2)**2 + (fwhm_2/2)**2))  # Lorentzian formula

    background = getLinearBackground(x, a, b, x1, x2)

    lorentzian = lorentzian1 + lorentzian2 + background

    return lorentzian


def linear_fit(x,y,initial_guess):
    """
    Fits data with a linear curve.
    """
    
    try:
        popt, pcov = curve_fit(line_curve, x, y, initial_guess, bounds = ([0,0], [np.inf,np.inf]))
        [a,b] = popt
        return a, b
        
    except:  # TODO specificare l'eccezione giusta, questo deve venire riportato se non trova la giusta interpolazione
        return float("nan"), float("nan")
    

def line_curve(x, a=0, b=0):
    """
    Generates a line curve.
    """
    line =  a*x+b

    return line