# Integrated Concepts:
#   - Lab 2: Data Acquisition & Downsampling
#   - Lab 3: Simple Anomaly Detection
#   - Lab 13: Queue Overflow Handling


import time
import random
import queue
from threading import Thread

# Compress every 20 raw samples into 1 averaged sample
DOWNSAMPLE_RATE = 20


def water_level_stream():
    """
    Simulates a water-level sensor.

    Raw sensor frequency:
        100 Hz (1 sample every 0.01 sec)

    Flood event:
        Every ~30 seconds, water level rises
        to simulate flooding conditions.
    """

    while True:
        # Normal water level around 2.0 meters
        level = 2.0 + random.uniform(-0.05, 0.05)

        # Simulate flood event
        if int(time.time()) % 30 > 20:
            level += 1.0
        yield level

        # 100 Hz sampling rate
        time.sleep(0.01)


class SensorProducer(Thread):

    def __init__(self, sensor_queue):
        super().__init__(daemon=True)
        self.sensor_queue = sensor_queue


        # Lab 3: Historical buffer for anomaly detection
        self.history = []
    def run(self):
        print("[SENSOR] Starting sensor stream...")

        # Buffer used for chunk-averaging downsampling
        buffer = []

        for value in water_level_stream():

            # Lab 2: Chunk Averaging Downsampling
            buffer.append(value)

            if len(buffer) >= DOWNSAMPLE_RATE:
                # Average 20 samples into 1 sample
                avg_level = sum(buffer) / len(buffer)


                # Lab 3: Simple Anomaly Detection
                # Compare current reading against recent history
                anomaly = False

                self.history.append(avg_level)

                # Keep only latest 20 downsampled readings
                if len(self.history) > 20:
                    self.history.pop(0)

                if len(self.history) >= 5:
                    historical_mean = (
                        sum(self.history[:-1]) /
                        (len(self.history) - 1)
                    )

                    # Trigger anomaly if deviation is large
                    if abs(avg_level - historical_mean) > 0.5:
                        anomaly = True

                payload = {
                    "timestamp": time.time(),
                    "water_level": round(avg_level, 3),
                    "anomaly": anomaly
                }


                # Lab 13: Queue Overflow Protection
                # Keep newest data when queue is full
                try:
                    self.sensor_queue.put_nowait(payload)

                except queue.Full:
                    try:
                        self.sensor_queue.get_nowait()

                    except queue.Empty:
                        pass

                    self.sensor_queue.put_nowait(payload)
                print(f"[SENSOR] {payload}")

                # Clear buffer for next chunk
                buffer.clear()