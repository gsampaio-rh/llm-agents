from pydub import AudioSegment
from pydub.playback import play
import numpy as np
import threading
from faster_whisper import WhisperModel
import io
import time

# Initialize Whisper model
model_size = "base"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

# Load an MP3 file
audio_file = "mp3_audio_files/audio.mp3"
audio = AudioSegment.from_file(audio_file, format="mp3")
audio = audio.set_channels(1)  # Convert to mono

# Constants
CHUNK_DURATION_MS = 500  # 0.5 seconds per chunk
OVERLAP_MS = 100  # 0.1 second overlap
CHUNK = int(audio.frame_rate * (CHUNK_DURATION_MS / 1000))  # Samples per chunk
OVERLAP = int(audio.frame_rate * (OVERLAP_MS / 1000))

# Buffer to hold transcribed text with timestamps
transcription_buffer = []


# Function to transcribe audio in chunks
def transcribe_audio(audio_segment, model):
    # Convert AudioSegment to bytes
    audio_bytes = io.BytesIO()
    audio_segment.export(audio_bytes, format="wav")
    audio_bytes.seek(0)

    # Transcribe the chunk using faster-whisper
    segments, _ = model.transcribe(audio_bytes)

    # Collect transcription results with timestamps
    transcriptions = [(segment.start, segment.text) for segment in segments]
    return transcriptions


# Function to process and transcribe audio chunks in real-time
def process_and_transcribe(audio):
    start_time = time.time()
    current_time = 0

    while current_time < len(audio):
        # Check the real playback time to synchronize
        actual_playback_time = time.time() - start_time
        if current_time / audio.frame_rate <= actual_playback_time:
            audio_chunk = audio[current_time : current_time + CHUNK]
            transcriptions = transcribe_audio(audio_chunk, model)

            # Add transcriptions to buffer
            transcription_buffer.extend(transcriptions)

            # Update the current time with overlap
            current_time += CHUNK - OVERLAP


# Function to play audio in a separate thread
def play_audio(audio):
    play(audio)


# Function to print transcriptions in sync with audio
def print_transcriptions():
    start_time = time.time()
    while transcription_buffer or audio_thread.is_alive():
        if transcription_buffer:
            start, text = transcription_buffer[0]
            actual_playback_time = time.time() - start_time
            # Ensure the transcription time matches or has passed
            if start <= actual_playback_time:
                print(
                    f"[Audio Current Time {actual_playback_time:.2f}s] [Text -> {text}]"
                )
                transcription_buffer.pop(0)
        time.sleep(0.01)


# Start audio playback and transcription concurrently
audio_thread = threading.Thread(target=play_audio, args=(audio,))
transcription_thread = threading.Thread(target=process_and_transcribe, args=(audio,))
printing_thread = threading.Thread(target=print_transcriptions)

audio_thread.start()
transcription_thread.start()
printing_thread.start()

audio_thread.join()
transcription_thread.join()
printing_thread.join()
