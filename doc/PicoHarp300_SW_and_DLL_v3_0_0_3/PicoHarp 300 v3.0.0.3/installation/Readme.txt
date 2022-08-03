PicoHarp 300 TCSPC Software Version 3.0.0.3 
PicoQuant GmbH - October 2015


Introduction

The PicoHarp 300 is a TCSPC system with USB 2.0 interface. 
It requires a 686 class PC with USB 2.0 host controller,
1 GB of memory and at least 1 GHz CPU clock. The PicoHarp software 
is suitable for Windows 7, 8 and 10, including the x64 versions. 


What's new in this version (3.0.0.3)

- a firmware fix to deal with occasional system errors


What was new in version 3.0.0.2

- a firmware fix for lost counts at very short measurement times (all modes)
- a firmware fix for T3 mode (data was corrupted at maximum binning)
- simplified access to support information and the support web site
- a new device driver meeting most recent signature requirements
- official support of Windows 10 (but dropping support of Windows XP and Vista)


What was new in version 3.0.0.1

- a bugfix to deal with firmware errors in some hardware devices
- functionality and documentation remained unchanged.


What was new in version 3.0.0.0 (the last major release "3.0")

- a programmable time offset in the sync input to replace adjustable 
  cable delays (4 ps resolution, ±100ns)
- a programmable time offset in all PHR 800 router channels to tune 
  for relative delay (4 ps resolution, ±8ns)
- a programmable marker holdoff  time to suppress marker glitches
- export of histograms directly to ASCII files
- a new future proof file format, unified with that of SymPhoTime 64 
- acquisition offset now also applicable in T3 mode
- prompts for sample changing in TRES mode


Installation 

The PicoHarp software can be distributed on CD or via download.
If you received the package via download it may be packed in a 
zip-file. Unzip that file and place the distribution setup files in a 
temporary disk folder.

Dependent on your version of Windows you may need to log on as administrator
in order to perform the software setup. It is important to perform the setup 
as administator because otherwise the device driver installation will fail.
Only if you intend to use the software without hardware, e.g. as a file 
viewer, you may run setup without administrator rights.

The setup program will install the PicoHarp software including driver, 
manual, online-help, sample data and programming demos for data access. 
Dependent on the version of Windows you may be  prompted to confirm the 
driver installation.

To uninstall the PicoHarp software you may need to log on as administrator 
(dependent on your version of Windows). Backup your measurement data.
From the start menu select:  PicoQuant - PicoHarp 300 v.x.x  >  uninstall.
Alternatively you can use the Control Panel Wizard 'Add/Remove Programs'
(in some Windows versions this Wizard is called 'Software')


Disclaimer

PicoQuant GmbH disclaims all warranties with regard to this software 
and associated documentation including all implied warranties of 
merchantability and fitness. In no case shall PicoQuant GmbH be 
liable for any direct, indirect or consequential damages or any material 
or immaterial damages whatsoever resulting from loss of data, time 
or profits arising from use or performance of this software.


License and Copyright Notice

With the PicoHarp hardware product you have purchased a license to use 
the PicoHarp software. You have not purchased the software itself. 
The software is protected by copyright and intellectual property laws. 
You may not distribute the software to third parties or reverse engineer, 
decompile or disassemble the software or any part thereof. Copyright 
of this software including manuals belongs to PicoQuant GmbH. No parts 
of it may be reproduced or translated into other languages without written 
consent of PicoQuant GmbH. You may use and modify demo code to create your 
own programs. Original or modified demo code may be re-distributed, 
provided that the original disclaimer and copyright notes are not 
removed from it.


Trademark Disclaimer

PicoHarp, HydraHarp TimeHarp and NanoHarp are registered trademarks of 
PicoQuant GmbH. Other products and corporate names appearing in the product 
manuals or in the online documentation may or may not be registered trademarks 
or copyrights of their respective owners. They are used only for identification 
or explanation and to the owner’s benefit, without intent to infringe.


Contact and Support

PicoQuant GmbH
Rudower Chaussee 29
12489 Berlin, Germany
Phone +49 30 6392 6929
Fax   +49 30 6392 6561
email info@picoquant.com
www http://www.picoquant.com
