from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import numpy as np
import scipy.io.wavfile as wav
import json
import uuid
from audio.visualize_audio import plot_combined
from audio.audio_utils import generate_waveform
from audio.synthesis import apply_synthesis
from audio.effects import apply_effects
from audio.envelope import apply_envelope
from audio.drum_synthesis import generate_drum_beat, save_drum_beat

app = Flask(__name__)

# Define paths
UPLOAD_FOLDER = 'output/sample_v2/audio'
VIDEO_FOLDER = 'src/mp4'  # Path to the folder containing video files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIDEO_FOLDER'] = VIDEO_FOLDER

# Function for audio generation
def generate_audio(json_data, wave_type, file_name, synthesis_type, effects_type, envelope_type, drum_params):
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
        brightness = frame['brightness']
        freq = np.clip(brightness * 10, 100, 1000)  # Example mapping
        wave = generate_waveform(wave_type, freq, frame_duration, sample_rate)
        
        # Apply synthesis
        wave = apply_synthesis(wave, synthesis_type)
        
        # Apply envelope
        wave = apply_envelope(wave, envelope_type)
        
        # Apply effects
        wave = apply_effects(wave, effects_type)
        
        audio_data = np.concatenate((audio_data, wave))
    
    # Add drum sequence if parameters are provided
    if drum_params:
        drum_tempo, beats_per_measure, num_measures = drum_params
        drum_signal = generate_drum_beat(drum_tempo, beats_per_measure, num_measures)
        
        # Ensure the upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        drum_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'drum_beat.wav')
        save_drum_beat(drum_file_path, drum_signal)
        
        # Mix drum signal with audio data (simple mix)
        drum_signal = np.resize(drum_signal, len(audio_data))  # Resize drum signal to match audio data length
        audio_data += drum_signal * 0.2  # Adjust drum volume
    
    # Normalize audio data
    audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
    
    # Save to WAV file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    wav.write(file_path, sample_rate, audio_data)

    # Generate visualizations
    plot_combined(file_path)
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
            
            file_name = f"{uuid.uuid4().hex}.wav"
            
            # Generate the audio file
            generate_audio(json_data, wave_type, file_name, synthesis_type, effects_type, envelope_type, drum_params)
            
            # Extract dominant colors for result page
            overall_dominant_colors = json_data['overall_dominant_colors']
            
            # Get the corresponding video file name (same as JSON filename but with .mp4)
            video_filename = os.path.splitext(json_file.filename)[0] + '.mp4'
            
            return render_template('result.html', file_name=file_name, overall_dominant_colors=overall_dominant_colors, video_filename=video_filename)
    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/video/<filename>')
def video(filename):
    return send_from_directory(app.config['VIDEO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
