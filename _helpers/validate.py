import re

def is_integer(value):
    return value.isdigit()

def is_in_list(values_list, value):
    if value in values_list:
        return True
    return False

def is_hex_color(code):
    pattern = r'^#([0-9A-Fa-f]{6})$'
    return bool(re.match(pattern, code))
