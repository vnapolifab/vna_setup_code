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
    [traces, Us] = analysisFMR_Maria(freq, fields, amplitudes, phases, measurement_path, show_plots=True)  # Plots imag(U), real(U), trasmission
    phase = analysisFMR_MariaPhase(freq, fields, amplitudes, phases, measurement_path, show_plots=True) 

    return(traces, freq, fields,phase)



if __name__ == "__main__":
    print("*** LOG SCREEN ***")

    measurement_path1 = gui_analysis_startup()
    #measurement_path2 = gui_analysis_startup()
    measurement_path3 = gui_analysis_startup()
    measurement_path4 = gui_analysis_startup()
    measurement_path5 = gui_analysis_startup()
    measurement_path6 = gui_analysis_startup()
    #[trace1,freq,fields,phase1] = analysis(measurement_path1)
    #[trace2,freq,fields,phase2] = analysis(measurement_path2)
    [trace3,freq,fields,phase3] = analysis(measurement_path3)
    [trace4,freq,fields,phase4] = analysis(measurement_path4)
    [trace5,freq,fields,phase5] = analysis(measurement_path5)
    [trace6,freq,fields,phase6] = analysis(measurement_path6)



plt.figure()
plt.title("Im(S12)")
#plt.plot(freq[0:], trace1[1,0:]) #zero field
#plt.plot(freq[0:], trace2[1,0:]) #zero field
plt.plot(freq[0:], trace3[1,0:]) #zero field
plt.plot(freq[0:], trace4[1,0:]) #zero field
plt.plot(freq[0:], trace5[1,0:]) #zero field
plt.plot(freq[0:], trace6[1,0:]) #zero field
plt.xlabel("Frequency (GHz)")
plt.ylabel("Im(S12) [arb. u.]")
plt.legend(['3 um', '4 um', '10 um', '15 um'])
plt.show()

plt.figure()
plt.title("Phase")
#plt.plot(freq[0:], phase1[1,0:]) #zero field
#plt.plot(freq[0:], phase2[1,0:]) #zero field
plt.plot(freq[0:], phase3[1,0:]) #zero field
plt.plot(freq[0:], phase4[1,0:]) #zero field
plt.plot(freq[0:], phase5[1,0:]) #zero field
plt.plot(freq[0:], phase6[1,0:]) #zero field
plt.xlabel("Frequency (GHz)")
plt.ylabel("Phase [arb. u.]")
plt.legend(['3 um', '4 um', '10 um', '15 um'])
plt.show()

