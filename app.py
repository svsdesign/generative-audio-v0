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

app = Flask(__name__)

# Define paths
UPLOAD_FOLDER = 'output/sample_v2/audio'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function for audio generation
def generate_audio(json_data, wave_type, file_name, synthesis_type, effects_type, envelope_type):
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
    
    # Normalize audio data
    audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
    
    # Save to WAV file
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
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
            file_name = f"{uuid.uuid4().hex}.wav"
            
            generate_audio(json_data, wave_type, file_name, synthesis_type, effects_type, envelope_type)
            return redirect(url_for('result', file_name=file_name))
    return render_template('index.html')

@app.route('/result/<file_name>')
def result(file_name):
    return render_template('result.html', file_name=file_name)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)