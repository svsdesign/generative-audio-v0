import numpy as np

def apply_synthesis(wave, synthesis_type):
    if synthesis_type == 'additive':
        # Additive synthesis example: overlaying a sine wave
        additional_wave = np.sin(2 * np.pi * np.arange(len(wave)) * 2 / len(wave))
        wave += additional_wave
    # More synthesis techniques can be added here
    return wave
