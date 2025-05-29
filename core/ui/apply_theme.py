import ctypes
import platform
import sys
import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional

from libs import darkdetect
from libs import sv_ttk
from libs.logbook import Logger

TITLEBAR_COLORS = {
    "dark" : "#2f2f2f",
    "light": "#e7e7e7",
    "dialog_dark": "#1c1c1c",
    "dialog_light": "#fafafa"
}
THEME_CHANGED_EVENT = "<<ThemeChanged>>"

class ThemeHelper:
    def __init__(
            self, root: tk.Tk, mode, custom_styles=(), flags=None, logger: Logger = None
        ):
        self.root = root
        self.logger = logger
        self.flags = flags or []
        self.mode = mode.lower()
        self.custom_styles = custom_styles
        self.root.lift()

    def start(self):
        if self.mode == "auto":
            self.listener = darkdetect.Listener(self._change_theme)
            self._listener_thread = threading.Thread(
                target=self.listener.listen,
                daemon=True
            )
            self._listener_thread.start()

        if isinstance(self.root, tk.Tk):
            sv_ttk.set_theme(self._get_current_theme(), self.root)

        if 'disable_auto_titlebar' not in self.flags:
            self._apply_titlebar()
        self._apply_custom_styles()
        self._apply_matched_styles()
        self.root.event_generate(THEME_CHANGED_EVENT, when="tail")

    def _get_current_theme(self) -> str:
        """
        Return the current theme: auto-detected or forced.
        """
        if self.mode == "auto":
            return darkdetect.theme().lower()
        return self.mode

    def _get_window_bg_color(self) -> Optional[str]:
        """
        Get the current background color of the window.
        """
        try:
            return self.root.cget("background")
        except tk.TclError:
            self.logger.warning(
                "Could not retrieve window background color"
            )
            return None

    def _apply_custom_styles(self):
        s = ttk.Style()
        for _, (element, options) in enumerate(self.custom_styles):
            s.configure(element, **options)

    def _apply_matched_styles(self) -> None:
        """
        Configure MatchedBg.TButton and MatchedBg.TFrame styles
        to match the window background, based on flags.
        """
        bg_color = self._get_window_bg_color()
        if not bg_color:
            return

        style = ttk.Style()
        if "matched_button" in self.flags:
            style.configure(
                "MatchedBg.TButton", background=bg_color
            )
            self.logger.debug(
                f"MatchedBg.TButton bg set to {bg_color}"
            )
        if "matched_frame" in self.flags:
            style.configure(
                "MatchedBg.TFrame", background=bg_color
            )
            self.logger.debug(
                f"MatchedBg.TFrame bg set to {bg_color}"
            )

    def _change_theme(self, theme):
        if isinstance(self.root, tk.Tk):
            sv_ttk.set_theme(theme, self.root)
        if 'disable_auto_titlebar' not in self.flags:
            self._apply_titlebar()
        self._apply_custom_styles()
        self._apply_matched_styles()
        self.root.event_generate(THEME_CHANGED_EVENT, when="tail")
        self.root.update_idletasks()

    def _apply_titlebar(self, override_color=None):
        theme = self._get_current_theme()
        prefix = (
            "dialog_" if isinstance(self.root, tk.Toplevel) else ""
        )
        key = f"{prefix}{theme}"
        bg_color = override_color or TITLEBAR_COLORS.get(key)
        
        try:
            self.root.configure(background=bg_color)
        except tk.TclError:
            self.logger.warning(
                "Could not set window background color"
            )

        if platform.system() == "Windows":
            from libs import pywinstyles

            winver = sys.getwindowsversion()
            if winver.major == 10 and winver.build >= 22000:
                # Windows 11 Method
                hwnd = ctypes.windll.user32.FindWindowW(None, self.root.title())
                pywinstyles.change_header_color(hwnd, color=bg_color)
            elif winver.major == 10:
                # Windows 10 Method
                if self.mode == "dark":
                    pywinstyles.apply_style(self.root, "dark")
                else:
                    pywinstyles.apply_style(self.root, "normal")

                # A hacky way to update the title bar's color on Windows 10
                # (it doesn't update instantly like on Windows 11)
                self.root.wm_attributes("-alpha", 0.99)
                self.root.wm_attributes("-alpha", 1)

    def stop(self):
        if hasattr(self, "listener"):
            self.listener.stop(0)
