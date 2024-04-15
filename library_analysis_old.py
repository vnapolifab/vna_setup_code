# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.ndimage import gaussian_filter1d
# from scipy.optimize import curve_fit 
# import json


# def analysisFMR(freq, fields, amplitudes, phases, ref_n = 0):

#     n_traces = len(amplitudes[:,0])
#     n_points = len(freq)
    
#     amp_ref, phase_ref = amplitudes[ref_n], phases[ref_n]
#     phase_ref = unwrap_phase(phase_ref)

#     traces = np.zeros((n_traces, n_points))
#     Ur = np.zeros((n_traces, n_points))

#     # Calculate U
#     for i in range(n_traces):
#         amp, phase = amplitudes[i], phases[i]
#         phase = unwrap_phase(phase)

#         #U = 1j * (np.log((amp * np.exp(1j * phase*0)) / (amp_ref * np.exp(0))) / np.log(amp_ref * np.exp(0)))
#         #U = 1j * (np.log((amp * np.exp(1j * phase)) / (amp_ref * np.exp(1j * phase_ref))) / np.log(amp_ref * np.exp(1j * phase_ref)))
#         U = -1j * (((amp * np.exp(1j * phase)) - (amp_ref * np.exp(1j * phase_ref))) / (amp_ref * np.exp(1j * phase_ref)))
#         U[0] = 0  # First value explodes due to discontinuity
 
#         Ur[i,:] = np.real(U)
#         # amplitudes[i, :] = amp
#         traces[i, :] = np.imag(U)
#         # phases[i, :] = phase

#     Us = Ur+1j*traces

#     # # post-processing   ( removed )
#     # for i in range(n_traces):
#     #     traces_postprocessing[i,:] = gaussian_filter1d(traces[i, :], 6)

#     # Plotting
#     plt.figure(figsize=(15,24))

#     plt.subplot(3,1,1)
#     # plt.title("Imag(U)")
#     for i in range(n_traces): 
#         plt.plot(freq[3:]/10**9, traces[i,3:], linewidth=1.5)
#     plt.legend([str(field) + " mT" for field in fields])
#     plt.ylabel("Imag(U) [arb. u.]", fontsize=16)
#     plt.xlabel("Frequency (GHz)", fontsize=16)
#     plt.xticks(fontsize=16)
#     plt.yticks(fontsize=16)
#     plt.grid()

#     plt.subplot(3,1,2)
#     # plt.title("Re(U)")
#     for i in range(len(traces)): 
#         plt.plot(freq[3:]/10**9, Ur[i,3:], linewidth=1.5)
#     plt.legend([str(field) + " mT" for field in fields])
#     plt.ylabel("Re(U) [arb. u.]", fontsize=16)
#     plt.xlabel("Frequency (GHz)", fontsize=16)
#     plt.xticks(fontsize=16)
#     plt.yticks(fontsize=16)
#     plt.grid()

#     plt.subplot(3,1,3)
#     # plt.title("Trasmission coefficient")
#     for i in range(n_traces): 
#         plt.plot(freq[3:]/10**9, amplitudes[i,3:], linewidth=1.5)
#     plt.legend([str(field) + " mT" for field in fields])
#     plt.ylabel("Transmission coefficient", fontsize=16)
#     plt.xlabel("Frequency (GHz)", fontsize=16)
#     plt.xticks(fontsize=16)
#     plt.yticks(fontsize=16)
#     plt.grid()

#     plt.show()

#     return [traces, Us]



# def analysisKittel(f, traces, fields):

#     f_max = []
#     for trace in traces[1:]:  # excludes reference from peak finder
#         index = np.argmax(trace)
#         f_max.append( f[index] )

#     # f_max = np.concatenate([[190], f_max])

#     # fields[0] = 0

#     popt, pcov = curve_fit(FMR_tang, fields[1:], f_max, 1e6)
#     M_fit = popt[0]

#     print("Fitted value for Ms: " + str(M_fit))

#     plt.figure()
    
#     plt.plot(fields[1:], np.array(f_max)/10**9)
#     plt.plot(fields[1:], FMR_tang(fields[1:], M_fit)/10**9)

#     plt.xlabel("External Field (mT)", fontsize=16);
#     plt.ylabel("Frequency (GHz)", fontsize=16);
#     plt.xticks(fontsize=16);
#     plt.yticks(fontsize=16);

#     plt.legend(["Measurement data", f"Fitted Kittel, Ms={M_fit/10**6:.3}e6 A/m"])
#     plt.grid()

#     plt.show()

#     return f_max, M_fit




# def load_and_convert(filename):
#     matrix = np.genfromtxt(filename, delimiter=",")
#     freq = matrix[:, 0]
#     # amp = 10 ** (matrix[:, 1] / 10)
#     amp = matrix[:, 1]
#     #phase = matrix[:, 2] * np.pi / 180
#     phase = matrix[:, 2]

