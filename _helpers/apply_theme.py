import platform
import sys

from _helpers import sv_ttk

def apply_theme(root, theme):
    root.lift()
    theme = theme.lower()

    # Apply the Sun Valley theme
    sv_ttk.set_theme(theme)

    apply_title_bar_theme(root.frame(), theme)

def apply_title_bar_theme(root, theme, override_color=None):
    theme = theme.lower()
    if platform.system() == "Windows":
        from _helpers import pywinstyles

        winver = sys.getwindowsversion()
        titlebar_colours = {
            "dark" : "#2f2f2f",
            "light": "#e7e7e7",
            "dialog_dark": "#1c1c1c",
            "dialog_light": "#fafafa"
        }

        if winver.major == 10 and winver.build >= 22000:
            # Windows 11 Method
            if override_color is not None:
                new_col = override_color
            else:
                new_col = titlebar_colours.get(theme, "white")
            pywinstyles.change_header_color(root, color=new_col)

            # print(root)
            # print(new_col)
        elif winver.major == 10:
            # Windows 10 Method
            match theme:
                case "dark":
                    pywinstyles.apply_style(root, "dark")
                case _:
                    pywinstyles.apply_style(root, "normal")

            # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
            root.wm_attributes("-alpha", 0.99)
            root.wm_attributes("-alpha", 1)
