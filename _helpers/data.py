import asyncio
import json
import re

from _helpers import aiofiles



class JSONHandler:
    def __init__(self, json_file=None, encoding="utf-8"):
        self.file_name = json_file
        self.encoding = encoding
        self.json_data = self._run_sync(self._read_json())

    async def _read_json(self) -> dict[str, any]:
        try:
            async with aiofiles.open(self.file_name, "r", encoding=self.encoding) as json_file:
                data = await json_file.read()
                return json.loads(data)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            raise e

    async def _write_json(self, data: dict[str, any]):
        try:
            async with aiofiles.open(self.file_name, "w", encoding=self.encoding) as json_file:
                await json_file.write(json.dumps(data, indent=4))
        except Exception as e:
            raise e

    def _run_sync(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        else:
            task = loop.create_task(coro)
            return loop.run_until_complete(task)

    def _resolve_keys(self, keys):
        if isinstance(keys, str):
            keys = keys.split('.')
        if not isinstance(keys, list):
            raise TypeError("Keys must be a string or a list.")
        return keys

    def get(self, keys, default=None):
        keys = self._resolve_keys(keys)
        data = self.json_data
        try:
            for key in keys:
                if not isinstance(data, dict):
                    return default
                data = data.get(key, default)
                if data is None:
                    return default
            return data
        except (KeyError, TypeError):
            return default

    def set(self, keys, value):
        """
        Update the in-memory JSON data of a specific key without writing to the file.
        
        Args:
            keys (str | list): Dot-separated string or list of keys representing the path.
            value (any): The value to set at the specified path.
        """
        keys = self._resolve_keys(keys)
        data = self.json_data
        try:
            for key in keys[:-1]:
                if key not in data or not isinstance(data[key], dict):
                    data[key] = {}
                data = data[key]
            data[keys[-1]] = value
        except (TypeError, KeyError) as e:
            raise ValueError(f"Invalid key path: {'.'.join(keys)}") from e

    def write(self):
        """
        Write the in-memory JSON data to the file.
        """
        self._run_sync(self._write_json(self.json_data))

    def revert(self):
        """
        Revert the in-memory data to the original state from the file on disk.
        """
        self.json_data = self._run_sync(self._read_json())
    
    def overwrite(self, new_data: dict):
        """
        Overwrite the entire JSON data with the new data.
        
        Args:
            new_data (dict): The new data to replace the existing JSON data.
        
        Raises:
            TypeError: If new_data is not a dictionary.
        """
        if not isinstance(new_data, dict):
            raise TypeError("New data must be a dictionary.")
        
        self.json_data = new_data


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class JSONValidator:
    def __init__(self, schema):
        self.schema = schema
        self.errors = []

    def _validate(self, value, schema, path="root"):
        if 'type' in schema:
            if schema['type'] == 'object':
                if not isinstance(value, dict):
                    self.errors.append(f"{path}: Expected object, got {type(value).__name__}")
                    return False
                
                # Check required fields
                required = schema.get('required', [])
                for key in required:
                    if key not in value:
                        self.errors.append(f"{path}: Missing required field '{key}'")
                
                # Check properties
                properties = schema.get('properties', {})
                for key, sub_schema in properties.items():
                    if key in value:
                        self._validate(value[key], sub_schema, path=f"{path}.{key}")

            elif schema['type'] == 'array':
                if not isinstance(value, list):
                    self.errors.append(f"{path}: Expected array, got {type(value).__name__}")
                    return False
                
                if 'minItems' in schema and len(value) < schema['minItems']:
                    self.errors.append(f"{path}: Array too short ({len(value)} items)")

                if 'maxItems' in schema and len(value) > schema['maxItems']:
                    self.errors.append(f"{path}: Array too long ({len(value)} items)")

                item_schema = schema.get('items')
                if item_schema:
                    for i, item in enumerate(value):
                        self._validate(item, item_schema, path=f"{path}[{i}]")

            elif schema['type'] == 'string':
                if not isinstance(value, str):
                    self.errors.append(f"{path}: Expected string, got {type(value).__name__}")
                
                if 'enum' in schema and value not in schema['enum']:
                    self.errors.append(f"{path}: Invalid enum value '{value}'")
                
                if 'pattern' in schema and not re.match(schema['pattern'], value):
                    self.errors.append(f"{path}: Invalid pattern for value '{value}'")

            elif schema['type'] == 'integer':
                if not isinstance(value, int):
                    self.errors.append(f"{path}: Expected integer, got {type(value).__name__}")

            elif schema['type'] == 'boolean':
                if not isinstance(value, bool):
                    self.errors.append(f"{path}: Expected boolean, got {type(value).__name__}")

            else:
                self.errors.append(f"{path}: Unsupported type '{schema['type']}'")

        return not bool(self.errors)
    
    def validate(self, data):
        self.errors = []  # Reset errors
        if not self._validate(data, self.schema):
            error_message = "\n".join(self.errors)
            raise ValidationError(f"Configuration Validation failed:\n{error_message}")
        return True
    

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

def rgb_to_hex(r, g, b):
    if not all(0 <= x <= 255 for x in (r, g, b)):
        raise ValueError("RGB values must be between 0 and 255")
    
    return f'#{r:02x}{g:02x}{b:02x}'
