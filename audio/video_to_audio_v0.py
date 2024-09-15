import cv2
import numpy as np
from pyo import *

# Initialize the audio server
s = Server().boot()

# Load video
cap = cv2.VideoCapture('/src/mp4/sample_v1.MP4')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Analyze the average color of the frame
    avg_color = frame.mean(axis=0).mean(axis=0)

    # Convert the color to a pitch (example mapping)
    hue = cv2.cvtColor(np.uint8([[avg_color]]), cv2.COLOR_BGR2HSV)[0][0][0]
    pitch = 440 + (hue - 128) * 2  # A basic mapping to frequency (A4 = 440 Hz)

    # Generate a sine wave based on the pitch
    sine = Sine(freq=pitch, mul=0.5).out()

    s.start()
    s.stop()

cap.release()
