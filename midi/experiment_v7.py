import numpy as np
import random
from midiutil import MIDIFile
from utils.nearest_color import find_nearest_color
import logging

logger = logging.getLogger(__name__)

def add_music_layers(frames, color_to_instrument, duration_per_frame, color_mapping, bpm, num_tracks):
    midi = MIDIFile(num_tracks)
    
    # Initialize each track with a tempo
    for track in range(num_tracks):
        midi.addTempo(track, 0, bpm)  # Track, Time, BPM
        logger.debug(f"Track {track} initialized with Tempo: {bpm} BPM")
    
    logger.debug(f"add_music_layers - experiment with algorithmic composition and emotional mapping, {midi}")
    
    markov_transition_prob = {60: {62: 0.5, 64: 0.5}, 62: {64: 0.7, 60: 0.3}, 64: {60: 0.6, 62: 0.4}}
    fractal_depth = 3
    last_notes = {0: 60, 1: 48, 2: 60, 3: 72}
    duration_per_frame_seconds = 60.0 / bpm


    for color, getinstrument in color_to_instrument.items():
            logger.debug(f"Instrument number: {getinstrument}")  # Logs only the number part
            logger.debug(f"Instrument color: {color}")  # Logs only the color part 
            setinstrument = getinstrument # instrument = instrument # int(color_to_instrument.get(nearest_color, 0))  # Default to instrument 0 if color not found
            instrument = int(setinstrument)  #int(color_to_instrument.get(nearest_color, 0))  # Default to instrument 0 if color not found
   



    for i, frame in enumerate(frames):
        if frame['dominant_colors']:
            frame_color = frame['dominant_colors'][3]['hex']
        else:
            frame_color = "#000000"

        brightness = frame['brightness']
        pitch = int(np.clip(brightness * 10, 60, 80))

        # nearest_color, color_number = find_nearest_color(frame_color, color_mapping)
        # try:
        #     color_number = int(color_number)
        # except (ValueError, TypeError):
        #     color_number = 0
        # instrument = int(np.clip(color_number, 0, 127))

        if i % 10 == 0:
            if num_tracks > 0:
                midi.addProgramChange(0, 0, i * duration_per_frame, instrument)
            prev_pitch = last_notes[0]
            if prev_pitch in markov_transition_prob:
                current_pitch = random.choices(list(markov_transition_prob[prev_pitch].keys()), 
                                               weights=markov_transition_prob[prev_pitch].values())[0]
            else:
                scale_notes = get_scale_notes(pitch)
                current_pitch = random.choice(scale_notes)
            
            last_notes[0] = current_pitch

            velocity = random.randint(70, 127)
            if num_tracks > 0:
                midi.addNote(0, 0, current_pitch, i * duration_per_frame, duration_per_frame_seconds, velocity)

            if num_tracks > 1:
                bass_pitch = current_pitch - 24
                midi.addProgramChange(0, 1, i * duration_per_frame, instrument)
                midi.addNote(0, 1, bass_pitch, i * duration_per_frame, duration_per_frame_seconds, 100)
                last_notes[1] = bass_pitch

            if num_tracks > 2:
                chord_pitch = current_pitch - 12
                midi.addProgramChange(0, 2, i * duration_per_frame, instrument)
                midi.addNote(0, 2, chord_pitch, i * duration_per_frame, duration_per_frame_seconds * 2, 90)
                last_notes[2] = chord_pitch

            if num_tracks > 3:
                arp_pitch = current_pitch + 12
                midi.addProgramChange(0, 3, i * duration_per_frame, instrument)
                midi.addNote(0, 3, arp_pitch, i * duration_per_frame, duration_per_frame_seconds / 2, 80)

        if i % 16 == 0 and num_tracks > 4:
            for depth in range(fractal_depth):
                note_pitch = pitch + (depth * 2)
                midi.addProgramChange(0, 4, i * duration_per_frame, instrument)
                midi.addNote(0, 4, note_pitch, i * duration_per_frame + (depth * 0.1), duration_per_frame_seconds / (depth + 1), 100)

        if i % 4 == 0 and num_tracks > 8:
            kick_velocity = random.randint(100, 127)
            midi.addProgramChange(0, 8, i * duration_per_frame, 0)
            midi.addNote(0, 8, 36, i * duration_per_frame, 0.5, kick_velocity)
        if i % 8 == 4 and num_tracks > 8:
            snare_velocity = random.randint(80, 110)
            midi.addNote(0, 8, 38, i * duration_per_frame + 0.25, 0.5, snare_velocity)

        if i % 40 == 0 and num_tracks > 4:
            chords = get_chord_progression(pitch)
            for note in chords:
                midi.addNote(0, 4, note, i * duration_per_frame, 1, 100)

    # Ensure there are no empty tracks
    for track in range(num_tracks):
        if len(midi.tracks[track].eventList) == 0:
            logger.warning(f"Track {track} is empty.")
        else:
            logger.debug(f"Track {track} contains {len(midi.tracks[track].eventList)} events.")

    return midi

def get_scale_notes(root_pitch, scale='major'):
    scales = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10]
    }
    scale_notes = scales.get(scale, scales['major'])
    return [root_pitch + n for n in scale_notes]

def get_chord_progression(root_pitch):
    return [root_pitch, root_pitch + 4, root_pitch + 7, root_pitch + 12]
