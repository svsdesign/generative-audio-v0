import cv2
import numpy as np
import os
import json
import csv
import argparse
import webcolors
from sklearn.cluster import MiniBatchKMeans
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

def get_dominant_colors(image, num_colors=4):
    image = cv2.GaussianBlur(image, (5, 5), 0)
    image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    pixels = image_lab.reshape(-1, 3).astype(np.float32)

    kmeans = MiniBatchKMeans(n_clusters=num_colors, n_init=10).fit(pixels)
    colors_lab = kmeans.cluster_centers_
    labels = kmeans.labels_

    count = Counter(labels)
    sorted_colors_lab = [colors_lab[i] for i in sorted(count, key=count.get, reverse=True)]

    sorted_colors_rgb = []
    for color in sorted_colors_lab:
        lab_color = np.uint8([[color]])
        rgb_color = cv2.cvtColor(lab_color, cv2.COLOR_Lab2BGR)
        sorted_colors_rgb.append(rgb_color.flatten())

    return np.array(sorted_colors_rgb, dtype=int)

def crop_to_center(frame, crop_fraction=0.4):
    height, width, _ = frame.shape
    start_x = int((1 - crop_fraction) / 2 * width)
    start_y = int((1 - crop_fraction) / 2 * height)
    end_x = int(start_x + crop_fraction * width)
    end_y = int(start_y + crop_fraction * height)

    return frame[start_y:end_y, start_x:end_x]

def save_frame(image, folder_path, frame_idx, stage):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = os.path.join(folder_path, f'{stage}_frame_{frame_idx}.png')
    cv2.imwrite(file_path, image)

def process_frame(frame, frame_idx, output_dir):
    cropped_frame = crop_to_center(frame)
    save_frame(cropped_frame, output_dir, frame_idx, 'cropped')

    frame_resized = cv2.resize(cropped_frame, (cropped_frame.shape[1] // 8, cropped_frame.shape[0] // 8))
    save_frame(frame_resized, output_dir, frame_idx, 'resized')

    return frame_resized.reshape(-1, 3)

def analyze_frame(frame, prev_frame, frame_idx, output_dir):
    cropped_frame = crop_to_center(frame)
    save_frame(cropped_frame, output_dir, frame_idx, 'analyzed')

    avg_color = cropped_frame.mean(axis=0).mean(axis=0).astype(float).tolist()

    mask = cv2.inRange(cropped_frame, (0, 0, 0), (100, 100, 100))
    mass = int(cv2.countNonZero(mask))

    gray_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray_frame))
    contrast = float(np.std(gray_frame))

    motion = 0.0
    if prev_frame is not None:
        prev_cropped_frame = crop_to_center(prev_frame)
        flow = cv2.calcOpticalFlowFarneback(cv2.cvtColor(prev_cropped_frame, cv2.COLOR_BGR2GRAY),
                                            gray_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        motion = float(np.mean(np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)))

    return avg_color, mass, brightness, contrast, motion

def process_video_frames(video_path, frames_dir):
    data = []
    all_colors = []

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = frame_count / fps

    prev_frame = None

    with Pool() as pool:
        with tqdm(total=frame_count, desc='Processing Frames') as pbar:
            for frame_idx in range(frame_count):
                ret, frame = cap.read()
                if not ret:
                    break

                # Use multiprocessing to process frames
                colors = pool.apply(process_frame, args=(frame, frame_idx, frames_dir))
                all_colors.extend(colors)

                avg_color, mass, brightness, contrast, motion = analyze_frame(frame, prev_frame, frame_idx, frames_dir)

                dominant_colors = get_dominant_colors(frame, num_colors=4)
                dominant_colors_info = [
                    {
                        "rgb": color.tolist(),
                        "hex": webcolors.rgb_to_hex(tuple(color)),
                        "name": rgb_to_name(tuple(color))
                    } for color in dominant_colors
                ]

                frame_data = {
                    'avg_color': avg_color,
                    'mass': mass,
                    'brightness': brightness,
                    'contrast': contrast,
                    'motion': motion,
                    'dominant_colors': dominant_colors_info
                }
                data.append(frame_data)

                prev_frame = frame
                pbar.update(1)

    cap.release()
    cv2.destroyAllWindows()

    return data, all_colors, video_duration

def main():
    parser = argparse.ArgumentParser(description='Process a video file to extract data.')
    parser.add_argument('--file-name', type=str, required=True, help='Name of the input video file (without extension)')
    args = parser.parse_args()

    video_path = f'/Users/simonvanstipriaan/Sites/generative-audio-v0/src/mp4/{args.file_name}.mp4'
    output_dir = f'output/{args.file_name}'
    json_dir = os.path.join(output_dir, 'json')
    csv_dir = os.path.join(output_dir, 'csv')
    frames_dir = os.path.join(output_dir, 'frames')

    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(frames_dir, exist_ok=True)

    json_file_path = os.path.join(json_dir, f'{args.file_name}.json')
    csv_file_path = os.path.join(csv_dir, f'{args.file_name}.csv')

    data, all_colors, video_duration = process_video_frames(video_path, frames_dir)

    all_colors = np.array(all_colors, dtype=np.uint8)
    all_colors_image = np.zeros((1, len(all_colors), 3), dtype=np.uint8)
    all_colors_image[0, :, :] = all_colors
    overall_dominant_colors = get_dominant_colors(all_colors_image, num_colors=8)
    overall_dominant_colors_info = [
        {
            "rgb": color.tolist(),
            "hex": webcolors.rgb_to_hex(tuple(color)),
            "name": rgb_to_name(tuple(color))
        } for color in overall_dominant_colors
    ]

    json_data = {
        'video_duration': video_duration,
        'overall_dominant_colors': overall_dominant_colors_info,
        'frames': data
    }

    with open(json_file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    with open(csv_file_path, 'w', newline='') as csv_file:
        fieldnames = ['avg_color', 'mass', 'brightness', 'contrast', 'motion', 'dominant_colors']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            entry['dominant_colors'] = str(entry['dominant_colors'])
            writer.writerow(entry)

    print(f"Data has been saved to {json_file_path} and {csv_file_path}")

if __name__ == '__main__':
    main()
