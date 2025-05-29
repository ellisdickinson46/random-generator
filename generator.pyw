import random
import threading
import tkinter as tk
from tkinter import ttk

from core.__info__ import (
    CONFIG_DIR, GENERATOR_SCHEMA, LOCALE_DIR, SOUNDS_DIR
)
from core.configuration import GeneratorAppSettings
from core.data import JSONHandler
from core.ui.widgets.dialogs import ChoiceDialog, DialogAction
from core.ui.wcag_contrast import determine_text_color
from core.ui.base_window import BaseTkWindow
from core.locale_manager import LocaleManager
from libs.playsound3 import playsound

class RandomGenerator(BaseTkWindow):
    def __init__(self, config: GeneratorAppSettings):
        super().__init__(
            app_size=config.app_size,
            app_icon="appicon.png",
            theme=config.app_theme,
            topmost=config.enable_always_on_top,
            logger_name="generator",
            log_to_file=config.enable_log_to_file,
            theme_flags="disable_auto_titlebar"
        )
        self.config = config
        self.locale_manager = LocaleManager(
            domain="generator",
            localedir=LOCALE_DIR,
            default_locale=self.config.language,
            logger_instance=self.logger
        )

        self.title(self._('_window_title'))

        self._list_data = JSONHandler(json_file=f"{CONFIG_DIR}/lists.json")
        self.loaded_list = []
        self.loaded_list_name = tk.StringVar()
        self.call_index = 0

        # Add callback function to update the window title when the list value is changed
        self.loaded_list_name.trace_add('write', callback=lambda a,b,c: self.title(
            f"{self._('_window_title')} - {self._('Loaded List')}: {self.loaded_list_name.get()}"
        ))

        # Configure additional styles
        self.bind("<<ThemeChanged>>", lambda _: self.update_styles(self.cget("background")))

        self._define_interface()
        self.mainloop()


    def _change_list(self):
        self.logger.info("Change list requested...")
        available_lists = self._list_data.json_data.keys()

        self.attributes('-topmost', False)
        dialog = ChoiceDialog(
            self,
            title=self._("Choose an option"),
            message=f"{self._('Choose an option')}:",
            choices=available_lists,
            size=(350, 350),
            buttons=[
                (self._("Cancel"), DialogAction.CANCEL),
                (self._("OK"), DialogAction.OK)
            ],
            primary_action=DialogAction.OK
        )
        dialog.wait_window(dialog)  # Wait until the dialog is closed before continuing
        self.attributes('-topmost', self.config.app_on_top)

        if dialog.return_value:
            self.logger.info(f"Selected list: '{dialog.return_value}'")
            self.loaded_list_name.set(dialog.return_value)
            self.call_index = 0
            self._item_lbl.configure(text="")
            self._refresh_list()


    def _refresh_list(self):
        new_list = self._list_data.get(self.loaded_list_name.get())
        self.loaded_list = new_list
        self._randomize_elements()
        self.logger.info(f"Loaded list with length {len(new_list)} items")


    def _define_interface(self):
        self.logger.debug("Creating interface...")
        self._interface_container = tk.Frame(self)
        self._item_lbl = ttk.Label(
            self._interface_container, text="", anchor="w",
            font=(self.config.app_fontface, self.config.app_fontsize)
        )

        # Define buttons in the format (text, attribute name, command, expand)
        buttons = [
            ("_btn_sequential", self.sequential_random, True),
            ("_btn_random", self.random, True),
            ("_btn_chg_list", self._change_list, False)
        ]

        for i, (btn_attr_name, command, expand) in enumerate(buttons):
            setattr(self, btn_attr_name, ttk.Button(
                self._interface_container, text=self._(btn_attr_name), command=command, style="MatchedBg.TButton")
            )
            getattr(self, btn_attr_name).grid(
                row=1, column=i, sticky="ew", ipady=6, padx=5, pady=5
            )
            if expand:
                self._interface_container.grid_columnconfigure(i, weight=1, uniform="button_controls")

        self._interface_container.pack(side="left", fill="both", expand=True, ipadx=20)
        self._item_lbl.grid(
            row=0, column=0, columnspan=3, sticky="news", padx=5,
            pady=((self._titlebar_height, 0) if hasattr(self, "_titlebar_height") else 0)
        )
        self._interface_container.grid_rowconfigure(0, weight=1)
        self._random_bgcols()


    def random(self):
        try:
            item = random.choice(self.loaded_list)
            self._item_lbl.config(text=item)
            self.logger.info(f"Insequential random called, returned '{item}'")
            self._post_selection_actions()
        except IndexError as e:
            self.logger.error(e)


    def sequential_random(self):
        if len(self.loaded_list) == 0:
            self.logger.error("Cannot choose from an empty sequence")
            return
        if self.call_index == (len(self.loaded_list)):
            self._randomize_elements()
            self.call_index = 0

        item = self.loaded_list[self.call_index]

        self.logger.info(f"Sequential random called, returned '{item}'")
        self._item_lbl.config(text=item)
        self.call_index += 1
        self._post_selection_actions()


    def _randomize_elements(self):
        self.loaded_list = random.sample(self.loaded_list, len(self.loaded_list))


    def _post_selection_actions(self):
        if self.config.enable_sound:
            audio_thread = threading.Thread(target=self._play_sound, daemon=True)
            audio_thread.start()
        self._random_bgcols()


    def _play_sound(self):
        sound_fname = self.config.sound_fname
        if sound_fname:
            try:
                self.logger.debug(f"Attempting to play sound... [{sound_fname}]")
                playsound(f"{SOUNDS_DIR}/{sound_fname}")
            except OSError as e:
                self.logger.error(f"Error playing sound: {e}")


    def _random_bgcols(self):
        new_col = random.choice(self.config.random_cols)

        elements_to_update = [
            self,
            self._interface_container,
            self._item_lbl
        ]
        for element in elements_to_update:
            element.configure(background=new_col)

        self.update_styles(new_col)

    def update_styles(self, new_col):
        self.style.configure("MatchedBg.TButton", background=new_col)
        self.theme_helper._apply_titlebar(override_color=new_col)
        self._item_lbl.configure(foreground=determine_text_color(
            self.cget("background"),
            dark_color=self.config.app_dark_text_col,
            light_color=self.config.app_light_text_col
        ))


if __name__ == "__main__":
    try:
        APP_CONFIG = GeneratorAppSettings(f"{CONFIG_DIR}/app_config.json", GENERATOR_SCHEMA)
        instance = RandomGenerator(APP_CONFIG)
    except Exception as e:
        print(e)
