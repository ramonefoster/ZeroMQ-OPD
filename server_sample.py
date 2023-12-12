import time
import zmq
import requests

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
   
context = zmq.Context()

publer = context.socket(zmq.PUB)
publer.bind("tcp://192.168.11.71:7001")

puller = context.socket(zmq.PULL)
puller.bind("tcp://192.168.11.71:7005")

print("Codigo iniciado!")
poller = zmq.Poller()
poller.register(puller, zmq.POLLIN)

#foc_dev.move(8000)

previous_is_mov = '0'
previous_pos = '0'

publer.send_multipart([b'/focuser/0/ismoving', previous_is_mov.encode()])
publer.send_multipart([b'/focuser/0/postion', previous_pos.encode()])

while True:
    socks = dict(poller.poll(200))
    if socks.get(puller) == zmq.POLLIN:
        # Send our address and a random value
        # for worker availability
        msg_pull = puller.recv().decode()
        try:
            foc_dev.move(int(msg_pull))
        except:
            print("Invalid Position")

    publer.send_string(f"/focuser/0/name {FocuserMetadata.Name}")
    publer.send_string(f"/focuser/0/description {FocuserMetadata.Description}")

        # Retrieve current values
    current_is_mov = str(foc_dev.is_moving)
    current_pos = str(foc_dev.position)

    if current_is_mov != previous_is_mov:
        print("is_mov", current_is_mov)
        publer.send_multipart([b"/focuser/0/ismoving", current_is_mov.encode()])
        previous_is_mov = current_is_mov

    if current_pos != previous_pos:
        print("pos", current_pos)
        publer.send_multipart([b"/focuser/0/position", current_pos.encode()])
        previous_pos = current_pos

        # Add a small delay to avoid excessive processing
        # You can adjust this delay as needed
    time.sleep(0.1)