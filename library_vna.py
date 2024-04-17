from library_analysis import *
from library_power_supply import *
from library_misc import *
import numpy as np
from time import sleep
import json
from RsInstrument.RsInstrument import RsInstrument

"""
This file contains necessary functions to control and operate the VNA.
# TODO implement shared VNA object

Unused queries list:
:MMEMORY:STORE:CORRection 1, 'calibration_30_01_2024.cal'     Save calibration
"""


def setupConnectionVNA(give_additional_info: bool = False) -> RsInstrument:
    """
    Connects to the VNA.
    Returns object that contains methods to control the vna.
    """
    
    resource_string_1 = 'TCPIP::192.168.2.101::INSTR'  # Standard LAN connection (also called VXI-11)
    resource_string_2 = 'TCPIP::192.168.2.101::hislip0'  # Hi-Speed LAN connection - see 1MA208
    resource_string_3 = 'GPIB::20::INSTR'  # GPIB Connection
    resource_string_4 = 'USB::0x0AAD::0x0119::022019943::INSTR'  # USB-TMC (Test and Measurement Class)
    resource_string_5 = 'RSNRP::0x0095::104015::INSTR'  # R&S Powersensor NRP-Z86
    instr = RsInstrument(resource_string_3, True, False)

    idn = instr.query_str('*IDN?')
    print("VNA connected correctly via GPIB")

    if give_additional_info:
        print(f"\nHello, I am: '{idn}'")
        print(f'RsInstrument driver version: {instr.driver_version}')
        print(f'Instrument full name: {instr.full_instrument_model_name}')
        print(f'Instrument installed options: {",".join(instr.instrument_options)}')

    return instr


def applySettings(instr: RsInstrument, settings: object) -> None:
    """
    This function takes the instrument object and a settings dict variable, then translates settings from the settings variable in queries for the VNA.
    """

    # Set start frequency
    instr.write("SENS1:FREQ:STAR " + f"{settings['start_frequency']}")  # Replace with your desired start frequency

    # Set stop frequency
    instr.write("SENS1:FREQ:STOP "+ f"{settings['stop_frequency']}")  # Replace with your desired stop frequency

    # Set bandwidth
    instr.write("SENS1:BAND " + f"{settings['bandwidth']}")  # Replace with your desired bandwidth

    # Set power
    instr.write("SOUR1:POW " + f"{settings['power']}")  # Replace with your desired power level

    # Set number of points
    instr.write("SENS1:SWE:POIN " + f"{settings['number_of_points']}")  # Replace with your desired number of points

    # Reload calibration
    instr.write_str(":MMEMORY:LOAD:CORRection 1, 'MoNiFe HF 10Hz.cal'") #TODO rendere la calibration accessibile allo user anche lato codice
    # instr.write_str(":MMEMORY:LOAD:CORRection  1, 'calibration_08_02_2024.cal'")

    instr.visa_timeout = ( settings['bandwidth']**-1 * settings['number_of_points'] *10 )*1000  + 100  # estimation times an arbitrary coeff 


