import ctypes
import json
import os
import platform
import signal
import traceback
import tkinter as tk
from tkinter import ttk, font
import webbrowser

from _helpers.apply_theme import ThemeHelper
from _helpers.custom_tk import Limiter, ReadOnlyTextWithVar, OptionMenuWrapper, ScrollableListbox, ListVar, DictVar
from _helpers.configuration import EditorAppSettings
from _helpers.data import JSONHandler, custom_json_dump, hex_to_rgb, rgb_to_hex
from _helpers.logger import init_logger
from _helpers import validate
import __info__


class ConfigurationUtility(tk.Tk):
    def __init__(self, config: EditorAppSettings):
        tk.Tk.__init__(self)
        self.config = config

        self.logger = init_logger("editor", "DEBUG", True)
        self.logger.info("Launching Editor...")

        style_customisations = [('Treeview', {"rowheight": 25})]
        self.loaded_config = JSONHandler(f"{__info__.CONFIG_DIR}/app_config.json")
        self.list_data = JSONHandler(f"{__info__.CONFIG_DIR}/lists.json")

        self._set_window_properties()

        # Window Bindings
        self.bind('<<NotebookTabChanged>>', lambda _: self.update_idletasks())
        self.bind("<<ComboboxSelected>>", self.post_select_focus)
        self.bind("<Button-1>", self.clear_focus)

        self.fontsize_defaults = (12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48)
        self.fontfaces_available = font.families()
        self.supported_languages = self.get_supported_languages()
        self.sound_files_available = self.get_available_sounds()
        self.supported_themes = {"Light": "light", "Dark": "dark", "Follow System": "auto"}

        # Interface Variables
        vars_to_define = [
            ("_language", tk.StringVar(), [self.update_json_previews]),
            ("_theme", tk.StringVar(), [self.update_json_previews]),
            ("_enable_always_on_top", tk.BooleanVar(), [self.update_json_previews]),
            ("_enable_log_to_file", tk.BooleanVar(), [self.update_json_previews]),
            ("_enable_sound", tk.BooleanVar(), [self.update_json_previews]),
            ("_sound_file", tk.StringVar(), [self.update_json_previews]),
            ("_font_face", tk.StringVar(), [self.update_json_previews, self.update_font_preview]),
            ("_font_size", tk.StringVar(), [self.update_json_previews, self.update_font_preview]),
            ("_config_preview_ctntvar", tk.StringVar(), [None]),
            ("_list_preview_ctntvar", tk.StringVar(), [None]),
            ("_sliderval_r", tk.IntVar(), [self.update_colpreview]),
            ("_sliderval_g", tk.IntVar(), [self.update_colpreview]),
            ("_sliderval_b", tk.IntVar(), [self.update_colpreview]),
            ("_random_cols", ListVar(), [self.update_json_previews]),
            ("_list_data", DictVar(), [self.update_json_previews])
        ]
        for _, (var_name, var_type, _) in enumerate(vars_to_define):
            setattr(self, var_name, var_type)

        # Apply the Sun Valley theme, and title bar colour (Windows Only)
        self.theme_helper = ThemeHelper(self, config.app_theme, customisations=style_customisations)
        self.theme_helper.apply_theme()

        self._define_interface()
        self.populate_interface()

        # Define update callbacks for variables
        for _, (var_name, _, write_callbacks) in enumerate(vars_to_define):
            for callback in write_callbacks:
                if callback is not None:
                    getattr(self, var_name).trace_add("write", callback=lambda *_, cb=callback: cb())

        self.mainloop()

    def _set_window_properties(self):
        tk_version = tuple(int(part) for part in str(tk.TkVersion).split('.'))
        self.logger.debug(f"Configuring window properties... (tk Version: {str(tk_version)})")

        # Configure Tk Window Properties
        self.lift()
        self.focus_force()

        if tk_version >= (8, 6):
            self.app_icon = tk.PhotoImage(file=f"{__info__.CONFIG_DIR}/icons/appicon_config.png").subsample(3,3)

        self.geometry('x'.join(str(x) for x in self.config.app_size))
        self.title(self.config.app_title)
        self.resizable(0, 0)
        self.attributes('-topmost', True)
        self.after_idle(self.attributes,'-topmost', False)
        if hasattr(self, "app_icon"):
            self.iconphoto(True, self.app_icon)
        self.protocol('WM_DELETE_WINDOW', self._on_closing)
        signal.signal(signal.SIGINT, self._on_closing)

        # Define Application ID for Windows environments
        if platform.system() == "Windows":
            app_id = getattr(__info__, "APP_ID", "fallback")
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)


    def clear_focus(self, event):
        ttk_focusable_widgets = (ttk.Entry, ttk.Button, ttk.Combobox, ttk.Spinbox, ttk.Scale)
        tk_focusable_classes = ['Entry', 'Button', 'Text', 'Scale', 'Spinbox']

        # Check if the clicked widget is focusable
        if (
            isinstance(event.widget, ttk_focusable_widgets) or 
            event.widget.winfo_class() in tk_focusable_classes
        ):
            return  # Let the widget keep focus
        self.focus_set()


    def get_available_sounds(self) -> list:
        sound_dir = f"{__info__.CONFIG_DIR}/sounds"
        supported_formats = (".mp3", '.wav')
        available_sounds = []
        for file in os.listdir(sound_dir):
            if file.endswith(supported_formats):
                available_sounds.append(file)
        return sorted(available_sounds)


    def get_supported_languages(self) -> dict:
        available_locales = {}
        locale_dir = __info__.LOCALE_DIR

        # Walk through the locale directory to find .mo files
        for root, _, files in os.walk(locale_dir):
            if root.endswith('LC_MESSAGES'):
                if any(file.endswith('.mo') for file in files):
                    # Extract the locale from the parent directory of LC_MESSAGES
                    locale_code = os.path.basename(os.path.dirname(root))
                    
                    if locale_code not in available_locales:
                        try:
                            # Resolve language name using langcodes
                            display_name = __info__.LANGUAGE_MAP.get(locale_code)
                        except Exception:
                            # Fallback to the code itself if langcodes fails
                            display_name = locale_code
                        
                        available_locales[display_name] = locale_code

        # Return a sorted dictionary
        return dict(sorted(available_locales.items()))


    def post_select_focus(self, event):
        event.widget.selection_clear()
        self.focus_set()


    def populate_interface(self):
        self.logger.info("Loading configuration values from configuration file...")
        self._enable_always_on_top.set(self.loaded_config.get(["generator_config", "feature_flags", "enable_always_on_top"], False))
        self._enable_log_to_file.set(self.loaded_config.get(["generator_config", "feature_flags", "enable_log_to_file"], False))
        self._enable_sound.set(False if len(self.get_available_sounds()) == 0 else self.loaded_config.get(["generator_config", "feature_flags", "enable_sound"], False))
        self._theme_ctrl.set_backend_value(self.loaded_config.get(["generator_config", "theme"], "light"))
        self._list_data.set(self.list_data.json_data)
        
        saved_soundfile = self.loaded_config.get(["generator_config", "sound_file"])
        available_sounds = self.get_available_sounds()
        if saved_soundfile in available_sounds:
            self._sound_file.set(saved_soundfile)
        elif len(available_sounds) > 0:
            self._sound_file.set(available_sounds[0])

        for key in self._list_data.keys():
            self.list_lstbx.add_item(key)
        
        self.logger.debug("Reading currently defined random colours...")
        for color in self.loaded_config.get(["generator_config", "colours", "random_colours"], []):
            if validate.is_hex_color(color):
                self._random_cols.append(color.lower())
                self._random_colors_ctrl.add_item(color.lower())
                self.logger.debug(f"  -> Added {color.lower()}")

        self._font_face.set(self.loaded_config.get(["generator_config", "font", "face"], ""))
        self._font_size.set(self.loaded_config.get(["generator_config", "font", "size"], ""))
        self.update_font_preview()
        self.update_json_previews()


    def _change_intvar_by_amount(self, var: tk.IntVar, amount) -> None:
        if not isinstance(var, tk.IntVar):
            raise TypeError("Variable must be of type: tk.IntVar")
        new_val = int(var.get() + amount)
        if 0 <= new_val <= 255:
            var.set(new_val)

    def update_json_previews(self) -> None:
        self.logger.info("Syncing configuration values...")
        try:
            configuration_updates = {
                # Feature flags
                ("generator_config", "feature_flags", "enable_always_on_top"): self._enable_always_on_top.get(),
                ("generator_config", "feature_flags", "enable_log_to_file"): self._enable_log_to_file.get(),
                ("generator_config", "feature_flags", "enable_sound"): False if (len(self.get_available_sounds()) == 0) else self._enable_sound.get(),

                # Generator settings
                ("generator_config", "language"): self._language_ctrl.get_backend_value(),
                ("generator_config", "theme"): self._theme_ctrl.get_backend_value(),
                ("generator_config", "font", "face"): self._font_face.get(),
                ("generator_config", "font", "size"): self._font_size.get(),
                ("generator_config", "sound_file"): self._sound_file.get(),
                ("generator_config", "colours", "random_colours"): self._random_cols.get(),

                # Editor settings
                ("editor_config", "theme"): self._theme_ctrl.get_backend_value(),
            }
            for keys, value in configuration_updates.items():
                try:
                    # Coerce booleans
                    if keys[-1].startswith('enable_'):
                        value = bool(value)
                    # Coerce font size to int if applicable
                    if keys == ("generator_config", "font", "size"):
                        value = int(value)
                    # Update using the new `set` method in JSONHandler
                    self.logger.debug(f"Updating configuration value for '{' -> '.join(keys)}': {value}")
                    self.loaded_config.set(list(keys), value)
                except (ValueError, TypeError) as e:
                    self.logger.warning(
                        f"Skipping invalid value for '{' -> '.join(keys)}': {value} ({e})"
                    )

            self.logger.info("Syncing list data...")
            self.list_data.overwrite(self._list_data.get())

            self.logger.info("Updating configuration previews...")

            # Format and update previews
            format_options = {"indent": 4, "separators": (',', ': '), "ensure_ascii": False}
            self._config_preview_ctntvar.set(json.dumps(self.loaded_config.json_data, **format_options))
            self._list_preview_ctntvar.set(custom_json_dump(self.list_data.json_data, **format_options))

        except Exception as e:
            self.logger.error(f"Failed to update configuration previews: {e}")
            print(traceback.format_exc())


    def update_colpreview(self) -> None:
        red_value = self._sliderval_r.get()
        green_value = self._sliderval_g.get()
        blue_value = self._sliderval_b.get()

        new_col = f"#{red_value:02x}{green_value:02x}{blue_value:02x}"
        self._hexentry.delete(0, tk.END)
        self._hexentry.insert(0, new_col)
        self._colpreview.configure(background=new_col)


    def update_from_hex(self, color_input) -> None:
        if (rgb_tuple := hex_to_rgb(color_input)):
            r, g, b = rgb_tuple
            self._slider_r.set(r)
            self._slider_g.set(g)
            self._slider_b.set(b)


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
            setattr(self, tab_attr_name, tk.Frame(self._tab_control))
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
        treeviews = [
            ("list", "Lists"),
            ("items", "Items")
        ]
        for i, (listbox_name, header) in enumerate(treeviews):
            setattr(self, f"{listbox_name}_lstbx", ScrollableListbox(
                self._editor_tab, header=header,
            ))
            getattr(self, f"{listbox_name}_lstbx").grid(row=1, column=(i * 3), columnspan=3, sticky="nesw", padx=5, pady=5)
            self._editor_tab.grid_columnconfigure(i * 3, weight=(i * 3))

            treeview_controls = [
                (f"{listbox_name}_textbox", ttk.Entry, "", {}),
                (f"{listbox_name}_add_btn", ttk.Button, "+", {}),
                (f"{listbox_name}_rem_btn", ttk.Button, "-", {})
            ]
            for j, (ctrl_name, ctrl_type, text, ctrl_options) in enumerate(treeview_controls):
                setattr(self, ctrl_name, ctrl_type(
                    self._editor_tab, text=text, **ctrl_options
                ))
                getattr(self, ctrl_name).grid(row=2, column=(j + (i * 3)), sticky="nesw", padx=5, pady=(0, 5))

        self._editor_controls = ttk.Frame(self._editor_tab)
        self._editor_controls.grid(row=0, column=0, padx=10, pady=10, columnspan=(len(treeviews) * len(treeview_controls)), sticky="nw")

        # Define save controls
        editor_controls = [
            ("revert_list_changes_btn", "Revert changes", ttk.Button, {"state": "disabled"})
        ]
        for i, (ctrl_attr_name, text, ctrl_type, options) in enumerate(editor_controls):
            setattr(self, f"_{ctrl_attr_name}", ctrl_type(self._editor_controls, text=text, **options))
            getattr(self, f"_{ctrl_attr_name}").grid(row=0, column=i, padx=(0, 10), sticky="ew")


        self.after_idle(lambda: self.list_lstbx.treeview.bind("<<TreeviewSelect>>", self._load_list))

        self.list_add_btn.configure(command=self.create_new_list)
        self.list_rem_btn.configure(command=self.remove_list)
        self.items_add_btn.configure(command=self.add_list_item)
        self.items_rem_btn.configure(command=self.rem_list_item)

        self._editor_tab.grid_rowconfigure(1, weight=1)

    def create_new_list(self, *_):
        new_list = self.list_textbox.get()
        if new_list != "" and new_list not in self._list_data.keys():
            self.list_lstbx.add_item(new_list)
            self._list_data.update(new_list, [])
        
    def remove_list(self, *_):
        selection = self.list_lstbx.treeview.selection()
        for item in selection:
            list_name = self.list_lstbx.treeview.item(item, 'text')
            self._list_data.remove(list_name)
        self.list_lstbx.rem_item()
        self.list_lstbx.treeview.selection_add(self.list_lstbx.treeview.get_children()[0])

    def add_list_item(self, *_):
        new_item = self.items_textbox.get()
        list_data = []
        for item in self.items_lstbx.treeview.get_children():
            list_data.append(self.items_lstbx.treeview.item(item, 'text'))

        if new_item != "" and new_item not in list_data:
            list_data.append(new_item)
            self.items_lstbx.add_item(new_item)
            self._list_data.update(self._current_list, list_data)

    def rem_list_item(self, *_):
        self.items_lstbx.rem_item()
        list_data = []

        for item in self.items_lstbx.treeview.get_children():
            list_data.append(self.items_lstbx.treeview.item(item, 'text'))
        self._list_data.update(self._current_list, list_data)


    def _load_list(self, _):
        selected_list = self.list_lstbx.treeview.selection()
        if not selected_list:
            return

        # Get the selected list name
        new_list = self.list_lstbx.treeview.item(selected_list[0], 'text')
        
        # Check if the list is already loaded to avoid redundant refresh
        if getattr(self, '_current_list', None) == new_list:
            return

        # Update the current list reference
        self._current_list = new_list

        # Clear previous treeview items
        self.logger.debug("Clearing item preview...")
        for items in self.items_lstbx.treeview.get_children():
            self.items_lstbx.treeview.delete(items)

        # Load the new list
        self.logger.info(f"Loading list: {self._current_list}")
        item_count = 0
        for item in self._list_data.find(self._current_list):
            self.items_lstbx.add_item(item)
            item_count += 1
        self.logger.info(f"  -> Loaded {item_count} values")


    def _save_tab_ui(self):
        self._save_controls = ttk.Frame(self._save_tab)
        self._save_controls.grid(row=0, column=0, padx=10, pady=(10, 2), columnspan=2, sticky="nw")

        # Define save controls
        save_controls = [
            ("save_btn", "Save configuration...", ttk.Button, {"style": "Accent.TButton", "command": lambda *_: self.save_configuration()}),
            ("save_status_lbl", "Check your configuration options before saving!", ttk.Label, {})
        ]
        for i, (ctrl_attr_name, text, ctrl_type, options) in enumerate(save_controls):
            setattr(self, f"_{ctrl_attr_name}", ctrl_type(self._save_controls, text=text, **options))
            getattr(self, f"_{ctrl_attr_name}").grid(row=0, column=i, padx=(0, 10), sticky="ew")

        # Define interface section containers
        preview_containers = [
            ("config_preview", "Configuration Preview", 1, {
                "row": 1, "column": 0, "sticky": "nesw",
                "padx": 5, "pady": 5
            }),
            ("list_preview", "List File Preview", 1, {
                "row": 1, "column": 1, "sticky": "nesw",
                "padx": 5, "pady": 5
            })
        ]
        for i, (container_name, text, num_of_columns, grid_options) in enumerate(preview_containers):
            setattr(self, f"_{container_name}_container", ttk.LabelFrame(
                self._save_tab, text=f" {text} "
            ))
            getattr(self, f"_{container_name}_container").grid(**grid_options)
            for x in range(num_of_columns):
                getattr(self, f"_{container_name}_container").grid_columnconfigure(x, weight=1, uniform="column")
            self._save_tab.grid_columnconfigure(i, weight=1, uniform="column")
            setattr(self, f"_{container_name}_ctnt", ReadOnlyTextWithVar(
                getattr(self, f"_{container_name}_container"), 
                highlightthickness=0, border=0, foreground="gray64", 
                textvariable=getattr(self, f"_{container_name}_ctntvar")
            ))
            getattr(self, f"_{container_name}_ctnt").pack(fill="both", expand=True, padx=10, pady=5)

        self._save_tab.grid_rowconfigure(1, weight=1)


    def _preference_tab_ui(self):
        # Define interface section containers
        containers = [
            ("preferences", "Preferences", 2, {
                "row": 0, "column": 0,
                "rowspan": 2, "sticky": "nesw",
                "padx": 5, "pady": 5, "ipadx": 50, "ipady": 50
            }),
            ("color_select", "Colour Selection", 1, {
                "row": 0, "column": 1,
                "sticky": "nesw",
                "padx": 5, "pady": (5, 2), "ipadx": 20, "ipady": 20
            }),
            ("font_preview", "Font Preview", 1, {
                "row": 1, "column": 1,
                "sticky": "nesw",
                "padx": 5, "pady": (2, 5), "ipadx": 20, "ipady": 20
            })
        ]
        for _, (container_name, text, num_of_columns, grid_options) in enumerate(containers):
            setattr(self, f"_{container_name}_container", ttk.LabelFrame(
                self._preference_tab, text=f" {text} "
            ))
            getattr(self, f"_{container_name}_container").grid(**grid_options)
            for x in range(num_of_columns):
                getattr(self, f"_{container_name}_container").grid_columnconfigure(x, weight=1, uniform="column")

        self._color_select_container.grid_rowconfigure(0, weight=1)

        # Define configurable setting controls
        settings = [
            ("language", "Interface Language", OptionMenuWrapper, {
                "variable": self._language,
                "values": self.supported_languages
            }, "ew"),
            ("theme", "Application Theme", OptionMenuWrapper, {
                "variable": self._theme,
                "values": self.supported_themes
            }, "ew"),
            ("ontop", "Always on top", ttk.Checkbutton, {
                "variable": self._enable_always_on_top
            }, "w"),
            ("log_to_file", "Log to file", ttk.Checkbutton, {
                "variable": self._enable_log_to_file
            }, "w"),
            ("enable_sound", "Enable Sound", ttk.Checkbutton, {
                "variable": self._enable_sound,
                "state": 'disabled' if (len(self.sound_files_available) == 0) else 'normal'
            }, "w"),
            ("sound_file", "Sound File", OptionMenuWrapper, {
                "variable": self._sound_file,
                "values": self.sound_files_available,
                "state": 'disabled' if (len(self.sound_files_available) == 0) else 'normal'
            }, "ew"),
            ("font_face", "Font Face", ttk.Combobox, {
                "textvariable": self._font_face,
                "values": self.fontfaces_available,
                "validate": "focusout",
                "validatecommand": lambda: validate.is_in_list(self.fontfaces_available, self._font_face.get())
            }, "ew"),
            ("font_size", "Font Size", ttk.Combobox, {
                "textvariable": self._font_size,
                "values": self.fontsize_defaults,
                "validate": "focus",
                "validatecommand": lambda: validate.is_integer(self._font_size.get())
            }, "ew"),
            ("random_colors", "Random Colours", ScrollableListbox, {
                "height": 6
            }, "ew"),
            ("random_color_btns", "", tk.Frame, {}, "ew")
        ]
        for i, (setting_name, description, control_type, control_options, sticky_option) in enumerate(settings):
            setattr(self, f"_{setting_name}_lbl", ttk.Label(
                self._preferences_container, text=description, anchor="e"
            ))
            setattr(self, f"_{setting_name}_ctrl", control_type(
                self._preferences_container, **control_options
            ))
            getattr(self, f"_{setting_name}_lbl").grid(row=i, column=0, sticky="ew", padx=(5,0))
            getattr(self, f"_{setting_name}_ctrl").grid(row=i, column=1, sticky=sticky_option, padx=10, pady=2)
            self._preferences_container.grid_rowconfigure(i, minsize=35)

        # Define random colour treeview controls
        self._add_col_btn = ttk.Button(self._random_color_btns_ctrl, text="Add", command=self.add_random_color)
        self._rem_col_btn = ttk.Button(self._random_color_btns_ctrl, text="Remove", command=self.rem_random_color)
        self._add_col_btn.grid(row=1, column=0, padx=(0, 2), sticky="ew")
        self._rem_col_btn.grid(row=1, column=1, padx=(2, 0), sticky="ew")

        self._random_color_btns_ctrl.grid_columnconfigure(0, weight=1, uniform="_random_color_btns_ctrl")
        self._random_color_btns_ctrl.grid_columnconfigure(1, weight=1, uniform="_random_color_btns_ctrl")

        # Define mixer controls and color preview frame
        self._colpreview = tk.Frame(self._color_select_container, background="black", width=40, highlightbackground="black", highlightthickness=1)
        self._colselect_frm = ttk.Frame(self._color_select_container)
        self._colselect_frm.grid(row=1, column=0, sticky="nesw", padx=10, pady=5)
        self._colpreview.grid(row=0, column=0, sticky="nesw", padx=10, pady=(5 ,0))
        
        for i, color in enumerate(["r", "g", "b"]):
            setattr(self, f"_label_{color}", ttk.Label(
                self._colselect_frm, text=color.upper(), anchor="e")
            )
            getattr(self, f"_label_{color}").grid(row=i, column=0, sticky="ew", padx=10)
            setattr(self, f"_slider_{color}", Limiter(
                self._colselect_frm, variable=getattr(self, f"_sliderval_{color}"), to=255, precision=0)
            )
            getattr(self, f"_slider_{color}").grid(row=i, column=1, sticky="ew", padx=5)
            setattr(self, f"_minus_{color}", ttk.Button(
                self._colselect_frm, text="-", takefocus=0,
                command=lambda color=color: self._change_intvar_by_amount(getattr(self, f"_sliderval_{color}"), -1))
            )
            getattr(self, f"_minus_{color}").grid(row=i, column=2, sticky="ew")
            setattr(self, f"_sliderval_lbl_{color}", ttk.Label(
                self._colselect_frm, textvariable=getattr(self, f"_sliderval_{color}"), anchor="center")
            )
            getattr(self, f"_sliderval_lbl_{color}").grid(row=i, column=3, sticky="ew", padx=5)
            setattr(self, f"_plus_{color}", ttk.Button(
                self._colselect_frm, text="+", takefocus=0,
                command=lambda color=color: self._change_intvar_by_amount(getattr(self, f"_sliderval_{color}"), 1))
            )
            getattr(self, f"_plus_{color}").grid(row=i, column=4, sticky="ew")
            self._colselect_frm.grid_rowconfigure(i, minsize=35)

        self._hexentry_lbl = ttk.Label(self._colselect_frm, text="Hex")
        self._hexentry_lbl.grid(row=3, column=0, sticky="ew", padx=10)
        self._hexentry = ttk.Entry(self._colselect_frm)
        self._hexentry.insert(0, "#000000")
        self._hexentry.grid(row=3, column=1, columnspan=4, sticky="ew", pady=5)
        self._hexentry.bind("<FocusOut>", lambda _: self.update_from_hex(self._hexentry.get()))
        
        self._colselect_frm.grid_columnconfigure(3, minsize=40)
        self._colselect_frm.grid_columnconfigure(1, weight=1)
        self._colselect_frm.grid_rowconfigure(0, weight=1)

        # Define font preview
        self._font_preview_lbl = ttk.Label(self._font_preview_container, text="Sample", anchor="nw")
        self._font_preview_lbl.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab Grid Settings
        self._preference_tab.grid_columnconfigure(0, weight=1, uniform="column")
        self._preference_tab.grid_columnconfigure(1, weight=1, uniform="column")
        self._preference_tab.grid_rowconfigure(0, weight=1, uniform="row")
        self._preference_tab.grid_rowconfigure(1, weight=1, uniform="row")

    def rem_random_color(self):
        """Remove selected color random colors pool"""
        selected_items = list(self._random_colors_ctrl.treeview.selection())[::-1]
        if not selected_items:
            return

        for item in selected_items:
            value = self._random_colors_ctrl.treeview.item(item, 'text')
            self.logger.info(f"Removing {value} from random colors")
            self._random_cols.remove(value)
            self._random_colors_ctrl.treeview.delete(item)

    def add_random_color(self):
        """Add color to the random colors pool"""
        r = self._sliderval_r.get()
        g = self._sliderval_g.get()
        b = self._sliderval_b.get()

        if (hex_color := rgb_to_hex(r, g, b)) not in self._random_cols.get():
            self.logger.info(f"Adding {hex_color} to random colors")
            self._random_cols.append(hex_color)
            self._random_colors_ctrl.add_item(hex_color)
            return
        self.logger.warning(f"Colour '{hex_color}' already added to the color pool")


    def _on_closing(self, *_):
        self.logger.info("Termination signal received")
        self.logger.debug("  -> Stopping theme listener...")
        self.theme_helper.stop_listener()
        self.logger.info("  -> Exiting...")
        self.destroy()


    def update_font_preview(self):
        font_face = self._font_face.get()
        # Check if the font face is a string
        if not isinstance(font_face, str):
            self.logger.warning("Cannot update font preview: Invalid font face, the font face must be a string")
            return

        # Attempt to convert font size to an integer
        try:
            font_size = int(self._font_size.get())
        except ValueError:
            self.logger.warning("Cannot update font preview: Invalid font size, the font face must be an integer")
            return

        # If both conditions are met, update the preview
        self.logger.info(f"Updating font preview... ({font_face}, {font_size})")
        self._font_preview_lbl.configure(font=(font_face, font_size))


    def save_configuration(self):
        self.logger.info("Saving configuration...")

        previous_text = self._save_status_lbl.cget("text")
        self._save_btn.configure(state="disabled")
        self._save_status_lbl.configure(text="Saving...")

        self.loaded_config.write()
        self.list_data.write()
        
        self._save_status_lbl.configure(text="Configuration saved!")
        self.after(1000, lambda: self._save_status_lbl.configure(text=previous_text))
        self._save_btn.configure(state="normal")


if __name__ == "__main__":
    try:
        APP_CONFIG = EditorAppSettings(f"{__info__.CONFIG_DIR}/app_config.json", __info__.EDITOR_SCHEMA)
        instance = ConfigurationUtility(APP_CONFIG)
    except Exception as e:
        print(traceback.format_exc())
