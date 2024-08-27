from colorama import Fore, Style
from backstage.schema import Exercise, Story, StoryBlock
from demo.SpeechAnalysis import SpeechAnalysis


class ExerciseManager:
    def __init__(self, language: str = "swedish"):
        self.pronunciation_analyzer = SpeechAnalysis(language=language)

    def handle_exercise(self, exercise: Exercise, story: Story):
        """
        Determines how to handle each type of exercise when displayed in the terminal.
        Calls the appropriate method based on the exercise type.
        """
        exercise_type = exercise.type

        if exercise_type == "comp-mcq":
            self.handle_comp_mcq(exercise)
        elif exercise_type == "comp-tf":
            self.handle_comp_tf(exercise)
        elif exercise_type == "speak-replace":
            self.handle_speak_replace(exercise, story)
        elif exercise_type == "speak-question":
            self.handle_speak_question(exercise, story)
        elif exercise_type == "interact":
            self.handle_interact(exercise, story)
        elif exercise_type == "comp-listen":
            self.handle_comp_listen(exercise)
        elif exercise_type == "pronounce-rep":
            self.handle_pronounce_rep(exercise, story)
        elif exercise_type == "pronounce-deaf":
            self.handle_pronounce_deaf(exercise, story)
        else:
            print(f"{Fore.RED}Unknown exercise type: {exercise_type}{Style.RESET_ALL}")

    def handle_comp_mcq(self, exercise: Exercise):
        # Handles a multiple-choice question (MCQ) exercise.

        print(f"\t{Fore.GREEN}Question:{Style.RESET_ALL} {exercise.query}")
        if exercise.answer_options:
            for k in exercise.answer_options.keys():
                idx = k
                text = exercise.answer_options[k].text
                print(f"\t{idx}. {text}")

        self._evaluate_user_answer(exercise)

    def handle_comp_tf(self, exercise: Exercise):
        # Handles a true-false question

        self.handle_comp_mcq(exercise)

    def handle_speak_replace(self, exercise: Exercise, story: Story):
        # Handles a speak-and-replace exercise.

        print("\tSpeak-and-Replace Exercise:")
        if exercise.query:
            print(f"\tPrompt: {exercise.query}")
        print("\tTry to speak the correct phrase.")
        self._evaluate_user_speech(exercise)

    def handle_speak_question(self, exercise: Exercise, story: Story):
        # Handles a speak-and-answer question exercise.

        print("\tSpeak-and-Answer Question Exercise:")
        if exercise.query:
            print(f"\tQuestion: {exercise.query}")
        print("\tRespond by speaking your answer.")
        self._evaluate_user_speech(exercise)

    def handle_interact(self, exercise: Exercise, story: Story):
        # Handles an interactive exercise.
        print("\tInteractive Exercise:")
        if exercise.query:
            print(f"\tInteraction prompt: {exercise.query}")
        print("\tEngage with the prompt interactively.")
        self._evaluate_interaction(exercise)

    def handle_comp_listen(self, exercise: Exercise) -> None:
        # Handles a listening comprehension exercise.
        print("\tListening Comprehension Exercise:")

        if exercise.answer_options:
            for option in exercise.answer_options:
                idx = option["id"]
                text = option["text"]
                print(f"\t{idx}. {text}")

            self._evaluate_user_answer(exercise)

    def handle_pronounce_rep(self, exercise: Exercise, story: Story):
        target_sentence = self._get_affected_line(exercise, story)
        # Handles a pronunciation repetition exercise.
        if target_sentence:
            # Start listening for the pronunciation
            self.pronunciation_analyzer.start_listening(target_sentence)

    # TODO: these are identical right now
    def handle_pronounce_deaf(self, exercise: Exercise, story: Story):
        target_sentence = self._get_affected_line(exercise, story)
        # Handles a pronunciation deaf exercise.
        if target_sentence:
            # Start listening for the pronunciation
            self.pronunciation_analyzer.start_listening(target_sentence)

    def _evaluate_user_answer(self, exercise: Exercise):
        # A private method to evaluate the user's answer for text-based exercises.

        user_answer = input("\tAnswer with the ID: ")
        is_correct = False
        while is_correct == False:
            try:
                is_correct = exercise.answer_options[user_answer].is_correct
                if is_correct:
                    print(f"\t{Fore.GREEN}Correct!{Style.RESET_ALL}")
                else:
                    print(f"\t{Fore.RED}Incorrect.{Style.RESET_ALL}")
                    user_answer = input("\tAnswer with the ID: ")
            except:
                print(f"\tInvalid answer. Please enter a valid option ID.")
                user_answer = input("\tAnswer with the ID: ")

    def _evaluate_user_speech(self, exercise: Exercise):
        # A private method to simulate speech evaluation.
        input("\tPress Enter when you are ready to speak...")
        print(
            "\t[Simulated speech recognition]"
        )  # Placeholder for actual speech recognition
        print(f"\tExpected correct phrase: {exercise.answer_options}")

    def _evaluate_interaction(self, exercise: Exercise):
        # A private method to handle user interaction.
        input("\tPress Enter to engage with the prompt...")
        print(
            "\t[Simulated interaction handling]"
        )  # Placeholder for actual interaction logic
        print("\tInteraction complete.")

    def _get_affected_line(self, exercise: Exercise, story: Story) -> str | None:
        # Check if there's an affected line specified
        if exercise.affected_line:
            print(f"\tRefer to block: {exercise.affected_line}")

            # Parse the affected_line string
            try:
                _, chapter_number, block_id, line_id = map(
                    int, exercise.affected_line.split("-")
                )

                # Find the chapter
                chapter = next(
                    (ch for ch in story.chapters if ch.chapter == chapter_number), None
                )
                if not chapter:
                    print("\tChapter not found.")
                    return None

                # Find the block within the chapter
                block = next(
                    (bl for bl in chapter.blocks if bl.block_id == block_id), None
                )
                if not block:
                    print("\tBlock not found.")
                    return None

                # Ensure the block is a StoryBlock
                if not isinstance(block, StoryBlock):
                    print("\tBlock is not a StoryBlock.")
                    return None

                # Find the line within the block
                line = next((ln for ln in block.lines if ln.line_id == line_id), None)
                if not line:
                    print("\tLine not found.")
                    return

                return line.text
            except ValueError:
                print("\tInvalid format for affected_line.")
        else:
            print("\tNo affected block specified.")
            return None


# Example usage
if __name__ == "__main__":
    # Example exercise instantiation
    sample_exercise = Exercise(
        exercise_id=1,
        type="comp-mcq",
        cefr=["A1", "A2"],
        query="What is the capital of France?",
        answer_options=[
            {"id": 1, "text": "Berlin"},
            {"id": 2, "text": "Madrid"},
            {"id": 3, "text": "Paris", "is_correct": True},
            {"id": 4, "text": "Rome"},
        ],
        correct_answer=3,
        affected_line="1-1-story-1",
    )

    manager = ExerciseManager()
    manager.handle_exercise(sample_exercise)
