import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from utils.story_schema import ExerciseBlock, Story, StoryBlock
from backstage.firebase_storage import FirebaseStorage
import logging
from tqdm import tqdm
import utils.story_compiler as story_compiler


class AudioIntegrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Load environment variables
        load_dotenv()

        # Get environment variables
        self.elevenlabs_api_key = os.getenv("XI_API_KEY")

        # Initialize Eleven Labs and Firebase Storage clients
        self.xi_client = ElevenLabs(api_key=self.elevenlabs_api_key)
        self.firebase_storage = FirebaseStorage()

    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """
        Converts text to speech using Eleven Labs and returns the audio content as bytes.
        """
        response = self.xi_client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.8,
                style=0.0,
                use_speaker_boost=True,
            ),
        )

        audio_content = b"".join(response)
        return audio_content

    def upload_audio_to_storage(
        self,
        audio_content: bytes,
        language: str,
        story_title: str,
        story_id: int,
        character: str,  # character is the narrator if it is an exercise
        chapter: Optional[int] = None,
        block_id: Optional[int] = None,
        exercise_id: Optional[int] = None,
        line_id: Optional[int] = None,
    ) -> str:
        """
        Uploads the audio content to Firebase Storage and returns the URL.
        """
        extra_identifier = ""
        if exercise_id:
            extra_identifier = f"e{exercise_id}"

        if line_id:
            extra_identifier = f"l{line_id}"

        if chapter is None:
            destination_blob_name = (
                f"audio/{language}/{story_id}_{story_title.replace(" ", "_").lower()}/"
                f"description_c{character.capitalize()}.mp3"
            )
            destination_blob_name = self.firebase_storage.upload_blob_from_memory(
                audio_content, destination_blob_name
            )
            return destination_blob_name
        
        if block_id is None:
            destination_blob_name = (
                f"audio/{language}/{story_id}_{story_title.replace(" ", "_").lower()}/chapter_{chapter}/"
                f"summary_c{character.capitalize()}.mp3"
            )
            destination_blob_name = self.firebase_storage.upload_blob_from_memory(
                audio_content, destination_blob_name
            )
            return destination_blob_name

        destination_blob_name = (
            f"audio/{language}/{story_id}_{story_title.replace(" ", "_").lower()}/chapter_{chapter}/"
            f"b{block_id}_{extra_identifier}_c{character.capitalize()}.mp3"
        )
        destination_blob_name = self.firebase_storage.upload_blob_from_memory(
            audio_content, destination_blob_name
        )
        return destination_blob_name

    def integrate_audio_into_story(self, story: Story, character_voice_map: Dict[str, str]) -> Story:
        """
        Integrates audio files into the story by generating and uploading them,
        including for the story description and chapter summaries,
        then updates the story structure with the audio file locations.
        """
        def process_line_or_exercise(text, voice_id, language, title, story_id, chapter, character, block_id=None, line_id=None, exercise_id=None):
            if voice_id is None:
                self.logger.error(f"Voice ID not found for character: {character}, in block {block_id}")
                return None
            audio_content = self.text_to_speech(text, voice_id)
            return self.upload_audio_to_storage(
                audio_content, language, title, story_id, character, chapter=chapter, block_id=block_id, exercise_id=exercise_id, line_id=line_id, 
            )

        # Process Story Description Audio
        story.audio = process_line_or_exercise(
            story.description,
            character_voice_map.get("Narrator"),
            story.language,
            story.title,
            story.story_id,
            chapter=None,
            character="Narrator"
        )

        total_blocks = sum(len(chapter.blocks) for chapter in story.chapters)
        with tqdm(total=total_blocks, desc="Integrating Audio") as pbar:
            for chapter in story.chapters:
                try:
                    # Process Chapter Summary Audio
                    chapter.audio = process_line_or_exercise(
                        chapter.summary,
                        character_voice_map.get("Narrator"),
                        story.language,
                        story.title,
                        story.story_id,
                        chapter.chapter,
                        character="Narrator"
                    )

                    for block in chapter.blocks:
                        if isinstance(block, StoryBlock):
                            for line in block.lines:
                                if line.audio is None:
                                    line.audio = process_line_or_exercise(
                                        line.text,
                                        character_voice_map.get(line.character),
                                        story.language, story.title, story.story_id,
                                        chapter.chapter, line.character, block.block_id, line.line_id
                                    )
                        elif isinstance(block, ExerciseBlock):
                            for exercise in block.exercise_options:
                                if exercise.type in {"comp-mcq", "comp-tf", "speak-replace", "speak-question", "interact"} and exercise.audio is None:
                                    exercise.audio = process_line_or_exercise(
                                        exercise.query,
                                        character_voice_map.get("Narrator"),
                                        story.language, story.title, story.story_id,
                                        chapter.chapter, "Narrator", block.block_id, exercise_id=exercise.exercise_id
                                    )
                except Exception as e:
                    self.logger.error(f"Error processing chapter {chapter.chapter}: {str(e)}")
                finally:
                    pbar.update(1)
        return story



if __name__ == "__main__":

    # Specify the path to your JSON file
    json_file_path = "stories/se/beginner-fika.json"

    # Read JSON data from the file
    json_data = story_compiler.read_json_file(json_file_path)

    # Example usage
    story = story_compiler.compile_json_to_story(json_data)

    character_voice_map = {
        "Narrator": "IKne3meq5aSn9XLyUdCD",
        "Anna": "pFZP5JQG7iQjIQuC4Bku",
        "Karl": "bIHbv24MWmeRgasZH58o",
    }

    integrator = AudioIntegrator()
    updated_story = integrator.integrate_audio_into_story(story, character_voice_map)

    json_string = updated_story.model_dump_json()

    # Deserialize the JSON string back into a Python dictionary
    story_dict = json.loads(json_string)

    # Save the updated story to a file or database as needed
    with open("stories/se/beginner-fika.json", "w", encoding="utf-8") as f:
        json.dump(story_dict, f, indent=4, ensure_ascii=False)
