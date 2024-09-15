import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for Matplotlib

import matplotlib.pyplot as plt
import numpy as np
import librosa
import librosa.display
import scipy.io.wavfile as wav
from matplotlib.gridspec import GridSpec

def plot_waveform(file_path):
    sample_rate, data = wav.read(file_path)
    time = np.linspace(0, len(data) / sample_rate, num=len(data))
    plt.figure(figsize=(10, 4))
    plt.plot(time, data)
    plt.title('Waveform')
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.savefig('static/waveform.png')
    plt.close()

def plot_spectrogram(file_path):
    # Load audio file
    y, sr = librosa.load(file_path)

    # Compute the spectrogram (get magnitude of complex-valued STFT)
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)

    # Create a figure
    plt.figure(figsize=(10, 4))

    # Plot the spectrogram
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')

    # Add color bar and labels
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.tight_layout()

    # Save or show the figure
    plt.savefig(f'{file_path}_spectrogram.png')
    plt.close()

def plot_mel_spectrogram(file_path):
    y, sr = librosa.load(file_path)
    mel = librosa.feature.melspectrogram(y=y, sr=sr)  # Correctly call with keyword arguments
    mel_db = librosa.power_to_db(mel, ref=np.max)
    plt.figure(figsize=(12, 8))
    librosa.display.specshow(mel_db, sr=sr, x_axis='time', y_axis='mel')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel Spectrogram')
    plt.savefig('static/mel_spectrogram.png')
    plt.close()

def plot_spectral_centroid(file_path):
    y, sr = librosa.load(file_path)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    plt.figure(figsize=(12, 4))
    plt.semilogy(librosa.times_like(centroid), centroid[0], label='Spectral centroid')
    plt.ylabel('Spectral centroid (Hz)')
    plt.xticks([])
    plt.xlim(0, centroid.shape[-1])
    plt.title('Spectral Centroid')
    plt.tight_layout()
    plt.savefig('static/spectral_centroid.png')
    plt.close()

def plot_combined(file_path):
    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, 2, width_ratios=[1, 1], height_ratios=[1, 1])

    ax0 = plt.subplot(gs[0])
    plot_waveform(file_path)
    ax0.imshow(plt.imread('static/waveform.png'))
    ax0.set_title('Waveform')

    ax1 = plt.subplot(gs[1])
    plot_spectrogram(file_path)
    ax1.imshow(plt.imread('static/spectrogram.png'))
    ax1.set_title('Spectrogram')

    ax2 = plt.subplot(gs[2])
    plot_mel_spectrogram(file_path)
    ax2.imshow(plt.imread('static/mel_spectrogram.png'))
    ax2.set_title('Mel Spectrogram')

    ax3 = plt.subplot(gs[3])
    plot_spectral_centroid(file_path)
    ax3.imshow(plt.imread('static/spectral_centroid.png'))
    ax3.set_title('Spectral Centroid')

    plt.tight_layout()
    plt.savefig('static/combined_visualization.png')
    plt.close()
