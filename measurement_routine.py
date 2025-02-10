from library_analysis import *
from library_power_supply import *
from library_misc import *
from library_vna import *
from library_file_management import *
import CONSTANTS as c

def measurement_routine(settings, ps1: PowerSupply, ps2: PowerSupply, instr: RsInstrument, field_sweep: list[float], angle: float, user_folder: str, sample_folder: str, measurement_name: str, dipole: int, Ports: str, avg:int = 1, demag: bool = False) -> str:
    """
    Main function that is called by other files. 
    Goes through the whole routine for initializing, measuring and saving.
    """

    try:    # Everything is encapsulated in a try except to always set the current to 0 in case of an exeption


        # ============================
        # Based on dipole variable, the program assigns a value to 'ps' which is used to govern the power supply and 'conversion' which holds the A to mT conversion value
        # ============================

        #Magnet used: DexinMag

            
        if (dipole == 1): 
            ps = ps1
            #conversion = 55.494 
            offset =  1.9831#2.7001 #0 #2.153 #Latest calibration by Alberto and Lorenzo Q in 05/02/2025, pole shoes where moved again after this
            conversion = 54.747#50.027 #5.8 #52.498

            offset1 =  0
            conversion1 = 0

            offset2 =  0
            conversion2 = 0

        
        #elif (dipole == 1 and (Sparam == 'S11' or Sparam == 'S14' or Sparam == 'S41' or Sparam == 'S44')):
            #ps = ps2
            # conversion = 63.150
            #conversion = 8.240  #coils gap = 29mm
            #conversion = 5.620   # coils gap = 55mm
            # conversion = 6.886  # Coils 
            # conversion = 9.646 # Coils 
            #print("Debug please")

        #elif (dipole == 3):
        #    ps = ps1
        #    conversion = 42.421

        #elif (dipole == 4):
        #    ps = ps1
        #    conversion = 45.217

            # Routine if a quadrupole is used
        elif dipole == 2: # TODO the code does not support different coonversions for the two power supplies, fix this
            if ps1 == None or ps2 == None:
                raise Exception("Quadrupole selected but one of the power supplies is not properly connected.")
            psq1 = ps1  #TwoPowerSupply(ps1=ps1, ps2=ps2)
            psq2 = ps2

            conversion = 0
            offset = 0

            offset1 =  1.7091
            conversion1 = 43.884

            offset2 =  1.4364
            conversion2 = 42.473
                
        else:
            ps = None
            
        if conversion == None:
            raise Exception("Invalid dipole_mode parameter")
            

        # ============================
        # Now the actual measurement routine starts
        # ============================

        #if demag:  # First demagnetization sweep 
            #ps.demag_sweep()

        #second_demag = demag and field_sweep[0]!=0  # If ref field != 0 a second demag field is needed 

        

        freqs_S11, fields_S11, amps_S11, phases_S11, S11 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype = 'complex_')
        freqs_S12, fields_S12, amps_S12, phases_S12, S12 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype = 'complex_')
        freqs_S21, fields_S21, amps_S21, phases_S21, S21 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype = 'complex_')
        freqs_S22, fields_S22, amps_S22, phases_S22, S22 = np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype = 'complex_')
        currents = np.array([])
        currents1 = np.array([])
        currents2 = np.array([])

        j = 0

        #if (dipole == 1):
        #    maxval = 3.5
        #    ps.setCurrent(maxval)
        #    sleep(SETTLING_TIME)
