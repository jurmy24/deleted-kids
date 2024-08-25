from pydantic import BaseModel, Field, model_validator
from typing import Any, Dict, List, Optional, Literal, Union


class AnswerOption(BaseModel):
    text: str
    is_correct: bool


class Exercise(BaseModel):
    exercise_id: int
    type: Literal[
        "comp-mcq",
        "comp-tf",
        "comp-listen",  # affects text
        "pronounce-rep",  # affects text
        "pronounce-deaf",  # affects text
        "speak-replace",  # affects text
        "speak-question",
        "interact",
    ]
    cefr: List[Literal["A1", "A2", "B1", "B2", "C1"]]
    skip_condition: Optional[Literal["if-not-voice", "if-not-audio"]] = None
    query: Optional[str] = None
    answer_options: Optional[Dict[str, AnswerOption]] = None
    hints: Optional[List[str]] = None
    audio: Optional[Any] = None
    action: Optional[
        Literal["hide-text", "hide-audio", "emphasize-text", "hide-all"]
    ] = Field(default=None)
    affected_line: Optional[str] = Field(
        default=None,
        description="Should follow the format 'StoryID-ChapterNumber-BlockID-LineID', e.g., '1-1-2-1'.",
    )

    # Main validator that checks all conditions
    @model_validator(mode="before")
    @classmethod
    def validate(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values = cls.check_action(values)
        values = cls.check_hints(values)
        return values

    @classmethod
    def check_action(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that the action matches the exercise type requirements.
        Raises ValueError if the action does not match the expected action for the exercise type.
        """
        action = values.get("action")
        exercise_type = values.get("type")

        # Mapping exercise types to required actions
        type_to_action = {
            "comp-listen": "hide-text",
            "pronounce-rep": "emphasize-text",
            "pronounce-deaf": "hide-audio",
            "speak-replace": "hide-all",
        }

        if exercise_type in type_to_action:
            expected_action = type_to_action[exercise_type]
            if action is not None and action != expected_action:
                raise ValueError(
                    f"Action for type '{exercise_type}' must be '{expected_action}', but '{action}' was provided."
                )
            # Set the action to the expected value if it's None
            values["action"] = expected_action

        return values

    @classmethod
    def check_hints(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that hints exist for specific exercise types.
        Raises ValueError if hints are required for the exercise type but are not provided.
        """
        exercise_type = values.get("type")
        hints = values.get("hints")

        # Check for hints requirement
        if exercise_type in {"speak-replace", "speak-question", "interact"}:
            if not hints:
                raise ValueError(
                    f"Hints are required for exercise type '{exercise_type}'"
                )

        return values

    # TODO: Add a method to validate the affected_line


# Define a base model for common attributes
class ExerciseBlock(BaseModel):
    block_id: int
    block_type: Literal["exercise"] = "exercise"
    exercise_options: List[Exercise]


class StoryLine(BaseModel):
    line_id: int
    character: str  # The character who is speaking (eg. narrator, character name)
    text: str
    audio: Optional[Any] = None


class StoryBlock(BaseModel):
    block_id: int
    block_type: Literal["story"] = "story"
    lines: List[StoryLine]


class Chapter(BaseModel):
    chapter: int
    title: str
    summary: str  # A brief summary of the chapter
    audio: Optional[Any] = None
    blocks: List[Union[StoryBlock, ExerciseBlock]]


class Story(BaseModel):
    title: str
    description: str
    audio: Optional[Any] = None
    language: Literal["en", "se", "fr"]
    story_id: int
    level: Literal["beginner", "intermediate", "advanced"]
    chapters: List[Chapter]
