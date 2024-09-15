# from flask import Flask, request, render_template, send_from_directory
# import os
# import numpy as np
# import scipy.io.wavfile as wav
# from scipy.io.wavfile import write
# import json
# import uuid
# import pretty_midi
# from midiutil import MIDIFile
# from colormath.color_objects import sRGBColor, LabColor
# from colormath.color_conversions import convert_color
# from colormath.color_diff import delta_e_cie2000
# from audio.visualize_audio import plot_combined
# from audio.audio_utils import generate_waveform
# from audio.synthesis import apply_synthesis
# from audio.effects import apply_effects
# from audio.envelope import apply_envelope
# from audio.drum_synthesis import generate_drum_beat, save_drum_beat
# import random
# import logging
# from midi2audio import FluidSynth
#  # from audio.utilities.nearest_color import find_nearest_color  # Import the function from the nearest_color file

# logging.basicConfig(level=logger.debug, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logging.getLogger('colormath').setLevel(logging.ERROR)

# # Function to find the nearest color
# def find_nearest_color(hex_color, color_mapping):
    
#     logger.debug(f"Finding nearest color: {hex_color}, {color_mapping}")  # Debugging line
#     logger.debug(f"Finding nearest color: {hex_color}")  # Debugging line

#     # Convert input color from hex to sRGB
#     color_rgb = sRGBColor.new_from_rgb_hex(hex_color)
#     color_lab = convert_color(color_rgb, LabColor)

#     nearest_color = None
#     min_distance = float('inf')
#     nearest_color_number = None

#     for color_number, color_value in color_mapping.items():
#         # Convert mapped color from hex to sRGB and then to Lab
#         mapped_rgb = sRGBColor.new_from_rgb_hex(color_value)
#         mapped_lab = convert_color(mapped_rgb, LabColor)
        
#         # Calculate color distance
#         distance = delta_e_cie2000(color_lab, mapped_lab)
#         if distance < min_distance:
#             min_distance = distance
#             nearest_color = color_value
#             nearest_color_number = color_number
    
#     # app.logger.debug(f"before RETURN Finding nearest color {nearest_color}, {nearest_color_number}" )

#     return nearest_color, nearest_color_number

import logging

logger = logging.getLogger(__name__)

# utils/color_utilities.py
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

def find_nearest_color(hex_color, color_mapping):
   
    # logger.debug(f"find_nearest_color")  

    color_rgb = sRGBColor.new_from_rgb_hex(hex_color)
    color_lab = convert_color(color_rgb, LabColor)

    # logger.debug(f"color_rgb: {color_rgb}")  # Debugging line
    # logger.debug(f"color_lab: {color_lab}")  # Debugging line
  
    nearest_color = None
    min_distance = float('inf')
    nearest_color_number = None

    for color_number, color_value in color_mapping.items():
        mapped_rgb = sRGBColor.new_from_rgb_hex(color_value)
        mapped_lab = convert_color(mapped_rgb, LabColor)
        distance = delta_e_cie2000(color_lab, mapped_lab)
        if distance < min_distance:
            min_distance = distance
            nearest_color = color_value
            nearest_color_number = color_number

    return nearest_color, nearest_color_number
