from PyQt5 import QtWidgets, uic, QtTest
from PyQt5.QtCore import QTimer, QUrl, QThreadPool, pyqtSlot, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt5 import QtGui

import zmq
import sys

from focuserDevice import Focuser

foc_dev = Focuser()
foc_dev.connected = True

class FocuserMetadata:
    """ Metadata describing the Focuser Device. Edit for your device"""
    Name = 'LNA Focuser'
    Version = '0.1.0'
    Description = 'Focuser Driver for Perkin-Elmer Focuser'
    DeviceType = 'Focuser'
    DeviceID = '3285e9af-8d1d-4f9d-b368-d129d8e9a24b' # https://guidgenerator.com/online-guid-generator.aspx
    Info = 'Alpaca Sample Device\nImplements IFocuser\nASCOM Initiative'
    MaxDeviceNumber = 1
    InterfaceVersion = 3

Ui_MainWindow, QtBaseClass = uic.loadUiType(r'assets\UI\focuser.ui')

class FocuserOPD(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.btnMove.clicked.connect(self.move_to)

        self.context = zmq.Context()       

        self.BarFocuser.setStyleSheet("QProgressBar::chunk ""{"'background-color: rgb(26, 26, 26)'"} QProgressBar { color: indianred; }")
        self.BarFocuser.setTextDirection(0) 

        self.previous_is_mov = None
        self.previous_pos = None

        self.is_moving = False
        self.position = 0

        self.start_client()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
    
    def start_client(self):
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(f"tcp://192.168.11.71:7001")
        topics_to_subscribe = '/focuser/0/'

        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topics_to_subscribe)

        self.poller = zmq.Poller()
        self.poller.register(self.subscriber, zmq.POLLIN)

        self.pusher = self.context.socket(zmq.PUSH)
        self.pusher.connect("tcp://192.168.11.71:7005")
    
    def move_to(self):
        if not self.is_moving:
            pos = self.txtMov.text()
            self.pusher.send_string(pos)
    
    def update(self):
        self.socks = dict(self.poller.poll(100))
        if self.socks.get(self.subscriber) == zmq.POLLIN:
            topic, message = self.subscriber.recv_multipart()
            topic = topic.decode()
            message = message.decode()
            try:      
                if topic == '/focuser/0/position':
                    pos = message
                    self.position = int(pos)                    
                    self.BarFocuser.setValue(int(self.position*3.16))
                elif topic == '/focuser/0/ismoving':
                    if message == 'True':
                        self.is_moving = True
                        self.statMov.setStyleSheet("background-color: lightgreen")
                    else:
                        self.is_moving = False
                        self.statMov.setStyleSheet("background-color: indianred")                
            except:
                self.BarFocuser.setValue(0)
        # else:
        #     print("ELSE")

if __name__ == "__main__":
    main_app = QtWidgets.QApplication(sys.argv)
    window = FocuserOPD()

    window.show()
    sys.exit(main_app.exec_())