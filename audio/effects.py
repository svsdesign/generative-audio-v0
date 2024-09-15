import numpy as np

def apply_effects(wave, effects_type):
    if effects_type == 'delay':
        delay_samples = 4410  # Example delay of 0.1 seconds at 44100 Hz
        delayed_wave = np.roll(wave, delay_samples)  # Apply delay
        delayed_wave[:delay_samples] = 0  # Fill the beginning with zeros to avoid wrapping
        
        # Ensure the shapes match
        if wave.shape != delayed_wave.shape:
            min_length = min(wave.shape[0], delayed_wave.shape[0])
            wave = wave[:min_length]
            delayed_wave = delayed_wave[:min_length]

        wave += delayed_wave * 0.5
    # Add other effects here
    return wave
