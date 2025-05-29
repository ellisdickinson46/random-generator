from __future__ import annotations
from enum import Enum
import platform
import tkinter as tk
from tkinter import ttk
from typing import Optional

from core.ui.base_window import BaseTkWindow
from core.ui.apply_theme import ThemeHelper
from core.ui.nswindow_style import set_nswindow_style

class DialogAction(Enum):
    OK = "ok"
    CANCEL = "cancel"


class BaseDialog(tk.Toplevel):
    def __init__(
        self, parent: tk.Widget, title: str, size: tuple[int, int],
        buttons: list[tuple[str, DialogAction]], primary_action: Optional[DialogAction] = None,
    ):
        super().__init__(parent)
        self.lift()

        # Window setup
        self.title(title)
        self.geometry(f"{size[0]}x{size[1]}")
        self.resizable(False, False)
        self.minsize(260, 200)
        self.attributes('-topmost', True)
        self.protocol("WM_DELETE_WINDOW", lambda: self._process_action(DialogAction.CANCEL))
        self.style = ttk.Style()
        
        if platform.system() == "Darwin":
            self.attributes("-alpha", 0.0)
            try:
                set_nswindow_style(self, size, title)
            except (RuntimeError, ImportError):
                self.logger.exception("Unable to set NSWindow properties")
            self.attributes("-alpha", 1.0)

        # Validate actions
        for _, action in buttons:
            if not isinstance(action, DialogAction):
                raise TypeError(f"Invalid dialog action: {action}. Must be a DialogAction.")
        if primary_action and not isinstance(primary_action, DialogAction):
            raise TypeError(f"Invalid primary action: {primary_action}. Must be a DialogAction.")

        self.buttons = buttons
        self.primary_action = primary_action
        self.return_value: str | DialogAction | None = None

        # Theme
        if hasattr(parent, 'theme'):
            style_customisations = [('Treeview', {"rowheight": 35})]
            self._theme_helper = ThemeHelper(
                self,
                parent.theme,
                custom_styles=style_customisations,
            )
            self._theme_helper.start()
        else:
            self._theme_helper = None

        # Content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(
            expand=True, fill="both", padx=10,
            pady=((self._titlebar_height + 10, 0) if hasattr(self, "_titlebar_height") else 10)
        )

        # Build dialog-specific content
        self._build_content()

        # Create buttons (layout delegated to subclass)
        self.button_frame = ttk.Frame(self)
        self._create_buttons()

        # Modal
        self.grab_set()
        self.focus()

    def _build_content(self) -> None:
        """Override to populate content_frame before buttons."""
        raise NotImplementedError

    def _create_buttons(self) -> None:
        """Create buttons in button_frame; subclass should layout button_frame."""
        for idx, (text, action) in enumerate(self.buttons):
            btn = ttk.Button(
                self.button_frame,
                text=text,
                command=lambda a=action: self._process_action(a)
            )
            if action == self.primary_action:
                btn.configure(style="Accent.TButton")
            btn.grid(row=0, column=idx, padx=5, ipadx=10, sticky="NEWS")
            self.button_frame.grid_columnconfigure(idx, weight=1)

    def _process_action(self, action: DialogAction) -> None:
        """Set return_value and destroy."""
        if isinstance(self, ChoiceDialog) and action == DialogAction.OK:
            # Handled in subclass
            pass
        else:
            self.return_value = None if action == DialogAction.CANCEL else action
        if self._theme_helper:
            self._theme_helper.stop()
        self.destroy()


class MessageDialog(BaseDialog):
    def __init__(
        self, parent: tk.Widget, title: str, message: str, size: tuple[int, int],
        buttons: list[tuple[str, DialogAction]], primary_action: Optional[DialogAction] = None,
    ):
        self.message = message
        super().__init__(parent, title, size, buttons, primary_action)
        # Layout buttons at bottom using pack
        self.button_frame.pack(fill="x", padx=5, pady=(0, 10))

    def _build_content(self) -> None:
        ttk.Label(
            self.content_frame,
            text=self.title(),
            anchor="w",
            font=("TkDefaultFont", 20, "bold")
        ).pack(fill="x", pady=(0, 5))

        ttk.Label(
            self.content_frame,
            text=self.message,
            anchor="nw",
            wraplength=300
        ).pack(fill="x", pady=(0, 10))

    def _process_action(self, action: DialogAction) -> None:
        self.return_value = action
        super()._process_action(action)


class ChoiceDialog(BaseDialog):
    def __init__(
        self, parent: tk.Widget, title: str, message: str, choices: list[str], size: tuple[int, int], 
        buttons: list[tuple[str, DialogAction]], primary_action: Optional[DialogAction] = None,
    ):
        self.message = message
        self.choices = choices
        super().__init__(parent, title, size, buttons, primary_action)

        # Layout content_frame children with grid; layout buttons via grid
        self.content_frame.pack_forget()
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(
            row=0, column=0, sticky="nsew", padx=10,
            pady=((self._titlebar_height + 10, 10) if hasattr(self, "_titlebar_height") else 10)
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_content()
        self._create_buttons()
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 10))

    def _build_content(self) -> None:
        ttk.Label(
            self.content_frame,
            text=self.message,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")

        tree = ttk.Treeview(
            tree_frame,
            show="tree",
            selectmode="browse",
            height=8
        )
        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=tree.yview
        )

        tree.configure(yscrollcommand=scrollbar.set)
        for choice in self.choices:
            tree.insert("", "end", text=choice)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._tree = tree
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

    def _process_action(self, action: DialogAction) -> None:
        if action == DialogAction.CANCEL:
            self.return_value = None
        else:
            selected = self._tree.focus()
            self.return_value = self._tree.item(selected, "text") or None
        super()._process_action(action)

class DemoApp(BaseTkWindow):
    def __init__(self):
        super().__init__(
            app_size=(100, 100),
            theme="auto",
            logger_name="DemoApplication",
            theme_flags=["matched_frame", "matched_button"]
        )
        self.title("Dialog Demo App")
        self.geometry("400x200")

        btn_frame = ttk.Frame(self, style="MatchedBg.TFrame")
        btn_frame.pack(
            expand=True,
            pady=((self._titlebar_height, 0) if hasattr(self, "_titlebar_height") else 0)
        )

        ttk.Button(
            btn_frame,
            text="Show Message",
            command=self.show_message,
            style="MatchedBg.TButton"
        ).grid(row=0, column=0, padx=(0, 5))

        ttk.Button(
            btn_frame,
            text="Show Choice",
            command=self.show_choice,
            style="MatchedBg.TButton"
        ).grid(row=0, column=1, padx=(5, 0))

    def show_message(self):
        dlg = MessageDialog(
            self,
            title="Hello",
            message="This is a message dialog.",
            size=(400, 100),
            buttons=[("OK", DialogAction.OK)],
            primary_action=DialogAction.OK
        )
        self.wait_window(dlg)
        self.logger.info(f"MessageDialog returned: {dlg.return_value}")

    def show_choice(self):
        dlg = ChoiceDialog(
            self,
            title="Select Option",
            message="Please choose an item:",
            choices=["Alpha", "Beta", "Gamma"],
            size=(350, 300),
            buttons=[("Cancel", DialogAction.CANCEL), ("OK", DialogAction.OK)],
            primary_action=DialogAction.OK
        )
        self.wait_window(dlg)
        self.logger.info(f"ChoiceDialog returned: {dlg.return_value}")

if __name__ == '__main__':
    app = DemoApp()
    app.mainloop()
