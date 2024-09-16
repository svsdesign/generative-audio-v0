import random
import logging
from midiutil import MIDIFile

logger = logging.getLogger(__name__)

def add_music_layers(midi, frames, color_to_instrument, duration_per_frame, color_mapping, bpm, num_tracks):
    logger.debug("add_music_layers - experiment with algorithmic composition and emotional mapping")

    # Set the tempo from the bpm parameter
    tempo = bpm
    logger.debug(f"Tempo set to: {tempo} BPM")

    # Ensure the MIDI file has the necessary number of tracks
    while len(midi.tracks) < num_tracks:
        track = len(midi.tracks)
        midi.addTrackName(track, 0, f"Track {track}")
        midi.addTempo(track, 0, tempo)
        logger.debug(f"Track {track} added with name and tempo")

    def get_instrument_for_color(color):
        if color not in color_to_instrument:
            logger.warning(f"Color {color} not found in color_to_instrument mapping. Using default instrument.")
            return 0  # Default instrument if color not found
        getinstrument = color_to_instrument[color]
        try:
            instrument = int(getinstrument)
            if not 0 <= instrument <= 127:
                raise ValueError(f"Instrument number out of range: {instrument}")
        except ValueError as e:
            logger.error(f"Error for color {color}: {e}")
            instrument = 0  # Set to default instrument if there's an error
        return instrument

    def add_melody_notes(track_num, start_frame, duration, notes):
        if track_num < len(midi.tracks):
            track = midi.tracks[track_num]
            for note in notes:
                track.addNote(track_num, 0, note, start_frame * duration_per_frame, duration_per_frame, velocity=random.randint(64, 127))
        else:
            logger.error(f"Track number {track_num} is out of range. Skipping note addition.")

    def add_chord_notes(track_num, start_frame, duration, chords):
        if track_num < len(midi.tracks):
            track = midi.tracks[track_num]
            for chord in chords:
                for note in chord:
                    track.addNote(track_num, 0, note, start_frame * duration_per_frame, duration_per_frame, velocity=random.randint(64, 127))
        else:
            logger.error(f"Track number {track_num} is out of range. Skipping chord addition.")

    def generate_chord_progression():
        # Example chord progressions
        return [
            [60, 64, 67],  # C Major
            [62, 65, 69],  # D Minor
            [65, 69, 72],  # F Major
            [67, 71, 74]   # G Major
        ]

    def generate_arpeggios(base_note):
        # Generate an arpeggio pattern based on a base note
        return [base_note, base_note + 4, base_note + 7, base_note + 12]

    for frame_number, frame_data in enumerate(frames):
        color = frame_data.get('color')
        instrument = get_instrument_for_color(color)

        track_num = frame_number % num_tracks
        logger.debug(f"Frame {frame_number}: Color {color}, Instrument {instrument}, Track number {track_num}")

        # Add program change to the track
        if track_num < len(midi.tracks):
            track = midi.tracks[track_num]
            track.addProgramChange(0, instrument, 0)  # Add program change to the track
        else:
            logger.error(f"Track number {track_num} does not exist. Skipping note addition.")
            continue

        # Add melody notes
        melody_notes = [random.randint(60, 72)]  # Single random note for simplicity
        add_melody_notes(track_num, frame_number, duration_per_frame, melody_notes)

        # Add bass notes
        bass_notes = [random.randint(36, 48)]  # Random bass note
        add_melody_notes((track_num + 1) % num_tracks, frame_number, duration_per_frame, bass_notes)

        # Add chord notes
        chords = generate_chord_progression()
        current_chord = chords[frame_number % len(chords)]
        add_chord_notes((track_num + 2) % num_tracks, frame_number, duration_per_frame, [current_chord])

        # Add arpeggios
        base_note = random.randint(60, 72)
        arpeggios = generate_arpeggios(base_note)
        add_melody_notes((track_num + 3) % num_tracks, frame_number, duration_per_frame, arpeggios)

    return midi
