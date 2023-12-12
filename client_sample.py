import zmq

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://200.131.64.237:7001")

# Subscribe to multiple topics
subscriber.setsockopt(zmq.SUBSCRIBE, b'/observingconditions/humidity')
subscriber.setsockopt(zmq.SUBSCRIBE, b'/observingconditions/temperature')
subscriber.setsockopt(zmq.SUBSCRIBE, b'/observingconditions/windspeed')
subscriber.setsockopt(zmq.SUBSCRIBE, b'/observingconditions/winddirection')
subscriber.setsockopt(zmq.SUBSCRIBE, b'/observingconditions/pressure')

poller = zmq.Poller()
poller.register(subscriber, zmq.POLLIN)

while True:
    socks = dict(poller.poll(100))
    if socks.get(subscriber) == zmq.POLLIN:
        message = subscriber.recv_multipart()
        topic = message[0]
        data = message[1]  # Assuming the data is received as the second part of the multipart message
        print(f"Received: {topic.decode()} - {data.decode()}")
    