import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from backstage.schema import ExerciseBlock, Story, StoryBlock
from backstage.firebase_storage import FirebaseStorage
import logging
from tqdm import tqdm
import story_compiler


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
        chapter: int,
        character: str,  # character is the narrator if it is an exercise
        block_id: int,
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

        destination_blob_name = (
            f"audio/{language}/{story_id}_{story_title.replace(" ", "_").lower()}/chapter_{chapter}/"
            f"b{block_id}_{extra_identifier}_c{character.capitalize()}.mp3"
        )
        self.firebase_storage.upload_blob_from_memory(
            audio_content, destination_blob_name
        )
        return destination_blob_name

    def integrate_audio_into_story(
        self, story: Story, character_voice_map: Dict[str, str]
    ) -> Story:
        """
        Integrates audio files into the story by generating and uploading them,
        then updates the story structure with the audio file locations.
        """

        # TODO: Add a check to see if the audio file identifier already exists in the storage

        total_blocks = sum(len(chapter.blocks) for chapter in story.chapters)
        with tqdm(total=total_blocks, desc="Integrating Audio") as pbar:
            for chapter in story.chapters:
                if chapter.chapter != 1:
                    continue
                for block in chapter.blocks:
                    if block.block_id != 1:
                        continue
                    try:
                        if isinstance(block, StoryBlock):
                            for line in block.lines:
                                if line.audio is None:
                                    voice_id = character_voice_map.get(line.character)

                                    if voice_id is None:
                                        self.logger.error(
                                            f"Voice ID not found for character: {line.character}, "
                                            f"in block {block.id} and line {line.id}"
                                        )
                                        continue  # skip and generate this line's audio later

                                    audio_content = self.text_to_speech(
                                        line.text, voice_id
                                    )
                                    line.audio = self.upload_audio_to_storage(
                                        audio_content,
                                        language=story.language,
                                        story_title=story.title,
                                        story_id=story.story_id,
                                        chapter=chapter.chapter,
                                        character=line.character,
                                        block_id=block.block_id,
                                        line_id=line.line_id,
                                    )
                        elif isinstance(block, ExerciseBlock):
                            for exercise in block.exercise_options:
                                if exercise.type in {
                                    "comp-mcq",
                                    "comp-tf",
                                    "speak-replace",
                                    "speak-question",
                                    "interact",
                                }:
                                    if exercise.audio is None:
                                        voice_id = character_voice_map.get("Narrator")

                                        if voice_id is None:
                                            self.logger.error(
                                                f"Voice ID not found for character: Narrator, "
                                                f"in exercise block {block.id}"
                                            )
                                            continue  # skip and generate this line's audio later

                                        audio_content = self.text_to_speech(
                                            exercise.query,
                                            voice_id,
                                        )
                                        exercise.audio = self.upload_audio_to_storage(
                                            audio_content,
                                            language=story.language,
                                            story_title=story.title,
                                            story_id=story.story_id,
                                            chapter=chapter.chapter,
                                            character="Narrator",
                                            block_id=block.block_id,
                                            exercise_id=exercise.exercise_id,
                                        )
                    except Exception as e:
                        self.logger.error(
                            f"Error processing block {block.id} in chapter {chapter.chapter}: {str(e)}"
                        )
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
