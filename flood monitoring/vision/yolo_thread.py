# Integrated Concepts:
#   - Lab 7 : Visual Quality Control (QC)
#   - Lab 9 : Vectorized Image Pipeline
#   - Lab 12: Object Detection & NMS Benchmark
#   - Lab 13: Multi-threading & Frame Dropping

import cv2
import time
import queue
from threading import Thread
from ultralytics import YOLO


# Lab 7: Visual Quality Control
def blur_score(frame):
    """
    Estimate image sharpness using
    Laplacian variance.

    Higher value = sharper image
    Lower value = blurry image
    """
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )
    return cv2.Laplacian(
        gray,
        cv2.CV_64F).var()


def brightness_score(frame):
    """
    Estimate image brightness.

    Higher value = brighter image
    Lower value = darker image
    """
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )
    return gray.mean()


class VisionProducer(Thread):
    """
    Producer Thread

    Responsibilities:
    - Read frames from video source
    - Perform visual quality control
    - Run YOLOv10 inference
    - Publish metadata to vision queue
    """
    def __init__(self, video_path, video_queue):
        super().__init__(daemon=True)

        self.video_path = video_path
        self.video_queue = video_queue

        # Counter for periodic logging
        self.frame_count = 0

    def run(self):
        print("[VISION] Loading YOLOv10...")


        # Lab 12: YOLOv10 Object Detection
        model = YOLO("yolov10n.pt")

        print("[VISION] Model loaded.")
        # Open video source
        cap = cv2.VideoCapture(
            self.video_path
        )

        if not cap.isOpened():
            print(
                f"[VISION ERROR] "
                f"Cannot open video: "
                f"{self.video_path}"
            )
            return

        print("[VISION] Video stream started.")
        while True:


            # Read next frame
            ret, frame = cap.read()

            # Loop video if end reached
            if not ret:
                cap.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )
                continue

            # Lab 9: Vectorized Image Pipeline
            # Resize frame using OpenCV vectorized operation
            frame = cv2.resize(
                frame,
                (640, 640),
                interpolation=cv2.INTER_LINEAR
            )

            # BGR -> RGB using NumPy slicing
            frame = frame[:, :, ::-1]

            # Lab 7: Visual Quality Control
            blur = blur_score(frame)
            if blur < 50:
                print(
                    f"[QC] Blurry frame skipped "
                    f"(score={blur:.2f})"
                )
                continue

            brightness = brightness_score(
                frame
            )

            if brightness < 40:
                print(
                    f"[QC] Dark frame skipped "
                    f"(brightness={brightness:.2f})"
                )
                continue


            # Lab 12: YOLOv10 Inference
            results = model(
                frame,
                verbose=False
            )

            # Timing information
            speed = results[0].speed

            pre_ms = speed["preprocess"]
            inf_ms = speed["inference"]
            post_ms = speed["postprocess"]

            # Count detected objects
            object_count = 0

            for result in results:
                if result.boxes is not None:
                    object_count += len(
                        result.boxes
                    )

            # Create metadata payload
            payload = {
                "timestamp": time.time(),
                
                # Detection result
                "object_count": object_count,

                # Lab 9
                "frame_width": frame.shape[1],
                "frame_height": frame.shape[0],

                # Lab 7
                "blur_score": round(blur, 2),
                "brightness": round(brightness, 2),

                # Lab 12
                "preprocess_ms": pre_ms,
                "inference_ms": inf_ms,
                "postprocess_ms": post_ms
            }


            # Lab 13: Frame Dropping Strategy
            # Queue size = 1
            # Keep only freshest result
            try:
                self.video_queue.put_nowait(
                    payload
                )
            except queue.Full:
                try:
                    self.video_queue.get_nowait()
                except queue.Empty:
                    pass

                self.video_queue.put_nowait(
                    payload
                )


            # Periodic Status Logging
            self.frame_count += 1
            if self.frame_count % 30 == 0:
                print(
                    f"[VISION] "
                    f"Objects={object_count} | "
                    f"Blur={blur:.2f} | "
                    f"Bright={brightness:.2f} | "
                    f"Infer={inf_ms:.2f}ms"
                )

            # Simulate ~30 FPS camera
            time.sleep(0.03)

        cap.release()