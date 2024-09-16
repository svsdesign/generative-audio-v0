from midiutil import MIDIFile
import subprocess
import os
import logging
import random

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name=s - %(levelname)s - %(message)s')

def create_aphex_twin_style_midi_with_audible_drums(file_path):
    # Create a MIDI file with multiple tracks (instruments)
    midi = MIDIFile(1)
    bpm = random.randint(120, 150)  # Random tempo between 120 and 150 BPM
    midi.addTempo(0, 0, bpm)  # Set tempo

    # Define instruments (using more experimental synth-like MIDI program numbers)
    instruments = [82, 89, 81, 101, 122, 98, 110, 119]  # Saws, Pads, Synths, FX
    logging.debug(f"Instruments chosen: {instruments}")

    # Define more complex rhythms (mix of short and long durations)
    notes = [60, 62, 64, 67, 69, 71, 73, 76]  # C4, D4, E4, G4, A4, B4, C5, E5
    durations = [0.5, 1, 1.5, 2, 3, 0.25]  # Short to longer note durations

    # Adding a drum beat using one of the existing instruments (Acoustic Grand Piano)
    drum_channel = 8  # Let's use channel 8 for the beat (MIDI channels 0-7 used for melody)
    kick_note = 36  # C2 - Bass drum
    snare_note = 38  # D2 - Snare drum
    hihat_note = 42  # F#2 - Closed Hi-hat

    # Increase the velocity for drums to make them louder
    kick_velocity = 127  # Max velocity for a strong, audible kick
    snare_velocity = 110  # Slightly lower for snare
    hihat_velocity = 100  # Even lower for hi-hat

    # Simple kick-snare pattern with hi-hat
    for j in range(32):  # Longer loop for the beat
        beat_time = j * 0.5  # Beat every half second

        if j % 4 == 0:  # Kick on the 1 and 3
            midi.addProgramChange(0, drum_channel, 0, 0)  # Acoustic Grand Piano as placeholder for drums
            midi.addNote(0, drum_channel, kick_note, beat_time, 0.5, kick_velocity)  # Add louder kick with longer duration

        if j % 4 == 2:  # Snare on the 2 and 4
            midi.addNote(0, drum_channel, snare_note, beat_time, 0.5, snare_velocity)  # Add snare with higher velocity

        if j % 2 == 1:  # Hi-hat on every offbeat
            midi.addNote(0, drum_channel, hihat_note, beat_time, 0.25, hihat_velocity)  # Add hi-hat

    # Use random velocities and durations for each note to create more variety in melody
    for i, instrument in enumerate(instruments):
        channel = i
        midi.addProgramChange(0, channel, 0, instrument)

        for j in range(16):  # Loop to create a more layered, intricate pattern
            pitch = random.choice(notes)
            duration = random.choice(durations)
            start_time = j * random.uniform(0.5, 1.5)  # Start each note at irregular intervals
            velocity = random.randint(50, 127)  # Randomize velocity for dynamics

            logging.debug(f"Channel: {channel}, Pitch: {pitch}, Duration: {duration}, Start time: {start_time}")

            midi.addNote(0, channel, pitch, start_time, duration, velocity)

            # Add some overlapping notes in adjacent channels for polyphonic textures
            if random.random() > 0.5:
                overlapping_pitch = random.choice(notes)
                overlapping_channel = (channel + 1) % len(instruments)  # Choose a different channel
                midi.addNote(0, overlapping_channel, overlapping_pitch, start_time + random.uniform(0, 0.5), duration, velocity)

    # Save the MIDI file
    with open(file_path, 'wb') as midi_file:
        midi.writeFile(midi_file)

# Function to convert MIDI to WAV using FluidSynth
def midi_to_wav(midi_file, wav_file, soundfont_path):
    # Use subprocess to call the FluidSynth command-line tool
    command = ['fluidsynth', '-ni', soundfont_path, midi_file, '-F', wav_file, '-r', '44100']
    subprocess.run(command, check=True)

# Define file paths
midi_output_path = 'output/aphex_twin_with_louder_drums.mid'
wav_output_path = 'output/aphex_twin_with_louder_drums.wav'
soundfont_path = 'src/FluidR3_GM/FluidR3_GM.sf2'  # Path to your SoundFont file

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# Step 1: Create Aphex Twin style MIDI file with audible drums
create_aphex_twin_style_midi_with_audible_drums(midi_output_path)

# Step 2: Convert MIDI to WAV using FluidSynth
midi_to_wav(midi_output_path, wav_output_path, soundfont_path)

print(f'MIDI file saved at: {midi_output_path}')
print(f'WAV file saved at: {wav_output_path}')
