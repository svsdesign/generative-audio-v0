import os
from midi2audio import FluidSynth
import pretty_midi

SOUNDFONT_PATH = 'src/FluidR3_GM/FluidR3_GM.sf2'
OUTPUT_FOLDER = 'static/sounds'
NUM_INSTRUMENTS = 128

# Create the output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def create_midi_for_instrument(instrument_number, midi_file_path):
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=instrument_number)
    
    # Create some notes for testing
    for pitch in range(60, 72):  # MIDI notes from C4 to B4
        note = pretty_midi.Note(
            velocity=100, pitch=pitch, start=0, end=1
        )
        instrument.notes.append(note)
    
    midi.instruments.append(instrument)
    midi.write(midi_file_path)

def generate_wav_from_midi(midi_file_path, wav_file_path):
    fs = FluidSynth(SOUNDFONT_PATH)
    fs.midi_to_audio(midi_file_path, wav_file_path)

for i in range(NUM_INSTRUMENTS):
    midi_file_path = os.path.join(OUTPUT_FOLDER, f'{i}.mid')
    wav_file_path = os.path.join(OUTPUT_FOLDER, f'{i}.wav')
    
    create_midi_for_instrument(i, midi_file_path)
    generate_wav_from_midi(midi_file_path, wav_file_path)
    
    print(f'Generated sound for instrument {i}')
