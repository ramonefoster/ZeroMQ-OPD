import zmq

context = zmq.Context()

subscriber = context.socket(zmq.PUB)
subscriber.connect("tcp://192.168.11.71:7001")
subscriber.curve_publickey = b"seNhApUbLiCa_#ExeMpL0"  # PUBLIC KEY

subscriber.getsockopt_string(zmq.SUBSCRIBE, '/focuser/0/position')

while True:
    subscriber.recv_string()
    