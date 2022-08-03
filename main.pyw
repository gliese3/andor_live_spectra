from configparser import Interpolation
import sys
from PyQt5 import QtCore, QtWidgets, QtGui, QtTest
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib_additional import MplCanvas

from list_ports import seeAvaliablePorts # to view available ports

import numpy as np
import serial, time
import ctypes as ct

from interface import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):        

        # from compiled file
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Lifetime") #! edit here
        
#================================ CONNECTIONS =================================

        self.start_but.clicked.connect(self.onStart)
        self.apply_settings_but.clicked.connect(self.onApply)
        self.save_all_data_action.triggered.connect(self.onSaveAllData)
        self.save_cut_action.triggered.connect(self.onSaveCutData)
        self.single_mode_action.triggered.connect(self.onModeChoose)
        self.multiple_mode_action.triggered.connect(self.onModeChoose)
        self.plot_cut_but.clicked.connect(self.onPlotCut)
        self.clear_cut_but.clicked.connect(self.onClear)

#================================ /CONNECTIONS ================================

        # VARIABLES
        self.mode = "Multiple" # mode
        self.cb = None # color bar init
        self.cut_data = [] # init cut data
        

        # CONSTANTS
        # from phdefin.h
        self.HISTCHAN = 65536
        self.MAXDEVNUM = 8
        self.MODE_HIST = 0
        
        self.DEVICE = 0 # we use only this device number

        self.UPDATE_TIME = 500 # update current values time
        
        # open window in maximized size
        self.showMaximized()
        
        # TIMERS
        self.update_cur_values_timer = QtCore.QTimer()
        self.update_cur_values_timer.timeout.connect(self.updateCurrentValues)
        
        self.remaining_time_timer = QtCore.QTimer()
        self.remaining_time_timer.setSingleShot(True)

        # set icon
        self.setWindowIcon(QtGui.QIcon("images/laser.png"))
        
        # plot init
        self.canvas = MplCanvas(self) # canvas to plot
        self.toolbar = NavigationToolbar(self.canvas, self) # navigation toolbar
        
        # arrange matplotlib elements on GUI
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.canvas)
        
        # find all COM ports
        self.avaliable_ports = seeAvaliablePorts()
        if self.avaliable_ports:
            
            # enbale start button if there are avaliable COM ports
            self.apply_settings_but.setEnabled(True)
            for port in self.avaliable_ports:
                self.port_comBox.addItem(port) # add items to combo box
        else:
            # some pause before showing the message
            QtTest.QTest.qWait(500)
            QtWidgets.QMessageBox.critical(self, "Port", "No avalaible COM ports.")
            return

