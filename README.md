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
- **`adio/video_to_data/video_to_data.py`**: Extracts visual features from video and saves them to JSON and CSV files. Includes the `video_duration` in the JSON file for accurate audio length.

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

1. **Prepare Your Video File**

   Place your video file in the `src/mp4/` directory or specify a path to your video file in the script.

2. **Run the Script to Extract Visual Data**


    ```bash
    python audio/video_to_data/video_to_data.py --file-name namoofmp4file
    ```

   This script processes the video and generates JSON and CSV files with visual data. The JSON file will include the `video_duration` field, which is essential for correlating the length of the generated audio with the length of the video.

3. **Generate Audio from Visual Data**

   **Legacy Method (v0):**
   
    ```bash
    python audio/audio_from_data_v0.py
    ```

   This script creates a WAV file based on the extracted visual data using basic sine wave synthesis. It uses the `video_duration` field from the JSON file to ensure that the length of the audio file corresponds to the length of the video.

   **Enhanced Method (v1):**
   
    ```bash
    python audio/audio_from_data_v1.py --wave-type sine
    python audio/audio_from_data_v1.py --wave-type sawtooth
    python audio/audio_from_data_v1.py --wave-type square
    python audio/audio_from_data_v1.py --wave-type triangle
    python audio/audio_from_data_v1.py --wave-type additive
    python audio/audio_from_data_v1.py --wave-type subtractive
    ```

   This script creates a WAV file based on the extracted visual data using advanced synthesis techniques. It supports multiple waveform types and synthesis methods, which can be selected via command-line arguments. You can also specify the output filename using the `--file-name` argument. The `video_duration` field from the JSON file is used to ensure that the length of the audio file corresponds to the length of the video.

4. **Using the Web Interface**

   - Start the Flask server:

     ```bash
     python app.py
     ```

   - Navigate to `http://localhost:5000` in your web browser.
   - Upload your json file file (from output folders) and configure the audio generation parameters via the web interface.
    


## Project Structure


The main project directory is structured as follows:
  ```
  run: tree -I 'myenv|__pycache__|output|static' > output.txt
  ```

  ```
   .
├── README.md                              # Primary project documentation and instructions
├── README_old_v0.1.md                     # Legacy documentation from version 0.1
├── app                                    # Folder containing the main app and associated scripts
│   ├── _legacy                            # Backup and legacy versions of the application
│   │   ├── app_backup_v1.py               # Backup of the app (version 1)
│   │   ├── app_backup_v2.py               # Backup of the app (version 2)
│   │   ├── app_backup_v3.py               # Backup of the app (version 3)
│   │   ├── app_backup_v4.py               # Backup of the app (version 4)
│   │   ├── app_backup_v5.py               # Backup of the app (version 5)
│   │   ├── app_backup_v6.py               # Backup of the app (version 6)
│   │   ├── app_backup_v7.py               # Backup of the app (version 7)
│   │   ├── app_backup_v8.py               # Backup of the app (version 8)
│   │   ├── app_new-broken_v1.py           # Newer broken version of the app (v1)
│   │   ├── app_old-broken.py              # Older broken version of the app
│   │   └── app_old-broken_v2.py           # Another older broken version of the app (v2)
│   ├── audio_from_data                    # Scripts to generate audio from visual data
│   │   ├── audio_from_data_v0.py          # Audio generation script from visual data (version 0)
│   │   └── audio_from_data_v1.py          # Audio generation script from visual data (version 1)
│   ├── effects                            # Audio effects and synthesis related scripts
│   │   ├── drum_synthesis.py              # Script for synthesizing drum sounds
│   │   ├── effects.py                     # Script for applying audio effects (e.g., reverb, echo)
│   │   ├── envelope.py                    # Script to control audio envelope (attack, decay, sustain, release)
│   │   └── synthesis.py                   # Core script for sound synthesis
│   ├── generate_colors                    # Scripts for generating colors from visual data
│   │   ├── _legacy                        # Legacy color generation scripts
│   │   ├── generate_colors.py             # Main script to generate color mappings from visual data
│   │   └── generate_colors_v2.py          # Updated version of color generation script
│   ├── generate_sounds                    # Scripts related to generating sound from processed data
│   │   ├── check_sound.py                 # Utility script to check and verify sound output
│   │   └── generate_sounds.py             # Main script for generating sounds from processed visual data
│   ├── video_to_data                      # Scripts to extract data from video frames
│   │   ├── _legacy                        # Legacy scripts for converting video data to audio or color
│   │   │   ├── video_to_audio_v0.py       # Converts video data to audio (version 0)
│   │   │   ├── video_to_audio_v1.py       # Converts video data to audio (version 1)
│   │   │   ├── video_to_audio_v2.py       # Converts video data to audio (version 2)
│   │   │   ├── video_to_data_v0.py        # Extracts visual data from video frames (version 0)
│   │   │   ├── video_to_data_v1.py        # Extracts visual data from video frames (version 1)
│   │   │   ├── video_to_data_v2.py        # Extracts visual data from video frames (version 2)
│   │   │   ├── video_to_data_v3.py        # Extracts visual data from video frames (version 3)
│   │   │   ├── video_to_data_v4.py        # Extracts visual data from video frames (version 4)
│   │   │   └── video_to_data_v5.py        # Extracts visual data from video frames (version 5)
│   │   └── video_to_data.py               # Main script for video-to-data conversion
│   └── visualize_audio                    # Scripts for visualizing audio output
│       ├── crete.py                       # Script related to creating visual representations of audio
│       └── visualize_audio.py             # Main script for visualizing the generated audio
├── app.py                                 # Main Flask application for generating audio from video
├── fluidsynth.wav                         # Example generated audio using FluidSynth
├── generative-audio-v0.code-workspace     # VS Code workspace configuration file for the project
├── midi                                   # MIDI generation and processing scripts
│   ├── experiments                        # Experimental scripts for MIDI generation
│   │   ├── experiment_template.py         # Template for MIDI generation experiments
│   │   ├── experiment_v1.py               # MIDI experiment (version 1)
│   │   ├── experiment_v2.py               # MIDI experiment (version 2)
│   │   ├── experiment_v3.py               # MIDI experiment (version 3)
│   │   ├── experiment_v4.py               # MIDI experiment (version 4)
│   │   ├── experiment_v5.py               # MIDI experiment (version 5)
│   │   ├── experiment_v6.py               # MIDI experiment (version 6)
│   │   └── experiment_v7.py               # MIDI experiment (version 7)
│   └── misc                               # Miscellaneous MIDI-related scripts
│       ├── makeaphexsound.py              # Script to generate Aphex Twin-inspired sounds
│       ├── makegamesound.py               # Script to generate sounds suitable for games
│       └── makesound.py                   # General sound generation script
├── output.txt                             # Output file listing the project's structure
├── requirements.txt                       # List of Python dependencies for the project
├── src                                    # Source folder containing soundfont files and sample videos
│   ├── FluidR3_GM                         # Folder for FluidR3 GM soundfont files
│   │   ├── FluidR3_GM.sf2           

   ```
## Dependencies

Ensure you have the following Python packages installed: - svs note: needs updating

- numpy
- midiutil
- opencv-python
- flask

You can install the required packages using pip: - svs note: needs updating

    pip install -r requirements.txt

## License

This project is licensed under the MIT License. See the LICENSE file for details.
