import numpy as np

def apply_envelope(wave, envelope_type):
    if envelope_type == 'fade_in':
        # Example envelope: fade in
        fade_in = np.linspace(0, 1, len(wave))
        wave = wave * fade_in
    # More envelope shaping techniques can be added here
    return wave
