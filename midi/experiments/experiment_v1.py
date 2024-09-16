import numpy as np
import random
# import os
# import json
from midiutil import MIDIFile
# import midi
from midi2audio import FluidSynth
# import pretty_midi
from midiutil import MIDIFile
from utils.nearest_color import find_nearest_color
import logging

logger = logging.getLogger(__name__)

# Function to add MIDI notes for different layers (melody, bass, chords, arpeggios)
# Function to add MIDI notes for different layers (melody, bass, chords, arpeggios)
def add_music_layers(midi, frames, color_to_instrument, duration_per_frame, color_mapping):

    logger.debug(f"add_music_layers")  # Debugging line
    logger.debug(f"midi object{midi}")  # Debugging line

    for i, frame in enumerate(frames):
        if frame['dominant_colors']:
            frame_color = frame['dominant_colors'][3]['hex']  # Selecting last dominant color
            # frame_color = frame['dominant_colors'][0]['hex']  # Selecting first dominant color
            # logger.debug(f"frame_color: {frame_color}")  # Debugging line

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
        # logger.debug(f"instrument: {instrument}")  # Debugging line



        # # Set instruments periodically based on frame index and dominant color mapping
        if i % 10 == 0:  # Change instrument every 10 frames
            instrument_index = (i // 10) % len(color_to_instrument)
            midi.addProgramChange(0, 0, i * duration_per_frame, instrument)  # Set instrument on channel 0 (melody)
            logger.debug(f"#Change instrument every 10 frames: {instrument}")  # Debugging line
            logger.debug(f"instrument_index,{instrument_index}")
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


            if i % 80 == 1:  # Play every 40 frames
                # Set the instrument (program change) on a different channel for each instrument
                midi.addProgramChange(0, 4, i * duration_per_frame, instrument)
                
                # logger.debug(f"instrument = {instrument}")
                
                # Add a small time offset for the notes to give time for the program change to take effect
                note_start_time = i * duration_per_frame + 0.01  # small delay to let program change take effect
                
                # Add multiple notes to form a chord (like in your soundboard)
                for pitch in range(60, 72):  # C4 to B4
                    midi.addNote(0, 4, pitch, note_start_time, 1, 100)


        #test  
        # if i % 2 == 1:
        #     midi.addProgramChange(0, 10, i * duration_per_frame, instrument)  # Set arpeggio instrument on channel 3
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

    return midi
