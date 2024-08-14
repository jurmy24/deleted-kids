from pydantic import BaseModel, Field, model_validator
from typing import Any, Dict, List, Optional, Literal, Union


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
    answer_options: Optional[List[str]] = (
        None  # TODO: This should be a dict with key as the identifier and value as the text
    )
    correct_answer: Optional[str] = (
        None  # TODO: This should be the identifier of the correct answer (eg. an int)
    )
    hints: Optional[List[str]] = None
    audio: Optional[Any] = None
    action: Optional[
        Literal["hide-text", "hide-audio", "emphasize-text", "hide-all"]
    ] = Field(default=None)
    affected_text: Optional[str] = Field(default=None)

    # Main validator that checks all conditions
    @model_validator(mode="before")
    @classmethod
    def validate(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values = cls.check_action(values)
        values = cls.check_hints(values)
        values = cls.check_affected_text(values)
        values = cls.check_correct_answer(values)
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

    @classmethod
    def check_affected_text(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that affected_text is provided when action is not None.
        Raises ValueError if affected_text is required but not provided.
        """
        action = values.get("action")
        affected_text = values.get("affected_text")

        # Check for affected_text requirement
        if action is not None and not affected_text:
            raise ValueError("affected_text is required when action is not None")

        return values

    @classmethod
    def check_correct_answer(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that correct_answer is provided for certain exercise types.
        Raises ValueError if correct_answer is required but not provided.
        """
        exercise_type = values.get("type")
        correct_answer = values.get("correct_answer")

        # Check for correct_answer requirement
        if exercise_type in {"comp-mcq", "comp-tf", "comp-listen"}:
            if correct_answer is None:
                raise ValueError(
                    f"correct_answer is required for exercise type '{exercise_type}'"
                )

        return values


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
    blocks: List[Union[StoryBlock, ExerciseBlock]]


class Story(BaseModel):
    title: str
    description: str
    level: Literal["beginner", "intermediate", "advanced"]
    chapters: List[Chapter]
