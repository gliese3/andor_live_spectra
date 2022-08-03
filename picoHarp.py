#PicoHarp 300 Hardware via PHLIB.DLL v 3.0. demo code by Keno Goertz, PicoQuant GmbH, February 2018
#CM110 code by Kuno
#overall implementation by Kuno

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import time as t                   #for general use
import serial                      #for CM110 serial communication
from serial import SerialException #for CM110 serial communication
import sys                         #for exit function
import ctypes as ct                #for PicoHarp300
from ctypes import byref           #for PicoHarp300

#***************************USER DEFINED. MUST CHANGE***************************
#CM110 SETTINGS
portname='COM1'        #for serial communication
user_filename='irinatest_TRES.txt'
initial_wave=600       #units of nm
end_wave=650           #units of nm
step_wave=5           #units of nm
total_steps=int((end_wave-initial_wave)/step_wave)      #typecast int
master_array=np.zeros((total_steps+1,65536),dtype=int)  #this implicitly assumes PicoHarp300 always takes 65536 elements

#PICOHARP300 settings
binning = 0            #you can change this
offset = 39
tacq = 1000            #Measurement time in millisec, you can change this
syncDivider = 2        #you can change this 
CFDZeroCross0 = 10     #you can change this (in mV) CHANNEL 0
CFDLevel0 = 200        #you can change this (in mV) CHANNEL 0
CFDZeroCross1 = 10     #you can change this (in mV) CHANNEL 1
CFDLevel1 = 30         #you can change this (in mV) CHANNEL 1
#*******************************************************************************

#_______________________________________________________________________________
#DEFINITIONS: From phdefin.h (DO NOT CHANGE)
LIB_VERSION = "3.0"
HISTCHAN = 65536
MAXDEVNUM = 8
MODE_HIST = 0
FLAG_OVERFLOW = 0x0040

#DEFINITIONS: CM110 commands summarized (DO NOT CHANGE)
command_serial=bytearray([56,19])            #query serial number of unit        
command_curr_pos=bytearray([56,0])           #query current grating position in nm
command_step_size=bytearray([55,step_wave])  #this implicitly assumes step_wave fits into 1 byte (0-255)
command_step=bytearray([54])                 #tells CM110 to step 1, overkill but whatever
init_pos=initial_wave.to_bytes(2,'big')      #big means most significant bit first
command_initial=bytearray([16,init_pos[0],init_pos[1]]) #command goto initial position in nm

#REQUIRED: PicoHarp300 variables to store information read from DLLs (DO NOT CHANGE)
counts = (ct.c_uint * HISTCHAN)()            #this is the main array we care about
dev = []                                     #device list in case there are multiple units
libVersion = ct.create_string_buffer(b"", 8)
hwSerial = ct.create_string_buffer(b"", 8)
hwPartno = ct.create_string_buffer(b"", 8)
hwVersion = ct.create_string_buffer(b"", 8)
hwModel = ct.create_string_buffer(b"", 16)
errorString = ct.create_string_buffer(b"", 40)
resolution = ct.c_double()
countRate0 = ct.c_int()
countRate1 = ct.c_int()
flags = ct.c_int()

#REQUIRED: load the Picoquant C library of commands
phlib = ct.CDLL("phlib64.dll") #pot the library in the same folder as this file

#REQUIRED: PicoHarp300 functions
def closeDevices():
    for i in range(0, MAXDEVNUM):
        phlib.PH_CloseDevice(ct.c_int(i))
    print('Closing PicoHarp300, Finished or Crashed. SystemExit code 0 OK.')
    sys.exit(0)# the zero here means success

def tryfunc(retcode, funcName):
    if retcode < 0:
        phlib.PH_GetErrorString(errorString, ct.c_int(retcode))
        print("PH_%s error %d (%s). Aborted." % (funcName, retcode,\
              errorString.value.decode("utf-8")))
        closeDevices()
       
print("\nSearching for PicoHarp devices...")
print("Dev. ID     Status")

#INITIALIZE communication with PicoHarp300
for i in range(0, MAXDEVNUM):
    retcode = phlib.PH_OpenDevice(ct.c_int(i), hwSerial)
    if retcode == 0:
        print("  %1d        S/N %s" % (i, hwSerial.value.decode("utf-8")))
        dev.append(i)
    else:
        if retcode == -1: # ERROR_DEVICE_OPEN_FAIL
            print("  %1d        no device" % i)
        else:
            phlib.PH_GetErrorString(errorString, ct.c_int(retcode))
            print("  %1d        %s" % (i, errorString.value.decode("utf8")))

if len(dev) < 1:
    print("No device available.")
    closeDevices()
print("Using device #%1d" % dev[0])
print("\nInitializing the device...")

#INITIALIZE PicoHarp300
tryfunc(phlib.PH_Initialize(ct.c_int(dev[0]), ct.c_int(MODE_HIST)), "Initialize")
tryfunc(phlib.PH_GetHardwareInfo(dev[0], hwModel, hwPartno, hwVersion),\
        "GetHardwareInfo")
print("Found Model %s Part no %s Version %s" % (hwModel.value.decode("utf-8"),\
    hwPartno.value.decode("utf-8"), hwVersion.value.decode("utf-8")))
