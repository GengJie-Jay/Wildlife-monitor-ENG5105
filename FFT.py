

import pyaudio
import numpy as np

# Define the sampling rate and chunk size
RATE = 44100  # Sampling rate in Hz
CHUNK = 1024  # Number of frames per buffer

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open a streaming stream
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

# Define the cutoff frequency for the low-pass filter (in Hz)
cutoff_frequency = 1000.0  # Adjust this value based on your requirements

print("Streaming...")

try:
    while True:
        # Read audio input
        input_data = stream.read(CHUNK)
        audio_data = np.frombuffer(input_data, dtype=np.int16)

        # Apply FFT
        spectrum = np.fft.fft(audio_data)
        frequencies = np.fft.fftfreq(len(spectrum))

        # Apply a low-pass filter
        filtered_spectrum = spectrum.copy()
        filtered_spectrum[frequencies > cutoff_frequency] = 0

        # Apply inverse FFT
        filtered_audio_data = np.fft.ifft(filtered_spectrum)

        # Play filtered audio
        stream.write(filtered_audio_data.astype(np.int16).tobytes())

except KeyboardInterrupt:
    print("Stopped streaming.")

finally:
    # Stop streaming
    stream.stop_stream()
    stream.close()

    # Close PyAudio
    p.terminate()
