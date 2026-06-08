import time
import queue

class TemporalFusion:
    def __init__(
        self,
        sensor_queue,
        video_queue,
        fusion_queue
    ):
        self.sensor_queue = sensor_queue
        self.video_queue = video_queue
        self.fusion_queue = fusion_queue

    def run(self):
        while True: 
            vis = self.video_queue.get()
            best_match = None
            min_diff = 1.0
            while not self.sensor_queue.empty():
                s = self.sensor_queue.get()
                diff = abs(
                    vis["timestamp"]
                    - s["timestamp"]
                )
                if diff < min_diff:
                    min_diff = diff
                    best_match = s

            if best_match and min_diff < 0.1:
                payload = {
                    "timestamp": vis["timestamp"],
                    "water_level": best_match["water_level"],
                    "anomaly": best_match["anomaly"],
                    "object_count": vis["object_count"],

                    "blur_score": vis["blur_score"],
                    "brightness": vis["brightness"],
                    "inference_ms": vis["inference_ms"],

                    "sync_error_ms": round(min_diff * 1000, 2)
                }

                try:
                    self.fusion_queue.put_nowait(payload)
                except queue.Full:
                    pass
                
                print(
                    "[FUSION]",
                    payload
                )