def measure_dB(instr: RsInstrument, Sparam: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Queries the VNA for values.
    Takes as input the vna instrument object and the S parameter that should be measured.
    Returns frequencies and amplitude in dB.
    """

    # Create a trace on channel 1 with the specified S-parameter
    instr.write(f'SENS:SWE:TYPE LIN')  # Set sweep type to linear
    instr.write(f'CALC:PAR:DEF:EXT "Trc1", {Sparam}')  # Create trace with specified S-parameter
    instr.write(f'DISP:WIND:TRAC:FEED "Trc1"')  # Display the trace

    # Trigger single sweep
    instr.write(":INITiate1:CONTinuous 0")
    instr.write(":INITiate1:IMMediate")

    # Wait for measurement to complete
    instr.query_with_opc(":INITiate1:IMMediate; *OPC?", 2000000)  # TODO mettere un numero più sensato

    tracedata = instr.query_str('CALCulate1:DATA? FDAT')  # Get measurement values for complete trace
    tracelist = list(map(str, tracedata.split(',')))  # Convert the received string into a list
    amp_db = np.array(tracelist, dtype='float32')

    freqdata = instr.query_str('CALCulate1:DATA:STIMulus?')  # Get frequency list for complete trace
    freqlist = list(map(str, freqdata.split(',')))  # Convert the received string into a list
    freq = np.array(freqlist, dtype='float32')
    phase = np.zeros(len(amp_db))

    return freq, amp_db, phase


def measure_amp_and_phase(instr: RsInstrument, Sparam: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Queries the VNA for values.
    Takes as input the vna instrument object and the S parameter that should be measured.
    Returns frequencies, amplitude (linear) and phase.
    """
        
    # Create a trace on channel 1 with the specified S-parameter
    #instr.write(f'SENS:SWE:TYPE LIN')  # Set sweep type to linear 
    instr.write(f'CALC:PAR:DEF:EXT "Trc2", {Sparam}')  # Create trace with specified S-parameter
    # instr.write(f'DISP:WIND:TRAC:FEED "Trc1"')  # Display the trace

    # Trigger single sweep
    instr.write(":INITiate1:CONTinuous 0")
    instr.query_with_opc(":INITiate1:IMMediate; *OPC?", 2000000)  # TODO mettere un numero più sensato

    # Wait for measurement to complete
    # instr.query_opc(999999999)
    # instr.query()

    tracedata = instr.query_str('CALCulate1:DATA? SDAT')  # Get measurement values for complete trace
    tracelist = list(map(str, tracedata.split(',')))  # Convert the received string into a list
    tracelist = np.array(tracelist, dtype='float32')
    re = []
    im = []
    S = []
    amp = []
    phase = []

    i = 0
    for i in range(len(tracelist)):
        if (i%2)==0:
            re.append(tracelist[i])
        else:
            im.append(tracelist[i])

    for i in range(len(re)):
        S.append(re[i]+1j*im[i]) 
        amp.append(np.abs(S[i]))
        phase.append(np.angle(S[i])) #Bisogna capire perchè con la fase non ci viene bene (*0 non ci andrebbe)

    freqdata = instr.query_str('CALCulate1:DATA:STIMulus?')  # Get frequency list for complete trace
    freqlist = list(map(str, freqdata.split(',')))  # Convert the received string into a list
    freq = np.array(freqlist, dtype='float32')


    return freq, amp, phase


def measurement_routine(ps1: PowerSupply, ps2: PowerSupply, instr: RsInstrument, field_sweep: list[float], angle: float, user_folder: str, sample_folder: str, filename: str, dipole: int, Sparam: str, demag: bool = True) -> str:
    """
    Main function that is called by other files. 
    Goes through the whole routine for initializing, measuring and saving.
    """


    # Routine if a dipole is used
    if dipole == 1 or dipole == 3 or dipole == 4:
        
        if (dipole == 1 and (Sparam == 'S22' or Sparam == 'S24' or Sparam == 'S42' or Sparam == 'S44')):
            ps = ps1
            conversion = 55.494
        
        elif (dipole == 1 and (Sparam == 'S11' or Sparam == 'S13' or Sparam == 'S31' or Sparam == 'S33')):
            ps = ps2
            conversion = 63.150

        elif (dipole == 3):
            ps = ps1
            conversion = 42.421

        elif (dipole == 4):
            ps = ps1
            conversion = 45.217

        else:
            ps = None
            
        if conversion == None or ps == None:
            logger.error("Invalid dipole_mode parameter")
            return
        
        if demag: ps.demag_sweep()
        current_sweep = np.array(field_sweep)/conversion

        for i in range(len(current_sweep)):
            if i == 1 and demag and field_sweep[0]!=0:
                ps.demag_sweep()

            current = current_sweep[i]

            ps.setCurrent(current)
            logger.info(f"Field set to {field_sweep[i]} mT")
            sleep(SETTLING_TIME)
            logger.info("Measuring... ")
            x,y,p = measure_amp_and_phase(instr, Sparam)
            #x,y,p = measure_dB(instr,Sparam)
            
            filename = saveData(x,y,p, user_folder, sample_folder, filename, index=i)
            logger.info(f'Saved file "{filename} ({i+1}).csv"')
            print("")

        ps.setCurrent(0)

    # Routine if a quadrupole is used
    elif dipole == 2:
        if ps1 == None or ps2 == None:
            logger.error("One of the power supplies is not properly connected.")
            return
        
        if demag: 
            ps1.demag_sweep()
            ps2.demag_sweep()

        conversion1 = 42.421
        conversion2 = 45.217

        current_sweep1 = ( np.array(field_sweep) * np.cos(np.pi/4 -angle) ) / conversion1
        current_sweep2 = ( np.array(field_sweep) * np.cos(np.pi/4 +angle) ) / conversion2  # Negative current to adjust field direction

        for i in range(len(current_sweep1)):
            current1 = current_sweep1[i]
            current2 = current_sweep2[i]

            ps1.setCurrent(current1)
            ps2.setCurrent(current2)
            logger.info(f"Field set to {field_sweep[i]} mT")
            sleep(SETTLING_TIME)
            logger.info("Measuring... ")
            x,y,p,re,im = measure_amp_and_phase(instr, Sparam)
            
            filename = saveData(x,y,p, user_folder, filename, index=i)
            logger.info(f'Saved file "{filename} ({i+1}).csv"')
            print("\n")


        ps1.setCurrent(0)
        ps2.setCurrent(0)
        
    return filename