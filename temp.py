import serial

serial_port = serial.Serial()
serial_port.port = "COM1"
serial_port.baudrate = 9600
serial_port.bytesize = 8
serial_port.stopbits = serial.STOPBITS_ONE
serial_port.timeout = 0.5

initial_wavelen = 496
wavelen_step    = 2

# DEFINITIONS: CM110 commands summarized (DO NOT CHANGE)
command_serial    = bytearray([56, 19]) # query serial number of unit        
command_curr_pos  = bytearray([56, 0]) # query current grating position in nm
command_step_size = bytearray([55, wavelen_step]) # this implicitly assumes step_wave fits into 1 byte (0-255)
command_step      = bytearray([54]) # tells CM110 to step 1, overkill but whatever
init_pos          = initial_wavelen.to_bytes(2, "big") # big means most significant bit first
command_initial   = bytearray([16, init_pos[0], init_pos[1]]) # command goto initial position in nm


serial_port.open()
serial_port.open()

serial_port.write(command_curr_pos) # query CM110 serial number
serial_port.reset_input_buffer()
rep = serial_port.readline()
print(256 * rep[0] + rep[1])



