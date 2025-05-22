from __future__ import annotations
from enum import Enum
import tkinter as tk
from tkinter import ttk
from typing import List

from core.ui.apply_theme import ThemeHelper

class TTKDialogAction(Enum):
    OK = "ok"
    CANCEL = "cancel"

class TTKDialogType(Enum):
    MESSAGE = "message"
    SELECT = "select"

class TTKDialog(tk.Toplevel):
    def __init__(self, parent, diag_type: TTKDialogType, diag_size: tuple[int, int], diag_buttons: List[tuple[str, TTKDialogAction]],
             diag_title="", diag_message="", diag_choices=None, primary_action=TTKDialogAction):
        super().__init__(parent)
        self.lift()

        if not isinstance(diag_type, TTKDialogType):
            raise TypeError(f"Invalid dialog type: {diag_type}. Must be a TTKDialogType.")

        for _, action in diag_buttons:
            if not isinstance(action, TTKDialogAction):
                raise TypeError(f"Invalid dialog action: {action}. Must be a TTKDialogAction.")

        if primary_action and not isinstance(primary_action, TTKDialogAction):
            raise TypeError(f"Invalid primary button action: {primary_action}. Must be a TTKDialogAction.")

        self.diag_type = diag_type
        self.diag_title = diag_title
        self.diag_message = diag_message
        self.diag_choices = diag_choices or []
        self.diag_buttons = diag_buttons
        self.primary_action = primary_action
        self.return_value = ""

        # Configure window options
        self.resizable(False, False)
        self.geometry(f"{diag_size[0]}x{diag_size[1]}")
        self.title(self.diag_title)
        self.attributes('-topmost', True)
        self.protocol("WM_DELETE_WINDOW", self._close_dialog)

        diag_type_map = {
            TTKDialogType.MESSAGE: self._build_msg_dialog,
            TTKDialogType.SELECT: self._build_choice_dialog
        }
        if diag_type in diag_type_map:
            diag_type_map[diag_type]()

        # Apply theme if parent has config and app_theme
        if hasattr(parent, 'config') and hasattr(parent.config, 'app_theme'):
            style_customisations = [('Treeview', {"rowheight": 35})]
            self._theme_helper = ThemeHelper(self, parent.config.app_theme, customisations=style_customisations)
            self._theme_helper.apply_theme()
        else:
            self._theme_helper = None

        # Set modal behavior
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

        # Add items to treeview
        for choice in self.diag_choices:
            self._choices_view.insert("", "end", text=choice)

        # Create buttons
        for i, (text, action) in enumerate(self.diag_buttons):
            dynamic_btn = ttk.Button(
                self._button_frm, text=text,
                command=lambda a=action: self._process_choice(a)
            )
            if action == self.primary_action:
                dynamic_btn.configure(style="Accent.TButton")

            dynamic_btn.grid(row=0, column=i+1, padx=5, ipadx=10, sticky="NEWS")
            self._button_frm.grid_columnconfigure(i+1, uniform="buttons")
        self._button_frm.grid_columnconfigure(0, weight=1)

        # Layout configuration
        self._content_title.grid(row=0, column=0, sticky="nesw", padx=10, pady=10)
        self._choices_view.pack(side="left", fill="both", expand=True)
        self._choices_scrl.pack(side="right", fill="y")
        self._choices_frm.grid(row=1, column=0, sticky="nesw", padx=10, pady=5)
        self._button_frm.grid(row=2, column=0, sticky="esw", padx=10, pady=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def _build_msg_dialog(self):
        """Build interface for a message dialog."""
        self._content_frm = ttk.Frame(self)

        self._content_title = ttk.Label(self._content_frm, text=self.diag_title, anchor="w", font=('TkDefaultFont', 16))
        self._content_body = ttk.Label(self._content_frm, text=self.diag_message, anchor="nw", wraplength=300)

        self._button_frm = ttk.Frame(self._content_frm)
        for i, (text, action) in enumerate(self.diag_buttons):
            dynamic_btn = ttk.Button(
                self._button_frm, text=text,
                command=lambda a=action: self._process_choice(a)
            )
            dynamic_btn.grid(row=0, column=i, padx=5, ipadx=10, sticky="NEWS")
            self._button_frm.grid_columnconfigure(i, weight=1)

        self._content_title.pack(fill="x", pady=(0, 5))
        self._content_body.pack(fill="x", pady=(0, 10))
        self._button_frm.pack(fill="x")

        self._content_frm.pack(expand=True, fill="both", padx=10, pady=10)

    def _process_choice(self, button_pressed):
        if self.diag_type == TTKDialogType.SELECT:
            if button_pressed == TTKDialogAction.CANCEL:
                self.return_value = ""
            else:
                focused_item = self._choices_view.focus()
                self.return_value = self._choices_view.item(focused_item)["text"]
        else:
            self.return_value = button_pressed
        self._close_dialog()

    def _close_dialog(self):
        if self._theme_helper:
            self._theme_helper.stop_listener()
        self.destroy()


class DemoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Application")
        self.geometry("500x400")

        ttk.Button(self, text="Open Dialog", command=self.open_dialog).pack(pady=20)

    def open_dialog(self):
        dialog = TTKDialog(
            self, TTKDialog.TYPE_SELECT,
            diag_size=(350, 350),
            diag_title="Choose an option",
            diag_message="Choose an option",
            diag_choices=['test1', 'test2'],
            diag_buttons=[("Cancel", TTKDialog.ACTION_CANCEL), ("OK", TTKDialog.ACTION_OK)]
        )
        dialog.wait_window()
        print(dialog.return_value)


if __name__ == '__main__':
    app = DemoApp()
    app.mainloop()
