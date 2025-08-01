# Import required modules
from datetime import datetime  # For handling date and time

# Import custom libraries for logging, analysis, GUI, VNA, power supply, and constants
from logger import logger  
from library_analysis import *  
from library_gui import *  
from library_vna import *  
from library_power_supply import *  
from CONSTANTS import *  
from measurement_routine import measurement_routine  

# Display a log screen header
print("*** LOG SCREEN ***")

# Launch GUI to get user-defined measurement settings
settings = gui_measurement_startup()

# If the user closes the GUI without input, raise an exception
if settings is None:
    raise Exception("The GUI was closed manually")

# Add the current date and time to the measurement settings dictionary
settings["datetime"] = str(datetime.now()).rstrip("0123456789").rstrip(".")

# Establish connections with power supplies and VNA
print("Power supply 1 > ", end="")  
ps1 = setupConnectionPS('COM4', 9600)  # Connect to power supply 1 via COM4 at 9600 baud rate

print("Power supply 2 > ", end="")  
ps2 = setupConnectionPS('COM3', 9600)  # Connect to power supply 2 via COM3 at 9600 baud rate

print("VNA            > ", end="")  
instr = setupConnectionVNA()  # Connect to the Vector Network Analyzer (VNA)

# Ensure the field sweep list starts with the reference field value
settings["field_sweep"] = list(np.concatenate([[float(settings["ref_field"])], settings["field_sweep"]]))

# Apply user-defined settings to the VNA
applySettings(instr, settings)

# Save the settings for future reference
save_settings(settings)

# Execute the measurement routine with the provided parameters
measurement_routine(
    settings,      # User-defined settings
    ps1,           # Power supply 1 connection
    ps2,           # Power supply 2 connection
    instr,         # VNA connection
    settings["field_sweep"],  # List of field values for the sweep
    settings["angle"],        # Measurement angle
    settings["user_name"],    # User's name
    settings["sample_name"],  # Sample name
    settings["measurement_name"],  # Measurement session name
    settings["dipole_mode"],  # Dipole mode setting
    settings["ports"],        # Port configuration
    settings["avg_factor"],   # Averaging factor for measurements
    demag=False  # Demagnetization sweep is by default not applied (the functionnality will likely be deprecated in future versions of the code)
)

# Update the log file with measurement details
update_log(settings)
