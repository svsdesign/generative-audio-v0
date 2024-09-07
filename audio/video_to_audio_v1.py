import cv2
import os
import json
import csv

# Define paths
video_path = '/Users/simonvanstipriaan/Sites/generative-audio-v0/src/mp4/sample_v1.mp4'
output_dir = f'output/sample_v1'
json_dir = os.path.join(output_dir, 'json')
csv_dir = os.path.join(output_dir, 'csv')

# Create output directories if they don't exist
os.makedirs(json_dir, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)

# Define output file paths
json_file_path = os.path.join(json_dir, 'sample_v1.json')
csv_file_path = os.path.join(csv_dir, 'sample_v1.csv')

# Initialize lists to store the data
data = []

# Load video
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Analyze average color
    avg_color = frame.mean(axis=0).mean(axis=0).tolist()  # Convert to list for JSON serialization

    # Calculate mass as the number of pixels within a certain color range
    lower_bound = (0, 0, 0)  # Lower bound for color range (e.g., dark pixels)
    upper_bound = (100, 100, 100)  # Upper bound for color range
    mask = cv2.inRange(frame, lower_bound, upper_bound)
    mass = int(cv2.countNonZero(mask))  # Convert to int for JSON serialization

    # Store the data
    frame_data = {
        'avg_color': avg_color,
        'mass': mass
    }
    data.append(frame_data)

cap.release()
cv2.destroyAllWindows()

# Write data to JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Write data to CSV file
with open(csv_file_path, 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=['avg_color', 'mass'])
    writer.writeheader()
    for entry in data:
        writer.writerow(entry)

print(f"Data has been saved to {json_file_path} and {csv_file_path}")
