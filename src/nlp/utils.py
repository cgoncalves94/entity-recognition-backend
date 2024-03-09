import os
import json
import aiofiles


async def load_json_file(file_path):
    # Detailed explanation of the function's purpose
    """
    Load a JSON file from the given file path.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The contents of the JSON file as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    # Check if the file exists at the given path
    if os.path.exists(file_path):
        async with aiofiles.open(file_path, mode="r") as file:
            # Load the JSON content from the file and return it as a dictionary
            return json.loads(await file.read())
    else:
        # Raise an error if the file does not exist
        raise FileNotFoundError(f"File not found: {file_path}")
