from pydub import AudioSegment
from pydub.playback import play
import matplotlib.pyplot as plt
import numpy as np
import simpleaudio as sa
import threading
import time

# Function to play audio in a separate thread
def play_audio(audio):
    play(audio)

# Load an MP3 file
audio = AudioSegment.from_file("mp3_audio_files/audio.mp3", format="mp3")
audio = audio.set_channels(1)  # Convert to mono

# Extract raw audio data
samples = np.array(audio.get_array_of_samples())

# Constants
CHUNK = 1024 * 2  # Samples per frame
RATE = audio.frame_rate  # Samples per second
UPDATE_INTERVAL = CHUNK / RATE  # Update interval in seconds

# Create matplotlib figure and axes
fig, ax = plt.subplots(1, figsize=(15, 7))

# Variable for plotting
x = np.arange(0, 2 * CHUNK, 2)

# Create a line object with initial data
(line,) = ax.plot(x, np.random.rand(CHUNK), "-", lw=2)

# Basic formatting for the axes
ax.set_title("AUDIO WAVEFORM")
ax.set_xlabel("samples")
ax.set_ylabel("volume")
ax.set_ylim(-32768, 32767)  # 16-bit audio range
ax.set_xlim(0, 2 * CHUNK)
plt.setp(ax, xticks=[0, CHUNK, 2 * CHUNK])

# Function to update the plot
def update_plot():
    start_time = time.time()
    for i in range(0, len(samples), CHUNK):
        data_chunk = samples[i : i + CHUNK]
        if len(data_chunk) < CHUNK:
            break

        # Update plot with new data
        line.set_ydata(data_chunk)

        # Update figure canvas
        fig.canvas.draw()
        fig.canvas.flush_events()

        # Wait to synchronize with the audio playback
        elapsed_time = time.time() - start_time
        time.sleep(max(0, (i / CHUNK) * UPDATE_INTERVAL - elapsed_time))

# Play audio in a separate thread to avoid blocking
threading.Thread(target=play_audio, args=(audio,)).start()

# Show the plot and update it
plt.show(block=False)
update_plot()
