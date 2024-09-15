from midiutil import MIDIFile
import subprocess
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_midi_file(file_path):
    # Create a MIDI file with one track
    midi = MIDIFile(1)
    midi.addTempo(0, 0, 120)  # Set tempo to 120 BPM

    # Define 8 different instruments (General MIDI program numbers)
    # instruments = [5, 45, 67, 34, 1, 23, 120, 12]
    instruments = [0, 10, 20, 30, 40, 50, 60, 70]  # Acoustic Grand Piano, Bright Acoustic Piano, etc.

    # Define notes and durations
    notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C4, D4, E4, F4, G4, A4, B4, C5
    durations = [1, 1, 2, 2]  # Quarter note, half note

    # Generate a melody for each instrument
    for i, instrument in enumerate(instruments):
        # Use a different channel for each instrument (channels 0-7)
        channel = i
        nextchannel = i + 1

        midi.addProgramChange(0, channel, 0, instrument)
         # Use a simple pattern: 8 notes for each instrument

        logging.debug(f"Instruments Used: {instruments[i]}")  # Using logging

        for j in range(8):
            pitch = notes[j % len(notes)]
            duration = durations[j % len(durations)]
            start_time = j * 2  # Start each note 2 seconds apart
            plusstart_time = j * 3  # Start each note 2 seconds apart

            velocity = 100  # Fixed velocity for simplicity
            logging.debug(f"Channel: {channel}")  # Using logging
            logging.debug(f"Pitch: {pitch}")  # Using logging

            # Add note to the respective channel
            midi.addNote(0, channel, pitch, start_time, duration, velocity)
            midi.addNote(0, channel, pitch, plusstart_time, duration, velocity)
            midi.addNote(0, nextchannel, pitch, start_time, duration, velocity)

    # Save the MIDI file
    with open(file_path, 'wb') as midi_file:
        midi.writeFile(midi_file)

# Function to convert MIDI to WAV using FluidSynth (command-line tool)
def midi_to_wav(midi_file, wav_file, soundfont_path):
    # Use subprocess to call the FluidSynth command-line tool
    command = ['fluidsynth', '-ni', soundfont_path, midi_file, '-F', wav_file, '-r', '44100']
    subprocess.run(command, check=True)

# Define file paths
midi_output_path = 'output/music_piece.mid'
wav_output_path = 'output/music_piece.wav'
soundfont_path = 'src/FluidR3_GM/FluidR3_GM.sf2'  # Path to your SoundFont file

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# Step 1: Create MIDI file
create_midi_file(midi_output_path)

# Step 2: Convert MIDI to WAV using FluidSynth
midi_to_wav(midi_output_path, wav_output_path, soundfont_path)

print(f'MIDI file saved at: {midi_output_path}')
print(f'WAV file saved at: {wav_output_path}')
