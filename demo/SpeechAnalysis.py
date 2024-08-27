from typing import Literal
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import sounddevice as sd
from sounddevice import CallbackFlags
import numpy as np
from termcolor import colored
import logging
import re


class LivePronunciationCheck:
    sampling_rate: int = 16000

    def __init__(
        self,
        target_sentence: str,
        language: Literal["english", "swedish", "french"],
        model_name: Literal[
            "openai/whisper-tiny", "openai/whisper-base", "openai/whisper-small"
        ] = "openai/whisper-tiny",
    ):
        # Setup Whisper model and processor
        self.processor: WhisperProcessor = WhisperProcessor.from_pretrained(model_name)
        self.model: WhisperForConditionalGeneration = (
            WhisperForConditionalGeneration.from_pretrained(model_name)
        )
        self.forced_decoder_ids = self.processor.get_decoder_prompt_ids(
            language=language, task="transcribe"
        )

        # Preprocess target sentence
        self.target_sentence = self._process_text(target_sentence)

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Add some other variables
        self.is_listening = True
        self.buffer = []
        self.recognized_words = set()

    def _process_text(self, sentence: str) -> str:
        # Convert to lowercase
        sentence = sentence.lower().strip()

        # Remove all non-alphanumeric characters (except spaces)
        sentence = re.sub(r"[^\w\s]", "", sentence)

        return sentence

    def _callback(
        self, indata: np.ndarray, frames: int, time, status: CallbackFlags
    ) -> None:  # time is of type CData but its not used

        if status:
            self.logger.info(f"Status: {status}")

        # Collect audio data
        audio_data = indata[:, 0]  # View all the frames from the first channel
        self.buffer.extend(audio_data)

        # Process in chunks of ~2 seconds for better context
        if len(self.buffer) > 2.5 * LivePronunciationCheck.sampling_rate:
            # Extract the first 3 seconds of audio data
            audio_chunk = np.array(
                self.buffer[: int(2.5 * LivePronunciationCheck.sampling_rate)]
            )
            self.buffer = self.buffer[
                int(1 * LivePronunciationCheck.sampling_rate) :
            ]  # Keep the last 1 second of context

            # Convert audio data to tensor and preprocess for Whisper
            input_features = self.processor(
                audio_chunk,
                sampling_rate=LivePronunciationCheck.sampling_rate,
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
            self.highlight_text(self._process_text(transcription[0]))

    def highlight_text(self, recognized_text: str):
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
        # Clear the current line by overwriting it with spaces
        print("\r" + " " * 100, end="")
        print(
            "\r"
            + highlighted_sentence.strip()
            + f"\t|\t Transcription: {recognized_text}",
            end="",
        )

        # Check if all words have been recognized
        if all(word in self.recognized_words for word in target_words):
            self.is_listening = False
            print("\n")
            self.logger.info("\nYou pronounced the entire sentence correctly!")

    def start_listening(self):
        self.logger.info(f"Target sentence: {self.target_sentence}")
        self.logger.info("Please start speaking... Press Ctrl+C to stop.")
        with sd.InputStream(
            samplerate=LivePronunciationCheck.sampling_rate,
            channels=1,
            callback=self._callback,
        ):
            while self.is_listening:
                sd.sleep(1000)


if __name__ == "__main__":
    target_sentence = "roligt att träffas"
    live_checker = LivePronunciationCheck(target_sentence, language="swedish")
    live_checker.start_listening()
