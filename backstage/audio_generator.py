import os
import uuid
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from backstage.schema import ExerciseBlock, Story, StoryBlock

# Load environment variables from .env file
load_dotenv()

# Initialize the Eleven Labs client with the API key from the environment
ELEVENLABS_API_KEY = os.getenv("XI_API_KEY")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


def text_to_speech_file(text: str, voice_id: str, name: str) -> str:
    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
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

    # Generate a unique file name for the output MP3 file
    save_file_path = f"voices/output-{name}-{uuid.uuid4()}.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    # Return the path of the saved audio file
    return save_file_path


def integrate_audio_into_story(story: Story) -> Story:
    for chapter in story.chapters:
        for block in chapter.blocks:
            if isinstance(block, StoryBlock):
                for line in block.lines:
                    if line.audio is None:
                        line.audio = text_to_speech_file(
                            line.text, "IKne3meq5aSn9XLyUdCD", "Charlie"
                        )
            elif isinstance(block, ExerciseBlock):
                for exercise in block.exercise_options:
                    if exercise.type in {
                        "comp-listen",
                        "pronounce-rep",
                        "pronounce-deaf",
                        "speak-replace",
                    }:
                        if exercise.audio is None:
                            exercise.audio = text_to_speech_file(
                                exercise.query or exercise.affected_text,
                                "XB0fDUnXU5powFXDhCwa",
                                "Charlotte",
                            )
    return story


if __name__ == "__main__":
    # Example usage of get_audio_for_text
    audio_file = text_to_speech_file(
        "Skärgården är vacker på sommaren.",
        "IKne3meq5aSn9XLyUdCD",
        name="Charlie",
    )
    print(f"Audio saved to {audio_file}")


# Sarah: Great, maybe Anna - EXAVITQu4vr4xnSDxMaL
# Laura: bad - FGY2WhTYpPnrIDTdsKH5
# Charlie: Great (narrator voice) - IKne3meq5aSn9XLyUdCD
# George: Great (maybe Karl) - JBFqnCBsd6RMkjVDRZzb
# Callum: Great (maybe narrator) - N2lVS1w4EtoT3dr4eOWO
# Liam: Quite good (better as Karl) - TX3LPaxmHKxFdv7VOQHJ
# Charlotte: Quite good (better as narrator) - XB0fDUnXU5powFXDhCwa
# Alice: Bad - Xb7hH8MSUJpSbSDYk0k2
# Matilda: Not great - XrExE9yKIg1WjnnlVkGX
# Will: Great (Karl) - bIHbv24MWmeRgasZH58o
# Jessica: Not great - cgSgspJ2msm6clMCkdW9
# Chris: Good (maybe Karl) - iP95p4xoKVk53GoZ742B
# Brian: Quite good (narrator) - nPczCjzI2devNBz1zQrb
# Daniel; Awesome (narrator) -  onwK4e9ZLuTAKqWW03F9
# Lily: Great (anna) - pFZP5JQG7iQjIQuC4Bku
# Bill: Great (maybe narrator) - pqHfZKP75CvOlQylNhV4
