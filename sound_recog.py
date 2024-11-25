import whisper
import sounddevice as sd
import numpy as np
import time
import os

# Load the Whisper model
model = whisper.load_model('base')

def get_transcribe(audio_data, language: str = 'pl'):
    return model.transcribe(audio=audio_data, language=language, verbose=True)

def clear_terminal():
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    # Recording settings
    duration = 5  # Duration in seconds
    fs = 16000    # Sampling rate
    update_interval = 0.2  # Interval to print audio stats

    print(f"Recording for {duration} seconds...")

    # Record audio from the microphone
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')

    # Initialize time tracking
    start_time = time.time()

    while time.time() - start_time < duration:
        # Wait for the update interval
        time.sleep(update_interval)

        # Clear the terminal
        clear_terminal()

        # Flatten the array to one dimension up to the current recorded time
        current_samples = int((time.time() - start_time) * fs)
        audio_data = myrecording[:current_samples].flatten()

        # Print stats about the recorded audio so far
        print("Audio data stats (current):")
        print(f"Elapsed time: {time.time() - start_time:.1f} seconds")
        print(f"Number of samples: {len(audio_data)}")
        print(f"Max amplitude: {np.max(audio_data)}")
        print(f"Min amplitude: {np.min(audio_data)}")
        print(f"Mean amplitude: {np.mean(audio_data)}")

    sd.wait()  # Wait until recording is finished
    print("Recording finished.")

    # Flatten the final recorded array
    audio_data = myrecording.flatten()

    # Transcribe the audio data
    result = get_transcribe(audio_data=audio_data)
    print('-'*50)
    print(result.get('text', ''))
