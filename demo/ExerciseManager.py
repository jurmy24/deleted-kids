from colorama import Fore, Style
from backstage.schema import Exercise, Story, StoryBlock
from demo.SpeechRecognizer import SpeechRecognizer
from demo.PronunciationRecognizer import PronunciationRecognizer
import random


class ExerciseManager:
    def __init__(self, language: str = "swedish"):
        self.pronunciation_recognizer = PronunciationRecognizer(language=language)
        self.speech_recognizer = SpeechRecognizer(language=language)

    def handle_exercise(self, exercise: Exercise, story: Story):
        """
        Directs the handling of each exercise based on its type.
        """
        self.story = story
        self.exercise = exercise
        handlers = {
            "comp-mcq": self._handle_multiple_choice,
            "comp-tf": self._handle_true_false,
            "speak-replace": self._handle_speak_replace,
            "speak-question": self._handle_speak_question,
            "interact": self._handle_interaction,
            "comp-listen": self._handle_listening_comprehension,
            "pronounce-rep": self._handle_pronunciation_repetition,
            "pronounce-deaf": self._handle_pronunciation_deaf,
        }

        handler = handlers.get(exercise.type)
        if handler:
            handler()
        else:
            print(f"{Fore.RED}Unknown exercise type: {exercise.type}{Style.RESET_ALL}")

    def _handle_multiple_choice(self) -> None:
        """Handles a multiple-choice question (MCQ) exercise."""
        print(f"\t{Fore.GREEN}Question:{Style.RESET_ALL} {self.exercise.query}")
        self._display_answer_options()
        self._evaluate_user_answer()

    def _handle_true_false(self) -> None:
        """Handles a true/false question exercise."""
        self._handle_multiple_choice()

    def _handle_speak_replace(self) -> None:
        """Handles a speak-and-replace exercise."""
        print("\tSpeak-and-Replace Exercise:")
        if self.exercise.query:
            print(f"\tPrompt: {self.exercise.query}")
        print("\tTry to speak the correct phrase.")
        self._evaluate_user_speech()

    def _handle_speak_question(self) -> None:
        """Handles a speak-and-answer question exercise."""
        print("\tSpeak-and-Answer Question Exercise:")
        if self.exercise.query:
            print(f"\tQuestion: {self.exercise.query}")
        print("\tRespond by speaking your answer.")
        self._evaluate_user_speech()

    def _handle_interaction(self) -> None:
        """Handles an interactive exercise."""
        print("\tInteractive Exercise:")
        if self.exercise.query:
            print(f"\tInteraction prompt: {self.exercise.query}")
        print("\tEngage with the prompt interactively.")

    def _handle_listening_comprehension(self) -> None:
        """Handles a listening comprehension exercise."""
        print("\tListening Comprehension Exercise:")
        self._display_answer_options()
        self._evaluate_user_answer()

    def _handle_pronunciation_repetition(self) -> None:
        """Handles a pronunciation repetition exercise."""
        target_sentence = self._get_target_sentence()
        if target_sentence:
            self.pronunciation_recognizer.start_listening(target_sentence)

    def _handle_pronunciation_deaf(self) -> None:
        """Handles a pronunciation deaf exercise."""
        target_sentence = self._get_target_sentence()
        if target_sentence:
            self.pronunciation_recognizer.start_listening(target_sentence)

    def _display_answer_options(self) -> None:
        """Displays answer options for exercises."""
        if self.exercise.answer_options:
            for option_id, option in self.exercise.answer_options.items():
                print(f"\t{option_id}. {option.text}")

    def _evaluate_user_answer(self) -> None:
        """Evaluates the user's answer for text-based exercises."""
        while True:
            user_answer = input("\tAnswer with the ID: ")
            if user_answer in self.exercise.answer_options:
                if self.exercise.answer_options[user_answer].is_correct:
                    print(f"\t{Fore.GREEN}Correct!{Style.RESET_ALL}")
                else:
                    print(f"\t{Fore.RED}Incorrect.{Style.RESET_ALL}")
                break
            else:
                print(f"\tInvalid answer. Please enter a valid option ID.")

    def _evaluate_user_speech(self) -> None:
        """Evaluate user speech and provide feedback."""

        # Display a random hint if available
        if self.exercise.hints:
            random_hint = random.choice(self.exercise.hints)
            print(f"\tHint: {random_hint}")

        # Use SpeechRecognizer to record and transcribe the user's speech

        transcription = self.speech_recognizer.recognize_speech()
        print(f"\tTranscription: {transcription}")

    def _get_target_sentence(self) -> str | None:
        """Retrieves the target sentence from the affected line in the story."""
        if not self.exercise.affected_line:
            print("\tNo affected block specified.")
            return None

        print(f"\tRefer to block: {self.exercise.affected_line}")

        try:
            _, chapter_number, block_id, line_id = map(
                int, self.exercise.affected_line.split("-")
            )

            chapter = next(
                (ch for ch in self.story.chapters if ch.chapter == chapter_number), None
            )
            if not chapter:
                print("\tChapter not found.")
                return None

            block = next((bl for bl in chapter.blocks if bl.block_id == block_id), None)
            if not block:
                print("\tBlock not found.")
                return None

            if not isinstance(block, StoryBlock):
                print("\tBlock is not a StoryBlock.")
                return None

            line = next((ln for ln in block.lines if ln.line_id == line_id), None)
            if not line:
                print("\tLine not found.")
                return None

            return line.text

        except ValueError:
            print("\tInvalid format for affected_line.")
            return None
