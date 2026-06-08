from queue import Queue
from threading import Thread
from sensor.sensor_thread import SensorProducer
from vision.yolo_thread import VisionProducer
from fusion.temporal_fusion import TemporalFusion
from cloud.mqtt_publisher import CloudPublisher
import time


sensor_queue = Queue(maxsize=100)
video_queue = Queue(maxsize=1)
fusion_queue = Queue(maxsize=50)

sensor = SensorProducer(sensor_queue)

vision = VisionProducer(
    "data/flood1.mp4",
    video_queue
)

fusion = TemporalFusion(
    sensor_queue,
    video_queue,
    fusion_queue
)

cloud = CloudPublisher()

sensor.start()
vision.start()
Thread(
    target=fusion.run,
    daemon=True
).start()


# Run system for 60 seconds and collect statistics
start_time = time.time()
message_count = 0

while True:
    if time.time() - start_time > 60:
        print("\n================================")
        print("[MAIN] Demo completed.")
        print(f"[MAIN] Total Messages: {message_count}")
        print("================================")
        break

    payload = fusion_queue.get()
    cloud.publish(payload)
    message_count += 1