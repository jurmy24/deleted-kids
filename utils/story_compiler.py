import json
from typing import Any, Dict
from pydantic import ValidationError
from utils.story_schema import Story


def compile_json_to_story(json_data: Dict[str, Any]) -> Story:
    """
    Compiles JSON data into a Pydantic Story object.

    Args:
        json_data (Dict[str, Any]): The JSON data to be compiled.

    Returns:
        Story: The compiled Pydantic Story object.
    """
    try:
        # Create a Story object from the JSON data
        story = Story(**json_data)
        return story

    except ValidationError as e:
        print("Error in validating JSON data:")
        print(e)
        raise


def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Reads a JSON file and returns its content as a dictionary.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        Dict[str, Any]: The JSON content as a dictionary.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    # Specify the path to your JSON file
    json_file_path = "stories/se/beginner-fika.json"

    # Read JSON data from the file
    json_data = read_json_file(json_file_path)

    # Compile the JSON data into a Pydantic Story object
    try:
        story_object = compile_json_to_story(json_data)
        print("Story compiled successfully!")

        # Accessing the Story object
        print("Title:", story_object.title)
        print("Description:", story_object.description)
        print("Level:", story_object.level)
        print("Number of Chapters:", len(story_object.chapters))
        print("Chapter Titles:", [chapter.title for chapter in story_object.chapters])

    except ValidationError as e:
        print("Failed to compile the story. Check the JSON data for errors.")