#     return freq, amp, phase

# def unwrap_phase(phase):
#     phase_unwrapped = np.zeros_like(phase)
#     for i in range(1, len(phase)):
#         phase_unwrapped[i] = phase[i]
#         while phase_unwrapped[i] > phase_unwrapped[i - 1]:
#             phase_unwrapped[i] -= 2 * np.pi
#     return phase_unwrapped


# def calculate_FWHM(freq, data):
#     max_val = np.max(data)
#     max_idx = np.argmax(data)

#     half_max = max_val / 2

#     ind1 = max_idx
#     while data[ind1] > half_max:
#         ind1 -= 1

#     ind2 = max_idx
#     while data[ind2] > data[max_idx] / 2:
#         ind2 += 1

#     fwhm = freq[ind2] - freq[ind1]
#     return fwhm


# def FMR_tang(H0, M):
#     g = 1.7e11
#     mu0 = 4e-7 * np.pi
#     H = H0 * 1e-3 / mu0
#     FMR =  ((g * mu0)/(2*np.pi)) * np.sqrt(H * (H + M))
#     return FMR


# def lorentzian_curve(x, center, fwhm, peak_height):
#     """
#     Generate a Lorentzian curve.

#     Parameters:
#     - x: NumPy array, x-axis values.
#     - center: Center of the Lorentzian curve.
#     - fwhm: Full Width at Half Maximum of the Lorentzian curve.
#     - peak_height: Desired maximum value of the Lorentzian curve.

#     Returns:
#     - NumPy array representing the Lorentzian curve.
#     """
#     A = np.pi*fwhm*peak_height/2
#     lorentzian = (A / np.pi) * (fwhm/2 / ((x - center)**2 + (fwhm/2)**2))  # Lorentzian formula

#     return lorentzian


# def lorentzian_fit(x,y,initial_guess):
#     # popt, pcov = curve_fit(lorentzian_curve, x,y, initial_guess, bounds=([0.75*initial_guess[0], 0, 0], [1.25*initial_guess[0],np.inf , np.inf]))
#     popt, pcov = curve_fit(lorentzian_curve, x,y, initial_guess)
#     [center, fwhm, peak_height] = popt
#     return center, fwhm, peak_height


# def getFWHMFitted(x, curve, peak):
#     # plt.figure()
#     FWHMs = []
#     plt.plot(x, curve)
#     center, width, peak = lorentzian_fit(x, curve, [peak, 0.1*peak, np.max(curve)])
#     # plt.plot(x, curve)
#     plt.plot(x, lorentzian_curve(x, center, width, peak), "--")
#     FWHMs.append(width)

#     return FWHMs


# def load_measurement(user_folder, folder_name):
#     with open(f"DATA/{user_folder}/{folder_name}/measurement_info.json", "r") as f:
#         metadata = json.load(f)
#     field_sweep = metadata["field sweep"]
#     measurement_name = metadata["measurement_name"]
#     amps = []
#     phases = []

#     for i in range(len(field_sweep)):
#         file = f"DATA/{user_folder}/{folder_name}/{measurement_name} ({i+1}).csv"
#         f,a,p = load_and_convert(file)
#         amps.append(a)
#         phases.append(p)
    
#     return np.array(f), np.array(field_sweep), np.array(amps), np.array(phases)


# # TODO cancellare se funziona il codice
# # def analysisFMR_field(freq, fields, amplitudes, phases, ref_n = 0):

# #     n_traces = len(amplitudes[:,0])
# #     n_points = len(freq)
    
# #     amp_ref, phase_ref = amplitudes[ref_n], phases[ref_n]
# #     phase_ref = unwrap_phase(phase_ref)

# #     traces = np.zeros((n_traces, n_points))
# #     Ur = np.zeros((n_traces, n_points))

# #     # Calculate U
# #     for i in range(n_traces):
# #         amp, phase = amplitudes[i], phases[i]
# #         phase = unwrap_phase(phase)

# #         #U = 1j * (np.log((amp * np.exp(1j * phase*0)) / (amp_ref * np.exp(0))) / np.log(amp_ref * np.exp(0)))
# #         #U = 1j * (np.log((amp * np.exp(1j * phase)) / (amp_ref * np.exp(1j * phase_ref))) / np.log(amp_ref * np.exp(1j * phase_ref)))
# #         U = -1j * (((amp * np.exp(1j * phase)) - (amp_ref * np.exp(1j * phase_ref))) / (amp_ref * np.exp(1j * phase_ref)))
# #         # U[0] = 0  # First value explodes due to discontinuity
 
# #         Ur[i,:] = np.real(U)
# #         # amplitudes[i, :] = amp
# #         traces[i, :] = np.imag(U)
# #         # phases[i, :] = phase

# #     Us = Ur+1j*traces

# #     return [traces, Us]