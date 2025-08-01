# Import necessary libraries and modules
from library_analysis import *  # Custom library for analysis functions
from library_power_supply import *  # Custom library for power supply control
from library_misc import *  # Custom library for miscellaneous functions
import numpy as np  # Numpy for numerical operations
from time import sleep  # Sleep function for time delays
import json  # JSON library for parsing and handling JSON data
from RsInstrument.RsInstrument import RsInstrument  # RsInstrument library for instrument control

"""
This file contains necessary functions to control and operate the Vector Network Analyzer (VNA).
"""


def setupConnectionVNA(give_additional_info: bool = False) -> RsInstrument:
    """
    Connects to the VNA using different possible connection types.
    Returns an RsInstrument object that contains methods to control the VNA.
    
    Args:
    - give_additional_info (bool): Whether to print additional information about the VNA.
    
    Returns:
    - instr (RsInstrument): The connected instrument object to interact with the VNA.
    """
    # Define possible connection strings for the VNA
    resource_string_1 = 'TCPIP::192.168.2.101::INSTR'  # Standard LAN connection (VXI-11)
    resource_string_2 = 'TCPIP::192.168.2.101::hislip0'  # Hi-Speed LAN connection (alternative)
    resource_string_3 = 'GPIB::20::INSTR'  # GPIB Connection, currently in use
    resource_string_4 = 'USB::0x0AAD::0x0119::022019943::INSTR'  # USB-TMC (Test and Measurement Class)
    resource_string_5 = 'RSNRP::0x0095::104015::INSTR'  # R&S Powersensor NRP-Z86 (not used here)

    # Create an RsInstrument object to connect to the VNA via GPIB
    instr = RsInstrument(resource_string_3, True, False)

    # Query the instrument for its identification string
    idn = instr.query_str('*IDN?')
    print("VNA connected correctly via GPIB")
    
    # Reset the VNA to a default state
    instr.write(f'*RST')
    
    # Delete any existing traces on the VNA
    instr.write("CALC1:PAR:DEL 'Trc1'")

    # Optionally print additional details about the VNA
    if give_additional_info:
        print(f"\nHello, I am: '{idn}'")
        print(f'RsInstrument driver version: {instr.driver_version}')
        print(f'Instrument full name: {instr.full_instrument_model_name}')
        print(f'Instrument installed options: {",".join(instr.instrument_options)}')

    # Return the instrument object for further communication
    return instr


def applySettings(instr: RsInstrument, settings: object) -> None:
    """
    Applies settings from the provided dictionary to the VNA instrument.
    These settings include frequency range, bandwidth, power, number of points, and calibration file.
    
    Args:
    - instr (RsInstrument): The instrument object to which settings will be applied.
    - settings (dict): Dictionary containing the settings to be applied.
    """
    # Set the start frequency for the measurement
    instr.write("SENS1:FREQ:STAR " + f"{settings['start_frequency']}")  # Example: 1e9 for 1 GHz

    # Set the stop frequency for the measurement
    instr.write("SENS1:FREQ:STOP " + f"{settings['stop_frequency']}")  # Example: 2e9 for 2 GHz

    # Set the bandwidth for the measurement
    instr.write("SENS1:BAND " + f"{settings['bandwidth']}")  # Example: 1000 for 1 kHz bandwidth

    # Set the power level for the VNA output
    instr.write("SOUR1:POW " + f"{settings['power']}")  # Example: -10 for -10 dBm output power

    # Set the number of measurement points in the sweep
    instr.write("SENS1:SWE:POIN " + f"{settings['number_of_points']}")  # Example: 201 for 201 points

    # Load the calibration file
    instr.write_str(":MMEMORY:LOAD:CORRection 1, " + f"'{settings['cal_name']}.cal'")  # Calibration file name
    
    # Estimate the timeout based on the bandwidth and number of points (the estimation follows an arbitrary empirical formula)
    instr.visa_timeout = (settings['bandwidth']**-1 * settings['number_of_points'] * 10) * 1000 + 100



