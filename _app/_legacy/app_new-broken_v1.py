from flask import Flask, request, render_template, send_from_directory
import os
import numpy as np
import scipy.io.wavfile as wav
import json
import uuid
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

import logging

# Fix for an imported library error
def patch_asscalar(a):
    return a.item()

setattr(np, "asscalar", patch_asscalar)

app = Flask(__name__)

# Set up logging configuration
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set a higher logging level for specific libraries
logging.getLogger('colormath').setLevel(logging.ERROR)
logging.getLogger('matplotlib').setLevel(logging.ERROR)

# Define paths
UPLOAD_FOLDER = 'output/sample_v2/audio'
VIDEO_FOLDER = 'src/mp4'
SOUNDFONT_PATH = 'src/FluidR3_GM/FluidR3_GM.sf2'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIDEO_FOLDER'] = VIDEO_FOLDER

# Function to convert MIDI to WAV
def midi_to_wav(midi_file_path, wav_file_path):
    app.logger.debug("midi_to_wav")  # Using logging

    midi_data = pretty_midi.PrettyMIDI(midi_file_path)
    midi_data.synthesize(filename=wav_file_path, soundfont=SOUNDFONT_PATH)

# Function to create MIDI file from video frames
def create_midi_from_frames(json_data, relevant_instruments, midi_file_path, drum_tempo=None):
    app.logger.debug("create_midi_from_frames")  # Using logging

    midi = MIDIFile(1)
    bpm = drum_tempo if drum_tempo else 120
    midi.addTempo(0, 0, bpm)

    video_duration = json_data['video_duration']
    frames = json_data['frames']
    duration = video_duration / len(frames)

    instruments_used = {}  # Dictionary to store instrument usage by frame index
    app.logger.debug("Instruments Used array", instruments_used)  # Debugging line

    for i, frame in enumerate(frames):
        brightness = frame['brightness']
        pitch = int(np.clip(brightness * 10, 60, 80))

        # Determine the instrument based on the color
        color_hex = frame.get('color_hex')
        color_number = None
        for number, hex_color in relevant_instruments.items():
            if hex_color == color_hex:
                color_number = number
                break
        instrument = color_number if color_number is not None else 0

        if i % 10 == 0:
            midi.addProgramChange(0, 0, i * duration, instrument)

        midi.addNote(0, 0, pitch, i * duration, duration, 100)

        instruments_used[i] = instrument  # Store the instrument used for this frame

        app.logger.debug("Instruments Used:",instruments_used[i])  # Using logging

    with open(midi_file_path, 'wb') as midi_file:
        midi.writeFile(midi_file)

    return instruments_used


# Function to find the nearest color
def find_nearest_color(hex_color, color_mapping):
    app.logger.debug("find_nearest_color", hex_color, color_mapping)  # Using logging

    color_rgb = sRGBColor.new_from_rgb_hex(hex_color)
    color_lab = convert_color(color_rgb, LabColor)

    nearest_color = None
    min_distance = float('inf')
    nearest_color_number = None

    for color_number, color_value in color_mapping.items():
        mapped_rgb = sRGBColor.new_from_rgb_hex(color_value)
        mapped_lab = convert_color(mapped_rgb, LabColor)
        distance = delta_e_cie2000(color_lab, mapped_lab)
        if distance < min_distance:
            min_distance = distance
            nearest_color = color_value
            nearest_color_number = color_number

    return nearest_color, nearest_color_number

# Function to load color mapping
def load_color_mapping():
    color_mapping_path = os.path.join('static', 'color_mapping.json')
    with open(color_mapping_path, 'r') as f:
        return json.load(f)

# Function for audio generation from video frames and optional MIDI
def generate_audio(json_data, wave_type, file_name, synthesis_type, effects_type, envelope_type, drum_params, include_sine=True):
    app.logger.debug("Generate_audio")
   
    video_duration = json_data['video_duration']
    frames = json_data['frames']
    
    sample_rate = 44100
    frame_duration = video_duration / len(frames)
    
    audio_data = np.zeros(int(sample_rate * video_duration))
    
    for i, frame in enumerate(frames):
        brightness = frame['brightness']
        wave = generate_waveform(wave_type, sample_rate, frame_duration, brightness)
        
        if synthesis_type:
            wave = apply_synthesis(wave, synthesis_type)
        
        if include_sine:
            sine_wave = generate_waveform('sine', sample_rate, frame_duration, brightness)
            wave += sine_wave * 0.5

        if envelope_type:
            wave = apply_envelope(wave, envelope_type)
        
        wave = apply_effects(wave, effects_type)
        
        start_index = int(i * frame_duration * sample_rate)
        end_index = start_index + len(wave)
        
        if end_index > len(audio_data):
            end_index = len(audio_data)
            wave = wave[:end_index - start_index]

        audio_data[start_index:end_index] += wave
    
    if drum_params:
        drum_tempo, beats_per_measure, num_measures = drum_params
        drum_signal = generate_drum_beat(drum_tempo, beats_per_measure, num_measures)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        drum_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'drum_beat.wav')
        save_drum_beat(drum_file_path, drum_signal)
        
        drum_signal = np.resize(drum_signal, len(audio_data))
        audio_data += drum_signal * 0.2
    
    audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
    
    generated_audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    wav.write(generated_audio_file_path, sample_rate, audio_data)

    audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
    
    final_audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    wav.write(final_audio_file_path, sample_rate, audio_data)

    plot_combined(final_audio_file_path)
    return file_name


@app.route('/', methods=['GET', 'POST'])
def index():
    app.logger.debug("Index route accessed")  # Using logging
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
            
            drum_tempo = request.form.get('drum-tempo', type=int)
            beats_per_measure = request.form.get('beats-per-measure', type=int)
            num_measures = request.form.get('num-measures', type=int)
            drum_params = (drum_tempo, beats_per_measure, num_measures) if all([drum_tempo, beats_per_measure, num_measures]) else None

            include_drums = 'use_drums' in request.form
            include_sine = 'include_sine' in request.form
            include_midi = 'use_midi' in request.form

            # Define MIDI file path
            midi_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.mid")
            
            file_name = f"{uuid.uuid4().hex}.wav"
            
            color_mapping = load_color_mapping()
            relevant_instruments = {}

            # Find nearest colors and WAV files
            for color in json_data['overall_dominant_colors']:
                nearest_color, color_number = find_nearest_color(color['hex'], color_mapping)
                if color_number is not None:
                    relevant_instruments[color_number] = nearest_color
                    color['nearest_color'] = nearest_color
                    color['wav_file'] = f"sounds/{color_number}.wav"

            if include_midi:
                create_midi_from_frames(json_data, relevant_instruments, midi_file_path, drum_tempo)


            generate_audio(json_data, wave_type, file_name, synthesis_type, effects_type, envelope_type, drum_params if include_drums else None, include_sine)

            video_filename = os.path.splitext(json_file.filename)[0] + '.mp4'

            return render_template('result.html', file_name=file_name, 
                                overall_dominant_colors=json_data['overall_dominant_colors'], 
                                video_filename=video_filename,
                                color_mapping=color_mapping,
                                instruments_used={})
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