#=================================== SLOTS ====================================
    
    def onClear(self):
        self.canvas.axs[0].clear()
        self.canvas.draw()


    def onPlotCut(self):
        
        # reset axis
        self.canvas.axs[0].clear()
        
        # init cut data
        self.cut_data = []
        
        # need for proper work of "Reset" button in matplotlib
        self.toolbar.update()

        self.canvas.axs[0].grid()
        

        # check cut type
        if self.lambda_radBut.isChecked():
            self.cut_type = "lambda"
            self.canvas.axs[0].set_title("λ cut")
            self.canvas.axs[0].set_xlabel("Time, ns")
            self.canvas.axs[0].set_ylabel("Counts")
            self.canvas.axs[0].set_xlim(0, 25)
        else:
            self.cut_type = "tau"
            self.canvas.axs[0].set_title("τ cut")
            self.canvas.axs[0].set_xlabel("λ, nm")
            self.canvas.axs[0].set_ylabel("Counts")

        raw_values = self.values_lineEdit.text()

        try:
            values = raw_values.split(";")

            # check that everything is digit
            values_bool = [val.replace('.', '').isdigit() for val in values]
            flag = all(values_bool)
            if not flag:
                QtWidgets.QMessageBox.critical(self, "Cut", "Enter proper values!")
                return
        except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Cut", e)
                return

        # plot cuts
        if self.cut_type == "lambda":
            keys = list(self.time_pos_map.keys())
            x_data = list([float(item) for item in keys])
            for val in values: # values is a list with chosen lambdas
                if val in self.lam_pos_map:
                    data = self.master_array[self.lam_pos_map[val]]
                    self.canvas.axs[0].plot(x_data, data, label="λ = " + val + " nm")
                    self.cut_data.append(data)
                else:
                    self.statusbar.showMessage(f"λ = {val} is not correct!", 3000)
                    QtWidgets.QMessageBox.warning(self, "Cut", f"λ = {val} is not correct!")

        elif self.cut_type == "tau":
            keys = list(self.time_pos_map.keys())
            keys_float = list([float(item) for item in keys])
            for val in values: # values is a list with chosen taus
                index = np.searchsorted(keys_float, float(val))
                if index > len(keys_float) - 1: index -= 1
                key = str(keys[index])
                data = self.master_array[:, self.time_pos_map[key]]
                self.canvas.axs[0].plot(self.lambda_array,
                                        data,
                                        "-o",
                                        label="τ = " + key + " ns",
                                        markersize=5)
                self.cut_data.append(data)

        self.canvas.axs[0].legend()
        self.canvas.draw()

        
    def onSaveAllData(self):
        save_file_name = QtWidgets.QFileDialog.getSaveFileName(
            self, 
            caption="Save data to file",
            filter="*.csv")[0]

        if not save_file_name: # no file name
            return

        # try:
        
        # make proper header
        header = f"lambdas: {list(self.lambda_array)}\nstep: {self.wavelen_step} nm\naq. time: {self.tacq / 1000} secs"
        np.savetxt(save_file_name, np.concatenate((np.array([self.time_array]).T, self.master_array.T), axis=1), fmt="%1.3f", header=header)
        
        # except Exception:
        #     QtWidgets.QMessageBox.critical(self, "Save file", "Error saving file.")
    
    
    def onSaveCutData(self):
        save_file_name = QtWidgets.QFileDialog.getSaveFileName(
            self, 
            caption="Save cut data to file",
            filter="*.csv")[0]

        if not save_file_name: # no file name
            return

        try:
            np.savetxt(save_file_name, np.transpose(self.cut_data), fmt="%d")
        except Exception:
            QtWidgets.QMessageBox.critical(self, "Save file", "Error saving file.")
            

    def onApply(self):
        
        # success flag
        self.is_ok = True
        
        self.emergancy_stop = False

        # configure COM port
        try:
            self.serial_port = serial.Serial()
            self.serial_port.port = self.port_comBox.currentText()
            self.serial_port.baudrate = 9600
            self.serial_port.bytesize = 8
            self.serial_port.stopbits = serial.STOPBITS_ONE
            self.serial_port.timeout = 0.05 # secs
            self.serial_port.open() # open port
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Port", "Error opening serial port.")
            return
        
        ## READ VALUES FROM GUI
        # cm110 settings
        self.initial_wavelen = self.initial_wavelen_spBox.value()
        self.end_wavelen     = self.end_wavelen_spBox.value()
        self.wavelen_step    = self.wavelen_step_spBox.value()

        # array of available lambdas
        self.lambda_array = range(self.initial_wavelen,
                                    self.end_wavelen + self.wavelen_step,
                                    self.wavelen_step)
        
        # picoharp300 settings
        self.binning         = self.binning_spBox.value()
        self.offset          = self.offset_spBox.value() * 1000 # in nanosecs
        self.tacq            = self.tacq_spBox.value() * 1000 # in secs
        self.sync_divider    = self.sync_divider_spBox.value()
        self.sync_offset     = self.sync_offset_spBox.value()
        self.cfd_zero_cross0 = self.cfd_zero_cross0_spBox.value()
        self.cfd_level0      = self.cfd_level0_spBox.value()
        self.cfd_zero_cross1 = self.cfd_zero_cross1_spBox.value()
        self.cfd_level1      = self.cfd_level1_spBox.value()
        
        # estimate experiment time in seconds
        self.est_time = self.tacq * len(self.lambda_array)
        
        if self.mode == "Multiple":
            self.total_steps = int((self.end_wavelen - self.initial_wavelen) / self.wavelen_step) + 1
        else:
            self.total_steps = 1
            
        # PicoHarp300 always takes 65536 elements
        self.master_array = np.zeros((self.total_steps, self.HISTCHAN), dtype=int)
        
        # DEFINITIONS: CM110 commands summarized (DO NOT CHANGE)
        self.command_serial    = bytearray([56, 19]) # query serial number of unit        
        self.command_curr_pos  = bytearray([56, 0]) # query current grating position in nm
        self.command_step_size = bytearray([55, self.wavelen_step]) # this implicitly assumes step_wave fits into 1 byte (0-255)
        self.command_step      = bytearray([54]) # tells CM110 to step 1, overkill but whatever
        init_pos               = self.initial_wavelen.to_bytes(2, "big") # big means most significant bit first
        self.command_initial   = bytearray([16, init_pos[0], init_pos[1]]) # command goto initial position in nm
            
        #REQUIRED: PicoHarp300 variables to store information read from DLLs (DO NOT CHANGE)
        self.counts = (ct.c_uint * self.HISTCHAN)() # "()" to create an array
        self.libVersion = ct.create_string_buffer(b"", 8)
        self.hwSerial = ct.create_string_buffer(b"", 8)
        self.hwPartno = ct.create_string_buffer(b"", 8)
        self.hwVersion = ct.create_string_buffer(b"", 8)
        self.hwModel = ct.create_string_buffer(b"", 16)
        self.errorString = ct.create_string_buffer(b"", 40)
        self.resolution = ct.c_double()
        self.countRate0 = ct.c_int()
        self.countRate1 = ct.c_int()
        self.flags = ct.c_int()
        
        # load lib
        self.phlib = ct.CDLL("libs/phlib64.dll")
        
        # initialize communication with PicoHarp300
        retcode = self.phlib.PH_OpenDevice(ct.c_int(0), self.hwSerial)
        if retcode == 0:
                print(f"PicoHarp300 is working.")
        else:
            print(f"PicoHarp300 is not working.")      
            
        #INITIALIZE PicoHarp300
        self.statusbar.showMessage("Initilizing PicoHarp300...")

        # initialize
        self.tryFunc(self.phlib.PH_Initialize,
                    args = [ct.c_int(self.DEVICE),
                            ct.c_int(self.MODE_HIST)])
        
        # getHardwareInfo
        self.tryFunc(self.phlib.PH_GetHardwareInfo,
                    args = [self.DEVICE,
                            self.hwModel,
                            self.hwPartno,
                            self.hwVersion])
        
        # calibrate
        self.tryFunc(self.phlib.PH_Calibrate,
                    args = [ct.c_int(self.DEVICE)])
        
        # setSyncDiv
        self.tryFunc(self.phlib.PH_SetSyncDiv,
                    args = [ct.c_int(self.DEVICE),
                            ct.c_int(self.sync_divider)])
        
        # setInputCFD
        self.tryFunc(self.phlib.PH_SetInputCFD,
                    args = [ct.c_int(self.DEVICE),
                            ct.c_int(0),
                            ct.c_int(self.cfd_level0),
                            ct.c_int(self.cfd_zero_cross0)])

        # setInputCFD
        self.tryFunc(self.phlib.PH_SetInputCFD,
                    args = [ct.c_int(self.DEVICE),
                            ct.c_int(1),
                            ct.c_int(self.cfd_level1),
                            ct.c_int(self.cfd_zero_cross1)])
            
            
        # set self.binning
        self.tryFunc(self.phlib.PH_SetBinning,
                    args = [ct.c_int(self.DEVICE),
                            ct.c_int(self.binning)])
        
        # set self.offset
        self.tryFunc(self.phlib.PH_SetOffset,
                    args = [ct.c_int(self.DEVICE),
                            ct.c_int(self.offset)])
        
        # getResolution
        self.tryFunc(self.phlib.PH_GetResolution,
                    args = [ct.c_int(self.DEVICE),
                            ct.byref(self.resolution)])
        
        # set sync offset
        self.tryFunc(self.phlib.PH_SetSyncOffset,
                    args = [ct.c_int(self.DEVICE),
                            ct.c_int(self.sync_offset)])
        
        # Note: after Init or SetSyncDiv you must allow 100 ms for valid count rate readings
        QtTest.QTest.qWait(200)
        
        # setStopOverflow
        self.tryFunc(self.phlib.PH_SetStopOverflow,
                    args = [ct.c_int(self.DEVICE),
                            ct.c_int(1),
                            ct.c_int(65535)])

        # enable start button
        if self.is_ok:
            self.statusbar.showMessage("Initilizing PicoHarp300... Ok!", 3000)

            #INTIIALIZE CM110
            self.statusbar.showMessage("Initilizing CM110...", 3000)
            self.serial_port.flush() # flush serial buffer    
                    
            self.serial_port.write(self.command_serial) # query CM110 serial number
            self.serial_port.readline()

            self.serial_port.write(self.command_step_size) # set CM110 step size in nm  
            self.serial_port.readline()           
            
            self.serial_port.write(self.command_initial) # request CM110 move to desired user initial position
            self.serial_port.readline()
            self.statusbar.showMessage("Initilizing CM110... Ok!", 3000)
            QtTest.QTest.qWait(3000) # some pause

            self.statusbar.showMessage("Ready to start!", 3000)
            self.start_but.setEnabled(True)
            
            # launch timer
            self.update_cur_values_timer.start(self.UPDATE_TIME)
            
            # init progress bar
            self.prog_bar.reset()

            # create a map between lambdas and their position in self.master array
            # to plot cuts easily
            self.lam_pos_map = {}
            for i, lam in enumerate(self.lambda_array):
                self.lam_pos_map[str(lam)] = i

            # create a map between times and their position in self.master array
            # to plot cuts easily
            self.time_pos_map = {}
            self.time_array = []
            for i in range(self.HISTCHAN):
                val = i * self.resolution.value / 1000
                self.time_array.append(val)
                self.time_pos_map[str(val)] = i # in nano seconds

        else:
            self.statusbar.showMessage("Initilizing PicoHarp300... Bad!")
            self.serial_port.close()
        
        
    def onStart(self):

        # check type
        but_text = self.start_but.text()
        
        if but_text == "Start measurment":
            
            # change button text
            self.start_but.setText("Stop measurment")

            # clear canvas
            self.canvas.axs[1].clear()
            self.canvas.axs[1].set_title("Real time heatmap")
            self.canvas.axs[1].set_yticks(np.arange(self.initial_wavelen, 
                                                    self.end_wavelen + self.wavelen_step,
                                                    step=self.wavelen_step))
            # self.canvas.axs[1].set_yticklabels(self.lambda_array)
            self.canvas.axs[1].grid(color='w', linewidth=1, axis="y", alpha=0.3)

            if self.cb: # if color bar exists
                self.cb.remove()

            # init plot
            self.im = self.canvas.axs[1].imshow(self.master_array, #! maybe flip array
                                        cmap="jet",
                                        aspect="auto",
                                        interpolation="spline36",
                                        extent=[0,
                                                self.resolution.value * self.HISTCHAN / 1000, # in nano seconds
                                                self.end_wavelen,
                                                self.initial_wavelen])
                                        
            self.canvas.axs[1].set_xlabel("Time, ns") #! check if ps
            self.canvas.axs[1].set_ylabel("λ, nm")
                                        
            # set x axis limit
            self.canvas.axs[1].set_xlim(0, 25)

            self.cb = self.canvas.fig.colorbar(self.im)
            self.cb.set_label("Counts")
            self.canvas.draw()
            
            # init progress bar
            self.prog_bar.setRange(0, self.total_steps - 1)
            
            # start experiment timer
            self.remaining_time_timer.start(self.est_time)
            
            # step CM110 across all wavelengths in desired range
            for i in range(self.total_steps):
                
                # poll PicoHarp300 to get current counts on CHANNEL 0 and CHANNEL 1
                # gets countrate on channel 0
                self.tryFunc(self.phlib.PH_GetCountRate,
                            args = [ct.c_int(self.DEVICE),
                                    ct.c_int(0),
                                    ct.byref(self.countRate0)])
                
                # gets countrate on channel 1
                self.tryFunc(self.phlib.PH_GetCountRate,
                            args = [ct.c_int(self.DEVICE),
                                    ct.c_int(1),
                                    ct.byref(self.countRate1)])            
                
                # start actual PicoHarp300 measurement
                # clearHistMeM
                self.tryFunc(self.phlib.PH_ClearHistMem,
                            args = [ct.c_int(self.DEVICE),
                                    ct.c_int(0)])
                
                
                # start PicoHarp300 acquisition
                self.tryFunc(self.phlib.PH_StartMeas,
                            args = [ct.c_int(self.DEVICE),
                                    ct.c_int(self.tacq)])   
                
                # polls PicoHarp300 to see if it finished acquiring histogram, 
                # ctcstatus.value > 0 when done
                ctcstatus = ct.c_int(0)
                while ctcstatus.value == 0:
                    self.tryFunc(self.phlib.PH_CTCStatus,
                                args = [ct.c_int(self.DEVICE),
                                        ct.byref(ctcstatus)])
                    
                    # update timer value
                    rem_time = round(self.remaining_time_timer.remainingTime() / 1000) # in secs
                    if rem_time >= 0:
                        self.remaining_time_lab.setText("~" + str(rem_time))
                    
                    # process events for emergancy stop
                    QtWidgets.QApplication.processEvents()
                
                # stop PicoHarp300 acquisition
                self.tryFunc(self.phlib.PH_StopMeas,
                            args = [ct.c_int(self.DEVICE)])
                
                # get histogram
                self.tryFunc(self.phlib.PH_GetHistogram,
                            args = [ct.c_int(self.DEVICE),
                                    ct.byref(self.counts),
                                    ct.c_int(0)])
                
                # fill the master 2D data array here
                self.master_array[i] = self.counts
                    
                # step CM110 to next wavelength
                self.serial_port.write(self.command_step)       
                self.serial_port.readline()
                
                # draw in pause
                start = time.time()
                self.im.set_data(self.master_array)
                self.im.set_clim(vmin=self.master_array.min(), vmax=self.master_array.max())
                self.canvas.draw()

                delta = round( (time.time() - start) * 1000 ) # in millisec
                if delta < 1000: # 1000 ms
                    QtTest.QTest.qWait(delta)
                    
                # update progress bar
                if self.total_steps != 1: # to avoid undetermined state
                    self.prog_bar.setValue(i)
                
                if self.emergancy_stop:
                    break

            # to proper reset view
            self.toolbar.update()
            
            # ON EXIT stuff here
            self.serial_port.write(self.command_initial) # send CM110 to initial position
            self.serial_port.readline() # read the return 24 status byte from CM110 to flush the buffer
            self.statusbar.showMessage("Finished!", 3000)
            self.remaining_time_lab.setText("-")

            # disable start button
            self.start_but.setEnabled(False)
            
            # change button text
            self.start_but.setText("Start measurment")
            
        elif but_text == "Stop measurment":
            self.emergancy_stop = True


    def onModeChoose(self):
        """
        Switch checked mode.
        
        """
        action = self.sender()
        action_name = self.sender().objectName()
        if action_name == "single_mode_action" and action.isChecked():
            self.multiple_mode_action.setChecked(False)
            self.mode = "Single"

            # disable some elements
            self.end_wavelen_spBox.setEnabled(False)
            self.wavelen_step_spBox.setEnabled(False)

        elif action_name == "multiple_mode_action" and action.isChecked():
            self.single_mode_action.setChecked(False)
            self.mode = "Multiple"

            # enable some elements
            self.end_wavelen_spBox.setEnabled(True)
            self.wavelen_step_spBox.setEnabled(True)
