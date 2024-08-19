from typing import Any
from pydantic import BaseModel, Field, validator

from backstage.schema import Exercise


class ExerciseManager:
    def handle_exercise(self, exercise: Exercise):
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
            self.handle_speak_replace(exercise)
        elif exercise_type == "speak-question":
            self.handle_speak_question(exercise)
        elif exercise_type == "interact":
            self.handle_interact(exercise)
        elif exercise_type == "comp-listen":
            self.handle_comp_listen(exercise)
        elif exercise_type == "pronounce-rep":
            self.handle_pronounce_rep(exercise)
        elif exercise_type == "pronounce-deaf":
            self.handle_pronounce_deaf(exercise)
        else:
            print(f"Unknown exercise type: {exercise_type}")

    def handle_comp_mcq(self, exercise: "Exercise"):
        """
        Handles a multiple-choice question (MCQ) exercise.
        """
        print("\tMultiple Choice Exercise:")
        if exercise.query:
            print(f"\tQuestion: {exercise.query}")
        if exercise.answer_options:
            print("\tOptions:")
            for idx, option in enumerate(exercise.answer_options, 1):
                print(f"\t{idx}. {option['text']}")
        self._evaluate_user_answer(exercise)

    def handle_comp_tf(self, exercise: "Exercise"):
        """
        Handles a true/false exercise.
        """
        print("\tTrue/False Exercise:")
        if exercise.query:
            print(f"\tStatement: {exercise.query}")
        print("\tOptions: True / False")
        self._evaluate_user_answer(exercise)

    def handle_speak_replace(self, exercise: "Exercise"):
        """
        Handles a speak-and-replace exercise.
        """
        print("\tSpeak-and-Replace Exercise:")
        if exercise.query:
            print(f"\tPrompt: {exercise.query}")
        print("\tTry to speak the correct phrase.")
        self._evaluate_user_speech(exercise)

    def handle_speak_question(self, exercise: "Exercise"):
        """
        Handles a speak-and-answer question exercise.
        """
        print("\tSpeak-and-Answer Question Exercise:")
        if exercise.query:
            print(f"\tQuestion: {exercise.query}")
        print("\tRespond by speaking your answer.")
        self._evaluate_user_speech(exercise)

    def handle_interact(self, exercise: "Exercise"):
        """
        Handles an interactive exercise.
        """
        print("\tInteractive Exercise:")
        if exercise.query:
            print(f"\tInteraction prompt: {exercise.query}")
        print("\tEngage with the prompt interactively.")
        self._evaluate_interaction(exercise)

    def handle_comp_listen(self, exercise: "Exercise"):
        """
        Handles a listening comprehension exercise.
        """
        print("\tListening Comprehension Exercise:")
        if exercise.query:
            print(f"\tListen and respond: {exercise.query}")
        self._play_affected_block(exercise)

    def handle_pronounce_rep(self, exercise: "Exercise"):
        """
        Handles a pronunciation repetition exercise.
        """
        print("\tPronunciation Repetition Exercise:")
        if exercise.query:
            print(f"\tRepeat after: {exercise.query}")
        self._play_affected_block(exercise)

    def handle_pronounce_deaf(self, exercise: "Exercise"):
        """
        Handles a pronunciation deaf exercise.
        """
        print("\tPronunciation Deaf Exercise:")
        if exercise.query:
            print(f"\tRepeat after: {exercise.query}")
        self._play_affected_block(exercise)

    def _evaluate_user_answer(self, exercise: "Exercise"):
        """
        A private method to evaluate the user's answer for text-based exercises.
        """
        user_answer = input("\tYour answer: ")
        correct_answer = exercise.correct_answer
        if user_answer.lower() in (
            str(correct_answer).lower(),
            str(exercise.answer_options.index(correct_answer) + 1),
        ):
            print("\tCorrect!")
        else:
            print(f"\tIncorrect. The correct answer is: {correct_answer}")

    def _evaluate_user_speech(self, exercise: "Exercise"):
        """
        A private method to simulate speech evaluation.
        This can be expanded with actual speech recognition in a real application.
        """
        input("\tPress Enter when you are ready to speak...")
        print(
            "\t[Simulated speech recognition]"
        )  # Placeholder for actual speech recognition
        print(f"\tExpected correct phrase: {exercise.correct_answer}")

    def _evaluate_interaction(self, exercise: "Exercise"):
        """
        A private method to handle user interaction.
        """
        input("\tPress Enter to engage with the prompt...")
        print(
            "\t[Simulated interaction handling]"
        )  # Placeholder for actual interaction logic
        print("\tInteraction complete.")

    def _play_affected_block(self, exercise: "Exercise"):
        """
        Plays or emphasizes the affected block based on the exercise configuration.
        """
        if exercise.affected_block:
            print(f"\tRefer to block: {exercise.affected_block}")
            # Simulate fetching and playing the affected block
            print(f"\t[Simulated playback for block {exercise.affected_block}]")
        else:
            print("\tNo affected block specified.")


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
        affected_block="1-1-story-1",
    )

    manager = ExerciseManager()
    manager.handle_exercise(sample_exercise)
