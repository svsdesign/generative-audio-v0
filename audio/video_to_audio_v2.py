import cv2
import numpy as np
import os
import json
import csv

# Define paths
video_path = '/Users/simonvanstipriaan/Sites/generative-audio-v0/src/mp4/sample_v2.mp4'
output_dir = f'output/sample_v2'
json_dir = os.path.join(output_dir, 'json')
csv_dir = os.path.join(output_dir, 'csv')

# Create output directories if they don't exist
os.makedirs(json_dir, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)

# Define output file paths
json_file_path = os.path.join(json_dir, 'sample_v2.json')
csv_file_path = os.path.join(csv_dir, 'sample_v2.csv')

# Initialize lists to store the data
data = []

# Load video
cap = cv2.VideoCapture(video_path)

# Get video duration
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
video_duration = frame_count / fps

# Initialize previous frame for motion detection
prev_frame = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Analyze average color
    avg_color = frame.mean(axis=0).mean(axis=0).astype(float).tolist()  # Convert to list and float

    # Calculate mass as the number of pixels within a certain color range
    lower_bound = (0, 0, 0)  # Lower bound for color range (e.g., dark pixels)
    upper_bound = (100, 100, 100)  # Upper bound for color range
    mask = cv2.inRange(frame, lower_bound, upper_bound)
    mass = int(cv2.countNonZero(mask))  # Convert to int for JSON serialization

    # Calculate brightness
    brightness = float(np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))  # Convert to float

    # Calculate contrast (standard deviation of pixel intensities)
    contrast = float(np.std(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))  # Convert to float

    # Motion detection (optical flow)
    if prev_frame is not None:
        flow = cv2.calcOpticalFlowFarneback(cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY),
                                            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                                            None, 0.5, 3, 15, 3, 5, 1.2, 0)
        motion = float(np.mean(np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)))  # Convert to float
    else:
        motion = 0.0  # Use a float for consistency

    # Store the data
    frame_data = {
        'avg_color': avg_color,
        'mass': mass,
        'brightness': brightness,
        'contrast': contrast,
        'motion': motion
    }
    data.append(frame_data)

    # Update previous frame
    prev_frame = frame

cap.release()
cv2.destroyAllWindows()

# Add video duration to JSON data
json_data = {
    'video_duration': video_duration,
    'frames': data
}

# Write data to JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

# Write data to CSV file
with open(csv_file_path, 'w', newline='') as csv_file:
    fieldnames = ['avg_color', 'mass', 'brightness', 'contrast', 'motion']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for entry in data:
        writer.writerow(entry)

print(f"Data has been saved to {json_file_path} and {csv_file_path}")
