from typing import Literal
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import sounddevice as sd
import numpy as np
from transformers import logging as transformers_logging

# Suppress unnecessary logging from transformers
transformers_logging.set_verbosity_error()


class SpeechRecognizer:
    sampling_rate: int = 16000

    def __init__(
        self,
        language: Literal["english", "swedish", "french"] = "english",
        model_name: Literal[
            "openai/whisper-tiny", "openai/whisper-base", "openai/whisper-small"
        ] = "openai/whisper-tiny",
    ):
        # Setup Whisper model and processor
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
        self.language = language

        self.audio_buffer = []

    def audio_callback(self, indata: np.ndarray, frames: int, time, status):
        """Callback function to capture audio data."""
        if status:
            print(f"\tStatus: {status}")

        # Append audio data to the buffer
        self.audio_buffer.extend(indata[:, 0])

    def start_recording(self):
        """Record audio from the microphone."""
        print("\tRecording... Press Enter to stop.")

        with sd.InputStream(
            samplerate=self.sampling_rate,
            channels=1,
            callback=self.audio_callback,
        ):
            input()  # Wait for the user to press Enter to stop recording

        print("\tRecording stopped.")

    def transcribe_audio(self):
        """Transcribe the recorded audio using Whisper."""
        if not self.audio_buffer:
            print("\tNo audio recorded.")
            return

        # Convert audio buffer to a numpy array
        audio_data = np.array(self.audio_buffer)

        # Preprocess the audio for Whisper
        input_features = self.processor(
            audio_data,
            sampling_rate=self.sampling_rate,
            return_tensors="pt",
        ).input_features

        # Generate transcription
        with torch.no_grad():
            predicted_ids = self.model.generate(input_features)
            transcription = self.processor.batch_decode(
                predicted_ids, skip_special_tokens=True
            )[0]

        return transcription

    def recognize_speech(self):
        """Record and transcribe speech."""
        self.start_recording()
        return self.transcribe_audio()


if __name__ == "__main__":
    recognizer = SpeechRecognizer(language="english")
    print(recognizer.recognize_speech())
