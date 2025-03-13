import ctypes
import tkinter as tk
from tkinter import ttk
import platform

from _helpers.apply_theme import apply_title_bar_theme
from _helpers import sv_ttk

class TTKDialog(tk.Toplevel):
    def __init__(self, parent, diag_type, diag_title="", diag_message="", diag_choices=None):
        # Initialize as a Toplevel window
        super().__init__(parent)
        self.lift()
        self.diag_type = diag_type
        self.diag_title = diag_title
        self.diag_message = diag_message
        self.diag_choices = diag_choices
        self.return_value = "" # Placeholder

        # Configure window options
        self.resizable(0, 0)
        self.geometry('350x200')  # Default size, will be updated by dialog options
        self.maxsize(450, 350)
        self.title(self.diag_title)
        self.attributes('-topmost', True)

        if platform.system() == "Windows":
            hwnd = ctypes.windll.user32.FindWindowW(None, self.diag_title)
            apply_title_bar_theme(hwnd, f"dialog_{sv_ttk.get_theme()}")

        diag_options = {
            "info": {
                "type": "message",
                "buttons": ["OK"],
                "diag_size": (450, 200)
            },
            "warning": {
                "type": "message",
                "buttons": ["OK"],
                "diag_size": (450, 200)
            },
            "error": {
                "type": "message",
                "buttons": ["OK"],
                "diag_size": (450, 200)
            },
            "select": {
                "type": "select",
                "buttons": [
                    ("Cancel", "cancel"),
                    ("OK", "ok")
                ],
                "primary_btn": "ok",
                "diag_size": (350, 350)
            },
        }

        if (diag_options := diag_options.get(self.diag_type, None)):
            self._begin_dialog_build(diag_options)
        else:
            raise TypeError(f"No dialog builder could be found for type '{self.diag_type}'")

        self.protocol("WM_DELETE_WINDOW", self._close_dialog)  # Handle window close
        self.grab_set()  # Make this window modal
        self.focus()

    def _begin_dialog_build(self, options):
        DIAG_SIZE = options.get("diag_size")
        self.geometry('x'.join(str(x) for x in DIAG_SIZE))
        
        dispatcher = {
            "message": self._build_msg_dialog,
            "select": self._build_choice_dialog
        }
        dispatcher.get(options.get("type"))(options)

    def _build_choice_dialog(self, options):
        """Function to build the interface for a selection dialog box"""
        # Define static interface elements
        style = ttk.Style()
        style.configure('Treeview', rowheight=35)

        self._content_title = ttk.Label(self, text=self.diag_message, anchor="w")
        self._choices_frm = tk.Frame(self)
        self._choices_scrl = ttk.Scrollbar(self._choices_frm)
        self._choices_view = ttk.Treeview(self._choices_frm, show="tree", selectmode="browse", yscrollcommand=self._choices_scrl.set)
        self._choices_scrl.configure(command=self._choices_view.yview)
        self._button_frm = ttk.Frame(self)

        # Add items to treeview from diag_choices
        for choice in self.diag_choices:
            self._choices_view.insert("", "end", text=choice)

        # Create buttons from names in button options
        buttons_to_create = options.get("buttons")
        for i, (text, action) in enumerate(buttons_to_create):
            print(i)
            # Create button instance, each button calls processing function with its text value
            dynamic_btn = ttk.Button(
                self._button_frm, text=text,
                command=lambda a=action: self._process_choice(a)
            )

            # If button text matche the primary option, the button should use the accent colour
            if options.get("primary_btn") == action:
                dynamic_btn.configure(style="Accent.TButton")
            
            # Add the button instance to the interface
            dynamic_btn.grid(row=0, column=(i + 1), padx=(5,0), ipadx=10, sticky="NEWS")
            self._button_frm.grid_columnconfigure((i + 1), weight=1, uniform="button_control")
        self._button_frm.grid_columnconfigure(0, weight=1, uniform="button_control")

        # Add non-dynamic elements to the interface
        self._content_title.grid(row=0, column=0, sticky="nesw", padx=10, pady=10)
        self._choices_view.pack(side="left", fill="both", expand=True)
        self._choices_scrl.pack(side="right", fill="y")
        self._choices_frm.grid(row=1, column=0, sticky="nesw", padx=(10,5))
        self._button_frm.grid(row=2, column=0, sticky="esw", padx=10, pady=10)

        # Window column configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)


    def _build_msg_dialog(self, options):
        # Define content containers
        self._icon_frm = tk.Frame(self, bg="green")
        self._content_frm = ttk.Frame(self)

        # Define Content
        self._content_title = ttk.Label(self._content_frm, text=self.diag_title, anchor="w", font=('TkDefaultFont', 25))
        self._content_body = ttk.Label(self._content_frm, text=self.diag_message, anchor="nw", wraplength=300)
        self._content_separator = ttk.Separator(self._content_frm)
        self._button_frm = tk.Frame(self._content_frm)

        # Create buttons from names in button options
        buttons_to_create = options.get("buttons")
        for button in buttons_to_create:
            index = buttons_to_create.index(button)
            dynamic_btn = ttk.Button(self._button_frm, text=button, command=lambda b=button: self._process_choice(b))
            dynamic_btn.grid(row=0, column=index, padx=(5,0), pady=(5,0), ipadx=10, sticky="NEWS")
            self._button_frm.grid_columnconfigure(index, weight=1, uniform="button_control")

        # Add elements to interface
        self._icon_frm.grid(row=0, column=0, sticky="NEWS")
        self._content_frm.grid(row=0, column=1, sticky="NEWS", padx=10, pady=10)

        self._content_title.grid(row=0, column=0, sticky="NEWS")
        self._content_separator.grid(row=1, column=0, sticky="EW")
        self._content_body.grid(row=2, column=0, sticky="NEWS")
        self._button_frm.grid(row=3, column=0, sticky="ES")

        # Column Configurations
        self.grid_columnconfigure(0, weight=1, uniform="yes")
        self.grid_columnconfigure(1, weight=4, uniform="yes")
        self.grid_rowconfigure(0, weight=1)
        self._content_frm.grid_columnconfigure(0, weight=1)
        self._content_frm.grid_rowconfigure(0, weight=2, uniform="content")
        self._content_frm.grid_rowconfigure(1, weight=1, uniform="content")
        self._content_frm.grid_rowconfigure(2, weight=6, uniform="content")

    def _process_choice(self, button_pressed):
        button_pressed = button_pressed.lower()
        match self.diag_type:
            case "select":
                if button_pressed == "cancel":
                    self.return_value = ""
                else:
                    focused_item = self._choices_view.focus()
                    self.return_value = self._choices_view.item(focused_item)["text"]
            case _:
                self.return_value = button_pressed
        self.destroy()

    def _close_dialog(self):
        self.value = "yes"
        self.destroy()

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Application")
        self.geometry("500x400")

        # A Button to trigger the dialog
        self.open_dialog_btn = ttk.Button(self, text="Open Dialog", command=self.open_dialog)
        self.open_dialog_btn.pack(pady=20)

    def open_dialog(self):
        # Open the dialog as a popup
        dialog = TTKDialog(self, diag_type="select", diag_title="Select an Option", diag_message="Choose your option")
        print(dialog.value)
        dialog.wait_window(dialog)  # Wait until the dialog is closed before continuing


if __name__ == '__main__':
    app = MainApp()
    app.mainloop()
