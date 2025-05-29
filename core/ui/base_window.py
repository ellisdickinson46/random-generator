import ctypes
import builtins
import os
import platform
import signal
import tkinter as tk
from tkinter import ttk

from core.__info__ import APP_ID, ICONS_DIR, LOG_LEVEL
from core.logger import init_logger
from core.ui.apply_theme import ThemeHelper
from core.ui.nswindow_style import set_nswindow_style


class BaseTkWindow(tk.Tk):
    @property
    def _(self):
        # Return call to whatever builtins._ is currently bound to
        return builtins._

    def __init__(self, app_id=APP_ID, app_icon=None, app_size=(800, 600), app_title="App Window",
                 theme="light", topmost=False, logger_name="app", log_to_file=False, theme_flags=None):
        super().__init__()

        # Define logger instance
        self.logger = init_logger(logger_name, LOG_LEVEL, log_to_file)
        self.logger.info(f"Launching {logger_name}...")

        # Core configuration
        self.app_id = app_id
        self.theme = theme
        self.app_size = app_size
        self.app_title = app_title
        self.topmost = topmost
        self.theme_flags = theme_flags
        self.style = ttk.Style()

        # Set Window Icon
        if app_icon:
            self._set_icon(app_icon)

        # Set properties
        self._configure_window()
        self._apply_theme()

        # Set window protocols
        self.protocol('WM_DELETE_WINDOW', self._on_closing)
        signal.signal(signal.SIGINT, self._on_closing)

    def _configure_window(self):
        """Apply common Tk window properties."""
        self.logger.debug("Setting window properties...")
        self.geometry('x'.join(str(x) for x in self.app_size))
        self.title(self.app_title)
        self.attributes('-topmost', self.topmost)
        self.resizable(False, False)
        self.bind("<Button-1>", self.clear_focus)

        if platform.system() == "Darwin":
            self.attributes("-alpha", 0.0)
            try:
                set_nswindow_style(self, self.app_size, self.app_title)
            except (RuntimeError, ImportError):
                self.logger.exception("Unable to set NSWindow properties")
            self.attributes("-alpha", 1.0)

        # Define the App ID for the Windows Shell Environment
        # (This allows the display of app icons in the taskbar and window grouping across scripts)
        if platform.system() == "Windows" and self.app_id:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.app_id)

    def _set_icon(self, icon_file):
        """Set the application icon if the image is available and supported."""
        try:
            tk_version = tuple(int(part) for part in str(tk.TkVersion).split('.'))
            if tk_version >= (8, 6):
                icon_path = os.path.join(ICONS_DIR, icon_file)
                self.app_icon = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, self.app_icon)
                self.logger.debug(f"Loaded app icon: {icon_path}")
        except Exception as e:
            self.logger.warning(f"Failed to load icon: {e}")

    def _apply_theme(self):
        """Apply a consistent theme across platforms."""
        style_customisations = [('Treeview', {"rowheight": 25})]
        self.theme_helper = ThemeHelper(
            self, self.theme,
            custom_styles=style_customisations,
            flags=self.theme_flags,
            logger=self.logger
        )
        self.theme_helper.start()

    def _on_closing(self, *_):
        """Default close handler."""
        self.logger.info("Termination signal received.")
        if hasattr(self, "theme_helper"):
            self.theme_helper.stop()
        self.logger.info("Exiting...")
        self.destroy()

    def clear_focus(self, event):
        ttk_focusable_widgets = (ttk.Entry, ttk.Button, ttk.Combobox, ttk.Spinbox, ttk.Scale)
        tk_focusable_classes = ['Entry', 'Button', 'Text', 'Scale', 'Spinbox']

        # Check if the clicked widget is focusable
        if (
            isinstance(event.widget, ttk_focusable_widgets) or 
            event.widget.winfo_class() in tk_focusable_classes
        ):
            # Let the widget keep focus
            return  
        self.focus_set()
