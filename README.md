# Generative Audio v0

## Project Overview


**Disclaimer:** The contents of this file were created with the aid of AI (ChatGPT), as was much of the code in this repository. Please use with caution. https://chatgpt.com/c/66dc65dd-640c-8009-97c4-4d56e994b5f4


**Generative Audio v0** is a tool designed to transform video data into generative music. By analyzing visual aspects of video frames such as dominant colors and brightness, the system algorithmically generates MIDI files and synthesized audio, creating a dynamic relationship between visuals and sound. This makes it ideal for creative projects exploring the intersection of audio and video data.

## Features

- **Frame-by-frame analysis**: Extracts visual features (color, brightness) from each video frame.
- **Generative music creation**: Converts visual data into MIDI and synthesized audio.
- **Algorithmic composition**: Implements techniques such as fractals and Markov chains to generate musical patterns.
- **Customizable instruments and sound mappings**: Maps visual properties (e.g., color) to specific musical parameters like notes and instruments.

## Folder Structure

The project is organized as follows: - THIS IS WRONG- wip; will ater

generative-audio-v0/
├── audio_generation.py # Generates audio from frame data.
├── midi_generation.py # Converts visual data to MIDI format.
├── video_to_frames.py # Extracts visual properties from video frames.
├── app.py # Main application file.
├── color_mapping.py # Defines color-to-MIDI mappings.
├── /src
│   ├── /mp4 # Folder for input video files (.mp4 format).
├── /output
│   ├── /midi # Folder for generated MIDI files.
│   ├── /audio # Folder for generated audio files.
├── /audio
│   ├── experiment_v7.py # Advanced audio processing script.
├── /utils
│   ├── nearest_color.py # Utility script to find the nearest color from a mapping.
└── README.md # The current readme file.

### Explanation of Important Files:

- **`app.py`**: The main file that coordinates the project. This file includes the web-based interface for uploading videos, running the processing pipeline, and downloading the generated audio or MIDI files.
- **`video_to_frames.py`**: Extracts individual frames from videos and analyzes them for color and brightness.
- **`midi_generation.py`**: Converts visual data (e.g., brightness, dominant colors) from the frames into MIDI data.
- **`audio_generation.py`**: Synthesizes audio from visual data using various wave types (e.g., sine, square, etc.).
- **`/src/mp4`**: Folder where input video files are placed for processing.
- **`/output/midi`**: Folder where generated MIDI files are saved.
- **`/output/audio`**: Folder where generated audio files are stored.
- **`nearest_color.py`**: A utility to find the nearest color from a predefined mapping of colors to musical instruments.

## Prerequisites

Before running the project, make sure you have the following installed:

- Python 3.9 or higher
- `ffmpeg` (for video processing)
- `virtualenv` (recommended)

## Installation

1. Clone the repository to your local machine:

    git clone https://github.com/svsdesign/generative-audio-v0.git
    cd generative-audio-v0

2. Create and activate a virtual environment:

    python3 -m venv env
    source env/bin/activate  # On Windows: `env\Scripts\activate`

3. Install the necessary Python dependencies:

    pip install -r requirements.txt

## Usage

### Step 1: Add a Video

Place your `.mp4` video files inside the `/src/mp4` folder.

### Step 2: Extract Frames and Visual Data

To extract visual properties (e.g., dominant colors, brightness) from the video, use the `video_to_frames.py` script:

    python video_to_frames.py --input src/mp4/your_video.mp4 --output output/frames.json

This command will extract the frames from your video and save their visual properties in `frames.json`.

### Step 3: Generate MIDI

Once the frame data is ready, you can generate a MIDI file using the `midi_generation.py` script:

    python midi_generation.py --input output/frames.json --output output/midi/music_output.mid --bpm 120 --num-tracks 4

### Step 4: Generate Audio

To synthesize audio from the frame data, run the `audio_generation.py` script:

    python audio_generation.py --input output/frames.json --output output/audio/music_output.wav --wave-type sine

#### Command-Line Options

- `--bpm`: Set the tempo (beats per minute) for the MIDI file.
- `--num-tracks`: Specify the number of tracks for MIDI generation.
- `--wave-type`: Set the waveform type for synthesized audio (sine, square, etc.).
- `--instrument`: Specify a MIDI instrument number.

### Example Workflow

Here is a complete example of processing a video and generating music:

1. Place `your_video.mp4` inside the `/src/mp4` directory.

2. Run the following command to extract frames and save the visual data:

    python video_to_frames.py --input src/mp4/your_video.mp4 --output output/frames.json

3. Generate the MIDI file based on the extracted visual data:

    python midi_generation.py --input output/frames.json --output output/midi/music_output.mid --bpm 120 --num-tracks 4

4. Convert the frame data into audio:

    python audio_generation.py --input output/frames.json --output output/audio/music_output.wav --wave-type sine

## Project Structure

The main project directory is structured as follows:

generative-audio-v0/
├── audio/
│   ├── audio_generation.py  # Synthesizes audio from frame data
│   ├── midi_generation.py   # Converts visual data to MIDI format
│   └── utils/               # Helper scripts
│       └── nearest_color.py # Finds the closest matching color for a frame
├── src/
│   └── mp4/                 # Input folder for video files
├── output/
│   ├── frames.json          # Extracted visual data from frames
│   ├── midi/                # Folder containing generated MIDI files
│   └── audio/               # Folder containing generated audio files
├── video_to_frames.py       # Extracts visual data from video frames
├── app.py                   # Flask web app for interactive use
└── README.md                # Documentation for the project

## Dependencies

Ensure you have the following Python packages installed:

- numpy
- midiutil
- opencv-python
- flask

You can install the required packages using pip:

    pip install -r requirements.txt

## License

This project is licensed under the MIT License. See the LICENSE file for details.
