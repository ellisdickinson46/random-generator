import ctypes
import platform
import sys
import threading
import tkinter as tk
from tkinter import ttk

from libs import darkdetect
from libs import sv_ttk


class ThemeHelper:
    def __init__(self, root: tk.Tk, theme, customisations=()):
        self.root = root
        self.theme = theme.lower()
        self.customisations = customisations
        self.current_theme = lambda: darkdetect.theme().lower()

        self.root.lift()

    def apply_theme(self):
        if self.theme == "auto":
            self.listener = darkdetect.Listener(self._change_theme)
            self._listener_thread = threading.Thread(
                target=self.listener.listen,
                daemon=True
            )
            self._listener_thread.start()

        if isinstance(self.root, tk.Tk):
            sv_ttk.set_theme(self.current_theme(), self.root)

        self.apply_title_bar_theme()
        self._apply_customisations()

    def _apply_customisations(self):
        s = ttk.Style()
        for _, (element, options) in enumerate(self.customisations):
            s.configure(element, **options)

    def _change_theme(self, theme):
        if isinstance(self.root, tk.Tk):
            sv_ttk.set_theme(theme, self.root)
        self.apply_title_bar_theme()
        self._apply_customisations()
        self.root.update_idletasks()

    def apply_title_bar_theme(self, override_color=None):
        titlebar_colours = {
            "dark" : "#2f2f2f",
            "light": "#e7e7e7",
            "dialog_dark": "#1c1c1c",
            "dialog_light": "#fafafa"
        }

        if isinstance(self.root, tk.Tk):
            if new_col := titlebar_colours.get(self.current_theme()):
                self.root.configure(background=new_col)
        elif isinstance(self.root, tk.Toplevel):
            if new_col := titlebar_colours.get(f"dialog_{self.current_theme()}"):
                self.root.configure(background=new_col)

        if platform.system() == "Windows":
            from libs import pywinstyles

            winver = sys.getwindowsversion()
            if winver.major == 10 and winver.build >= 22000:
                # Windows 11 Method
                if override_color is not None:
                    new_col = override_color

                hwnd = ctypes.windll.user32.FindWindowW(None, self.root.title())
                pywinstyles.change_header_color(hwnd, color=new_col)
            elif winver.major == 10:
                # Windows 10 Method
                if self.theme == "dark":
                    pywinstyles.apply_style(self.root, "dark")
                else:
                    pywinstyles.apply_style(self.root, "normal")

                # A hacky way to update the title bar's color on Windows 10
                # (it doesn't update instantly like on Windows 11)
                self.root.wm_attributes("-alpha", 0.99)
                self.root.wm_attributes("-alpha", 1)



    def stop_listener(self):
        if hasattr(self, "listener"):
            self.listener.stop(0)
