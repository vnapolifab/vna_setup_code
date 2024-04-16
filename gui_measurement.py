from datetime import datetime
from logger import logger

from library_analysis import *
from library_gui import *
from library_vna import *
from library_power_supply import *
from CONSTANTS import *


# TODO list:
# - fare una demag_sweep per il quadrupoli che alterna i campi dei due invece di fare prima uno poi l'altro
# - Impedire di chiamare un sample o user "new sample" o "new user"


print("*** LOG SCREEN ***")
print("results and actions are reported here:\n")


settings = gui()


# Adds date time to measurement info
settings["datetime"] = str(datetime.now()).rstrip("0123456789").rstrip(".")


# Connects power supplies
print("Power supply 1 > ", end=""); 
if "ps1" in locals(): ps1.closeConnection()
ps1 = setupConnectionPS('COM4', 9600)

print("Power supply 2 > ", end=""); 
if "ps2" in locals(): ps2.closeConnection()
ps2 = setupConnectionPS('COM3', 9600)

# Connects VNA
print("VNA            > ", end=""); 
instr = setupConnectionVNA()
print()


# Add reference field
#settings["ref_field"] = settings["ref_field"].flip()
logger.info(f"Adding {settings['ref_field']} mT as reference field...")
settings["field_sweep"] = list(np.concatenate([[float(settings["ref_field"])], settings["field_sweep"]]))

applySettings(instr, settings)

settings["measurement_name"] = measurement_routine(
    ps1, 
    ps2, 
    instr, 
    settings["field_sweep"],
    settings["angle"],
    settings["user_name"],
    settings["sample_name"],
    settings["measurement_name"],
    settings["dipole_mode"],
    settings["s_parameter"]
)

# Save metadata:
save_metadata(settings)
update_log(settings)
