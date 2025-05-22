import re

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