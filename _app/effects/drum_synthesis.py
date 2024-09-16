import numpy as np
import scipy.io.wavfile as wav

def generate_drum_beat(tempo, beats_per_measure, num_measures, sample_rate=44100, stereo=False):
    """Generate a simple drum beat sequence."""
    t = np.arange(0, num_measures * beats_per_measure * 60 / tempo, 1 / sample_rate)
    signal = np.zeros(len(t))

    # Define a simple kick drum sound
    kick_freq = 150  # Kick frequency in Hz
    kick_duration = 0.1  # Duration of each kick in seconds
    kick_amplitude = 0.5  # Amplitude of the kick sound
    kick_start_times = np.arange(0, len(t) / sample_rate, 60 / tempo)
    for start_time in kick_start_times:
        start_index = int(start_time * sample_rate)
        end_index = int((start_time + kick_duration) * sample_rate)
        signal[start_index:end_index] += kick_amplitude * np.sin(2 * np.pi * kick_freq * t[start_index:end_index])
    
    # Normalize the signal
    signal = signal / np.max(np.abs(signal))  # Normalize to [-1, 1]

    if stereo:
        # Duplicate the mono signal to create a stereo effect
        signal = np.column_stack((signal, signal))
    
    # Convert to 16-bit PCM format
    signal = np.int16(signal * 32767)
    
    return signal

def save_drum_beat(filename, drum_signal, sample_rate=44100):
    wav.write(filename, sample_rate, drum_signal)