tryfunc(phlib.PH_Calibrate(ct.c_int(dev[0])), "Calibrate")
tryfunc(phlib.PH_SetSyncDiv(ct.c_int(dev[0]), ct.c_int(syncDivider)), "SetSyncDiv")
tryfunc(
    phlib.PH_SetInputCFD(ct.c_int(dev[0]), ct.c_int(0), ct.c_int(CFDLevel0),\
                         ct.c_int(CFDZeroCross0)),\
    "SetInputCFD"
)
tryfunc(
    phlib.PH_SetInputCFD(ct.c_int(dev[0]), ct.c_int(1), ct.c_int(CFDLevel1),\
                         ct.c_int(CFDZeroCross1)),\
    "SetInputCFD"
)
tryfunc(phlib.PH_SetBinning(ct.c_int(dev[0]), ct.c_int(binning)), "SetBinning")
tryfunc(phlib.PH_SetOffset(ct.c_int(dev[0]), ct.c_int(offset)), "SetOffset")
tryfunc(phlib.PH_GetResolution(ct.c_int(dev[0]), byref(resolution)), "GetResolution")
t.sleep(0.2)# Note: after Init or SetSyncDiv you must allow 100 ms for valid count rate readings
tryfunc(phlib.PH_SetStopOverflow(ct.c_int(dev[0]), ct.c_int(1), ct.c_int(65535)),\
        "SetStopOverflow")

#INITIALIZE CM110 communication on serial port COM1

try:
    serialPort = serial.Serial(port=portname,baudrate=9600,bytesize=8,timeout=1,stopbits=serial.STOPBITS_ONE)
except SerialException:
    print('COMM port already open. Will close')
    serialPort.close() #force close the serial port
    sys.exit(0)

#INTIIALIZE CM110
byte = serialPort.readline()                 #flush serial buffer
serialPort.write(command_serial)             #query CM110 serial number
byte = serialPort.readline()
print('CM110 serial number:',byte[0]*256+byte[1])
serialPort.write(command_step_size)          #set CM110 step size in nm  
byte = serialPort.readline()                 #read the return 24 status byte from CM110 to flush the buffer
serialPort.write(command_initial)            #request CM110 move to desired user initial position
byte = serialPort.readline()                 #read the return 24 status byte from CM110 to flush the buffer
t.sleep(3)
serialPort.write(command_curr_pos)           #query CM110 current position in nm
byte = serialPort.readline()
print('Current position:',byte[0]*256+byte[1],'nm')

#**********************************************************************************
#Main data acquisition loop
print("press RETURN to start measurement")
input()       #this is a retro feature of python
 
for i in range (0,total_steps+1):#Step CM110 across all wavelengths in desired range
       #query the current position of the CM110
       serialPort.write(command_curr_pos)   
       byte = serialPort.readline()
       
       #poll PicoHarp300 to get current counts on CHANNEL 0 and CHANNEL 1
       tryfunc(phlib.PH_GetCountRate(ct.c_int(dev[0]), ct.c_int(0), byref(countRate0)),\
             "GetCountRate")  #Gets countrate on channel 0
       tryfunc(phlib.PH_GetCountRate(ct.c_int(dev[0]), ct.c_int(1), byref(countRate1)),\
             "GetCountRate")  #Gets countrate on channel 1
       #tell the user what's going on
       print('Current position:',byte[0]*256+byte[1],'nm','CHANNEL 0:',countRate0.value,'CHANNEL 1:',countRate1.value)
    
       #start actual PicoHarp300 measurement
       tryfunc(phlib.PH_ClearHistMem(ct.c_int(dev[0]), ct.c_int(0)), "ClearHistMeM") #clear histogram
       tryfunc(phlib.PH_StartMeas(ct.c_int(dev[0]), ct.c_int(tacq)), "StartMeas")    #start PicoHarp300 acquisition
       
       #polls PicoHarp300 to see if it finished acquiring histogram, ctcstatus.value >0 when done
       ctcstatus = ct.c_int(0)
       while ctcstatus.value == 0: 
          tryfunc(phlib.PH_CTCStatus(ct.c_int(dev[0]), byref(ctcstatus)), "CTCStatus")
       
       #stop PicoHarp300 acquisition
       tryfunc(phlib.PH_StopMeas(ct.c_int(dev[0])), "StopMeas")                      
       tryfunc(phlib.PH_GetHistogram(ct.c_int(dev[0]), byref(counts), ct.c_int(0)),"GetHistogram")
       #Returns the count array 65536 long from internal memory of Picoharp300
       
       #Fill the master 2D data array here
       master_array[i]=counts
        
       #step CM110 to next wavelength
       serialPort.write(command_step)       
       byte=serialPort.readline()           #read the return 24 status byte from the CM110 to flush the buffer
       t.sleep(1)

#Dump master_array to file
np.savetxt(user_filename, np.transpose(master_array), fmt='%d')

#*******************************************************************************
#ON EXIT stuff here
serialPort.write(command_initial) #send CM110 to initial position
byte = serialPort.readline()      #read the return 24 status byte from CM110 to flush the buffer
t.sleep(5)                        #give the CM110 some time to reach its intial position
serialPort.close()                #close serial port COM1 to CM110
closeDevices()                    #shut down PicoHarp300




#flip the acquired master_array from high wavelength to low wavelength
master_array_flipped=np.flip(master_array,0) #0 indicates just the rows flipped

plt.pcolormesh(master_array_flipped,cmap="plasma")
plt.title("2D colormap of acquired TRES data")
plt.colorbar()
plt.show() 
