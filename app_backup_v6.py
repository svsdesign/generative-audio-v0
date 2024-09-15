from flask import Flask, request, render_template, send_from_directory
import os
import numpy as np
import scipy.io.wavfile as wav
from scipy.io.wavfile import write
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
import random
import logging
from midi2audio import FluidSynth


# Added this to fix an error in imported library
def patch_asscalar(a):
    return a.item()

setattr(np, "asscalar", patch_asscalar)
# End - added this to fix an error in imported library

app = Flask(__name__)

# Set up logging configuration
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set a higher logging level for specific libraries to reduce verbosity
logging.getLogger('colormath').setLevel(logging.ERROR)
logging.getLogger('matplotlib').setLevel(logging.ERROR)

# Define paths
UPLOAD_FOLDER = 'output/sample_v2/audio'
VIDEO_FOLDER = 'src/mp4'  # Path to the folder containing video files
SOUNDFONT_PATH = 'src/FluidR3_GM/FluidR3_GM.sf2'  # Path to your SoundFont
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIDEO_FOLDER'] = VIDEO_FOLDER

# Function to convert MIDI to WAV
# def midi_to_wav(midi_file_path, wav_file_path):
#     #reveiw this - use fluid synth? - Essetnially I need to ensure the sounds used are as per my colours and sound board
#     app.logger.debug("Converting MIDI to WAV")  # Debugging line

#     # Load MIDI file
#     midi_data = pretty_midi.PrettyMIDI(midi_file_path)

#     # Generate audio data
#     audio_data = midi_data.synthesize()

#     # Define a sample rate
#     sample_rate = 44100  # Hz

#     # Normalize audio_data (if it's not already)
#     max_amplitude = np.max(np.abs(audio_data))
#     if max_amplitude > 0:
#         audio_data = audio_data / max_amplitude  # Normalize to [-1, 1]

#     # Convert to int16 and write to WAV file
#     audio_data_int16 = (audio_data * 32767).astype(np.int16)
#     write(wav_file_path, sample_rate, audio_data_int16)


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

# Function to find the nearest color
def find_nearest_color(hex_color, color_mapping):
    # app.logger.debug(f"Finding nearest color: {hex_color}, {color_mapping}")  # Debugging line
    # app.logger.debug(f"Finding nearest color: {hex_color}")  # Debugging line

    # Convert input color from hex to sRGB
    color_rgb = sRGBColor.new_from_rgb_hex(hex_color)
    color_lab = convert_color(color_rgb, LabColor)

    nearest_color = None
    min_distance = float('inf')
    nearest_color_number = None

    for color_number, color_value in color_mapping.items():
        # Convert mapped color from hex to sRGB and then to Lab
        mapped_rgb = sRGBColor.new_from_rgb_hex(color_value)
        mapped_lab = convert_color(mapped_rgb, LabColor)
        
        # Calculate color distance
        distance = delta_e_cie2000(color_lab, mapped_lab)
        if distance < min_distance:
            min_distance = distance
            nearest_color = color_value
            nearest_color_number = color_number
    
    # app.logger.debug(f"before RETURN Finding nearest color {nearest_color}, {nearest_color_number}" )

    return nearest_color, nearest_color_number

