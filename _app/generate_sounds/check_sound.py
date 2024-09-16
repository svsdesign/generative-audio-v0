

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
import os
from midi2audio import FluidSynth
import pretty_midi

UPLOAD_FOLDER = 'output/sample_v2/audio'
VIDEO_FOLDER = 'src/mp4'  # Path to the folder containing video files
SOUNDFONT_PATH = 'src/FluidR3_GM/FluidR3_GM.sf2'  # Path to your SoundFont
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['VIDEO_FOLDER'] = VIDEO_FOLDER

# Test function to create a single instrument MIDI and convert to audio
def test_single_instrument(instrument_number, midi_file_path, wav_file_path):
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=instrument_number)

    # Create a few notes (C4 to B4)
    for pitch in range(60, 72):
        note = pretty_midi.Note(
            velocity=100, pitch=pitch, start=0, end=1
        )
        instrument.notes.append(note)
    
    midi.instruments.append(instrument)
    midi.write(midi_file_path)

    # Convert to audio using FluidSynth
    fs = FluidSynth(SOUNDFONT_PATH)
    fs.midi_to_audio(midi_file_path, wav_file_path)

# Test with a single known instrument
test_single_instrument(61, 'test_instrument_61.mid', 'test_instrument_61.wav')
