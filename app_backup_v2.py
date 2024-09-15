from flask import Flask, request, render_template, send_from_directory
import os
import numpy as np
import scipy.io.wavfile as wav
import json
import uuid
import pretty_midi
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
SOUNDFONT_PATH = 'src/FluidR3_GM/FluidR3_GM.sf2'  # Path to your SoundFont
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIDEO_FOLDER'] = VIDEO_FOLDER

# Function to convert MIDI to WAV
def midi_to_wav(midi_file_path, wav_file_path):
    midi_data = pretty_midi.PrettyMIDI(midi_file_path)
    # Create a FluidSynth object to handle SoundFont
    midi_data.synthesize(filename=wav_file_path, soundfont=SOUNDFONT_PATH)

# Function to create MIDI file from video frames
def create_midi_from_frames(json_data, midi_file_path, drum_tempo=None):
    from midiutil import MIDIFile
    
    midi = MIDIFile(1)
    bpm = drum_tempo if drum_tempo else 120  # Use drum tempo if provided, otherwise default to 120 BPM
    midi.addTempo(0, 0, bpm)  # Track, Time, BPM
    
    # Set different instruments for different notes
    instrument_list = [0, 1, 2, 3, 4]  # Example instrument list; adjust as needed
    midi.addProgramChange(0, 0, 0, instrument_list[0])  # Track, Channel, Key, Program Number

    video_duration = json_data['video_duration']
    frames = json_data['frames']
    duration = video_duration / len(frames)  # Duration per frame in seconds

    for i, frame in enumerate(frames):
        brightness = frame['brightness']
        pitch = int(np.clip(brightness * 10, 60, 80))  # Convert brightness to MIDI pitch (60-80 is a C4 to G4 range)
        
        # Change instruments periodically
        if i % 10 == 0:  # Change instrument every 10 frames, for example
            instrument_index = (i // 10) % len(instrument_list)
            midi.addProgramChange(0, 0, i * duration, instrument_list[instrument_index])
        
        midi.addNote(0, 0, pitch, i * duration, duration, 100)  # Track, Channel, Pitch, Start, Duration, Velocity
    
    with open(midi_file_path, 'wb') as midi_file:
        midi.writeFile(midi_file)


# Function for audio generation from video frames and optional MIDI
def generate_audio(json_data, wave_type, file_name, synthesis_type, effects_type, envelope_type, drum_params, midi_file_path=None, include_sine=True):
    # Extract video duration and frame data
    video_duration = json_data['video_duration']
    frames = json_data['frames']
    
    # Parameters for audio generation
    sample_rate = 44100  # Hz
    frame_duration = video_duration / len(frames)  # Duration per frame in seconds
    
    # Create empty audio data array with length matching video duration
    audio_data = np.zeros(int(sample_rate * video_duration))
    
    for i, frame in enumerate(frames):
        brightness = frame['brightness']
        wave = generate_waveform(wave_type, sample_rate, frame_duration, brightness)
        
        if synthesis_type:
            wave = apply_synthesis(wave, synthesis_type)
        
        if include_sine:
            sine_wave = generate_waveform('sine', sample_rate, frame_duration, brightness)
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
    
    # Save generated audio data to WAV file
    generated_audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    wav.write(generated_audio_file_path, sample_rate, audio_data)

    # Convert MIDI to WAV if a MIDI file is provided
    if midi_file_path:
        midi_wav_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'midi_output.wav')
        midi_to_wav(midi_file_path, midi_wav_file_path)
        
        # Load the MIDI WAV file
        midi_wav_data, midi_wav_sample_rate = wav.read(midi_wav_file_path)
        
        # Ensure the lengths match or mix accordingly
        if len(midi_wav_data) < len(audio_data):
            midi_wav_data = np.resize(midi_wav_data, len(audio_data))
        elif len(midi_wav_data) > len(audio_data):
            audio_data = np.resize(audio_data, len(midi_wav_data))
        
        # Mix MIDI WAV with the generated audio data
        audio_data += midi_wav_data * 0.5  # Adjust the mix level as needed
    
    # Normalize audio data again after mixing
    audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
    
    # Save the final mixed audio data to WAV file
    final_audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    wav.write(final_audio_file_path, sample_rate, audio_data)

    # Generate visualizations
    plot_combined(final_audio_file_path)
    return file_name


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        json_file = request.files.get('json_file')
        midi_file = request.files.get('midi_file')  # Optional MIDI file upload
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

            # Check if drums and MIDI are to be included
            include_drums = 'use_drums' in request.form
            include_midi = 'use_midi' in request.form
            include_sine = 'include_sine' in request.form

            file_name = f"{uuid.uuid4().hex}.wav"
            
            # Save the MIDI file if provided and generate MIDI from frames if necessary
            midi_file_path = None
            if include_midi and midi_file:
                midi_file_path = os.path.join(app.config['UPLOAD_FOLDER'], midi_file.filename)
                midi_file.save(midi_file_path)
                create_midi_from_frames(json_data, midi_file_path)
            
            # Generate the audio file
            generate_audio(json_data, wave_type, file_name, synthesis_type, effects_type, envelope_type, drum_params if include_drums else None, midi_file_path, include_sine)
            
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