#=================================== /SLOTS ====================================


#================================= FUNCTIONS ===================================

    def closeDevices(self):
        
        # close all devices
        for i in range(self.MAXDEVNUM):
            self.phlib.PH_CloseDevice(ct.c_int(i))


    def tryFunc(self, func, args):
        ret_value = func(*args)
        if ret_value < 0: # bad value
            
            # write error to <self.errorString>
            self.phlib.PH_GetErrorString(self.errorString, ct.c_int(ret_value))
            
            print("-"*50)
            print(func.__name__ + "error:")
            print(f"Error value: {self.errorString.value.decode('utf-8')}")
            print("-"*50, "\n")
            
            self.is_ok = False
            self.closeDevices()
            
    
    def updateCurrentValues(self):
        """
        Update current values (color frame).
        
        """
        if self.serial_port.isOpen():
            # update current wavelength
            self.serial_port.write(self.command_curr_pos) # query CM110 current position in nm
            byte = self.serial_port.readline()
            try:
                if byte: # is not empty
                    self.current_wavelen_lab.setText(str(byte[0] * 256 + byte[1]))

                # update current count rate on channel 0
                self.tryFunc(self.phlib.PH_GetCountRate,
                                args = [ct.c_int(self.DEVICE),
                                        ct.c_int(0),
                                        ct.byref(self.countRate0)])
                self.cannel0_lab.setText(str(self.countRate0.value))
                    
                # update current count rate on channel 1
                self.tryFunc(self.phlib.PH_GetCountRate,
                            args = [ct.c_int(self.DEVICE),
                                    ct.c_int(1),
                                    ct.byref(self.countRate1)])
                self.channel1_lab.setText(str(self.countRate1.value))
            except Exception:
                print(byte)
        else:
            self.current_wavelen_lab.setText("-")
            self.cannel0_lab.setText("-")
            self.channel1_lab.setText("-")
         
         
    def closeEvent(self, event):
        try:
            self.serial_port.close() # close serial port COM1 to CM110
            self.closeDevices() # shut down PicoHarp300
            event.accept() # let the window close
        except Exception:
              event.accept()      
    
#================================= /FUNCTIONS ==================================


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_() 
