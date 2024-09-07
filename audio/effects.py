import numpy as np

def apply_effects(wave, effects_type):
    if effects_type == 'reverb':
        # Reverb effect example: simple delay
        delay_samples = int(0.1 * 44100)  # 0.1 seconds delay
        delayed_wave = np.pad(wave, (delay_samples, 0))[:-delay_samples]
        wave += delayed_wave * 0.5
    # More effects can be added here
    return wave
