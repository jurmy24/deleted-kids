import warnings

# NOTE: this is not recommended practice in production code, but this is just a demo
# Suppress all user warnings
warnings.filterwarnings("ignore", category=UserWarning)

import random
from typing import Literal, Tuple
from colorama import Fore, Style

from backstage.firebase_storage import FirebaseStorage
from backstage.story_compiler import compile_json_to_story, read_json_file
from backstage.story_schema import Chapter, Exercise, ExerciseBlock, Story, StoryBlock
from demo.ExerciseManager import ExerciseManager  # Import the ExerciseManager
from demo.AudioPlayer import BackgroundAudioPlayer


class StoryPlayer:
    def __init__(self, story: Story, user_level: Literal["A1", "A2", "B1", "B2", "C1"]):
        self.story = story
        self.user_level = user_level
        self.audio_storage = FirebaseStorage()
        self.exercise_manager = ExerciseManager()  # Initialize the ExerciseManager
        self.audio_player = BackgroundAudioPlayer()
        self.line_modifications = {}  # Store modifications for specific lines
        self.selected_exercises = {}  # Store preprocessing selected exercises

    def _parse_affected_line(self, affected_line: str) -> Tuple[int, int, int]:
        # Parse the affected_line string to extract StoryID, ChapterNumber, BlockID, and LineID.
        _, chapter_number, block_id, line_id = map(int, affected_line.split("-"))
        return chapter_number, block_id, line_id

    def _play_audio(self, audio_url: str) -> None:
        # Assuming audio_url is a link to the audio file
        audio_data = self.audio_storage.download_blob_into_memory(audio_url)
        if audio_data:
            self.audio_player.play(audio_data)

    def play_intro(self) -> None:
        print("-" * 100)
        print(f"\n{Fore.CYAN}Story:{Style.RESET_ALL} {self.story.title}")
        print(f"{Fore.CYAN}Description:{Style.RESET_ALL} {self.story.description} \n")

        if self.story.audio:
            self._play_audio(self.story.audio)

        print("-" * 100)
        input(f"{Fore.YELLOW}Press enter to start the story...{Style.RESET_ALL}")

        if self.story.audio:
            self.audio_player.stop()

    def play_chapter(self, chapter_number: int):
        chapter = self._get_chapter(chapter_number)
        if not chapter:
            print(f"{Fore.RED}Chapter {chapter_number} not found.{Style.RESET_ALL}")
            return

        # Preprocess blocks to select exercises and identify necessary modifications
        self._preprocess_blocks(chapter.blocks)

        self._display_chapter_intro(chapter)

        for block in chapter.blocks:
            if isinstance(block, StoryBlock):
                self._display_story_block(block)
            elif isinstance(block, ExerciseBlock):
                self._display_exercise_block(block)

    def _get_chapter(self, chapter_number: int) -> Chapter:
        return next(
            (ch for ch in self.story.chapters if ch.chapter == chapter_number), None
        )

    def _preprocess_blocks(self, blocks):
        # Select exercises and store modifications for story lines based on the selected exercise.
        for block in blocks:
            if isinstance(block, ExerciseBlock):
                suitable_exercises = [
                    exercise
                    for exercise in block.exercise_options
                    if self.user_level in exercise.cefr
                ]

                if suitable_exercises:
                    selected_exercise = random.choice(suitable_exercises)
                    self.selected_exercises[block.block_id] = selected_exercise

                    if selected_exercise.affected_line and selected_exercise.action:
                        _, block_id, line_id = self._parse_affected_line(
                            selected_exercise.affected_line
                        )
                        self.line_modifications[(block_id, line_id)] = (
                            selected_exercise.action
                        )

    def _display_chapter_intro(self, chapter: Chapter):
        print(
            f"\n{Fore.BLUE}Chapter {chapter.chapter}:{Style.RESET_ALL} {chapter.title}"
        )
        print(f"{Fore.BLUE}Chapter summary:{Style.RESET_ALL} {chapter.summary}\n")
        print("-" * 100)
        if chapter.audio:
            self._play_audio(chapter.audio)
        input(f"{Fore.YELLOW}Press enter to begin the chapter...{Style.RESET_ALL}")
        if chapter.audio:
            self.audio_player.stop()

    def _display_story_block(self, block: StoryBlock):
        for line in block.lines:
            action = self.line_modifications.get((block.block_id, line.line_id), None)

            # Modify the display based on the action
            if action in ["hide-text", "hide-all"]:
                print(
                    f"\n{Fore.MAGENTA}{line.character}:{Style.RESET_ALL} [Text Hidden]\n"
                )
            elif action == "emphasize-text":
                print(
                    f"\n{Fore.MAGENTA}{line.character}:{Fore.LIGHTCYAN_EX} {line.text} {Style.RESET_ALL}\n"
                )
            else:
                print(
                    f"\n{Fore.MAGENTA}{line.character}:{Style.RESET_ALL} {line.text}\n"
                )

            if line.audio and action not in ["hide-all", "hide-audio"]:
                self._play_audio(line.audio)

            input(f"{Fore.YELLOW}Press enter to continue...{Style.RESET_ALL}")

            if line.audio and action not in ["hide-all", "hide-audio"]:
                self.audio_player.stop()

    def _display_exercise_block(self, block: ExerciseBlock):
        # Use the preselected exercise for this block
        selected_exercise = self.selected_exercises.get(block.block_id, None)

        if selected_exercise:
            self._display_exercise(selected_exercise)
            input(f"{Fore.YELLOW}Press enter to continue...{Style.RESET_ALL}")
        else:
            print(
                f"{Fore.RED}No suitable exercise available for your level.{Style.RESET_ALL}"
            )

    def _display_exercise(self, exercise: Exercise):
        print(f"\n\t{Fore.GREEN}EXERCISE{Style.RESET_ALL}")
        print(f"\t{Fore.GREEN}Type:{Style.RESET_ALL} {exercise.type} \n")
        self.exercise_manager.handle_exercise(exercise, self.story)


if __name__ == "__main__":
    json_file_path = "stories/se/beginner-fika.json"
    json_data = read_json_file(json_file_path)
    story_object = compile_json_to_story(json_data)

    story_player = StoryPlayer(story_object, user_level="A1")
    story_player.play_intro()
    story_player.play_chapter(chapter_number=1)
