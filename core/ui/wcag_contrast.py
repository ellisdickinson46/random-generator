def rgb_to_linear(rgb):
    """Convert RGB color to linear RGB using the gamma correction formula."""
    r, g, b = rgb
    return [
        (channel / 255.0) ** 2.2 if channel > 0.03928 else channel / 255.0 / 12.92
        for channel in (r, g, b)
    ]

def luminance(rgb):
    """Calculate the luminance of a color (using linear RGB)."""
    r, g, b = rgb_to_linear(rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(luminance1, luminance2):
    """Calculate the contrast ratio between two luminances."""
    lum1 = luminance1 + 0.05
    lum2 = luminance2 + 0.05
    if lum1 > lum2:
        return lum1 / lum2
    return lum2 / lum1

def parse_color(hex_color):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return (r, g, b)


def determine_text_color(background_color, dark_color, light_color):
    """Determine whether the text should be 'light' or 'dark' based on the background color."""

    # Calculate luminance of the background color
    background_luminance = luminance(parse_color(background_color))

    # Define the luminance of white (255, 255, 255) and black (0, 0, 0)
    light_luminance = luminance(parse_color(light_color))
    dark_luminance = luminance(parse_color(dark_color))

    # Calculate contrast ratios for both black and white text
    contrast_with_white = contrast_ratio(background_luminance, light_luminance)
    contrast_with_black = contrast_ratio(background_luminance, dark_luminance)

    # WCAG recommends at least a 4.5:1 contrast ratio for normal text and 3:1 for large text
    if contrast_with_white >= 4.5:
        return light_color  # If white text has a good contrast ratio, return "dark" text
    if contrast_with_black >= 4.5:
        return dark_color  # If black text has a good contrast ratio, return "light" text

    # If none of the contrast ratios are enough, prefer dark text for readability
    return dark_color

