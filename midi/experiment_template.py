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
        #the thing is - this script does reutnr correct things - as its on the basisof the freame
        #and thisfunction was made for the overal donoinamnt - so will maybe require different approach
        nearest_color, color_number = find_nearest_color(frame_color, color_mapping)
        try:
            color_number = int(color_number)
        except (ValueError, TypeError):
            color_number = 0
        instrument = int(np.clip(color_number, 0, 127))
 


    return midi
