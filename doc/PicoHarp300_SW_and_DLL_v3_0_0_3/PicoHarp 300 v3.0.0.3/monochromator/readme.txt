Mono.dll v1.1.0.9

The PicoHarp software supports monochromator control and the
measurement of Time-Resolved Emission Spectra (TRES). It requires the
dynamic link library "Mono.dll" to control the monochromator.
Currently Mono.dll works with selected monochromators, some requiring 
dedicated controller hardware from PicoQuant. If supported hardware 
is installed, Mono.dll must be placed in the same folder as PicoHarp.exe. 
In that case the monochromator configuration file "monochromator.cfg"
must also be placed in the same folder. The contents of this file are
readily adjusted for complete spectrometers sold by PicoQuant. It should
not be changed by the user. The "monochromator.cfg" provided here
is set up for a simulation mode that works without real stepper motor 
hardware. Do not use it for any other purpose. If you need to replace 
your configuration after a complete re-installation, use the 
"monochromator.cfg" file specifically adjusted for your spectrometer 
(usually supplied on floppy disk). Misconfigurations may lead to hardware 
damage. In case of doubt contact PicoQuant support.
Note that dependent on the physical connection of the stepper motor 
controller (PCI, USB, RS232) a device driver and special DLLs may also be
required. These are pre-installed on computers delivered with PicoQuant
spectrometers. If they need to be re-installed, please use the driver
disk(s) delivered with the computer.


- Disclaimer -

PicoQuant GmbH disclaims all warranties with regard to this software including 
all implied warranties of merchantability and fitness. In no case shall 
PicoQuant GmbH be liable for any direct, indirect or consequential damages or 
any material or immaterial damages whatsoever resulting from loss of data, time 
or profits arising from use or performance of this software.
Demo source code is provided 'as is' without any warranty whatsoever.
By installing the software you agree to these terms.


- License and Copyright Notice -

With the PicoHarp hardware you have purchased a license to use this
software. You have not purchased the software itself. 
The software is protected by copyright and intellectual property laws. 
You may not distribute the software to third parties or reverse engineer, 
decompile or disassemble the software or part thereof. You may use and modify 
demo code to create your own software. Original or modified demo code may be 
re-distributed, provided that the original disclaimer and copyright notes are 
not removed from it.

HydraHarp, PicoHarp, TimeHarp and NanoHarp are registered trademarks 
of PicoQuant GmbH. Other products and corporate names appearing in the 
product manuals or in the online documentation may or may not be registered 
trademarks or copyrights of their respective owners. They are used only 
for identification or explanation and to the owner’s benefit, without 
intent to infringe.


- Contact and Support -

PicoQuant GmbH
Rudower Chaussee 29
12489 Berlin, Germany
Phone +49 30 6392 6929
Fax   +49 30 6392 6561
email info@picoquant.com