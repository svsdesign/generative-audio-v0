from flask import Flask, request, render_template, send_from_directory
import os
import numpy as np
import scipy.io.wavfile as wav
from scipy.io.wavfile import write
import json
import uuid
import random
import pretty_midi
from midiutil import MIDIFile
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from audio.visualize_audio import plot_combined
from audio.audio_utils import generate_waveform
from audio.synthesis import apply_synthesis
from audio.effects import apply_effects
from audio.envelope import apply_envelope
from audio.drum_synthesis import generate_drum_beat, save_drum_beat
from midi2audio import FluidSynth
from utils.nearest_color import find_nearest_color  # Import the function from the nearest_color file
# from midi.experiment_v1 import add_music_layers
from midi.experiment_v2 import add_music_layers
import logging
from utils.logging_config import setup_logging



# Added this to fix an error in imported library
def patch_asscalar(a):
    return a.item()
setattr(np, "asscalar", patch_asscalar)
# End - added this to fix an error in imported library

setup_logging()

from flask import Flask
app = Flask(__name__)

# Flask logging setup
app.logger.setLevel(logging.DEBUG)  # Or any other appropriate level
app.logger.propagate = True


# Define paths
UPLOAD_FOLDER = 'output/sample_v2/audio'
VIDEO_FOLDER = 'src/mp4'  # Path to the folder containing video files
SOUNDFONT_PATH = 'src/FluidR3_GM/FluidR3_GM.sf2'  # Path to your SoundFont
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIDEO_FOLDER'] = VIDEO_FOLDER

# Function to convert MIDI to WAV using FluidSynth
def midi_to_wav(midi_file_path, wav_file_path):
    app.logger.debug("Converting MIDI to WAV using FluidSynth")  # Debugging line
    
    # Initialize FluidSynth with a SoundFont path
    fs = FluidSynth(SOUNDFONT_PATH)
    
    # Convert the MIDI file to a WAV file using the SoundFont
    fs.midi_to_audio(midi_file_path, wav_file_path)

# Function to load color mapping
def load_color_mapping():
    color_mapping_path = os.path.join('static', 'color_mapping.json')
    with open(color_mapping_path, 'r') as f:
        return json.load(f)

# Function to create MIDI file from video frames with dynamic music layers
def create_midi_from_frames(json_data, midi_file_path, color_mapping, drum_tempo=None):
    app.logger.debug("Creating MIDI from frames")  # Debugging line

    # Initialize MIDI file with 1 track
    midi = MIDIFile(1)
    bpm = drum_tempo if drum_tempo else 120  # Use drum tempo if provided, otherwise default to 120 BPM
    midi.addTempo(0, 0, bpm)  # Track, Time, BPM

    # Extract overall dominant colors and create instrument mapping
    overall_dominant_colors = json_data['overall_dominant_colors']
    app.logger.debug(f" overall_dominant_colors raw: {overall_dominant_colors}")
    app.logger.debug(f"BPM SET: {bpm}")

    color_to_instrument = {}
    for color in overall_dominant_colors:
        color_hex = color['hex']
        nearest_color, color_number = find_nearest_color(color_hex, color_mapping)
        color_to_instrument[color_hex] = color_number
    
    app.logger.debug(f"Color to instrument mapping: {color_to_instrument}")  # Debugging line
    app.logger.debug(f"Overall_dominant_colors after: {overall_dominant_colors}")
   
    # app.logger.debug(f"Color to instrument mapping: {color_to_instrument[0]}")  # Debugging line
    # Loop through the dictionary and log each number
    for color, instrument in color_to_instrument.items():
        app.logger.debug(f"Instrument number: {instrument}")  # Logs only the number part
        app.logger.debug(f"Instrument number: {color}")  # Logs only the color part

    video_duration = json_data['video_duration']
    frames = json_data['frames']
    duration_per_frame = video_duration / len(frames)  # Duration per frame in seconds
    duration_per_frame =  duration_per_frame * 4   
    # Layers setup based on video frame data
    melody_instruments = []  # Instruments for melody layer
    bass_instruments = []    # Instruments for bass layer
    chord_instruments = []   # Instruments for chord layer
    arp_instruments = []     # Instruments for arpeggios

    midi = add_music_layers(midi, frames, color_to_instrument, duration_per_frame, color_mapping, bpm)

    # Write MIDI data to file
    with open(midi_file_path, 'wb') as midi_file:
        midi.writeFile(midi_file)

