import asyncio
import json

from typing import Any
from _helpers import aiofiles


class JSONHandler:
    def __init__(self, json_file=None, encoding="utf-8"):
        self.file_name = json_file
        self.encoding = encoding
        self.json_data = asyncio.run(self._read_json())

    async def _read_json(self) -> dict[str, any]:
        try:
            async with aiofiles.open(self.file_name, "r", encoding=self.encoding) as json_file:
                data = await json_file.read()
                return json.loads(data)
        except FileNotFoundError as e:
            raise e
        except json.JSONDecodeError as e:
            raise e

def get_nested(dictionary, keys, default: Any | None=None):
    """
    A wrapper for Python's `get` function that supports nested dictionaries.
    
    Args:
        dictionary (dict): The dictionary to search.
        keys (list): A list of keys to traverse through the nested dictionary.
        default: The default value to return if any key is not found.
        
    Returns:
        The value associated with the keys, or the default value if any key is missing.
    """
    # Traverse through each key in the keys list
    for key in keys:
        # Check if the current dictionary is a valid dictionary
        if isinstance(dictionary, dict):
            # If the key is not found, return default value
            dictionary = dictionary.get(key, default)
        else:
            # If the dictionary structure is not valid or key not found
            return default
    return dictionary
