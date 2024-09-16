from midiutil import MIDIFile
import subprocess
import os
import logging
import random

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_video_game_midi(file_path, track_length=128):
    # Create a MIDI file with multiple tracks (instruments)
    midi = MIDIFile(1)
    bpm = random.randint(120, 160)  # Random tempo between 120 and 160 BPM
    midi.addTempo(0, 0, bpm)  # Set tempo

    # Define track length in beats (track_length variable)
    total_beats = track_length

    # Define 80s/90s style instruments
    instruments = {
        "bass": 38,  # Synth Bass 1
        "lead": 81,  # Square Lead
        "harmony": 88,  # New Age Pad
        "arpeggio": 87,  # Sweep Pad
        "drums": 0,  # Acoustic Grand Piano used for drums (we'll simulate percussion)
    }

    # Define basic note sequences for different elements (notes in different octaves)
    bass_notes = [36, 40, 43, 47]  # C2, E2, G2, B2 (Root, 3rd, 5th, 7th)
    lead_notes = [60, 62, 64, 67, 69, 72, 74]  # C4, D4, E4, G4, A4, C5, D5 (Lead melody)
    harmony_notes = [55, 59, 62, 65, 67]  # G3, B3, D4, F4, G4 (Supportive chords)
    arpeggio_notes = [60, 64, 67, 72]  # C4, E4, G4, C5 (Arpeggios)

    # Durations for variability in notes
    durations = [0.5, 1, 1.5, 2, 0.25]

    # Add Bass Line (Channel 0)
    channel = 0
    midi.addProgramChange(0, channel, 0, instruments['bass'])
    for i in range(total_beats // 2):  # Every 2 beats
        bass_note = random.choice(bass_notes)
        duration = random.choice(durations)
        start_time = i * 2  # Every 2 beats
        velocity = random.randint(60, 90)
        midi.addNote(0, channel, bass_note, start_time, duration, velocity)

    # Add Lead Melody (Channel 1)
    channel = 1
    midi.addProgramChange(0, channel, 0, instruments['lead'])
    for i in range(total_beats):  # Lead plays every beat
        lead_note = random.choice(lead_notes)
        duration = random.choice(durations)
        start_time = i * 1  # Every beat
        velocity = random.randint(70, 127)
        midi.addNote(0, channel, lead_note, start_time, duration, velocity)

    # Add Harmony Layer (Channel 2)
    channel = 2
    midi.addProgramChange(0, channel, 0, instruments['harmony'])
    for i in range(total_beats // 2):  # Harmony plays slower
        harmony_note = random.choice(harmony_notes)
        duration = random.choice(durations)
        start_time = i * 2  # Every 2 beats
        velocity = random.randint(60, 100)
        midi.addNote(0, channel, harmony_note, start_time, duration, velocity)

    # Add Arpeggio (Channel 3)
    channel = 3
    midi.addProgramChange(0, channel, 0, instruments['arpeggio'])
    for i in range(total_beats):  # Arpeggios play every beat
        arpeggio_note = random.choice(arpeggio_notes)
        duration = random.choice(durations)
        start_time = i * 1  # Every beat
        velocity = random.randint(80, 110)
        midi.addNote(0, channel, arpeggio_note, start_time, duration, velocity)

    # Add Drum Pattern (Channel 9 for Drums)
    channel = 9  # Standard MIDI for percussion channel
    kick_note = 36  # C2 - Bass drum
    snare_note = 38  # D2 - Snare drum
    hihat_note = 42  # F#2 - Closed Hi-hat

    kick_velocity = 127  # Max velocity for a strong, audible kick
    snare_velocity = 110  # Slightly lower for snare
    hihat_velocity = 100  # Even lower for hi-hat

    for i in range(total_beats):
        start_time = i * 0.5  # Drum beat every half second

        if i % 4 == 0:  # Kick on the 1 and 3
            midi.addNote(0, channel, kick_note, start_time, 0.5, kick_velocity)

        if i % 4 == 2:  # Snare on the 2 and 4
            midi.addNote(0, channel, snare_note, start_time, 0.5, snare_velocity)

        if i % 2 == 1:  # Hi-hat on every offbeat
            midi.addNote(0, channel, hihat_note, start_time, 0.25, hihat_velocity)

    # Save the MIDI file
    with open(file_path, 'wb') as midi_file:
        midi.writeFile(midi_file)

# Function to convert MIDI to WAV using FluidSynth
def midi_to_wav(midi_file, wav_file, soundfont_path):
    # Use subprocess to call the FluidSynth command-line tool

    # Save the MIDI file
#     with open(file_path, 'wb') as midi_file:
#         midi.writeFile(midi_file)

# # Function to convert MIDI to WAV using FluidSynth (command-line tool)
# def midi_to_wav(midi_file, wav_file, soundfont_path):
#     # Use subprocess to call the FluidSynth command-line tool
    command = ['fluidsynth', '-ni', soundfont_path, midi_file, '-F', wav_file, '-r', '44100']
    subprocess.run(command, check=True)

# Define file paths
midi_output_path = 'output/music_piece.mid'
wav_output_path = 'output/music_piece.wav'
soundfont_path = 'src/FluidR3_GM/FluidR3_GM.sf2'  # Path to your SoundFont file

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# Step 1: Create MIDI file
create_video_game_midi(midi_output_path)

# Step 2: Convert MIDI to WAV using FluidSynth
midi_to_wav(midi_output_path, wav_output_path, soundfont_path)

print(f'MIDI file saved at: {midi_output_path}')
print(f'WAV file saved at: {wav_output_path}')
