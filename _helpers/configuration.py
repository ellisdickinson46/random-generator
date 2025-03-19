from _helpers.data import JSONHandler, JSONValidator

class GeneratorAppSettings:
    def __init__(self, json_file_name, schema):
        self.json_data = JSONHandler(json_file_name)
        self.validator = JSONValidator(schema)
        self.validator.validate(self.json_data.get("generator_config"))

        # Define the variable map with keys and their corresponding paths and optional fallbacks
        var_map = {
            "app_size": (["window_size"], (1024, 768)),
            "app_fontface": (["font", "face"], "TkDefaultFont"),
            "app_fontsize": (["font", "size"], 30),
            "random_cols": (["colours", "random_colours"], False),
            "app_light_text_col": (["colours", "light_text"], "#FAFAFA"),
            "app_dark_text_col": (["colours", "dark_text"], "#1C1C1C"),
            "enable_log_to_file": (["feature_flags", "enable_log_to_file"], True),
            "sound_fname": (["sound_file"], ""),
            "language": (["language"], ""),
            "app_theme": (["theme"], "auto")
        }

        # Static values that don't need a path or fallback
        static_values = {
            "app_on_top": True
        }

        if self.json_data:
            # Use the variable map to set attributes
            for var_name, (path, fallback) in var_map.items():
                path = ["generator_config"] + path
                value = self.json_data.get(path, default=fallback)
                setattr(self, var_name, value)

            # Set static values directly
            for var_name, value in static_values.items():
                setattr(self, var_name, value)


class EditorAppSettings:
    def __init__(self, json_file_name, schema):
        self.json_data = JSONHandler(json_file_name)
        self.validator = JSONValidator(schema)
        self.validator.validate(self.json_data.get("editor_config"))

        # Define the variable map with keys and their corresponding paths and optional fallbacks
        var_map = {
            "app_theme": (["theme"], "auto"),
            "app_size": (["window_size"], (1024, 768)),
        }

        # Static values that don't need a path or fallback
        static_values = {
            "app_title": "Configuration Utility"
        }

        if self.json_data:
            # Use the variable map to set attributes
            for var_name, (path, fallback) in var_map.items():
                path = ["editor_config"] + path
                value = self.json_data.get(path, default=fallback)
                setattr(self, var_name, value)

            # Set static values directly
            for var_name, value in static_values.items():
                setattr(self, var_name, value)
