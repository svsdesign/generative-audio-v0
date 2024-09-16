import numpy as np
from scipy.signal import butter, lfilter

def generate_waveform(wave_type, sample_rate, frame_duration, brightness, stereo=False):
    # Time array for waveform generation
    t = np.linspace(0, frame_duration, int(sample_rate * frame_duration), endpoint=False)
    
    # Generate waveform based on type
    if wave_type == 'sine':
        wave = 0.5 * np.sin(2 * np.pi * brightness * t)
    elif wave_type == 'square':
        wave = 0.5 * np.sign(np.sin(2 * np.pi * brightness * t))
    elif wave_type == 'sawtooth':
        wave = 0.5 * (2 * (t * brightness - np.floor(t * brightness + 0.5)))
    elif wave_type == 'triangle':
        wave = 0.5 * np.abs((t * brightness) % 1 - 0.5) * 2
    elif wave_type == 'additive':
        # Example additive synthesis: sum of sine waves
        wave = 0.5 * (np.sin(2 * np.pi * brightness * t) + np.sin(2 * np.pi * (brightness / 2) * t))
    elif wave_type == 'subtractive':
        # Example subtractive synthesis: low-pass filtered square wave
        square_wave = 0.5 * np.sign(np.sin(2 * np.pi * brightness * t))
        b, a = butter(4, 0.1, btype='low')
        wave = lfilter(b, a, square_wave)
    else:
        raise ValueError(f"Unsupported wave type: {wave_type}")

    # If stereo is requested, duplicate the waveform for both channels
    if stereo:
        wave = np.column_stack((wave, wave))  # Duplicate for left and right channels

    return wave
