import numpy as np
import random
from midiutil import MIDIFile
from midi2audio import FluidSynth
from utils.nearest_color import find_nearest_color
import logging

logger = logging.getLogger(__name__)

# Function to add MIDI notes for different layers (melody, bass, chords, arpeggios)
def add_music_layers(midi, frames, color_to_instrument, duration_per_frame, color_mapping, bpm, num_tracks):

    logger.debug(f"add_music_layers - experiment with algorithmic composition and emotional mapping, {midi}")

    # Set the tempo from the bpm parameter
    tempo = bpm
    logger.debug(f"Tempo set to: {tempo} BPM")

    # Markov chain probabilities for melody transitions
    markov_transition_prob = {60: {62: 0.5, 64: 0.5}, 62: {64: 0.7, 60: 0.3}, 64: {60: 0.6, 62: 0.4}}  # Example probabilities

    # Fractal depth level, controls recursive pattern generation
    fractal_depth = 3

    # Dictionary to track the last note played on each channel
    last_notes = {0: 60, 1: 48, 2: 60, 3: 72}  # Initialize last notes for melody, bass, chords, arpeggios

    # Adjust the time duration based on BPM and the frame rate
    duration_per_frame_seconds = 60.0 / tempo  # 1 beat duration in seconds at the given BPM

    for i, frame in enumerate(frames):
        if frame['dominant_colors']:
            frame_color = frame['dominant_colors'][3]['hex']  # Selecting the third dominant color
        else:
            frame_color = "#000000"  # Default to black if no dominant colors

        brightness = frame['brightness']
        pitch = int(np.clip(brightness * 10, 60, 80))  # Convert brightness to MIDI pitch (C4 to G4 range)
        
        nearest_color, color_number = find_nearest_color(frame_color, color_mapping)

        # Assign instrument based on the nearest color
        try:
            color_number = int(color_number)
        except (ValueError, TypeError):
            color_number = 0  # Default to 0 if color_number is invalid
        instrument = int(np.clip(color_number, 0, 127))

        # Set instrument periodically based on frame index
        if i % 10 == 0:
            midi.addProgramChange(0, 0, i * duration_per_frame, instrument)  # Set instrument on channel 0 (melody)

            # Use a Markov Chain for melody note generation
            prev_pitch = last_notes[0]  # Get the last note for the melody channel (channel 0)
            if prev_pitch in markov_transition_prob:
                current_pitch = random.choices(list(markov_transition_prob[prev_pitch].keys()), 
                                               weights=markov_transition_prob[prev_pitch].values())[0]
            else:
                current_pitch = pitch

            # Update last note for melody channel
            last_notes[0] = current_pitch

            velocity = random.randint(90, 127)
            midi.addNote(0, 0, current_pitch, i * duration_per_frame, duration_per_frame_seconds, velocity)

            # Add bass (lower octave) and chord layers
            bass_pitch = current_pitch - 24
            chord_pitch = current_pitch - 12

            # Update last notes for bass and chords
            last_notes[1] = bass_pitch
            last_notes[2] = chord_pitch

            midi.addProgramChange(0, 1, i * duration_per_frame, instrument)  # Set bass instrument on channel 1
            midi.addProgramChange(0, 2, i * duration_per_frame, instrument)  # Set chord instrument on channel 2

            # Add bass and chords
            midi.addNote(0, 1, bass_pitch, i * duration_per_frame, duration_per_frame_seconds, 100)  # Bass on channel 1
            midi.addNote(0, 2, chord_pitch, i * duration_per_frame, duration_per_frame_seconds * 2, 90)  # Chords on channel 2

            # Add arpeggios (higher octave)
            arp_pitch = current_pitch + 12
            midi.addProgramChange(0, 3, i * duration_per_frame, instrument)  # Set arpeggio instrument on channel 3
            midi.addNote(0, 3, arp_pitch, i * duration_per_frame, duration_per_frame_seconds / 2, 80)  # Arpeggios on channel 3

        # Introduce fractal-based rhythm patterns to add complexity
        if i % 16 == 0:
            for depth in range(fractal_depth):
                note_pitch = pitch + (depth * 2)
                midi.addProgramChange(0, 4, i * duration_per_frame, instrument)  # Use a different instrument
                midi.addNote(0, 4, note_pitch, i * duration_per_frame + (depth * 0.1), duration_per_frame_seconds / (depth + 1), 100)

        # Add drum patterns, changing based on the frame index
        if i % 4 == 0:
            kick_velocity = random.randint(100, 127)
            midi.addProgramChange(0, 8, i * duration_per_frame, 0)  # Channel 8 for drums
            midi.addNote(0, 8, 36, i * duration_per_frame, 0.5, kick_velocity)  # Kick drum
        if i % 8 == 4:
            snare_velocity = random.randint(80, 110)
            midi.addNote(0, 8, 38, i * duration_per_frame, 0.5, snare_velocity)  # Snare drum

        # Add periodic emotional transitions (e.g., shifts in brightness lead to modulation changes)
        if i % 40 == 0:
            # For simplicity, modulate to different keys based on mood
            for note in range(60, 72):  # C4 to B4
                midi.addNote(0, 4, note, i * duration_per_frame, 1, 100)

    return midi