# Function for audio generation from video frames and optional MIDI
def generate_audio(json_data, wave_type, file_name, synthesis_type, effects_type, envelope_type, drum_params, midi_file_path=None, include_sine=True):
    app.logger.debug("Generating audio")  # Debugging line
    
    # Extract video duration and frame data
    video_duration = json_data['video_duration']
    frames = json_data['frames']
    
    # Parameters for audio generation
    sample_rate = 44100  # Hz
    frame_duration = video_duration / len(frames)  # Duration per frame in seconds
    
    # Create empty stereo audio data array with two channels
    audio_data = np.zeros((int(sample_rate * video_duration), 2), dtype=np.float64)  # Stereo: two channels

    # Process frames and generate waveform (assume stereo output from your synthesis functions)
    for i, frame in enumerate(frames):
        brightness = frame['brightness']
        wave = generate_waveform(wave_type, sample_rate, frame_duration, brightness, stereo=True)  # Stereo waveform stereo var dones't exist?

        if synthesis_type:
            wave = apply_synthesis(wave, synthesis_type)
        
        if include_sine:
            sine_wave = generate_waveform('sine', sample_rate, frame_duration, brightness, stereo=True)#stereo var dones't exist?
            wave += sine_wave * 0.5  # Mix in sine wave

        if envelope_type:
            wave = apply_envelope(wave, envelope_type)
        
        # Apply effects
        wave = apply_effects(wave, effects_type)
        
        # Calculate start and end indices in the audio data array
        start_index = int(i * frame_duration * sample_rate)
        end_index = start_index + len(wave)
        
        # Ensure end_index does not exceed the length of audio_data
        if end_index > len(audio_data):
            end_index = len(audio_data)
            wave = wave[:end_index - start_index]

        # Add wave to the audio data array
        audio_data[start_index:end_index] += wave

    # Handle drum synthesis if provided (assuming stereo drums)
    if drum_params:
        drum_tempo, beats_per_measure, num_measures = drum_params
        drum_signal = generate_drum_beat(drum_tempo, beats_per_measure, num_measures, stereo=True)
        drum_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'drum_beat.wav')
        save_drum_beat(drum_file_path, drum_signal)
        
        # Mix drum signal with audio data (stereo)
        drum_signal = np.resize(drum_signal, (len(audio_data), 2))  # Resize drum signal to match audio data length
        audio_data += drum_signal * 0.2  # Adjust drum volume

    # Convert MIDI to WAV if a MIDI file is provided
    if midi_file_path:
        midi_wav_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'midi_output.wav')
        midi_to_wav(midi_file_path, midi_wav_file_path)

        try:
            midi_wav_sample_rate, midi_wav_data = wav.read(midi_wav_file_path)
            
            # Check if the MIDI WAV is stereo and the sample rate matches
            if midi_wav_data.ndim == 2 and midi_wav_sample_rate == sample_rate:
                app.logger.debug(f"MIDI WAV data shape: {midi_wav_data.shape}, dtype: {midi_wav_data.dtype}")
                
                # Resize midi_wav_data if necessary (preserving stereo)
                if len(midi_wav_data) < len(audio_data):
                    midi_wav_data = np.resize(midi_wav_data, (len(audio_data), 2))
                elif len(midi_wav_data) > len(audio_data):
                    audio_data = np.resize(audio_data, (len(midi_wav_data), 2))
                
                # Convert midi_wav_data to float64 for mixing
                midi_wav_data = midi_wav_data.astype(np.float64)
                
                # Mix MIDI WAV with the generated audio data (both stereo)
                audio_data += midi_wav_data * 0.5  # Adjust the mix level as needed

            else:
                app.logger.error(f"MIDI WAV data not in expected format. Type: {type(midi_wav_data)}, Sample rate: {midi_wav_sample_rate}, Expected rate: {sample_rate}")
        
        except Exception as e:
            app.logger.error(f"Error reading MIDI WAV file: {e}")

    # Normalize the combined audio data
    audio_data = audio_data / np.max(np.abs(audio_data))  # Normalize to [-1, 1] range

    # Convert to int16 (stereo output)
    final_audio_data = (audio_data * 32767).astype(np.int16)

    # Save the final mixed stereo audio data to WAV file
    final_audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    wav.write(final_audio_file_path, sample_rate, final_audio_data)

    # Generate visualizations
    plot_combined(final_audio_file_path)
    return file_name

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        json_file = request.files.get('json_file')
        if json_file:
            json_file_path = os.path.join('output/sample_v2/json', json_file.filename)
            json_file.save(json_file_path)
            
            with open(json_file_path, 'r') as f:
                json_data = json.load(f)
            
            wave_type = request.form['wave_type']
            synthesis_type = request.form['synthesis_type']
            effects_type = request.form['effects_type']
            envelope_type = request.form['envelope_type']
            
            # Extract drum parameters if provided
            drum_tempo = request.form.get('drum-tempo', type=int)
            beats_per_measure = request.form.get('beats-per-measure', type=int)
            num_measures = request.form.get('num-measures', type=int)
            drum_params = (drum_tempo, beats_per_measure, num_measures) if all([drum_tempo, beats_per_measure, num_measures]) else None

            # Check if MIDI is to be included
            include_midi = 'include_midi' in request.form
            include_sine = 'include_sine' in request.form

            file_name = f"{uuid.uuid4().hex}.wav"
            
            # Load color mapping
            color_mapping = load_color_mapping()

            # Handle MIDI file creation if checkbox is ticked
            midi_file_path = None
            if include_midi:
                app.logger.debug("include midi")  # Debugging line

                midi_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'generated_midi.mid')
                create_midi_from_frames(json_data, midi_file_path, color_mapping, drum_tempo)

            # Generate the audio file
            generate_audio(json_data, wave_type, file_name, synthesis_type, effects_type, envelope_type, drum_params if 'include_drums' in request.form else None, midi_file_path, include_sine)
            
            instruments_used = []
            # Find nearest colors and WAV files
            for color in json_data['overall_dominant_colors']:
                nearest_color, color_number = find_nearest_color(color['hex'], color_mapping)
                color['nearest_color'] = nearest_color
                color['wav_file'] = f"sounds/{color_number}.wav"  # Path to the associated WAV file
                instruments_used.append(color_number)

            # Get the corresponding video file name (same as JSON filename but with .mp4)
            video_filename = os.path.splitext(json_file.filename)[0] + '.mp4'

            return render_template('result.html', file_name=file_name, 
                                overall_dominant_colors=json_data['overall_dominant_colors'], 
                                video_filename=video_filename,
                                color_mapping=color_mapping,
                                instruments_used=instruments_used)
    return render_template('index.html')

@app.route('/sounds')
def sounds():
    return render_template('sounds.html')

@app.route('/color_mapping')
def color_mapping():
    return send_from_directory('static', 'color_mapping.json')

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/video/<filename>')
def video(filename):
    return send_from_directory(app.config['VIDEO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)