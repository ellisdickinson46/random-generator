import ctypes
import gettext
import json
import os
import platform
import tkinter as tk
from tkinter import ttk, font
import webbrowser

from _helpers.apply_theme import ThemeHelper
from _helpers.custom_tk import Limiter, ReadOnlyTextWithVar, OptionMenuWrapper, ScrollableTreeview
from _helpers.configuration import EditorAppSettings
from _helpers.data import JSONHandler
import __info__


lorem = JSONHandler("_configuration/app_config.json").json_data
lorem = json.dumps(lorem, indent=4, separators=(',', ': '))


class ConfigurationUtility(tk.Tk):
    def __init__(self, config: EditorAppSettings):
        tk.Tk.__init__(self)

        self.app_icon = tk.PhotoImage(file=f"{__info__.CONFIG_DIR}/icons/appicon_config.png").subsample(3,3)

        # Window Properties
        self.geometry('x'.join(str(x) for x in config.app_size))
        self.title(config.app_title)
        self.resizable(0, 0)
        self.attributes('-topmost', True)
        self.after_idle(self.attributes,'-topmost', False)
        self.iconphoto(True, self.app_icon)
        self.protocol('WM_DELETE_WINDOW', self._on_closing)

        # Window Bindings
        self.bind('<<NotebookTabChanged>>', lambda event: self.update_idletasks())
        self.bind("<<ComboboxSelected>>",lambda e: self.focus())

        # Interface Variables
        self._language = tk.StringVar()
        self._enable_always_on_top = tk.BooleanVar()
        self._enable_log_to_file = tk.BooleanVar()
        self._enable_sound = tk.BooleanVar()
        self._sound_file = tk.StringVar()
        self._font_face = tk.StringVar()
        self._font_size = tk.StringVar()
        self._slidervals = {
            "r": tk.IntVar(),
            "g": tk.IntVar(),
            "b": tk.IntVar()
        }
        self._config_preview = tk.StringVar()

        # Add callback functions to change the colour displayed in the preview frame
        # when any colour value is chnaged.
        for color in ("r", "g", "b"):
            self._slidervals[color].trace_add('write', callback=lambda *args: self.update_colpreview())

        if platform.system() == "Windows":
            app_id = getattr(__info__, "APP_ID", "fallback")
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        # Apply the Sun Valley theme, and title bar colour (Windows Only)
        self.theme_helper = ThemeHelper(self, config.app_theme)
        self.theme_helper.apply_theme()

        self._define_interface()
        self.mainloop()

    def get_available_sounds(self) -> list:
        sound_dir = f"{__info__.CONFIG_DIR}/sounds"
        supported_formats = (".mp3", '.wav')
        available_sounds = []
        for file in os.listdir(sound_dir):
            if file.endswith(supported_formats):
                available_sounds.append(file)
        return sorted(available_sounds)
    
    def get_supported_sounds(self) -> list:
        available_locales = []
        
        # Traverse the directory and list all directories containing .mo files
        for root, dirs, files in os.walk(f"{__info__.LOCALE_DIR}"):
            if root.endswith('LC_MESSAGES'):
                for file in files:
                    if file.endswith('.mo'):
                        # Extract the locale from the directory structure
                        locale = os.path.basename(os.path.dirname(root))
                        if locale not in available_locales:
                            available_locales.append(locale)
        return sorted(available_locales)



    def _change_intvar_by_amount(self, var: tk.IntVar, amount) -> None:
        if not isinstance(var, tk.IntVar):
            raise TypeError("Variable must be of type: tk.IntVar")
        new_val = int(var.get() + amount)
        if 0 <= new_val <= 255:
            var.set(new_val)

    def update_colpreview(self) -> None:
        red_value = self._slidervals["r"].get()
        green_value = self._slidervals["g"].get()
        blue_value = self._slidervals["b"].get()

        new_col = f"#{red_value:02x}{green_value:02x}{blue_value:02x}"
        self._colpreview.configure(background=new_col)

    def _validate_input_integers(self, new_val):
        if new_val == "" or new_val.isdigit():
            return True
        return False


    def _define_interface(self):
        self._tab_control = ttk.Notebook(self, takefocus=0)
        self._tab_control.pack(expand=True, fill="both")

        tabs = [
            ("_preference_tab", "Generator Preferences"),
            ("_editor_tab", "List Editor"),
            ("_save_tab", "Save"),
            ("_about_tab", "About"),
        ]
        for _, (tab_attr_name, tab_text) in enumerate(tabs):
            setattr(self, tab_attr_name, ttk.Frame(self._tab_control))
            self._tab_control.add(
                getattr(self, tab_attr_name), text=tab_text
            )

        self._preference_tab_ui()
        self._editor_tab_ui()
        self._save_tab_ui()
        self._about_tab_ui()


    def _about_tab_ui(self):
        project_title = getattr(__info__, "PROJECT_TITLE", "PROJECT_TITLE")
        project_link = getattr(__info__, "PROJECT_LINK", "")
        app_versions = getattr(__info__, "APP_VERSIONS", {})
        
        self._about_tab_frm = ttk.Frame(self._about_tab)
        self._about_tab_frm.place(anchor="c", relx=.5, rely=.4)

        labels = [
            ("_app_icon_lbl", "", {"image": self.app_icon}),
            ("_about_name", project_title, {"font": ("TkDefaultFont", 25, "bold")}),
            ("_about_appver", f"Generator Version: {app_versions.get('generator', 'GENERATOR_VERSION')}", {}),
            ("_about_confver", f"Editor Version: {app_versions.get('editor', 'EDITOR_VERSION')}", {})
        ]
        for _, (lbl_attr_name, text, options) in enumerate(labels):
            setattr(self, lbl_attr_name, ttk.Label(
                self._about_tab_frm, text=text, **options
            ))
            getattr(self, lbl_attr_name).pack(pady=2)

        self._github_btn = ttk.Button(self._about_tab_frm, text="View the project on GitHub", takefocus=0, command=lambda: webbrowser.open(project_link))
        self._github_btn.pack(pady=(20, 0))


    def _editor_tab_ui(self):
        self._editor_controls_frm = ttk.Frame(self._editor_tab)
        self._editor_controls_frm.grid(row=0, column=0, padx=10, pady=10)

        editor_controls = [
            ("_creatlist_btn", "Create New List", ""),
            ("_editlist_btn", "Edit Selected List", ""),
            ("_removelist_btn", "Remove Select List", "")
        ]
        for i, (btn_attr_name, btn_text, btn_command) in enumerate(editor_controls):
            setattr(self, btn_attr_name, ttk.Button(
                self._editor_controls_frm, text=btn_text, command=btn_command
            ))
            getattr(self, btn_attr_name).grid(row=0, column=i, padx=5)


    def _save_tab_ui(self):
        self._save_controls_frm = ttk.Frame(self._save_tab)
        self._save_controls_frm.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self._save_config_btn = ttk.Button(self._save_controls_frm, text="Save configuration...", style="Accent.TButton", takefocus=0, state="disabled")
        self._save_lbl = ttk.Label(self._save_controls_frm, text="Check your configuration options before saving!")
        
        self._config_preview_frm = ttk.LabelFrame(self._save_tab, text=" Configuration Preview ")
        self._config_preview_scrl = ttk.Scrollbar(self._config_preview_frm)
        self._config_preview_lbl = ReadOnlyTextWithVar(self._config_preview_frm, takefocus=0, highlightthickness=0, border=0, textvariable=self._config_preview, yscrollcommand=self._config_preview_scrl.set, foreground="gray64")
        self._config_preview_scrl.configure(command=self._config_preview_lbl.yview)

        self._save_config_btn.grid(row=0, column=0, padx=5)
        self._save_lbl.grid(row=0, column=1, padx=(10,0))
        self._config_preview_frm.grid(row=1, column=0, sticky="NESW", padx=5, pady=(0, 5))
        self._config_preview_lbl.grid(row=0, column=0, sticky="NESW", padx=(10, 0), pady=10)
        self._config_preview_scrl.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 10))
        self._config_preview_frm.grid_rowconfigure(0, weight=1)
        self._config_preview_frm.grid_columnconfigure(0, weight=1)
        self._save_tab.grid_columnconfigure(0, weight=1)
        self._save_tab.grid_rowconfigure(1, weight=1)

        self._config_preview.set(lorem)

    def _preference_tab_ui(self):
        fontsize_defaults = (12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48)
        fontfaces_available = font.families()
        supported_languages = self.get_supported_sounds()
        sound_files_available = self.get_available_sounds()

        # Define interface section containers
        containers = [
            ("preferences", "Preferences", 2, {"row": 0, "column": 0, "rowspan": 2, "sticky": "nesw", "padx": 5, "pady": 5, "ipadx": 50, "ipady": 50}),
            ("color_select", "Colour Selection", 1, {"row": 0, "column": 1, "sticky": "nesw", "padx": 5, "pady": (5, 2), "ipadx": 20, "ipady": 20}),
            ("font_preview", "Font Preview", 1, {"row": 1, "column": 1, "sticky": "nesw", "padx": 5, "pady": (2, 5), "ipadx": 20, "ipady": 20})
        ]
        for _, (container_name, text, num_of_columns, grid_options) in enumerate(containers):
            setattr(self, f"_{container_name}_container", ttk.LabelFrame(
                self._preference_tab, text=f" {text} "
            ))
            getattr(self, f"_{container_name}_container").grid(**grid_options)
            for x in range(num_of_columns):
                getattr(self, f"_{container_name}_container").grid_columnconfigure(x, weight=1, uniform="column")

        self._color_select_container.grid_rowconfigure(0, weight=1)


        settings = [
            ("language", "Interface Language", OptionMenuWrapper, {"variable": self._language, "default_index": 0, "values": supported_languages}),
            ("ontop", "Always on top", ttk.Checkbutton, {"variable": self._enable_always_on_top}),
            ("log_to_file", "Log to file", ttk.Checkbutton, {"variable": self._enable_log_to_file}),
            ("enable_sound", "Enable Sound", ttk.Checkbutton, {"variable": self._enable_sound}),
            ("sound_file", "Sound File", OptionMenuWrapper, {"variable": self._sound_file, "default_index": 0, "values": sound_files_available}),
            ("font_face", "Font Face", ttk.Combobox, {"textvariable": self._font_face, "values": fontfaces_available}),
            ("font_size", "Font Size", ttk.Combobox, {"textvariable": self._font_size, "values": fontsize_defaults}),
            ("random_colors", "Random Colours", ScrollableTreeview, {"height": 6}),
            ("ranodm_color_btns", "", tk.Frame, {})
        ]
        for i, (setting_name, description, control_type, control_options) in enumerate(settings):
            setattr(self, f"_{setting_name}_lbl", ttk.Label(
                self._preferences_container, text=description, anchor="e"
            ))
            setattr(self, f"_{setting_name}_ctrl", control_type(
                self._preferences_container, **control_options
            ))
            getattr(self, f"_{setting_name}_lbl").grid(row=i, column=0, sticky="ew")
            getattr(self, f"_{setting_name}_ctrl").grid(row=i, column=1, sticky="ew", padx=10, pady=2)
            self._preferences_container.grid_rowconfigure(i, minsize=35)

        # self._font_size_dropdown = ttk.Combobox(self._preference_container, textvariable=self._fontsize, values=fontsize_defaults, takefocus=0, validate="focusout", validatecommand=lambda: self._validate_input_integers(self._fontsize.get()))
        self._add_col_btn = ttk.Button(self._ranodm_color_btns_ctrl, text="Add")
        self._rem_col_btn = ttk.Button(self._ranodm_color_btns_ctrl, text="Remove")
        self._add_col_btn.grid(row=1, column=0, padx=(0, 2), sticky="ew")
        self._rem_col_btn.grid(row=1, column=1, padx=(2, 0), sticky="ew")

        self._ranodm_color_btns_ctrl.grid_columnconfigure(0, weight=1, uniform="_ranodm_color_btns_ctrl")
        self._ranodm_color_btns_ctrl.grid_columnconfigure(1, weight=1, uniform="_ranodm_color_btns_ctrl")





        # Define mixer controls and color preview frame
        self._colpreview = tk.Frame(self._color_select_container, background="black", width=40, highlightbackground="black", highlightthickness=1)
        self._colselect_frm = ttk.Frame(self._color_select_container)
        self._colselect_frm.grid(row=1, column=0, sticky="nesw", padx=10, pady=5)
        self._colpreview.grid(row=0, column=0, sticky="nesw", padx=10, pady=(5 ,0))
        
        for i, color in enumerate(["r", "g", "b"]):
            setattr(self, f"_label_{color}", ttk.Label(
                self._colselect_frm, text=color.upper())
            )
            getattr(self, f"_label_{color}").grid(row=i, column=1, sticky="ew", padx=10)
            setattr(self, f"_slider_{color}", Limiter(
                self._colselect_frm, variable=self._slidervals[color], to=255, precision=0)
            )
            getattr(self, f"_slider_{color}").grid(row=i, column=2, sticky="ew", padx=5)
            setattr(self, f"_minus_{color}", ttk.Button(
                self._colselect_frm, text="-", takefocus=0,
                command=lambda color=color: self._change_intvar_by_amount(self._slidervals[color], -1))
            )
            getattr(self, f"_minus_{color}").grid(row=i, column=3, sticky="ew")
            setattr(self, f"_sliderval_lbl_{color}", ttk.Label(
                self._colselect_frm, textvariable=self._slidervals[color], anchor="center")
            )
            getattr(self, f"_sliderval_lbl_{color}").grid(row=i, column=4, sticky="ew", padx=5)
            setattr(self, f"_plus_{color}", ttk.Button(
                self._colselect_frm, text="+", takefocus=0,
                command=lambda color=color: self._change_intvar_by_amount(self._slidervals[color], 1))
            )
            getattr(self, f"_plus_{color}").grid(row=i, column=5, sticky="ew")
            self._colselect_frm.grid_rowconfigure(i, minsize=35)
        
        self._colselect_frm.grid_columnconfigure(4, minsize=40)
        self._colselect_frm.grid_columnconfigure(2, weight=1)
        self._colselect_frm.grid_rowconfigure(0, weight=1)

        # Tab Grid Settings
        self._preference_tab.grid_columnconfigure(0, weight=1, uniform="column")
        self._preference_tab.grid_columnconfigure(1, weight=1, uniform="column")
        self._preference_tab.grid_rowconfigure(0, weight=1, uniform="row")
        self._preference_tab.grid_rowconfigure(1, weight=1, uniform="row")


    def _on_closing(self):
        self.theme_helper.stop_listener()
        self.destroy()



if __name__ == "__main__":
    APP_CONFIG = EditorAppSettings(f"{__info__.CONFIG_DIR}/app_config.json")
    instance = ConfigurationUtility(APP_CONFIG)
