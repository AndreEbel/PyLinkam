# -*- coding: utf-8 -*-

#from PyQt5 import QtGui
from PyQt5.QtWidgets import  QWidget,QLineEdit, QLabel,QVBoxLayout, QHBoxLayout, QPushButton#,QTabWidget
from PyQt5.QtGui import QIntValidator # QDoubleValidator,
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal, QThread
import numpy as np

from time import sleep


class ControllerThread(QThread):
    temperature = pyqtSignal(np.float)
    status = pyqtSignal(str)
    error = pyqtSignal(str)
    on = False
    sleep_time = 1
    def __init__(self, controller, verbose = True):
        super().__init__()
        self.controller = controller
        self.verbose = verbose
        
    def run(self):
        if self.verbose: 
            print('running')
        self.on = True
        # read the temperature, status and error from the controller
        while self.on:
            #self.controller.get_T_bytes()
            self.temperature.emit(self.controller.temperature)
            sleep(self.sleep_time)
            self.status.emit(self.controller.status)
            sleep(self.sleep_time)
            self.error.emit(self.controller.error)
            sleep(self.sleep_time)
        self.status.emit('Furnace off')
    def stop(self):
        """Sets on flag to False and waits for thread to finish"""
        self.on = False
        self.wait()
        
class ControllerSimple(QWidget):
    def __init__(self, ControllerThread, ControllerName= 'TMS94', verbose = True):
        super().__init__()
        self.verbose = verbose
        self.controller_thread = ControllerThread
        self.controller_thread.start()
        self.setWindowTitle(ControllerName)
        # start the thread
        self.controller_thread.start()
        self.controller_thread.on = True
        self.controller_thread.temperature.connect(self.update_temp)
        self.controller_thread.status.connect(self.update_status)
        self.controller_thread.error.connect(self.update_error)
        
        # main vertical layout
        self.vbox = QVBoxLayout()
        
        # 1st row: Display, status, error
        display_layout = QHBoxLayout()
        self.temperature_display= QLabel('No value')
        self.status_display= QLabel('No value')
        self.error_display= QLabel('No value')
        display_layout.addWidget(self.temperature_display)
        display_layout.addWidget(self.status_display)
        display_layout.addWidget(self.error_display)
        self.vbox.addLayout(display_layout)
        
        
        #2nd row: start and stop program
        ss_layout = QHBoxLayout()
        self.ss_button = QPushButton('Start program',self)
        self.ss_button.clicked.connect(self.ClickStart)
        self.hold_button = QPushButton('Hold',self)
        self.hold_button.clicked.connect(self.ClickHold)
        ss_layout.addWidget(self.ss_button)
        ss_layout.addWidget(self.hold_button)
        self.vbox.addLayout(ss_layout)
        
        #3rd row: rate and limit commands 
        rl_layout = QHBoxLayout()
        rl_inputs = QVBoxLayout()
        rl_buttons = QVBoxLayout()
        
        #rate
        self.rate_input = QLineEdit()
        self.rate_input.setValidator(QIntValidator(top = 10))
        self.rate_input.setMaxLength(2)
        self.rate_input.setText('0')
        self.rate_input.setAlignment(Qt.AlignRight)
        self.rate_button = QPushButton('Set rate (°C)',self)
        self.rate_button.clicked.connect(self.ClickSetRate)
        #limit
        self.limit_input = QLineEdit()
        self.limit_input.setValidator(QIntValidator(top = 1500))
        self.limit_input.setText('0')
        self.limit_input.setMaxLength(4)
        self.limit_input.setAlignment(Qt.AlignRight)
        self.limit_button = QPushButton('Set limit (°C)',self)
        self.limit_button.clicked.connect(self.ClickSetLimit)
        
        
        rl_inputs.addWidget(self.rate_input)
        rl_inputs.addWidget(self.limit_input)
        rl_buttons.addWidget(self.rate_button)
        rl_buttons.addWidget(self.limit_button)
        
        rl_layout.addLayout(rl_inputs)
        rl_layout.addLayout(rl_buttons)
        self.vbox.addLayout(rl_layout)
        
        self.setLayout(self.vbox)
    
    @pyqtSlot(np.float)
    def update_temp(self, T_C):
        """
        Updates the temperature displayed in the app
        """
        text = f'{T_C}'
        self.temperature_display.setText(text)
        
    @pyqtSlot(str)
    def update_status(self, status):
        """
        Updates the status displayed in the app
        """
        text = status
        self.status_display.setText(text)
    
    @pyqtSlot(str)
    def update_error(self, error):
        """
        Updates the error displayed in the app
        """
        text = error
        self.error_display.setText(text)
    
    # Activates when Start/Stop video button is clicked to Start (ss_video
    def ClickStart(self):
        if self.verbose: 
            print('start program')
        self.ss_button.clicked.disconnect(self.ClickStart)
        self.controller_thread.controller.start()
        if self.verbose: 
            print('start command passed')
       
        # Change button to stop
        self.ss_button.setText('Stop')
        self.hold_button.setText('Hold')
        
        # Stop the video if button clicked
        self.hold_button.clicked.connect(self.ClickHold)
        self.ss_button.clicked.connect(self.ClickStop)
    
    # Activates when Start/Stop video button is clicked to Stop (ss_video)
    def ClickStop(self):
        self.ss_button.clicked.disconnect(self.ClickStop)   
        self.controller_thread.controller.stop()
        self.ss_button.setText('Start')
        self.ss_button.clicked.connect(self.ClickStart)
       
    
    def ClickHold(self):
        self.hold_button.clicked.disconnect(self.ClickHold)
        self.ss_button.clicked.disconnect(self.ClickStop) 
        self.ss_button.clicked.connect(self.ClickStart)
        self.ss_button.setText('Start')
        self.controller_thread.controller.hold()
        self.hold_button.setText('Holding')
       
       
        
    def ClickSetRate(self): 
        r = self.rate_input.text()
        if r !='': 
            e = float(r.replace(',', '.'))
            self.controller_thread.controller.set_rate(e)
            self.rate_input.setText(str(self.controller_thread.controller.rate))
        if self.verbose: 
            print('input', e)
            print('rate', self.controller_thread.controller.rate)
            
    def ClickSetLimit(self): 
        r = self.limit_input.text()
        if r !='': 
            e = float(r.replace(',', '.'))
            self.controller_thread.controller.set_limit(e)
            self.limit_input.setText(str(self.controller_thread.controller.limit))
            print('input', e)
        if self.verbose: 
            print('input', e)
            print('limit',self.controller_thread.controller.limit)
        
    def closeEvent(self, event):
        if self.controller_thread.on: 
            self.controller_thread.temperature.disconnect(self.update_temp)
            self.controller_thread.status.disconnect(self.update_status)
            self.controller_thread.error.disconnect(self.update_error)
            self.controller_thread.stop()
            self.controller_thread.controller.ser.close()
        event.accept()