# Function to create MIDI file from video frames with dynamic music layers
def create_midi_from_frames(json_data, midi_file_path, color_mapping, drum_tempo=None):
    app.logger.debug("Creating MIDI from frames")  # Debugging line

    # Initialize MIDI file with 1 track
    midi = MIDIFile(1)
    bpm = drum_tempo if drum_tempo else 120  # Use drum tempo if provided, otherwise default to 120 BPM
    midi.addTempo(0, 0, bpm)  # Track, Time, BPM

    # Extract overall dominant colors and create instrument mapping
    overall_dominant_colors = json_data['overall_dominant_colors']
    color_to_instrument = {}
    for color in overall_dominant_colors:
        color_hex = color['hex']
        nearest_color, color_number = find_nearest_color(color_hex, color_mapping)
        color_to_instrument[color_hex] = color_number
    
    app.logger.debug(f"Color to instrument mapping: {color_to_instrument}")  # Debugging line

    video_duration = json_data['video_duration']
    frames = json_data['frames']
    duration_per_frame = video_duration / len(frames)  # Duration per frame in seconds
    duration_per_frame =  duration_per_frame * 4   
    # Layers setup based on video frame data
    melody_instruments = []  # Instruments for melody layer
    bass_instruments = []    # Instruments for bass layer
    chord_instruments = []   # Instruments for chord layer
    arp_instruments = []     # Instruments for arpeggios

    for i, frame in enumerate(frames):
        if frame['dominant_colors']:
            frame_color = frame['dominant_colors'][3]['hex']  # Selecting last dominant color
            # app.logger.debug(f"frame_color:r {frame_color}")  # Debugging line

        else:
            frame_color = "#000000"  # Default to black if no dominant colors
            # app.logger.debug(f"default -frame_color:r {frame_color}")  # Debugging line

        brightness = frame['brightness']
        pitch = int(np.clip(brightness * 10, 60, 80))  # Convert brightness to MIDI pitch (C4 to G4 range)
        
        nearest_color, color_number = find_nearest_color(frame_color, color_mapping)
        # app.logger.debug(f"nearest_color: {nearest_color}")  # Debugging line
        # so this nearest color is on the basis of the color_mapping.json file - all 127
        # so can we also find the nearest colourin the dominant colours?
      
        # app.logger.debug(f"color_number: {color_number}")  # Debugging line

        # instrument = color_to_instrument.get(nearest_color, 0)  # Default to instrument 0 if not found
      # Convert color_number to an integer before using it
        try:
            color_number = int(color_number)
        except (ValueError, TypeError):
            color_number = 0  # Default to 0 if color_number is invalid

        # Now clip color_number to the valid MIDI instrument range (0 to 127)
        instrument = int(np.clip(color_number, 0, 127))
        # app.logger.debug(f"instrument: {instrument}")  # Debugging line


        # Set instruments periodically based on frame index and dominant color mapping
        if i % 10 == 0:  # Change instrument every 10 frames
            instrument_index = (i // 10) % len(color_to_instrument)
            midi.addProgramChange(0, 0, i * duration_per_frame, instrument)  # Set instrument on channel 0 (melody)
            app.logger.debug(f" #Change instrument every 10 frames: {instrument}")  # Debugging line
            app.logger.debug(f"instrument_index,{instrument_index}")
        # Add melody layer (lead synth)
        if i % 4 == 0:  # Play melody every 4 frames
            velocity = random.randint(90, 127)
            midi.addNote(0, 0, pitch, i * duration_per_frame, duration_per_frame, velocity)  # Melody on channel 0

        # Add bass layer (simple lower notes)
        if i % 8 == 0:  # Play bass every 8 frames
            bass_pitch = pitch - 24  # Lower octave for bass
            midi.addProgramChange(0, 1, i * duration_per_frame, instrument)  # Set bass instrument on channel 1
            midi.addNote(0, 1, bass_pitch, i * duration_per_frame, duration_per_frame, 100)  # Bass on channel 1
        
        # Add chord layer (sustained chords)
        if i % 16 == 0:  # Play chords every 16 frames
            chord_pitch = pitch - 12  # Mid-range notes for chords
            midi.addProgramChange(0, 2, i * duration_per_frame, instrument)  # Set chord instrument on channel 2
            midi.addNote(0, 2, chord_pitch, i * duration_per_frame, duration_per_frame * 2, 90)  # Chords on channel 2
        
        # Add arpeggios layer (fast, repeating notes)
        if i % 2 == 0:  # Play arpeggios every 2 frames
            arp_pitch = pitch + 12  # Higher octave for arpeggios
            midi.addProgramChange(0, 3, i * duration_per_frame, instrument)  # Set arpeggio instrument on channel 3
            midi.addNote(0, 3, arp_pitch, i * duration_per_frame, duration_per_frame / 2, 80)  # Arpeggios on channel 3

        # Optional: Add drum layer based on frame index or brightness (kick, snare, hi-hat)
        if i % 2 == 0:
            midi.addProgramChange(0, 8, i * duration_per_frame, 0)  # Channel 8 for drums
            kick_velocity = random.randint(100, 127)
            midi.addNote(0, 8, 36, i * duration_per_frame, 0.5, kick_velocity)  # Kick drum on beats 1 and 3
        if i % 4 == 2:
            snare_velocity = random.randint(80, 110)
            midi.addNote(0, 8, 38, i * duration_per_frame, 0.5, snare_velocity)  # Snare on beats 2 and 4

        #test  
        # if i % 2 == 1:
        #     midi.addProgramChange(0, 3, i * duration_per_frame, instrument)  # Set arpeggio instrument on channel 3
        #     # MyMIDI.addProgramChange(track, channel, time, program)
        #     app.logger.debug(f"i % 2 == 1: {instrument}")  # Debugging line
        #     midi.addNote(0, 10, 60, i * duration_per_frame, 10, 100)
        #     # MyMIDI.addNote(track,channel,pitch,time,duration,volume)

        # test  
        # if i % 20 == 1: # play every 20 freams
        #     # Set the instrument (program change) on channel 3
        #     # app.logger.debug(f"insturment changed {instrument} ")
        #     midi.addProgramChange(0, 3, i * duration_per_frame, instrument)  # Arpeggio instrument on channel 3
        #     # app.logger.debug(f"i % 2 == 1: {instrument}")  # Debugging line

        #     # Add a note on the same channel as the program change (channel 3 in this case)
        #     # Example: Adding a C4 (MIDI pitch 60) note for a duration of 10 units with velocity 100
        #     midi.addNote(0, 3, 60, i * duration_per_frame, 10, 100)
       
        # if i % 40 == 1:  # Play every 40 frames
        #     # Set the instrument (program change) on a different channel for each instrument
        #     midi.addProgramChange(0, 3, i * duration_per_frame, instrument)
            
        #     app.logger.debug(f"instrument = {instrument}")
            
        #     # Add a small time offset for the notes to give time for the program change to take effect
        #     note_start_time = i * duration_per_frame + 0.01  # small delay to let program change take effect
            
        #     # Add multiple notes to form a chord (like in your soundboard)
        #     for pitch in range(60, 72):  # C4 to B4
        #         midi.addNote(0, 3, pitch, note_start_time, 1, 100)


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
        # wave = generate_waveform(wave_type, sample_rate, frame_duration, brightness, stereo=True)  # Stereo waveform stereo var dones't exist?
        wave = generate_waveform(wave_type, sample_rate, frame_duration, brightness)


        if synthesis_type:
            wave = apply_synthesis(wave, synthesis_type)
        
        if include_sine:
            # sine_wave = generate_waveform('sine', sample_rate, frame_duration, brightness, stereo=True)#stereo var dones't exist?
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

            # Find nearest colors and WAV files
            for color in json_data['overall_dominant_colors']:
                nearest_color, color_number = find_nearest_color(color['hex'], color_mapping)
                color['nearest_color'] = nearest_color
                color['wav_file'] = f"sounds/{color_number}.wav"  # Path to the associated WAV file
            
            # Get the corresponding video file name (same as JSON filename but with .mp4)
            video_filename = os.path.splitext(json_file.filename)[0] + '.mp4'

            return render_template('result.html', file_name=file_name, 
                                overall_dominant_colors=json_data['overall_dominant_colors'], 
                                video_filename=video_filename,
                                color_mapping=color_mapping)
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