#
        #if (dipole == 2):
        #    maxval = 3.5
        #    psq1.setCurrent(maxval)
        #    psq2.setCurrent(maxval)
        #    sleep(SETTLING_TIME)

        for i, field in enumerate(field_sweep):  # MAIN FOR LOOP
            #if i == 1 and second_demag:
                #ps.demag_sweep()

            logger.info(f"Setting field...")
            if (dipole == 1):
                current = (field-offset)/conversion
                current1 = 0
                current2 = 0
                ps.setCurrent(current)

            if (dipole == 2):

                current = 0
                angle_rad = np.radians(angle)
                current1 = (field*np.cos(angle_rad)-offset1)/conversion1
                current2 = (field*np.sin(angle_rad)-offset2)/conversion2
                psq1.setCurrent(current1)
                psq2.setCurrent(current2)

            logger.info(f"Field set to {field_sweep[i]} mT")

            logger.info(f"Waiting {c.SETTLING_TIME}s...")
            sleep(SETTLING_TIME)
            logger.info("Settling time over")

            logger.info("Measuring...") 
            freq,a1,p1,a2,p2,a3,p3,a4,p4,S1,S2,S3,S4 = measure_amp_and_phase(instr, Ports, j, int(avg))
            j = j+1
            # x,y,p = measure_dB(instr,Sparam)
            logger.info("Finished measuring")

            currents = np.concatenate((currents,[current]*len(freq)))
            currents1 = np.concatenate((currents1,[current1]*len(freq)))
            currents2 = np.concatenate((currents2,[current2]*len(freq)))

            freqs_S11  = np.concatenate( (freqs_S11, freq) )    # Concatenation of new data with the already acquired data
            fields_S11 = np.concatenate( (fields_S11, [field]*len(freq)) )
            amps_S11   = np.concatenate( (amps_S11, a1) )
            phases_S11 = np.concatenate( (phases_S11, p1) )
            S11 = np.concatenate( (S11, S1) )
        
            freqs_S21  = np.concatenate( (freqs_S21, freq) )    # Concatenation of new data with the already acquired data
            fields_S21 = np.concatenate( (fields_S21, [field]*len(freq)) )
            amps_S21   = np.concatenate( (amps_S21, a2) )
            phases_S21 = np.concatenate( (phases_S21, p2) )
            S21 = np.concatenate( (S21, S2) )
        
            freqs_S12  = np.concatenate( (freqs_S12, freq) )    # Concatenation of new data with the already acquired data
            fields_S12 = np.concatenate( (fields_S12, [field]*len(freq)) )
            amps_S12   = np.concatenate( (amps_S12, a3) )
            phases_S12 = np.concatenate( (phases_S12, p3) )
            S12 = np.concatenate( (S12, S3) )
        
            freqs_S22  = np.concatenate( (freqs_S22, freq) )    # Concatenation of new data with the already acquired data
            fields_S22 = np.concatenate( (fields_S22, [field]*len(freq)) )
            amps_S22   = np.concatenate( (amps_S22, a4) )
            phases_S22 = np.concatenate( (phases_S22, p4) )
            S22 = np.concatenate( (S22, S4) )


            if (Ports == '12'):
                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S11, fields_S11, amps_S11, phases_S11, S11, user_folder, sample_folder, measurement_name = f"{measurement_name}_S11")
                logger.info(f'Saved file "{measurement_name}_S11.csv"')
                settings["measurement_name"] = f"{measurement_name}_S11"
                settings["s_parameter"] = 'S11'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S21, fields_S21, amps_S21, phases_S21, S21, user_folder, sample_folder, measurement_name = f"{measurement_name}_S21")
                logger.info(f'Saved file "{measurement_name}_S21.csv"')
                settings["measurement_name"] = f"{measurement_name}_S21"
                settings["s_parameter"] = 'S21'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S12, fields_S12, amps_S12, phases_S12, S12, user_folder, sample_folder, measurement_name = f"{measurement_name}_S12")
                logger.info(f'Saved file "{measurement_name}_S12.csv"')
                settings["measurement_name"] = f"{measurement_name}_S12"
                settings["s_parameter"] = 'S12'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S22, fields_S22, amps_S22, phases_S22, S22, user_folder, sample_folder, measurement_name = f"{measurement_name}_S22")
                logger.info(f'Saved file "{measurement_name}_S22.csv"')
                settings["measurement_name"] = f"{measurement_name}_S22"
                settings["s_parameter"] = 'S22'
                save_metadata(settings)


            if (Ports == '13'):
                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S11, fields_S11, amps_S11, phases_S11, S11, user_folder, sample_folder, measurement_name = f"{measurement_name}_S11")
                logger.info(f'Saved file "{measurement_name}_S11.csv"')
                settings["measurement_name"] = f"{measurement_name}_S11"
                settings["s_parameter"] = 'S11'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S21, fields_S21, amps_S21, phases_S21, S21, user_folder, sample_folder, measurement_name = f"{measurement_name}_S31")
                logger.info(f'Saved file "{measurement_name}_S31.csv"')
                settings["measurement_name"] = f"{measurement_name}_S31"
                settings["s_parameter"] = 'S31'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S12, fields_S12, amps_S12, phases_S12, S12, user_folder, sample_folder, measurement_name = f"{measurement_name}_S13")
                logger.info(f'Saved file "{measurement_name}_S13.csv"')
                settings["measurement_name"] = f"{measurement_name}_S13"
                settings["s_parameter"] = 'S13'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S22, fields_S22, amps_S22, phases_S22, S22, user_folder, sample_folder, measurement_name = f"{measurement_name}_S33")
                logger.info(f'Saved file "{measurement_name}_S33.csv"')
                settings["measurement_name"] = f"{measurement_name}_S33"
                settings["s_parameter"] = 'S33'
                save_metadata(settings)


            if (Ports == '14'):
                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S11, fields_S11, amps_S11, phases_S11, S11, user_folder, sample_folder, measurement_name = f"{measurement_name}_S11")
                logger.info(f'Saved file "{measurement_name}_S11.csv"')
                settings["measurement_name"] = f"{measurement_name}_S11"
                settings["s_parameter"] = 'S11'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S21, fields_S21, amps_S21, phases_S21, S21, user_folder, sample_folder, measurement_name = f"{measurement_name}_S41")
                logger.info(f'Saved file "{measurement_name}_S41.csv"')
                settings["measurement_name"] = f"{measurement_name}_S41"
                settings["s_parameter"] = 'S41'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S12, fields_S12, amps_S12, phases_S12, S12, user_folder, sample_folder, measurement_name = f"{measurement_name}_S14")
                logger.info(f'Saved file "{measurement_name}_S14.csv"')
                settings["measurement_name"] = f"{measurement_name}_S14"
                settings["s_parameter"] = 'S14'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S22, fields_S22, amps_S22, phases_S22, S22, user_folder, sample_folder, measurement_name = f"{measurement_name}_S44")
                logger.info(f'Saved file "{measurement_name}_S44.csv"')
                settings["measurement_name"] = f"{measurement_name}_S44"
                settings["s_parameter"] = 'S44'
                save_metadata(settings)


            if (Ports == '23'):
                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S11, fields_S11, amps_S11, phases_S11, S11, user_folder, sample_folder, measurement_name = f"{measurement_name}_S22")
                logger.info(f'Saved file "{measurement_name}_S22.csv"')
                settings["measurement_name"] = f"{measurement_name}_S22"
                settings["s_parameter"] = 'S22'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S21, fields_S21, amps_S21, phases_S21, S21, user_folder, sample_folder, measurement_name = f"{measurement_name}_S32")
                logger.info(f'Saved file "{measurement_name}_S32.csv"')
                settings["measurement_name"] = f"{measurement_name}_S32"
                settings["s_parameter"] = 'S32'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S12, fields_S12, amps_S12, phases_S12, S12, user_folder, sample_folder, measurement_name = f"{measurement_name}_S23")
                logger.info(f'Saved file "{measurement_name}_S23.csv"')
                settings["measurement_name"] = f"{measurement_name}_S23"
                settings["s_parameter"] = 'S23'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S22, fields_S22, amps_S22, phases_S22, S22, user_folder, sample_folder, measurement_name = f"{measurement_name}_S33")
                logger.info(f'Saved file "{measurement_name}_S33.csv"')
                settings["measurement_name"] = f"{measurement_name}_S33"
                settings["s_parameter"] = 'S33'
                save_metadata(settings)


            if (Ports == '24'):
                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S11, fields_S11, amps_S11, phases_S11, S11, user_folder, sample_folder, measurement_name = f"{measurement_name}_S22")
                logger.info(f'Saved file "{measurement_name}_S22.csv"')
                settings["measurement_name"] = f"{measurement_name}_S22"
                settings["s_parameter"] = 'S22'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S21, fields_S21, amps_S21, phases_S21, S21, user_folder, sample_folder, measurement_name = f"{measurement_name}_S42")
                logger.info(f'Saved file "{measurement_name}_S42.csv"')
                settings["measurement_name"] = f"{measurement_name}_S42"
                settings["s_parameter"] = 'S42'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S12, fields_S12, amps_S12, phases_S12, S12, user_folder, sample_folder, measurement_name = f"{measurement_name}_S24")
                logger.info(f'Saved file "{measurement_name}_S24.csv"')
                settings["measurement_name"] = f"{measurement_name}_S24"
                settings["s_parameter"] = 'S24'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S22, fields_S22, amps_S22, phases_S22, S22, user_folder, sample_folder, measurement_name = f"{measurement_name}_S44")
                logger.info(f'Saved file "{measurement_name}_S44.csv"')
                settings["measurement_name"] = f"{measurement_name}_S44"
                settings["s_parameter"] = 'S44'
                save_metadata(settings)


            if (Ports == '34'):
                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S11, fields_S11, amps_S11, phases_S11, S11, user_folder, sample_folder, measurement_name = f"{measurement_name}_S33")
                logger.info(f'Saved file "{measurement_name}_S33.csv"')
                settings["measurement_name"] = f"{measurement_name}_S33"
                settings["s_parameter"] = 'S33'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S21, fields_S21, amps_S21, phases_S21, S21, user_folder, sample_folder, measurement_name = f"{measurement_name}_S43")
                logger.info(f'Saved file "{measurement_name}_S43.csv"')
                settings["measurement_name"] = f"{measurement_name}_S43"
                settings["s_parameter"] = 'S43'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S12, fields_S12, amps_S12, phases_S12, S12, user_folder, sample_folder, measurement_name = f"{measurement_name}_S34")
                logger.info(f'Saved file "{measurement_name}_S34.csv"')
                settings["measurement_name"] = f"{measurement_name}_S34"
                settings["s_parameter"] = 'S34'
                save_metadata(settings)

                logger.info(f'Saving data...')
                save_data(currents, currents1, currents2, freqs_S22, fields_S22, amps_S22, phases_S22, S22, user_folder, sample_folder, measurement_name = f"{measurement_name}_S44")
                logger.info(f'Saved file "{measurement_name}_S44.csv"')
                settings["measurement_name"] = f"{measurement_name}_S44"
                settings["s_parameter"] = 'S44'
                save_metadata(settings)


        if (dipole == 1):
                ps.setCurrent(0)

        if (dipole == 2):
            psq1.setCurrent(0)
            psq2.setCurrent(0)  # Set current back to 0 at the end of the routine
        
        return




    except Exception as e:  # If any error occurs, first set the current to 0 then raise the exeption
        if (dipole == 1):
                ps.setCurrent(0)

        if (dipole == 2):
            psq1.setCurrent(0)
            psq2.setCurrent(0)  # Set current back to 0 at the end of the routine
        raise e