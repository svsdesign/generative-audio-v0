import numpy as np
import scipy.io.wavfile as wav
import json
import os

# Define paths
json_file_path = 'output/sample_v2/json/sample_v2.json'
audio_file_path = 'output/sample_v2/audio/sample_v2.wav'

# Load JSON data
with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)

# Extract video duration and frame data
video_duration = json_data['video_duration']
frames = json_data['frames']

# Parameters for audio generation
sample_rate = 44100  # Hz
num_frames = len(frames)
frame_duration = video_duration / num_frames  # Duration per frame

def generate_sine_wave(freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    return wave

# Generate audio data
audio_data = np.array([])

for frame in frames:
    # Map brightness to frequency
    brightness = frame['brightness']
    freq = np.clip(brightness * 10, 100, 1000)  # Example mapping

    # Generate sine wave for the frame duration
    wave = generate_sine_wave(freq, frame_duration, sample_rate)
    audio_data = np.concatenate((audio_data, wave))

# Normalize audio data
audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)

# Save to WAV file
os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)
wav.write(audio_file_path, sample_rate, audio_data)

print(f"Audio has been saved to {audio_file_path}")
