import re

def is_integer(value) -> bool:
    return value.isdigit()

def is_in_list(values_list, value) -> bool:
    if value in values_list:
        return True
    return False

def is_hex_color(code) -> bool:
    pattern = r'^#([0-9A-Fa-f]{6})$'
    return bool(re.match(pattern, code))

def is_valid_font_size(value) -> bool:
    if not is_integer(value):
        return False
    return int(value) <= 500
