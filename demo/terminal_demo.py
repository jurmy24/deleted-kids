import random
from typing import Literal

from story_compiler import compile_json_to_story, read_json_file
from schema import Exercise, ExerciseBlock, Story, StoryBlock


class StoryPlayer:
    def __init__(self, story: Story, user_level: Literal["A1", "A2", "B1", "B2", "C1"]):
        self.story = story
        self.user_level = user_level

    def play_chapter(self, chapter_number: int):
        chapter = next(
            (ch for ch in self.story.chapters if ch.chapter == chapter_number), None
        )
        if not chapter:
            print(f"Chapter {chapter_number} not found.")
            return

        print(f"Title: {chapter.title}")
        print(f"Summary: {chapter.summary} \n\n")
        print("-" * 100)

        for block in chapter.blocks:
            if block.block_type == "story":
                self.display_story_block(block)
            elif block.block_type == "exercise":
                self.display_exercise_block(block)

    def display_story_block(self, block: StoryBlock):
        for line in block.lines:
            input(f"{line.character}: {line.text}")

    def display_exercise_block(self, block: ExerciseBlock):
        # Filter exercises based on the user's level
        suitable_exercises = [
            exercise
            for exercise in block.exercise_options
            if self.user_level in exercise.cefr
        ]

        if suitable_exercises:
            exercise = random.choice(suitable_exercises)
            self.display_exercise(exercise)
            input("Press Enter to continue...")
        else:
            print("No suitable exercise available for your level.")

    def display_exercise(self, exercise: Exercise):
        print("\tExercise:")
        print(f"\tType: {exercise.type}")
        if exercise.query:
            print(f"\tQuestion: {exercise.query}")
        if exercise.answer_options:
            print("\tOptions:")
            for idx, option in enumerate(exercise.answer_options, 1):
                print(f"\t{idx}. {option}")
        if exercise.hints:
            print("\tHints:")
            for hint in exercise.hints:
                print(f"\t- {hint}")
        if exercise.correct_answer:
            input("\tYour answer: ")
            print(f"\tCorrect Answer: {exercise.correct_answer}")


# Example usage:
# Assume `example_story` is an instance of the Story class with chapters already populated.
if __name__ == "__main__":
    # Specify the path to your JSON file
    json_file_path = "stories/se/beginner-fika.json"

    json_data = read_json_file(json_file_path)  # Read JSON data from the file

    story_object = compile_json_to_story(
        json_data
    )  # Compile the JSON data into a Pydantic Story object

    story_player = StoryPlayer(story_object, user_level="A1")
    story_player.play_chapter(1)
