import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import sounddevice as sd
import numpy as np
from termcolor import colored


class LivePronunciationCheck:
    def __init__(
        self, target_sentence, model_name="openai/whisper-tiny", language="english"
    ):
        self.target_sentence = target_sentence.lower()
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
        self.forced_decoder_ids = self.processor.get_decoder_prompt_ids(
            language=language, task="transcribe"
        )
        self.sampling_rate = 16000
        self.is_listening = True
        self.buffer = []
        self.recognized_words = set()

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"Status: {status}")

        # Collect audio data
        audio_data = indata[:, 0]  # Use first channel if stereo
        self.buffer.extend(audio_data)

        # Process in chunks of ~2 seconds for better context
        if len(self.buffer) > 2 * self.sampling_rate:
            audio_chunk = np.array(self.buffer[: 2 * self.sampling_rate])
            self.buffer = self.buffer[
                int(1.5 * self.sampling_rate) :
            ]  # Keep the last 0.5 second of context

            # Convert audio data to tensor and preprocess for Whisper
            input_features = self.processor(
                audio_chunk,
                sampling_rate=self.sampling_rate,
                return_tensors="pt",
            ).input_features

            # Generate transcription
            with torch.no_grad():
                predicted_ids = self.model.generate(
                    input_features, forced_decoder_ids=self.forced_decoder_ids
                )
                transcription = self.processor.batch_decode(
                    predicted_ids, skip_special_tokens=True
                )

            # Highlight and display the recognized text
            self.highlight_text(transcription[0].lower())

    def highlight_text(self, recognized_text):
        recognized_words = recognized_text.split()
        target_words = self.target_sentence.split()

        # Update recognized words set
        self.recognized_words.update(
            word for word in recognized_words if word in target_words
        )

        highlighted_sentence = ""

        # Build the highlighted sentence
        for word in target_words:
            if word in self.recognized_words:
                highlighted_sentence += colored(word, "green") + " "
            else:
                highlighted_sentence += word + " "

        print("\r" + highlighted_sentence.strip(), end="")

        # Check if all words have been recognized
        if all(word in self.recognized_words for word in target_words):
            self.is_listening = False
            print("\nYou pronounced the entire sentence correctly!")

    def start_listening(self):
        print(f"Target sentence: {self.target_sentence}")
        print("Please start speaking... Press Ctrl+C to stop.")
        with sd.InputStream(
            samplerate=self.sampling_rate, channels=1, callback=self._callback
        ):
            while self.is_listening:
                sd.sleep(1000)


if __name__ == "__main__":
    target_sentence = "This is a test sentence to "
    live_checker = LivePronunciationCheck(target_sentence, language="english")
    live_checker.start_listening()
