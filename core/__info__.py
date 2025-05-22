"""
Configuration Definitions for Random Generator
"""
# Project Metadata
PROJECT_TITLE = "Random Generator"
PROJECT_LINK = "https://github.com/ellisdickinson46/random-generator"
APP_ID = "com.bytefloater.random-generator.generator"

# Application Versions
APP_VERSIONS = {
    "generator": "4.0",
    "editor": "2.2"
}

# Directory Definitions
ASSETS_DIR = "assets"
CONFIG_DIR = "config"
LOGS_DIR = "logs"
LOCALE_DIR = f"{ASSETS_DIR}/locales"
SOUNDS_DIR = f"{ASSETS_DIR}/sounds"
ICONS_DIR = f"{ASSETS_DIR}/icons"

# JSON Schemas
GENERATOR_SCHEMA = {
    "type": "object",
    "properties": {
        "theme": {"type": "string", "enum": ["auto", "dark", "light"]},
        "language": {"type": "string"},
        "window_size": {
            "type": "array",
            "items": {"type": "integer"},
            "minItems": 2,
            "maxItems": 2
        },
        "sound_file": {"type": "string"},
        "font": {
            "type": "object",
            "properties": {
                "face": {"type": "string"},
                "size": {"type": "integer"}
            },
            "required": ["face", "size"]
        },
        "colours": {
            "type": "object",
            "properties": {
                "light_text": {"type": "string", "pattern": "^#([A-Fa-f0-9]{6})$"},
                "dark_text": {"type": "string", "pattern": "^#([A-Fa-f0-9]{6})$"},
                "random_colours": {
                    "type": "array",
                    "items": {"type": "string", "pattern": "^#([A-Fa-f0-9]{6})$"},
                    "minItems": 1
                }
            },
            "required": ["light_text", "dark_text", "random_colours"]
        },
        "feature_flags": {
            "type": "object",
            "properties": {
                "enable_always_on_top": {"type": "boolean"},
                "enable_log_to_file": {"type": "boolean"},
                "enable_sound": {"type": "boolean"}
            },
            "required": ["enable_always_on_top", "enable_log_to_file", "enable_sound"]
        }
    },
    "required": [
        "theme", "language", "window_size", "sound_file", 
        "font", "colours", "feature_flags"
    ]
}

EDITOR_SCHEMA = {
    "type": "object",
    "properties": {
        "theme": {"type": "string", "enum": ["auto", "dark", "light"]},
        "window_size": {
            "type": "array",
            "items": {"type": "integer"},
            "minItems": 2,
            "maxItems": 2
        }
    },
    "required": ["theme", "window_size"]
}

MAIN_SCHEMA = {
    "type": "object",
    "properties": {
        "generator_config": GENERATOR_SCHEMA,
        "editor_config": EDITOR_SCHEMA
    },
    "required": ["generator_config", "editor_config"]
}

# Language Names Map
LANGUAGE_MAP = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'pa': 'Punjabi',
    'te': 'Telugu',
    'vi': 'Vietnamese',
    'ur': 'Urdu',
    'fa': 'Persian',
    'tr': 'Turkish',
    'ta': 'Tamil',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'or': 'Odia',
    'as': 'Assamese',
    'th': 'Thai',
    'my': 'Burmese',
    'km': 'Khmer',
    'id': 'Indonesian',
    'ms': 'Malay',
    'tl': 'Tagalog',
    'sw': 'Swahili',
    'nl': 'Dutch',
    'pl': 'Polish',
    'uk': 'Ukrainian',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'fi': 'Finnish',
    'sv': 'Swedish',
    'da': 'Danish',
    'no': 'Norwegian',
    'is': 'Icelandic',
    'el': 'Greek',
    'he': 'Hebrew',
    'am': 'Amharic',
    'so': 'Somali',
    'yo': 'Yoruba',
    'ig': 'Igbo',
    'zu': 'Zulu',
    'xh': 'Xhosa',
    'af': 'Afrikaans',
    'sq': 'Albanian',
    'bg': 'Bulgarian',
    'hr': 'Croatian',
    'sr': 'Serbian',
    'mk': 'Macedonian',
    'sl': 'Slovenian',
    'et': 'Estonian',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'mt': 'Maltese',
    'ga': 'Irish',
    'cy': 'Welsh',
    'eu': 'Basque',
    'ca': 'Catalan',
    'gl': 'Galician',
    'az': 'Azerbaijani',
    'hy': 'Armenian',
    'ka': 'Georgian',
    'mn': 'Mongolian',
    'ne': 'Nepali',
    'si': 'Sinhala',
    'lo': 'Lao',
    'bo': 'Tibetan',
    'ug': 'Uyghur',
    'ky': 'Kyrgyz',
    'uz': 'Uzbek',
    'tk': 'Turkmen',
    'ps': 'Pashto',
    'sd': 'Sindhi',
    'dz': 'Dzongkha',
    'ti': 'Tigrinya',
    'rw': 'Kinyarwanda',
    'lg': 'Ganda',
    'ny': 'Chichewa',
    'sn': 'Shona',
    'st': 'Sesotho',
    'ss': 'Swati',
    'tn': 'Tswana',
    've': 'Venda',
    'ts': 'Tsonga',
    'bm': 'Bambara',
    'ff': 'Fulah',
    'ha': 'Hausa',
}