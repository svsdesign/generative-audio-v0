import cv2
import numpy as np
import os
import json
import csv
import argparse
import webcolors
from sklearn.cluster import KMeans
from collections import Counter
from multiprocessing import Pool
from tqdm import tqdm

def closest_color(requested_color):
    min_colors = {}
    for name in webcolors.names("css3"):
        r_c, g_c, b_c = webcolors.name_to_rgb(name)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def rgb_to_name(rgb_tuple):
    try:
        return webcolors.rgb_to_name(rgb_tuple)
    except ValueError:
        return closest_color(rgb_tuple)

def get_dominant_colors(image, num_colors=4):  # Reduced the number of colors
    pixels = image.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors, n_init=5).fit(pixels)  # Reduced n_init
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_
    count = Counter(labels)
    dominant_colors = [colors[i] for i in count.keys()]
    return np.array(dominant_colors, dtype=int)

def process_frame(frame):
    frame_resized = cv2.resize(frame, (frame.shape[1] // 8, frame.shape[0] // 8))  # Further reduced size
    colors = frame_resized.reshape(-1, 3)
    return colors

def analyze_frame(frame, prev_frame):
    # Analyze average color
    avg_color = frame.mean(axis=0).mean(axis=0).astype(float).tolist()

    # Calculate mass as the number of pixels within a certain color range
    lower_bound = (0, 0, 0)
    upper_bound = (100, 100, 100)
    mask = cv2.inRange(frame, lower_bound, upper_bound)
    mass = int(cv2.countNonZero(mask))

    # Calculate brightness
    brightness = float(np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))

    # Calculate contrast
    contrast = float(np.std(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))

    # Motion detection
    if prev_frame is not None:
        flow = cv2.calcOpticalFlowFarneback(cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY),
                                            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                                            None, 0.5, 3, 15, 3, 5, 1.2, 0)
        motion = float(np.mean(np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)))
    else:
        motion = 0.0

    return avg_color, mass, brightness, contrast, motion

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process a video file to extract data.')
    parser.add_argument('--file-name', type=str, required=True, help='Name of the input video file (without extension)')
    args = parser.parse_args()

    # Define paths
    video_path = f'/Users/simonvanstipriaan/Sites/generative-audio-v0/src/mp4/{args.file_name}.mp4'
    output_dir = f'output/{args.file_name}'
    json_dir = os.path.join(output_dir, 'json')
    csv_dir = os.path.join(output_dir, 'csv')

    # Create output directories if they don't exist
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)

    # Define output file paths
    json_file_path = os.path.join(json_dir, f'{args.file_name}.json')
    csv_file_path = os.path.join(csv_dir, f'{args.file_name}.csv')

    # Initialize lists to store the data and accumulated colors
    data = []
    all_colors = []

    # Load video
    cap = cv2.VideoCapture(video_path)

    # Get video duration and frame count
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = frame_count / fps

    # Initialize previous frame for motion detection
    prev_frame = None

    # Process frames and accumulate colors
    with Pool() as pool:
        with tqdm(total=frame_count, desc='Processing Frames') as pbar:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Process frame and analyze
                colors = pool.apply(process_frame, args=(frame,))
                all_colors.extend(colors)

                avg_color, mass, brightness, contrast, motion = analyze_frame(frame, prev_frame)

                # Extract dominant colors for current frame
                dominant_colors = get_dominant_colors(frame, num_colors=4)  # Reduced number of colors
                dominant_colors_info = [
                    {
                        "rgb": color.tolist(),
                        "hex": webcolors.rgb_to_hex(tuple(color)),
                        "name": rgb_to_name(tuple(color))
                    } for color in dominant_colors
                ]

                # Store the data
                frame_data = {
                    'avg_color': avg_color,
                    'mass': mass,
                    'brightness': brightness,
                    'contrast': contrast,
                    'motion': motion,
                    'dominant_colors': dominant_colors_info
                }
                data.append(frame_data)

                # Update previous frame
                prev_frame = frame

                # Update progress bar
                pbar.update(1)

    cap.release()
    cv2.destroyAllWindows()

    # Determine overall dominant colors across video
    all_colors = np.array(all_colors, dtype=int)
    overall_dominant_colors = get_dominant_colors(all_colors, num_colors=4)  # Reduced number of colors
    overall_dominant_colors_info = [
        {
            "rgb": color.tolist(),
            "hex": webcolors.rgb_to_hex(tuple(color)),
            "name": rgb_to_name(tuple(color))
        } for color in overall_dominant_colors
    ]

    # Add video duration and overall dominant colors to JSON data
    json_data = {
        'video_duration': video_duration,
        'overall_dominant_colors': overall_dominant_colors_info,
        'frames': data
    }

    # Write data to JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    # Write data to CSV file
    with open(csv_file_path, 'w', newline='') as csv_file:
        fieldnames = ['avg_color', 'mass', 'brightness', 'contrast', 'motion', 'dominant_colors']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            entry['dominant_colors'] = str(entry['dominant_colors'])  # Convert list to string for CSV
            writer.writerow(entry)

    print(f"Data has been saved to {json_file_path} and {csv_file_path}")

if __name__ == '__main__':
    main()
