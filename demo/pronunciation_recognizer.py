from typing import Literal
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import sounddevice as sd
from sounddevice import CallbackFlags
import numpy as np
from termcolor import colored
import logging
import re
from multiprocessing import Process, Queue, Event
from transformers import logging as transformers_logging

# Suppress unnecessary logging from transformers
transformers_logging.set_verbosity_error()


class PronunciationRecognizer:
    sampling_rate: int = 16000

    def __init__(
        self,
        language: Literal["english", "swedish", "french"],
        model_name: Literal[
            "openai/whisper-tiny", "openai/whisper-base", "openai/whisper-small"
        ] = "openai/whisper-tiny",
    ):
        # Setup Whisper model and processor
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
        self.forced_decoder_ids = self.processor.get_decoder_prompt_ids(
            language=language, task="transcribe"
        )

        self.target_sentence = ""
        self.is_listening = Event()
        self.is_listening.set()  # Initialize to True
        self.audio_buffer = []
        self.long_audio_buffer = []
        self.recognized_words = set()
        self.transcription_queue = Queue()

        # Setup logging
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def preprocess_text(sentence: str) -> str:
        """Convert text to lowercase and remove non-alphanumeric characters."""
        return re.sub(r"[^\w\s]", "", sentence.lower().strip())

    def audio_callback(
        self, indata: np.ndarray, frames: int, time, status: CallbackFlags
    ) -> None:
        if status:
            self.logger.info(f"Status: {status}")

        if not self.is_listening.is_set():
            raise sd.CallbackStop()

        audio_data = indata[:, 0]
        self.audio_buffer.extend(audio_data)
        self.long_audio_buffer.extend(audio_data)

        if len(self.audio_buffer) > 2.5 * PronunciationRecognizer.sampling_rate:
            self.process_audio_buffer()

        if len(self.long_audio_buffer) > 5 * PronunciationRecognizer.sampling_rate:
            self.transcription_queue.put(np.array(self.long_audio_buffer))
            self.long_audio_buffer.clear()

    def process_audio_buffer(self):
        """Process the short audio buffer and generate transcription."""
        audio_chunk = np.array(
            self.audio_buffer[: int(2.5 * PronunciationRecognizer.sampling_rate)]
        )
        self.audio_buffer = self.audio_buffer[
            int(1 * PronunciationRecognizer.sampling_rate) :
        ]

        input_features = self.processor(
            audio_chunk,
            sampling_rate=PronunciationRecognizer.sampling_rate,
            return_tensors="pt",
        ).input_features

        with torch.no_grad():
            predicted_ids = self.model.generate(
                input_features, forced_decoder_ids=self.forced_decoder_ids
            )
            transcription = self.processor.batch_decode(
                predicted_ids, skip_special_tokens=True
            )[0]

        self.highlight_recognized_text(self.preprocess_text(transcription))

    def highlight_recognized_text(self, recognized_text: str):
        recognized_words = set(recognized_text.split())
        target_words = set(self.target_sentence.split())

        self.recognized_words.update(recognized_words & target_words)

        highlighted_sentence = " ".join(
            colored(word, "green") if word in self.recognized_words else word
            for word in self.target_sentence.split()
        )

        print("\r" + " " * 100, end="")  # Clear the current line
        print(f"\rSentence: {highlighted_sentence}", end="")

        if self.recognized_words == target_words:
            print("\nYou pronounced the entire sentence correctly!")
            self.is_listening.clear()  # Stop the listening loop

    def process_long_transcription(self):
        """Process longer chunks of audio from the queue."""
        while self.is_listening.is_set():
            try:
                long_chunk = self.transcription_queue.get(timeout=1)
            except Exception:
                continue

            input_features = self.processor(
                long_chunk,
                sampling_rate=PronunciationRecognizer.sampling_rate,
                return_tensors="pt",
            ).input_features

            with torch.no_grad():
                predicted_ids = self.model.generate(
                    input_features, forced_decoder_ids=self.forced_decoder_ids
                )
                transcription = self.processor.batch_decode(
                    predicted_ids, skip_special_tokens=True
                )[0]

            self.highlight_recognized_text(self.preprocess_text(transcription))

    def start_listening(self, target_sentence: str):
        self.target_sentence = self.preprocess_text(target_sentence)
        print(f"Target sentence: {target_sentence}")

        long_process = Process(target=self.process_long_transcription)
        long_process.start()

        with sd.InputStream(
            samplerate=PronunciationRecognizer.sampling_rate,
            channels=1,
            callback=self.audio_callback,
        ):
            print("Please start speaking... (Press 'Enter' to skip)")
            input()  # Wait for user input to skip
            self.is_listening.clear()  # Signal to stop listening

        long_process.join()

        self.evaluate_performance()

        self.reset()

    def reset(self):
        """Reset the recognizer for a new session."""
        self.target_sentence = ""
        self.is_listening = Event()
        self.is_listening.set()  # Initialize to True
        self.audio_buffer = []
        self.long_audio_buffer = []
        self.recognized_words = set()
        self.transcription_queue = Queue()

    def evaluate_performance(self):
        """Evaluate whether the user pronounced enough of the sentence correctly."""
        recognized_percentage = (
            len(self.recognized_words) / len(self.target_sentence.split())
        ) * 100

        if recognized_percentage >= 80:
            print(f"\nPass! You pronounced {recognized_percentage:.2f}% correctly.")
        else:
            print(f"\nYou only pronounced {recognized_percentage:.2f}% correctly.")


if __name__ == "__main__":
    target_sentence = "Det är roligt att träffas"
    speech_recognizer = PronunciationRecognizer(language="swedish")
    speech_recognizer.start_listening(target_sentence)
