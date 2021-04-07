from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore#, QtGui
import sys

from .PyLinkam import programmer
from .Pyqt_Widget import ControllerThread, ControllerSimple

def ControllerDisplay(port, prog_name, verbose = True):
    """
    basic display of the temperature returned by the pyrometer in its current opertion mode

    Parameters
    ----------
    port : string
        port used to establish the serial communication with the pyrometer
    """

    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    if verbose: 
        print('create programmer object')
    TMS94 = programmer(port)
    if verbose: 
        print('create programmer thread')
    prog_thread = ControllerThread(TMS94, verbose = verbose)
    if verbose: 
        print('create app')
    a = ControllerSimple(prog_thread, ControllerName = prog_name, verbose = verbose)
    a.show()
    app.exec_()
    
