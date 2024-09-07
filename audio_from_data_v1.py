import numpy as np
import scipy.io.wavfile as wav
import json
import os
import argparse
from scipy.signal import butter, lfilter

# Define argument parser
def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate audio from visual data.')
    parser.add_argument('--wave-type', type=str, choices=['sine', 'sawtooth', 'square', 'triangle', 'additive', 'subtractive'], default='sine',
                        help='Type of waveform to use (default: sine).')
    parser.add_argument('--file-name', type=str, default='output/sample_v2/audio/sample_v2_v1.wav',
                        help='Output WAV file name (default: output/sample_v2/audio/sample_v2_v1.wav).')
    return parser.parse_args()

# Load JSON data
def load_json_data(json_file_path):
    with open(json_file_path, 'r') as json_file:
        return json.load(json_file)

# Generate complex waveforms
def generate_waveform(wave_type, freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    if wave_type == 'sine':
        wave = 0.5 * np.sin(2 * np.pi * freq * t)
    elif wave_type == 'sawtooth':
        wave = 0.5 * (1 - np.mod(t * freq, 1))
    elif wave_type == 'square':
        wave = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == 'triangle':
        wave = 0.5 * (2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1)
    else:
        raise ValueError("Unsupported wave type")
    
    return wave

# Additive synthesis
def generate_additive_synthesis(freqs, amps, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.zeros_like(t)
    
    for freq, amp in zip(freqs, amps):
        wave += amp * np.sin(2 * np.pi * freq * t)
    
    return wave

# Subtractive synthesis with low-pass filter
def butter_filter(data, cutoff, fs, btype='low', order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    return lfilter(b, a, data)

def generate_subtractive_synthesis(wave_type, cutoff_freq, duration, sample_rate):
    wave = generate_waveform(wave_type, 440, duration, sample_rate)  # Base waveform
    filtered_wave = butter_filter(wave, cutoff_freq, sample_rate, btype='low')
    return filtered_wave
def main():
    args = parse_arguments()

    # Define paths
    json_file_path = 'output/sample_v2/json/sample_v2.json'
    audio_file_path = args.file_name

    # Load JSON data
    json_data = load_json_data(json_file_path)

    # Extract video duration and frame data
    video_duration = json_data['video_duration']
    frames = json_data['frames']

    # Parameters for audio generation
    sample_rate = 44100  # Hz
    num_frames = len(frames)
    frame_duration = video_duration / num_frames  # Duration per frame

    # Generate audio data
    audio_data = np.array([])

    for frame in frames:
        # Map brightness to frequency and other parameters
        brightness = frame['brightness']
        freq = np.clip(brightness * 10, 100, 1000)  # Example mapping

        # Choose synthesis method
        wave_type = args.wave_type
        if wave_type == 'additive':
            freqs = [freq, freq * 2, freq * 3]  # Example: Harmonics
            amps = [0.5, 0.3, 0.2]
            wave = generate_additive_synthesis(freqs, amps, frame_duration, sample_rate)
        elif wave_type == 'subtractive':
            cutoff_freq = 1000  # Example cutoff frequency
            wave = generate_subtractive_synthesis('sine', cutoff_freq, frame_duration, sample_rate)
        else:
            wave = generate_waveform(wave_type, freq, frame_duration, sample_rate)
        
        # Append to audio data
        audio_data = np.concatenate((audio_data, wave))

    # Normalize audio data
    audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(audio_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save to WAV file
    wav.write(audio_file_path, sample_rate, audio_data)

    print(f"Audio has been saved to {audio_file_path}")

if __name__ == "__main__":
    main()
