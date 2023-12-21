from PyQt5 import QtWidgets, uic, QtTest
from PyQt5.QtCore import QTimer, QUrl, QThreadPool, pyqtSlot, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt5 import QtGui

import zmq
import sys
import json

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

Ui_MainWindow, QtBaseClass = uic.loadUiType('assets/UI/focus.ui')

class FocuserOPD(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.btnMove.clicked.connect(self.move_to)
        self.btnConnect.clicked.connect(self.connect)
        self.btnHalt.clicked.connect(self.halt)
        self.btnHome.clicked.connect(self.home)

        self.context = zmq.Context()       

        self.BarFocuser.setStyleSheet("QProgressBar::chunk ""{"'background-color: rgb(26, 26, 26)'"} QProgressBar { color: indianred; }")
        self.BarFocuser.setTextDirection(0) 

        self.previous_is_mov = None
        self.previous_pos = None

        self.connected = False
        self.is_moving = False
        self.homing = False
        self.position = 0

        self.start_client()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
    
    def start_client(self):
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(f"tcp://192.168.1.101:7001")
        topics_to_subscribe = ''

        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, topics_to_subscribe)

        self.poller = zmq.Poller()
        self.poller.register(self.subscriber, zmq.POLLIN)

        self.pusher = self.context.socket(zmq.PUSH)
        self.pusher.connect("tcp://192.168.1.101:7002")

        self.req = self.context.socket(zmq.REQ)
        self.req.connect("tcp://192.168.1.101:7003")
    
    def connect(self):
        self.pusher.send("CONN".encode())
    
    def home(self):
        self.pusher.send("INIT".encode())
    
    def disconnect(self):
        self.pusher.send("DC".encode())
    
    def halt(self):
        self.pusher.send('HALT'.encode())

    def move_to(self):
        if not self.is_moving:
            pos = self.txtMov.text()
            self.pusher.send_string(f"M{pos}")
    
    def update(self):
        self.socks = dict(self.poller.poll(100))
        if self.socks.get(self.subscriber) == zmq.POLLIN:
            message = self.subscriber.recv_string()
            data = json.loads(message)
            try: 
                self.position = int(data["position"])                    
                self.BarFocuser.setValue(int(self.position))
                if data["homing"]:
                    self.homing = True
                    self.statInit.setStyleSheet("background-color: lightgreen")
                else:
                    self.homing = False
                    self.statInit.setStyleSheet("background-color: indianred") 
                if data["is_moving"]:
                    self.is_moving = True
                    self.statMov.setStyleSheet("background-color: lightgreen")
                else:
                    self.is_moving = False
                    self.statMov.setStyleSheet("background-color: indianred") 
                if data["connected"]:
                    self.connected = True
                    self.statConn.setStyleSheet("background-color: lightgreen")
                else:
                    self.connected = False
                    self.statConn.setStyleSheet("background-color: indianred")               
            except:
                self.BarFocuser.setValue(0)
    
    def closeEvent(self, event):
        """Close application"""
        print("Closing")
        self.disconnect()
        event.accept()

if __name__ == "__main__":
    main_app = QtWidgets.QApplication(sys.argv)
    window = FocuserOPD()

    window.show()
    sys.exit(main_app.exec_())
