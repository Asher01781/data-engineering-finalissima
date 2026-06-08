from ultralytics import YOLO
import cv2
import time

model = YOLO("yolov10n.pt")

cap = cv2.VideoCapture("data/flood1.mp4")

ret, frame = cap.read()

print("before")

start = time.time()

results = model(frame, verbose=False)

print("after")
print(time.time() - start)