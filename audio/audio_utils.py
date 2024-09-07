import numpy as np

def generate_waveform(wave_type, freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    if wave_type == 'sine':
        return 0.5 * np.sin(2 * np.pi * freq * t)
    elif wave_type == 'square':
        return 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == 'sawtooth':
        return 0.5 * (2 * (t * freq - np.floor(t * freq + 0.5)))
    elif wave_type == 'triangle':
        return 0.5 * np.abs((t * freq) % 1 - 0.5) * 2
    elif wave_type == 'additive':
        # Example additive synthesis: sum of sine waves
        return 0.5 * (np.sin(2 * np.pi * freq * t) + np.sin(2 * np.pi * (freq / 2) * t))
    elif wave_type == 'subtractive':
        # Example subtractive synthesis: low-pass filtered square wave
        from scipy.signal import butter, lfilter
        square_wave = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
        b, a = butter(4, 0.1, btype='low')
        return lfilter(b, a, square_wave)
    else:
        raise ValueError(f"Unsupported wave type: {wave_type}")
