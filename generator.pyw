import ctypes
import threading
import random
import sys
import platform
import tkinter as tk
from tkinter import ttk

from _helpers.apply_theme import apply_theme
from _helpers.dialog_boxes import TTKDialog
from _helpers.data import JSONHandler
from _helpers.logbook import Logger, StreamHandler, FileHandler
from _helpers.playsound import playsound
from _helpers.configuration import GeneratorAppSettings
from _helpers.readability import determine_text_color


class RandomGenerator(tk.Tk):
    def __init__(self, config: GeneratorAppSettings):
        tk.Tk.__init__(self)
        self.config = config

        self.logger = self._initialize_logger()
        self.loaded_list = []
        self.loaded_list_name = tk.StringVar()
        self.call_index = 0

        self.loaded_list_name.trace_add('write', callback=lambda a,b,c: self.title(
            f"Random Generator - Loaded List: {self.loaded_list_name.get()}"
        ))

        self._list_data = JSONHandler("_configuration/lists.json").json_data

        self.logger.info("Launching Random Generator...")
        self.geometry('x'.join(str(x) for x in self.config.app_size))
        self.resizable(0,0)
        self.title("Random Generator")
        self.attributes('-topmost', self.config.app_on_top)
        self.protocol('WM_DELETE_WINDOW', self._on_closing)

        photo = tk.PhotoImage(file='_configuration/icons/appicon_config.png')
        self.iconphoto(True, photo)

        if platform.system() == "Windows":
            myappid = 'bytefloater.rndgen.generator.4'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        apply_theme(self, config.app_theme)
        self._define_interface()
        self.mainloop()


    def _initialize_logger(self) -> Logger:
        logger = Logger("")
        filehandler = FileHandler('applog_generator.txt', level="DEBUG", bubble=True)
        logger.handlers.append(filehandler)

        if sys.stdout:
             streamhandler = StreamHandler(sys.stdout, level="DEBUG", bubble=True)
             logger.handlers.append(streamhandler)
        return logger


    def _on_closing(self):
        self.destroy()


    def _change_list(self):
        self.logger.info("Changing list...")
        available_lists = self._list_data.keys()

        self.logger.debug("Launching choice dialog...")
        self.attributes('-topmost', False)
        dialog = TTKDialog(
            self, diag_type="select", diag_title="Select an Option",
            diag_message="Choose your option",
            diag_choices=available_lists
        )
        dialog.wait_window(dialog)  # Wait until the dialog is closed before continuing
        self.attributes('-topmost', self.config.app_on_top)

        if dialog.return_value:
            self.logger.info(f"Selecting list '{dialog.return_value}'")
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
        self._item_lbl = tk.Label(self._interface_container, text="", anchor="w", font=(self.config.app_fontface, self.config.app_fontsize))

        self._btn_sequential = ttk.Button(self._interface_container, text="Sequential", command=self.sequential_random)
        self._btn_random = ttk.Button(self._interface_container, text="Random", command=self.insequential_random)
        self._btn_change_list = ttk.Button(self._interface_container, text="Change List", command=self._change_list)

        self._interface_container.pack(side="left", fill="both", expand=True)
        self._item_lbl.grid(row=0, column=0, columnspan=3, sticky="news", padx=5)
        self._btn_sequential.grid(row=1, column=0, sticky="ew", ipady=6)
        self._btn_random.grid(row=1, column=1, sticky="ew", ipady=6)
        self._btn_change_list.grid(row=1, column=2, sticky="ew", ipady=6)

        self._interface_container.grid_rowconfigure(0, weight=1)
        self._interface_container.grid_columnconfigure(0, weight=1, uniform="button_controls")
        self._interface_container.grid_columnconfigure(1, weight=1, uniform="button_controls")

        self._random_bgcols()


    def insequential_random(self):
        try:
            item = random.choice(self.loaded_list)
            self._item_lbl.config(text=item)
            self.logger.info(f"Insequential random called, returned '{item}'")
        except IndexError as e:
            self.logger.error(e)
        self._post_selection_actions()


    def sequential_random(self):
        if self.call_index == (len(self.loaded_list)):
            self._randomize_elements()
            self.call_index = 0

        self._item_lbl.config(text=self.loaded_list[self.call_index])
        self.call_index += 1
        print(self.loaded_list, self.call_index)
        self._post_selection_actions()


    def _randomize_elements(self):
        self.loaded_list = random.sample(self.loaded_list, len(self.loaded_list))


    def _post_selection_actions(self):
        audio_thread = threading.Thread(target=self._play_sound)
        audio_thread.start()
        self._random_bgcols()


    def _play_sound(self):
        playsound("_configuration/sounds/wav/ding.wav")


    def _random_bgcols(self):
        new_col = random.choice(self.config.random_cols)
        new_txt_col = determine_text_color(
            new_col,
            dark_color=self.config.app_dark_text_col,
            light_color=self.config.app_light_text_col
        )

        # Change background of elements
        elements_to_update = [
            self,
            self._interface_container,
            self._item_lbl
        ]
        for element in elements_to_update:
            element.configure(background=new_col)

        self._item_lbl.configure(foreground=new_txt_col)
        
        # self.configure(background=new_col)
        # self._interface_container.configure(background=new_col)
        # self._item_lbl.configure(background=new_col)



if __name__ == "__main__":
    APP_CONFIG = GeneratorAppSettings("_configuration/app_config.json")
    instance = RandomGenerator(APP_CONFIG)
