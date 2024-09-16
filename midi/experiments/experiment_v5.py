import numpy as np
import random
from midiutil import MIDIFile
from utils.nearest_color import find_nearest_color
import logging

logger = logging.getLogger(__name__)

def add_music_layers(frames, color_to_instrument, duration_per_frame, color_mapping, bpm, num_tracks):
    # Initialize MIDI file with the desired number of tracks
    midi = MIDIFile(num_tracks)

    # Set the tempo
    midi.addTempo(0, 0, bpm)  # Track, Time, BPM

    logger.debug(f"add_music_layers - experiment with algorithmic composition and emotional mapping, {midi}")
    logger.debug(f"Tempo set to: {bpm} BPM")

    for i, frame in enumerate(frames):
        if frame['dominant_colors']:
            frame_color = frame['dominant_colors'][3]['hex']
        else:
            frame_color = "#000000"
        
        brightness = frame['brightness']
        pitch = int(np.clip(brightness * 10, 60, 80))
        
        nearest_color, color_number = find_nearest_color(frame_color, color_mapping)
        try:
            color_number = int(color_number)
        except (ValueError, TypeError):
            color_number = 0
        instrument = int(np.clip(color_number, 0, 127))

        if i % 10 == 0:
            midi.addProgramChange(0, 0, i * duration_per_frame, instrument)
            velocity = random.randint(90, 127)
            midi.addNote(0, 0, pitch, i * duration_per_frame, duration_per_frame, velocity)

    return midi