def measure_amp_and_phase(instr: RsInstrument, Ports: str, i = 0, avg = 1) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Measures amplitude and phase for multiple S-parameters and handles averaging.
    
    Args:
    - instr (RsInstrument): The instrument object for communication with the VNA.
    - Ports (str): A string representing the port configuration (e.g., '12' for S11, S21, etc.).
    - i (int): Optional parameter for iteration (default is 0).
    - avg (int): Number of measurements on which an average is performed (default is 1).
    
    Returns:
    - tuple: Frequency, real and imaginary parts for the S-parameters.
    """
    # If this is not the first iteration, delete existing traces
    if (i > 0):
        instr.write("CALC1:PAR:DEL 'Tr1'")
        instr.write("CALC1:PAR:DEL 'Tr2'")
        instr.write("CALC1:PAR:DEL 'Tr3'")
        instr.write("CALC1:PAR:DEL 'Tr4'")


    # Set up the S-parameters and assign them to traces based on Ports input
    if (Ports == '12'):

        instr.write("CALC1:PAR:SDEF 'Tr1', 'S11AVG'")
        instr.write(f'DISP:WIND1:STAT ON') 
        instr.write(f"DISP:WIND1:TRAC1:FEED 'Tr1'") 

        instr.write("CALC1:PAR:SDEF 'Tr2', 'S21AVG'")
        instr.write(f'DISP:WIND2:STAT ON') 
        instr.write(f'DISP:WIND2:TRAC2:FEED "Tr2"') 

        instr.write("CALC1:PAR:SDEF 'Tr3', 'S12AVG'")
        instr.write(f'DISP:WIND3:STAT ON') 
        instr.write(f'DISP:WIND3:TRAC3:FEED "Tr3"') 

        instr.write("CALC1:PAR:SDEF 'Tr4', 'S22AVG'")
        instr.write(f'DISP:WIND4:STAT ON') 
        instr.write(f'DISP:WIND4:TRAC4:FEED "Tr4"') 


    if (Ports == '13'):

        instr.write("CALC1:PAR:SDEF 'Tr1', 'S11AVG'")
        instr.write(f'DISP:WIND1:STAT ON') 
        instr.write(f"DISP:WIND1:TRAC1:FEED 'Tr1'") 

        instr.write("CALC1:PAR:SDEF 'Tr2', 'S31AVG'")
        instr.write(f'DISP:WIND2:STAT ON') 
        instr.write(f'DISP:WIND2:TRAC2:FEED "Tr2"') 

        instr.write("CALC1:PAR:SDEF 'Tr3', 'S13AVG'")
        instr.write(f'DISP:WIND3:STAT ON') 
        instr.write(f'DISP:WIND3:TRAC3:FEED "Tr3"') 

        instr.write("CALC1:PAR:SDEF 'Tr4', 'S33AVG'")
        instr.write(f'DISP:WIND4:STAT ON') 
        instr.write(f'DISP:WIND4:TRAC4:FEED "Tr4"') 


    if (Ports == '14'):

        instr.write("CALC1:PAR:SDEF 'Tr1', 'S11AVG'")
        instr.write(f'DISP:WIND1:STAT ON') 
        instr.write(f"DISP:WIND1:TRAC1:FEED 'Tr1'") 

        instr.write("CALC1:PAR:SDEF 'Tr2', 'S41AVG'")
        instr.write(f'DISP:WIND2:STAT ON') 
        instr.write(f'DISP:WIND2:TRAC2:FEED "Tr2"') 

        instr.write("CALC1:PAR:SDEF 'Tr3', 'S14AVG'")
        instr.write(f'DISP:WIND3:STAT ON') 
        instr.write(f'DISP:WIND3:TRAC3:FEED "Tr3"') 

        instr.write("CALC1:PAR:SDEF 'Tr4', 'S44AVG'")
        instr.write(f'DISP:WIND4:STAT ON') 
        instr.write(f'DISP:WIND4:TRAC4:FEED "Tr4"') 


    if (Ports == '23'):

        instr.write("CALC1:PAR:SDEF 'Tr1', 'S22AVG'")
        instr.write(f'DISP:WIND1:STAT ON') 
        instr.write(f"DISP:WIND1:TRAC1:FEED 'Tr1'") 

        instr.write("CALC1:PAR:SDEF 'Tr2', 'S32AVG'")
        instr.write(f'DISP:WIND2:STAT ON') 
        instr.write(f'DISP:WIND2:TRAC2:FEED "Tr2"') 

        instr.write("CALC1:PAR:SDEF 'Tr3', 'S23AVG'")
        instr.write(f'DISP:WIND3:STAT ON') 
        instr.write(f'DISP:WIND3:TRAC3:FEED "Tr3"') 

        instr.write("CALC1:PAR:SDEF 'Tr4', 'S33AVG'")
        instr.write(f'DISP:WIND4:STAT ON') 
        instr.write(f'DISP:WIND4:TRAC4:FEED "Tr4"') 


    if (Ports == '24'):

        instr.write("CALC1:PAR:SDEF 'Tr1', 'S22AVG'")
        instr.write(f'DISP:WIND1:STAT ON') 
        instr.write(f"DISP:WIND1:TRAC1:FEED 'Tr1'") 

        instr.write("CALC1:PAR:SDEF 'Tr2', 'S42AVG'")
        instr.write(f'DISP:WIND2:STAT ON') 
        instr.write(f'DISP:WIND2:TRAC2:FEED "Tr2"') 

        instr.write("CALC1:PAR:SDEF 'Tr3', 'S24AVG'")
        instr.write(f'DISP:WIND3:STAT ON') 
        instr.write(f'DISP:WIND3:TRAC3:FEED "Tr3"') 

        instr.write("CALC1:PAR:SDEF 'Tr4', 'S44AVG'")
        instr.write(f'DISP:WIND4:STAT ON') 
        instr.write(f'DISP:WIND4:TRAC4:FEED "Tr4"') 


    if (Ports == '34'):

        instr.write("CALC1:PAR:SDEF 'Tr1', 'S33AVG'")
        instr.write(f'DISP:WIND1:STAT ON') 
        instr.write(f"DISP:WIND1:TRAC1:FEED 'Tr1'") 

        instr.write("CALC1:PAR:SDEF 'Tr2', 'S43AVG'")
        instr.write(f'DISP:WIND2:STAT ON') 
        instr.write(f'DISP:WIND2:TRAC2:FEED "Tr2"') 

        instr.write("CALC1:PAR:SDEF 'Tr3', 'S34AVG'")
        instr.write(f'DISP:WIND3:STAT ON') 
        instr.write(f'DISP:WIND3:TRAC3:FEED "Tr3"') 

        instr.write("CALC1:PAR:SDEF 'Tr4', 'S44AVG'")
        instr.write(f'DISP:WIND4:STAT ON') 
        instr.write(f'DISP:WIND4:TRAC4:FEED "Tr4"') 


    # Turn off continuous mode and set the number of measurements on which an average is performed
    instr.write(":INITiate1:CONTinuous:ALL OFF")
    instr.write(f":SENSE1:AVER:COUN {avg}; :AVER ON")


    # Perform the number of sweeps required for the selected averaging and wait for measurements to complete
    for i in range(avg):
        instr.query_with_opc(":INITiate1:IMMediate:ALL; *OPC?", 2000000)

    # Retrieve the trace data (real and imaginary parts)
    tracedata = instr.query_str('CALCulate1:DATA:ALL? SDAT')  # Get measurement values for complete trace
    chan_list = instr.query_str('CONF:CHAN:CATalog?') # Get channel list
    #print(chan_list) #Used for debugging

    trace_list = instr.query_str('CONF:CHAN:TRAC:CATalog?') # Get trace list
    #print(trace_list) #Used for debugging

    tracelist = list(map(str, tracedata.split(',')))  # Convert the received string into a list 
    tracelist = np.array(tracelist, dtype='float32')


    re1 = []
    im1 = []

    re2 = []
    im2 = []

    re3 = []
    im3 = []

    re4 = []
    im4 = []


    # Separate real and imaginary parts for each S-parameter 
    # The tracelist contains the real and imaginary parts of the S-parameters in the order: Re(S11), Im(S11), Re(S21), Im(S21), Re(S12), Im(S12), Re(S22), Im(S22)
    i = 0
    for i in range(int(len(tracelist)/4)):
        if (i%2)==0:
            re1.append(tracelist[i])
        else:
            im1.append(tracelist[i])


    for i in range(int(len(tracelist)/4),int(len(tracelist)/2),1):
        if (i%2)==0:
            re2.append(tracelist[i])
        else:
            im2.append(tracelist[i])


    for i in range(int(len(tracelist)/2),int(3*len(tracelist)/4),1):
        if (i%2)==0:
            re3.append(tracelist[i])
        else:
            im3.append(tracelist[i])


    for i in range(3*int(len(tracelist)/4),int(len(tracelist)),1):
        if (i%2)==0:
            re4.append(tracelist[i])
        else:
            im4.append(tracelist[i])


    # Retrieve the frequency data for the complete trace
    freqdata = instr.query_str('CALCulate1:DATA:STIMulus?')  # Get frequency list for complete trace
    freqlist = list(map(str, freqdata.split(',')))  # Convert the received string into a list
    freq = np.array(freqlist, dtype='float32')


    # Return frequency and real/imaginary parts for each S-parameter
    return freq, re1, im1, re2, im2, re3, im3, re4, im4 
