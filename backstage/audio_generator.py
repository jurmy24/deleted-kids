import os
from typing import Dict, Optional
import uuid
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from backstage.schema import ExerciseBlock, Story, StoryBlock
from firebase_storage import FirebaseStorage

# Load environment variables
load_dotenv()

# Get environment variables
ELEVENLABS_API_KEY = os.getenv("XI_API_KEY")

# Initialize Eleven Labs and Firebase Storage clients
xi_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
firebase_storage = FirebaseStorage()


# TODO: this should most likely be async later
def text_to_speech(text: str, voice_id: str) -> bytes:
    """
    Converts text to speech using Eleven Labs and returns the audio content as bytes.
    """
    response = xi_client.text_to_speech.convert(
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
    audio_content: bytes,
    language: str,
    story_title: str,
    story_id: int,
    chapter: int,
    character: str,  # character is the narrator if it is an exercise
    block_id: int,
    exercise_id: Optional[int],
    line_id: Optional[int],
) -> str:
    """
    Uploads the audio content to Firebase Storage and returns the URL.
    """
    extra_identifier = ""
    if exercise_id:
        extra_identifier = f"e{exercise_id}"

    if line_id:
        extra_identifier = f"l{line_id}"

    destination_blob_name = f"audio/{language}/{story_id}_{story_title}/chapter_{chapter}/b{block_id}_{extra_identifier}_c{character.capitalize()}.mp3"
    firebase_storage.upload_blob_from_memory(audio_content, destination_blob_name)
    return destination_blob_name


def integrate_audio_into_story(
    story: Story, character_voice_map: Dict[str, str]
) -> Story:
    """
    Integrates audio files into the story by generating and uploading them,
    then updates the story structure with the audio file locations.
    """

    # TODO: Implement logic to specify the types of exercises that should have audio generated
    for chapter in story.chapters:
        chapter.chapter
        for block in chapter.blocks:
            if isinstance(block, StoryBlock):
                for line in block.lines:
                    if line.audio is None:
                        audio_content = text_to_speech(
                            line.text, "IKne3meq5aSn9XLyUdCD", "Charlie"
                        )
                        line.audio = upload_audio_to_storage(audio_content, "Charlie")
            elif isinstance(block, ExerciseBlock):
                for exercise in block.exercise_options:
                    if exercise.type in {
                        "comp-listen",
                        "pronounce-rep",
                        "pronounce-deaf",
                        "speak-replace",
                    }:
                        if exercise.audio is None:
                            audio_content = text_to_speech(
                                exercise.query or exercise.affected_text,
                                "XB0fDUnXU5powFXDhCwa",
                                "Charlotte",
                            )
                            exercise.audio = upload_audio_to_storage(
                                audio_content, "Charlotte"
                            )
    return story


if __name__ == "__main__":
    # Example of loading a story and integrating audio
    story = Story(
        # Populate with your story data
    )

    updated_story = integrate_audio_into_story(story)

    # Save the updated story to a file or database as needed
    # For example:
    # with open("updated_story.json", "w") as f:
    #     json.dump(updated_story.dict(), f)
