from queue import Queue
from sensor_thread import SensorProducer

sensor_queue = Queue(maxsize=100)

sensor = SensorProducer(sensor_queue)

sensor.start()

while True:
    data = sensor_queue.get()

    print("[MAIN]", data)