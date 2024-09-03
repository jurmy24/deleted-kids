import json
import threading
from colorama import Fore, Style
from pydantic import UUID4
from models.story_schema import Exercise, ExerciseBlock, Story, StoryBlock
from demo.interaction_bot import InteractionBot
from demo.speech_recognizer import SpeechRecognizer
from demo.pronunciation_recognizer import PronunciationRecognizer
import random


class ExerciseManager:
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, language: str = "swedish", *args, **kwargs):
        with cls._lock:
            if language not in cls._instances:
                cls._instances[language] = super(ExerciseManager, cls).__new__(cls)
        return cls._instances[language]

    def __init__(self, language: str = "swedish"):
        if not hasattr(self, "_initialized"):
            self.language = language
            self.pronunciation_recognizer = PronunciationRecognizer(language=language)
            self.speech_recognizer = SpeechRecognizer(language=language)
            self.interaction_bot = InteractionBot()

            with open("stories/interaction_bots.json", "r") as file:
                self.voicebots = json.load(file)

            self._initialized = True

    def handle_exercise(self, exercise: Exercise, story: Story, processed_story: list):
        """
        Directs the handling of each exercise based on its type.
        """
        self.story = story
        self.exercise = exercise
        self.processed_story = processed_story
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
        self._evaluate_user_speech()

    def _handle_speak_question(self) -> None:
        """Handles a speak-and-answer question exercise."""
        print("\tSpeak-and-Answer Question Exercise:")
        if self.exercise.query:
            print(f"\tQuestion: {self.exercise.query}")
        self._evaluate_user_speech()

    # TODO: Add length limit
    def _handle_interaction(self) -> None:
        """Handles an interactive exercise."""
        if self.exercise.query:
            print(f"\tInteraction prompt: {self.exercise.query}")

        assistant_id: UUID4 = self.voicebots[str(self.story.story_id)]
        first_message: str = self.exercise.query
        context: str = "\n".join(self.processed_story)
        context += "\n\nGUIDANCE: Make sure the user speaks the language of the story and help them as needed. Speak in simple terminology in the language. You can also provide hints if they are struggling."

        self.interaction_bot.start_interaction(assistant_id, first_message, context)

        input("Press enter to stop voice call...")

        self.interaction_bot.stop_interaction()

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
