from library_analysis import *
from library_power_supply import *
from library_misc import *
from library_vna import *
from library_file_management import *
import CONSTANTS as c

def measurement_routine(settings, ps1: PowerSupply, ps2: PowerSupply, instr: RsInstrument, field_sweep: list[float], angle: float, user_folder: str, sample_folder: str, measurement_name: str, dipole: int, Sparam: str, avg:int = 1, demag: bool = False) -> str:
    """
    Main function that is called by other files. 
    Goes through the whole routine for initializing, measuring and saving.
    """

    try:    # Everything is encapsulated in a try except to always set the current to 0 in case of an exeption


        # ============================
        # Based on dipole variable, the program assigns a value to 'ps' which is used to govern the power supply and 'conversion' which holds the A to mT conversion value
        # ============================

        #Magnet used: GMW

        if dipole == 1 or dipole == 3 or dipole == 4:
            
            if (dipole == 1): 
                ps = ps1
                #conversion = 55.494 
                offset =  2.7001 #0 #2.153
                conversion = 50.027 #5.8 #52.498

            
            #elif (dipole == 1 and (Sparam == 'S11' or Sparam == 'S14' or Sparam == 'S41' or Sparam == 'S44')):
                #ps = ps2
                # conversion = 63.150
                #conversion = 8.240  #coils gap = 29mm
                #conversion = 5.620   # coils gap = 55mm
                # conversion = 6.886  # Coils 
                # conversion = 9.646 # Coils 
                #print("Debug please")

            elif (dipole == 3):
                ps = ps1
                conversion = 42.421

            elif (dipole == 4):
                ps = ps1
                conversion = 45.217

                # Routine if a quadrupole is used
            elif dipole == 2: # TODO the code does not support different coonversions for the two power supplies, fix this
                if ps1 == None or ps2 == None:
                    raise Exception("Quadrupole selected but one of the power supplies is not properly connected.")
                ps = TwoPowerSupply(ps1=ps1, ps2=ps2)
                    
            else:
                ps = None
                
            if conversion == None or ps == None:
                raise Exception("Invalid dipole_mode parameter")
            

        # ============================
        # Now the actual measurement routine starts
        # ============================

        #if demag:  # First demagnetization sweep 
            #ps.demag_sweep()

        #second_demag = demag and field_sweep[0]!=0  # If ref field != 0 a second demag field is needed 

        freqs_S22, fields_S22, amps_S22, phases_S22, S22 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype = 'complex_')
        freqs_S24, fields_S24, amps_S24, phases_S24, S24 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype = 'complex_')
        freqs_S42, fields_S42, amps_S42, phases_S42, S42 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype = 'complex_')
        freqs_S44, fields_S44, amps_S44, phases_S44, S44 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype = 'complex_')
        currents = np.array([])

        j = 0

        for i, field in enumerate(field_sweep):  # MAIN FOR LOOP
            #if i == 1 and second_demag:
                #ps.demag_sweep()

            current = (field-offset)/conversion


            logger.info(f"Setting field...")
            ps.setCurrent(current)
            logger.info(f"Field set to {field_sweep[i]} mT")

            logger.info(f"Waiting {c.SETTLING_TIME}s...")
            sleep(SETTLING_TIME)
            logger.info("Settling time over")

            logger.info("Measuring...") 
            freq,a1,p1,a2,p2,a3,p3,a4,p4,S1,S2,S3,S4 = measure_amp_and_phase(instr, Sparam, j, int(avg))
            j = j+1
            # x,y,p = measure_dB(instr,Sparam)
            logger.info("Finished measuring\n")

            currents = np.concatenate((currents,[current]*len(freq)))

            freqs_S22  = np.concatenate( (freqs_S22, freq) )    # Concatenation of new data with the already acquired data
            fields_S22 = np.concatenate( (fields_S22, [field]*len(freq)) )
            amps_S22   = np.concatenate( (amps_S22, a1) )
            phases_S22 = np.concatenate( (phases_S22, p1) )
            S22 = np.concatenate( (S22, S1) )
        
            freqs_S42  = np.concatenate( (freqs_S42, freq) )    # Concatenation of new data with the already acquired data
            fields_S42 = np.concatenate( (fields_S42, [field]*len(freq)) )
            amps_S42   = np.concatenate( (amps_S42, a2) )
            phases_S42 = np.concatenate( (phases_S42, p2) )
            S42 = np.concatenate( (S42, S2) )
        
            freqs_S24  = np.concatenate( (freqs_S24, freq) )    # Concatenation of new data with the already acquired data
            fields_S24 = np.concatenate( (fields_S24, [field]*len(freq)) )
            amps_S24   = np.concatenate( (amps_S24, a3) )
            phases_S24 = np.concatenate( (phases_S24, p3) )
            S24 = np.concatenate( (S24, S3) )
        
            freqs_S44  = np.concatenate( (freqs_S44, freq) )    # Concatenation of new data with the already acquired data
            fields_S44 = np.concatenate( (fields_S44, [field]*len(freq)) )
            amps_S44   = np.concatenate( (amps_S44, a4) )
            phases_S44 = np.concatenate( (phases_S44, p4) )
            S44 = np.concatenate( (S44, S4) )


            logger.info(f'Saving data...')
            save_data(currents, freqs_S22, fields_S22, amps_S22, phases_S22, S22, user_folder, sample_folder, measurement_name = f"{measurement_name}_S22")
            logger.info(f'Saved file "{measurement_name}_S22.csv"')
            settings["measurement_name"] = f"{measurement_name}_S22"
            settings["s_parameter"] = 'S22'
            save_metadata(settings)

            logger.info(f'Saving data...')
            save_data(currents, freqs_S42, fields_S42, amps_S42, phases_S42, S42, user_folder, sample_folder, measurement_name = f"{measurement_name}_S42")
            logger.info(f'Saved file "{measurement_name}_S42.csv"')
            settings["measurement_name"] = f"{measurement_name}_S42"
            settings["s_parameter"] = 'S42'
            save_metadata(settings)

            logger.info(f'Saving data...')
            save_data(currents, freqs_S24, fields_S24, amps_S24, phases_S24, S24, user_folder, sample_folder, measurement_name = f"{measurement_name}_S24")
            logger.info(f'Saved file "{measurement_name}_S24.csv"')
            settings["measurement_name"] = f"{measurement_name}_S24"
            settings["s_parameter"] = 'S24'
            save_metadata(settings)

            logger.info(f'Saving data...')
            save_data(currents, freqs_S44, fields_S44, amps_S44, phases_S44, S44, user_folder, sample_folder, measurement_name = f"{measurement_name}_S44")
            logger.info(f'Saved file "{measurement_name}_S44.csv"')
            settings["measurement_name"] = f"{measurement_name}_S44"
            settings["s_parameter"] = 'S44'
            save_metadata(settings)
            print("\n\n")


        ps.setCurrent(0)  # Set current back to 0 at the end of the routine
        
        return




    except Exception as e:  # If any error occurs, first set the current to 0 then raise the exeption
        ps.setCurrent(0)
        raise e