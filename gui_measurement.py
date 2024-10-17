from datetime import datetime

from logger import logger
from library_analysis import *
from library_gui import *
from library_vna import *
from library_power_supply import *
from CONSTANTS import *
from measurement_routine import measurement_routine

# TODO list:
# - fare una demag_sweep per il quadrupoli che alterna i campi dei due invece di fare prima uno poi l'altro
# - Impedire di chiamare un sample o user "new sample" o "new user"


print("*** LOG SCREEN ***")
settings = gui_measurement_startup()
if settings == None:
    raise Exception("The GUI was closed manually")

# Adds date time to measurement info
settings["datetime"] = str(datetime.now()).rstrip("0123456789").rstrip(".")


print("Power supply 1 > ", end=""); 
ps1 = setupConnectionPS('COM4', 9600)

print("Power supply 2 > ", end=""); 
ps2 = setupConnectionPS('COM3', 9600)

print("VNA            > ", end=""); 
instr = setupConnectionVNA()


settings["field_sweep"] = list(np.concatenate([[float(settings["ref_field"])], settings["field_sweep"]]))

applySettings(instr, settings)
save_settings(settings)

measurement_routine(
    settings,
    ps1, 
    ps2, 
    instr, 
    settings["field_sweep"],
    settings["angle"],
    settings["user_name"],
    settings["sample_name"],
    settings["measurement_name"],
    settings["dipole_mode"],
    settings["s_parameter"],
    settings["avg_factor"],
    demag=False
)

# Save metadata:
old_name = settings["measurement_name"]
for sparam in ["S11", "S41", "S14", "S44"]: #TODO scommenta
    settings["measurement_name"] = f"{old_name}_{sparam}"
    settings["s_parameter"] = sparam
update_log(settings)