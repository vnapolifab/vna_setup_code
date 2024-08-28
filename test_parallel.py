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

print("Power supply 1 > ", end=""); 
ps1 = setupConnectionPS('COM4', 9600)

print("Power supply 2 > ", end=""); 
ps2 = setupConnectionPS('COM3', 9600)

print("VNA            > ", end=""); 
instr = setupConnectionVNA()

Sparam1 = 'S33'
Sparam2 = 'S43'
Sparam3 = 'S34'
Sparam4 = 'S44'

instr.write("CALC1:PAR:DEL 'Trc1'")

instr.write("CALC1:PAR:SDEF 'Tr1', 'S33'")
instr.write(f'DISP:WIND1:STAT ON') 
instr.write(f"DISP:WIND1:TRAC1:FEED 'Tr1'") 

instr.write("CALC1:PAR:SDEF 'Tr2', 'S34'")
instr.write(f'DISP:WIND2:STAT ON') 
instr.write(f'DISP:WIND2:TRAC2:FEED "Tr2"') 

instr.write("CALC1:PAR:SDEF 'Tr3', 'S43'")
instr.write(f'DISP:WIND3:STAT ON') 
instr.write(f'DISP:WIND3:TRAC3:FEED "Tr3"') 

instr.write("CALC1:PAR:SDEF 'Tr4', 'S44'")
instr.write(f'DISP:WIND4:STAT ON') 
instr.write(f'DISP:WIND4:TRAC4:FEED "Tr4"') 

instr.write(":INITiate1:CONTinuous:ALL OFF")
instr.query_with_opc(":INITiate1:IMMediate:ALL; *OPC?", 2000000)

tracedata = instr.query_str('CALCulate1:DATA:ALL? SDAT')  # Get measurement values for complete trace
chan_list = instr.query_str('CONF:CHAN:CATalog?')
print(chan_list)

trace_list = instr.query_str('CONF:CHAN:TRAC:CATalog?')
print(trace_list)

tracelist = list(map(str, tracedata.split(',')))  # Convert the received string into a list 
tracelist = np.array(tracelist, dtype='float32')
print(len(tracelist))
print(len(tracelist)/4)
print(int(len(tracelist)/4))

re1 = []
im1 = []
S1 = []
amp1 = []
phase1 = []

re2 = []
im2 = []
S2 = []
amp2 = []
phase2 = []

re3 = []
im3 = []
S3 = []
amp3 = []
phase3 = []

re4 = []
im4 = []
S4 = []
amp4 = []
phase4 = []

i = 0
for i in range(int(len(tracelist)/4)):
    if (i%2)==0:
        re1.append(tracelist[i])
    else:
        im1.append(tracelist[i])

for i in range(len(re1)):
    S1.append(re1[i]+1j*im1[i]) 
    amp1.append(np.abs(S1[i]))
    phase1.append(np.angle(S1[i])) #Bisogna capire perchè con la fase non ci viene bene (*0 non ci andrebbe)


for i in range(int(len(tracelist)/4),int(len(tracelist)/2),1):
    if (i%2)==0:
        re2.append(tracelist[i])
    else:
        im2.append(tracelist[i])

for i in range(len(re2)):
    S2.append(re2[i]+1j*im2[i]) 
    amp2.append(np.abs(S2[i]))
    phase2.append(np.angle(S2[i])) #Bisogna capire perchè con la fase non ci viene bene (*0 non ci andrebbe)


for i in range(int(len(tracelist)/2),int(3*len(tracelist)/4),1):
    if (i%2)==0:
        re3.append(tracelist[i])
    else:
        im3.append(tracelist[i])

for i in range(len(re3)):
    S3.append(re3[i]+1j*im3[i]) 
    amp3.append(np.abs(S3[i]))
    phase3.append(np.angle(S3[i])) #Bisogna capire perchè con la fase non ci viene bene (*0 non ci andrebbe)


for i in range(3*int(len(tracelist)/4),int(len(tracelist)),1):
    if (i%2)==0:
        re4.append(tracelist[i])
    else:
        im4.append(tracelist[i])

for i in range(len(re4)):
    S4.append(re4[i]+1j*im4[i]) 
    amp4.append(np.abs(S4[i]))
    phase4.append(np.angle(S4[i])) #Bisogna capire perchè con la fase non ci viene bene (*0 non ci andrebbe)



freqdata = instr.query_str('CALCulate1:DATA:STIMulus?')  # Get frequency list for complete trace
freqlist = list(map(str, freqdata.split(',')))  # Convert the received string into a list
freq = np.array(freqlist, dtype='float32')