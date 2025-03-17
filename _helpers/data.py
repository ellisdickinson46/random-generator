import asyncio
import json
import re

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

def get_nested(dictionary, keys, default: any):
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

def custom_json_dump(data, **kwargs):
    indent = kwargs.get('indent', None)
    result = []
    outer_indent = ' ' * indent if indent is not None else ''
    inner_indent = ' ' * (indent * 2) if indent is not None else ''

    for key, value in data.items():
        # Add key with item count
        result.append(f'{outer_indent}{json.dumps(key, **kwargs)} ({len(value)} items): [')
        for item in value:
            result.append(f'{inner_indent}{json.dumps(item, **kwargs)},')
        # Remove trailing comma and close the list
        if value:
            result[-1] = result[-1][:-1]
        result.append(f'{outer_indent}],')

    # Remove trailing comma
    if result:
        result[-1] = result[-1][:-1]

    # Handle indentation and format properly
    newline = '\n' if indent is not None else ''
    return f'{{{newline}' + f'{newline}'.join(result) + f'{newline}}}'


def hex_to_rgb(hex_color):
    # Regular expression to match valid hex color formats
    pattern = r'^(#|0x)?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$'
    
    match = re.match(pattern, hex_color)
    if not match:
        return None
    
    hex_value = match.group(2)
    
    if len(hex_value) == 3:
        # Expand shorthand hex to full form, e.g., "f00" -> "ff0000"
        hex_value = ''.join(c * 2 for c in hex_value)
    
    try:
        r = int(hex_value[0:2], 16)
        g = int(hex_value[2:4], 16)
        b = int(hex_value[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None
