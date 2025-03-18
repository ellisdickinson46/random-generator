PROJECT_TITLE = "Random Generator"
PROJECT_LINK = "https://github.com/ellisdickinson46/random-generator" # Placeholder
APP_VERSIONS = {
    "generator": "4.0",
    "editor": "2.1"
}
LOCALE_DIR = "_locales"
CONFIG_DIR = "_configuration"
APP_ID = "com.bytefloater.random-generator.generator"
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
                    "items": {"type": "string", "pattern": "^#([A-Fa-f0-9]{6})$"}
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