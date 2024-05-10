from library_analysis import *
from library_power_supply import *
from library_misc import *
from library_vna import *

def measurement_routine(ps1: PowerSupply, ps2: PowerSupply, instr: RsInstrument, field_sweep: list[float], angle: float, user_folder: str, sample_folder: str, filename: str, dipole: int, Sparam: str, demag: bool = True) -> str:
    """
    Main function that is called by other files. 
    Goes through the whole routine for initializing, measuring and saving.
    """
    
    # field_sweep = [ref_field] + field_sweep  # List concatenation

    # Routine if a dipole is used
    if dipole == 1 or dipole == 3 or dipole == 4:
        
        if (dipole == 1 and (Sparam == 'S22' or Sparam == 'S24' or Sparam == 'S42' or Sparam == 'S44')):
            ps = ps1
            conversion = 55.494  
        
        elif (dipole == 1 and (Sparam == 'S11' or Sparam == 'S13' or Sparam == 'S31' or Sparam == 'S33')):
            ps = ps2
            # conversion = 63.150
            conversion = 8.240  #coils gap = coil radius 
            # conversion = 6.886  # Coils 
            #conversion = 9.646 # Coils 

        elif (dipole == 3):
            ps = ps1
            conversion = 42.421

        elif (dipole == 4):
            ps = ps1
            conversion = 45.217

        else:
            ps = None
            
        if conversion == None or ps == None:
            raise Exception("Invalid dipole_mode parameter")
        
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