import random
from typing import Literal
from colorama import Fore, Style

from backstage.firebase_storage import FirebaseStorage
from story_compiler import compile_json_to_story, read_json_file
from backstage.schema import Exercise, ExerciseBlock, Story, StoryBlock
from demo.ExerciseManager import ExerciseManager  # Import the ExerciseManager
from demo.AudioPlayer import BackgroundAudioPlayer
from pydub.exceptions import CouldntDecodeError


class StoryPlayer:
    def __init__(self, story: Story, user_level: Literal["A1", "A2", "B1", "B2", "C1"]):
        self.story = story
        self.user_level = user_level
        self.audio_storage = FirebaseStorage()
        self.exercise_manager = ExerciseManager()  # Initialize the ExerciseManager
        self.audio_player = BackgroundAudioPlayer()

        self.play_intro()

    def _play_audio(self, audio_url: str):
        # Assuming audio_url is a link to the audio file
        audio_data = self.audio_storage.download_blob_into_memory(audio_url)
        if audio_data:
            self.audio_player.play(audio_data)

    def play_intro(self):
        print("-" * 100)
        print(f"\n\n{Fore.CYAN}Story title:{Style.RESET_ALL} {self.story.title}")
        print(f"{Fore.CYAN}Description:{Style.RESET_ALL} {self.story.description} \n\n")
        # Play intro audio if available
        if self.story.audio:
            self._play_audio(self.story.audio)
        print("-" * 100)

        # Wait for user input asynchronously
        input()
        # Stop audio playback at the end of the chapter
        self.audio_player.stop()

    def play_chapter(self, chapter_number: int):
        chapter = self._get_chapter(chapter_number)
        if not chapter:
            print(f"Chapter {chapter_number} not found.")
            return

        self._display_chapter_intro(chapter)

        for block in chapter.blocks:
            if isinstance(block, StoryBlock):
                self._display_story_block(block)
            elif isinstance(block, ExerciseBlock):
                self._display_exercise_block(block)

    def _get_chapter(self, chapter_number: int):
        return next(
            (ch for ch in self.story.chapters if ch.chapter == chapter_number), None
        )

    def _display_chapter_intro(self, chapter):
        print(f"\n\nChapter title: {chapter.title}")
        print(f"Chapter summary: {chapter.summary}\n\n")
        print("-" * 100)
        input("Press enter to begin the chapter...")

    def _display_story_block(self, block: StoryBlock):
        for line in block.lines:
            print(f"\n{line.character}: {line.text}")
            # play_audio(line.audio)
            input("")

    def _display_exercise_block(self, block: ExerciseBlock):
        suitable_exercises = [
            exercise
            for exercise in block.exercise_options
            if self.user_level in exercise.cefr
        ]

        if suitable_exercises:
            exercise = random.choice(suitable_exercises)
            self._display_exercise(exercise)
            input("Press Enter to continue...")
        else:
            print("No suitable exercise available for your level.")

    def _display_exercise(self, exercise: Exercise):
        print("\tExercise:")
        print(f"\tType: {exercise.type}")

        # Delegate the exercise handling to ExerciseManager
        self.exercise_manager.handle_exercise(exercise)


if __name__ == "__main__":
    json_file_path = "stories/se/beginner-fika.json"
    json_data = read_json_file(json_file_path)
    story_object = compile_json_to_story(json_data)

    story_player = StoryPlayer(story_object, user_level="A1")
    story_player.play_chapter(chapter_number=1)
