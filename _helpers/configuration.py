from _helpers import darkdetect
from _helpers.data import JSONHandler, get_nested


class GeneratorAppSettings:
    def __init__(self, json_file_name):
        self._raw_data = JSONHandler(json_file_name).json_data.get("generator_config", None)

        if self._raw_data:
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
                "language": (["language"], "")
            }

            # Static values that don't need a path or fallback
            static_values = {
                "app_on_top": True,
                "app_theme": self._get_app_theme()
            }

            # Use the variable map to set attributes
            for var_name, (path, fallback) in var_map.items():
                # Fetch the value using get_nested and fall back if not found
                value = get_nested(self._raw_data, path, default=fallback)
                setattr(self, var_name, value)

            # Set static values directly
            for var_name, value in static_values.items():
                setattr(self, var_name, value)


    def _get_app_theme(self) -> str:
        match self._raw_data.get("theme"):
            case "dark": return "dark"
            case "light": return "light"
            case "auto": return darkdetect.theme()
            case _: raise KeyError


class EditorAppSettings:
    def __init__(self, json_file_name):
        self._raw_data = JSONHandler(json_file_name).json_data.get("editor_config")

        self.app_title = "Configuration Utility"
        self.app_theme = self._get_app_theme()
        self.app_size = tuple(self._raw_data.get("window_size", (1024, 768)))

    def _get_app_theme(self) -> str:
        match self._raw_data.get("theme"):
            case "dark": return "dark"
            case "light": return "light"
            case "auto": return darkdetect.theme()
            case _: raise KeyError