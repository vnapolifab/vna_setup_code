# Importing necessary libraries for measurement routines, control of instruments, etc.
from library_analysis import *
from library_power_supply import *
from library_misc import *
from library_vna import *
from library_file_management import *
import CONSTANTS as c

def measurement_routine(settings, ps1: PowerSupply, ps2: PowerSupply, instr: RsInstrument, field_sweep: list[float], angle: float, user_folder: str, sample_folder: str, measurement_name: str, dipole: int, Ports: str, avg:int = 1, demag: bool = False) -> str:
    """
    Main function that executes the entire measurement routine. It initializes the instruments, performs measurements, and saves the data.
    """

    try:    # Encapsulating the routine in a try-except block to handle errors, ensuring currents are reset to 0 in case of failure.

        # Define settings for the dipole magnet used (DexinMag operated in either dipole or quadrupole mode)
        if (dipole == 1): 
            ps = ps1  # Single power supply for dipole mode
            
            offset =  1.9831  # Offset for conversion
            conversion = 54.747  # Conversion factor for field to current

            # Placeholder offsets and conversions for other configurations (quadrupole)
            offset1 =  0
            conversion1 = 0
            offset2 =  0
            conversion2 = 0

        elif dipole == 2:  # Routine for quadrupole mode (two power supplies)
            if ps1 == None or ps2 == None:
                raise Exception("Quadrupole selected but one of the power supplies is not properly connected.")
            psq1 = ps1  # Set up two power supplies
            psq2 = ps2

            conversion = 0  # Not used in quadrupole mode
            offset = 0  # Not used in quadrupole mode

            # Define offsets and conversion factors specific to quadrupole operation
            offset1 =  1.7091
            conversion1 = 43.884
            offset2 =  1.4364
            conversion2 = 42.473

        else:  # Undefined dipole type
            ps = None  # No power supply initialized for this case

        # Raise an exception if no valid conversion factor is defined
        if conversion == None:
            raise Exception("Invalid dipole_mode parameter")
            

        # ============================
        # Start the actual measurement routine
        # ============================

        # Optionally perform a demagnetization sweep (currently commented out, will be deprecated)
        # if demag:  
            # ps.demag_sweep()

        #second_demag = demag and field_sweep[0]!=0  # If ref field != 0 a second demag field is needed 

        # Initialize empty arrays for storing measurement results
        freqs_m = np.array([])  # Frequency measurements
        fields_m = np.array([])  # Magnetic field measurements
        re_S11 = np.array([])  # Real part of S11 parameter
        im_S11 = np.array([])  # Imaginary part of S11 parameter
        re_S21 = np.array([])  # Real part of S21 parameter
        im_S21 = np.array([])  # Imaginary part of S21 parameter
        re_S12 = np.array([])  # Real part of S12 parameter
        im_S12 = np.array([])  # Imaginary part of S12 parameter
        re_S22 = np.array([])  # Real part of S22 parameter
        im_S22 = np.array([])  # Imaginary part of S22 parameter
        currents = np.array([])  # Array to store currents
        currents1 = np.array([])  # Currents for quadrupole configuration (if applicable)
        currents2 = np.array([])  # Currents for quadrupole configuration (if applicable)

        j = 0  # Counter for the measurements


        # Set the current to the maximum value for the dipole or quadrupole mode operation before satarting the measurement (optional: currently commented out)
        #if (dipole == 1):
        #    maxval = 3.5
        #    ps.setCurrent(maxval)
        #    sleep(SETTLING_TIME)

        #if (dipole == 2):
        #    maxval = 3.5
        #    psq1.setCurrent(maxval)
        #    psq2.setCurrent(maxval)
        #    sleep(SETTLING_TIME)

        # Loop through the field values and perform measurements

        for i, field in enumerate(field_sweep):  # MAIN FOR LOOP for sweeping the magnetic field
           #A second demag sweep is needed if the first field is not 0, (currently commented out, will be deprecated)
           #if i == 1 and second_demag:
                #ps.demag_sweep()
           
            logger.info(f"Setting field...")
            
            # For dipole mode (single power supply), calculate the current for the given field
            if (dipole == 1):
                current = (field - offset) / conversion  # Calculate the current for the dipole operation
                current1 = 0
                current2 = 0
                ps.setCurrent(current)  # Set the current in the power supply

            # For quadrupole mode (two power supplies), calculate currents for both power supplies
            if (dipole == 2):
                current = 0  # No direct current for dipole mode (only quadrupole)
                angle_rad = np.radians(angle)  # Convert the angle to radians
                current1 = (field * np.cos(angle_rad) - offset1) / conversion1  # Current for first power supply
                current2 = (field * np.sin(angle_rad) - offset2) / conversion2  # Current for second power supply
                psq1.setCurrent(current1)  # Set current for the first power supply
                psq2.setCurrent(current2)  # Set current for the second power supply

            logger.info(f"Field set to {field_sweep[i]} mT")

            # Wait for the power supply to settle before taking measurements
            logger.info(f"Waiting {c.SETTLING_TIME}s...")
            sleep(SETTLING_TIME)  # Sleep for settling time defined in constants
            logger.info("Settling time over")

            logger.info("Measuring...") 
            # Measure frequency and S-parameters (S11, S21, S12, S22)
            freq, re_S1, im_S1, re_S2, im_S2, re_S3, im_S3, re_S4, im_S4 = measure_amp_and_phase(instr, Ports, j, int(avg))
            j = j + 1
            
            logger.info("Finished measuring")

            # Concatenate new measurements with the already existing data
            currents = np.concatenate((currents, [current] * len(freq)))
            currents1 = np.concatenate((currents1, [current1] * len(freq)))
            currents2 = np.concatenate((currents2, [current2] * len(freq)))
            freqs_m = np.concatenate((freqs_m, freq))
            fields_m = np.concatenate((fields_m, [field] * len(freq)))
            re_S11 = np.concatenate((re_S11, re_S1))
            im_S11 = np.concatenate((im_S11, im_S1))
            re_S21 = np.concatenate((re_S21, re_S2))
            im_S21 = np.concatenate((im_S21, im_S2))
            re_S12 = np.concatenate((re_S12, re_S3))
            im_S12 = np.concatenate((im_S12, im_S3))
            re_S22 = np.concatenate((re_S22, re_S4))
            im_S22 = np.concatenate((im_S22, im_S4))

            logger.info(f'Saving data...')
            # Save the acquired data to a file
            save_data(Ports, currents, currents1, currents2, freqs_m, fields_m, re_S11, im_S11, re_S21, im_S21, re_S12, im_S12, re_S22, im_S22, user_folder, sample_folder, measurement_name=f"{measurement_name}")
            logger.info(f'Saved file "{measurement_name}.csv"')
            settings["measurement_name"] = f"{measurement_name}"  # Update the measurement name in settings
            save_metadata(settings)  # Save the metadata

        # Reset the current at the end of the measurement routine
        if (dipole == 1):
            ps.setCurrent(0)
        if (dipole == 2):
            psq1.setCurrent(0)
            psq2.setCurrent(0)  # Reset the currents for quadrupole power supplies
        
        return

    except Exception as e:  # If an error occurs, reset current to 0 and re-raise the exception
        if (dipole == 1):
            ps.setCurrent(0)
        if (dipole == 2):
            psq1.setCurrent(0)
            psq2.setCurrent(0)  # Reset current for quadrupole power supplies
        raise e  # Re-raise the exception
