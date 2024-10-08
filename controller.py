from library_analysis import *
from library_gui import *
from library_vna import *
from library_power_supply import *
from CONSTANTS import *


# Connects power supplies

print("Power supply 1 > ", end=""); 
if "ps1" in locals(): ps1.closeConnection()
ps1 = setupConnectionPS('COM4', 9600)
#ps1.demag_sweep()

field = 15

offset = 2.1676
conversion = 122.98

current = (field-offset)/conversion


ps1.setCurrent(current)







#print("Power supply 2 > ", end=""); 
#if "ps2" in locals(): ps2.closeConnection()
#ps2 = setupConnectionPS('COM3', 9600)

# Connects VNA
#print("VNA            > ", end=""); 
#instr = setupConnectionVNA()
#print()


#ps2.setCurrent(2)
