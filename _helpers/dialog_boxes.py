import tkinter as tk
from tkinter import ttk

from _helpers.apply_theme import ThemeHelper

class TTKDialog(tk.Toplevel):
    def __init__(self, parent, diag_type, diag_size: tuple[int,int], diag_buttons: list[tuple[str, str]],
                 diag_title="", diag_message="", diag_choices=None, primary_btn=""):
        # Initialize as a Toplevel window
        super().__init__(parent)
        self.lift()

        self.diag_type = diag_type
        self.diag_title = diag_title
        self.diag_message = diag_message
        self.diag_choices = diag_choices
        self.diag_buttons = diag_buttons
        self.primary_btn = primary_btn
        self.return_value = ""

        # Configure window options
        self.resizable(0, 0)
        self.geometry('x'.join(str(x) for x in diag_size))
        self.title(self.diag_title)
        self.attributes('-topmost', True)
        self.protocol("WM_DELETE_WINDOW", self._close_dialog)

        dispatcher = {
            "message": self._build_msg_dialog,
            "select": self._build_choice_dialog
        }
        dispatcher.get(diag_type)()

        style_customisations = [('Treeview', {"rowheight": 35})]
        self._theme_helper = ThemeHelper(self, parent.config.app_theme, customisations=style_customisations)
        self._theme_helper.apply_theme()

        self.grab_set()
        self.focus()

    def _build_choice_dialog(self):
        """Function to build the interface for a selection dialog box"""
        # Define static interface elements

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
        for i, (text, action) in enumerate(self.diag_buttons):
            # Create button instance, each button calls processing function with its text value
            dynamic_btn = ttk.Button(
                self._button_frm, text=text,
                command=lambda a=action: self._process_choice(a)
            )

            # If button text matched the primary option, the button should use the accent colour
            if self.primary_btn == action:
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
        self._close_dialog()

    def _close_dialog(self):
        self._theme_helper.stop_listener()
        self.destroy()


class DemoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Application")
        self.geometry("500x400")

        # A Button to trigger the dialog
        self.open_dialog_btn = ttk.Button(self, text="Open Dialog", command=self.open_dialog)
        self.open_dialog_btn.pack(pady=20)

    def open_dialog(self):
        # Open the dialog as a popup
        dialog = TTKDialog(
            self, 
            diag_type="select",
            diag_title="Choose an option",
            diag_message="Choose an option",
            diag_choices=['test1', 'test2'],
            diag_size=(350, 350),
            diag_buttons=[
                ("Cancel", "cancel"),
                ("OK", "ok")
            ]
        )
        dialog.wait_window(dialog)  # Wait until the dialog is closed before continuing
        print(dialog.return_value)

if __name__ == '__main__':
    app = DemoApp()
    app.mainloop()
