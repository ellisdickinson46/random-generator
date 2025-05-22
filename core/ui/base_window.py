import os
import platform
import signal
import tkinter as tk
from tkinter import ttk
import ctypes

from core.__info__ import APP_ID, ICONS_DIR, LOG_LEVEL
from core.logger import init_logger
from core.ui.apply_theme import ThemeHelper


class BaseTkWindow(tk.Tk):
    def __init__(self, app_id=APP_ID, app_icon=None, app_size=(800, 600), app_title="App Window",
                 theme="light", topmost=False, logger_name="app", log_to_file=False):
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
        self.title(self.app_title)
        self.geometry('x'.join(str(x) for x in self.app_size))
        self.attributes('-topmost', self.topmost)
        self.resizable(False, False)
        self.bind("<Button-1>", self.clear_focus)

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
        self.theme_helper = ThemeHelper(self, self.theme, customisations=style_customisations)
        self.theme_helper.apply_theme()

    def _on_closing(self, *_):
        """Default close handler."""
        self.logger.info("Termination signal received.")
        if hasattr(self, "theme_helper"):
            self.theme_helper.stop_listener()
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
