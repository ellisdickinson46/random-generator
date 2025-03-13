import ctypes
import platform
import tkinter as tk
from tkinter import ttk
import webbrowser

from _helpers.custom_tk import Limiter, ReadOnlyTextWithVar
from _helpers.configuration import EditorAppSettings
from _helpers.apply_theme import apply_theme
import __versions__

lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus vehicula consequat nibh vulputate vehicula. Suspendisse condimentum volutpat consectetur. Sed consectetur magna justo, a rutrum arcu luctus vitae. Etiam maximus iaculis risus et dignissim. Sed a tortor euismod, consequat sem in, lacinia est. Pellentesque magna erat, pulvinar at diam quis, ultrices scelerisque erat. Morbi lacus purus, dapibus in tempor id, porta id dolor. Suspendisse libero diam, fringilla et nibh a, venenatis fermentum lorem. In auctor risus in est consequat, et ornare eros mattis. Vestibulum a turpis scelerisque, pretium sapien at, aliquet nisi. Donec placerat augue a vulputate aliquet. Curabitur mattis ut lectus nec viverra. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae;"

class ConfigurationUtility(tk.Tk):
    def __init__(self, config: EditorAppSettings):
        tk.Tk.__init__(self)

        # Window Properties
        self.geometry('x'.join(str(x) for x in config.app_size))
        self.title(config.app_title)
        self.resizable(0, 0)
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes,'-topmost', False)

        # Improve drawing performance when switching tabs
        self.bind('<<NotebookTabChanged>>', lambda event: self.update_idletasks())
        self.bind("<<ComboboxSelected>>",lambda e: self.focus())

        # Interface Variables
        self._slidervals = {
            "r": tk.IntVar(),
            "g": tk.IntVar(),
            "b": tk.IntVar()
        }
        self._fontselect = tk.StringVar()
        self._fontsize = tk.StringVar()
        self._soundmode = tk.StringVar()
        self._alwaysontop = tk.BooleanVar()
        self.app_icon = tk.PhotoImage(file="_configuration/icons/appicon_config.png").subsample(3,3)

        # Add callback functions to change the colour displayed in the preview frame
        # when any colour value is chnaged.
        for color in ("r", "g", "b"):
            self._slidervals[color].trace_add('write', callback=lambda *args: self.update_colpreview())

        photo = tk.PhotoImage(file='_configuration/icons/appicon_config.png')
        self.iconphoto(True, photo)

        if platform.system() == "Windows":
            myappid = 'bytefloater.rndgen.generator.4'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Apply the Sun Valley theme, and title bar colour (Windows Only)
        apply_theme(self, config.app_theme)

        self._define_interface()
        self.mainloop()

    def _change_intvar_by_amount(self, var: tk.IntVar, amount) -> None:
        if not isinstance(var, tk.IntVar):
            raise TypeError("Variable must be of type: tk.IntVar")
        new_val = int(var.get() + amount)
        if 0 <= new_val <= 255:
            var.set(new_val)

    def update_colpreview(self) -> None:
        red_value = self._slidervals["r"].get()
        green_value = self._slidervals["g"].get()
        blue_value = self._slidervals["b"].get()

        new_col = f"#{red_value:02x}{green_value:02x}{blue_value:02x}"
        self._colpreview.configure(background=new_col)

    def _define_interface(self):
        self._tab_control = ttk.Notebook(self, takefocus=0)

        self._preference_tab = ttk.Frame(self._tab_control)
        self._editor_tab = ttk.Frame(self._tab_control)
        self._save_tab = ttk.Frame(self._tab_control)
        self._about_tab = ttk.Frame(self._tab_control)

        self._tab_control.add(self._preference_tab, text="Generator Preferences")
        self._tab_control.add(self._editor_tab, text="List Editor")
        self._tab_control.add(self._save_tab, text="Save")
        self._tab_control.add(self._about_tab, text="About")
        self._tab_control.pack(expand=True, fill="both")
        self._preference_tab_ui()
        self._editor_tab_ui()
        self._save_tab_ui()
        self._about_tab_ui()

    def _about_tab_ui(self):
        project_title = getattr(__versions__, "PROJECT_TITLE", "PROJECT_TITLE")
        project_link = getattr(__versions__, "PROJECT_LINK", "")
        app_versions = getattr(__versions__, "APP_VERSIONS", {})
        
        self._about_tab_frm = ttk.Frame(self._about_tab)

        self._app_icon_lbl = tk.Label(self._about_tab_frm, image=self.app_icon)
        self._about_name = tk.Label(self._about_tab_frm, text=project_title, font=('TkDefaultFont', 25, "bold"))
        self._about_appver = tk.Label(self._about_tab_frm, text=f"Generator Version: {app_versions.get("generator", "GENERATOR_VERSION")}")
        self._about_confver = tk.Label(self._about_tab_frm, text=f"Editor Version: {app_versions.get("editor", "EDITOR_VERSION")}")
        self._github_btn = ttk.Button(self._about_tab_frm, text="View the project on GitHub", takefocus=0, command=lambda: webbrowser.open(project_link))

        self._app_icon_lbl.pack()
        self._about_name.pack()
        self._about_appver.pack()
        self._about_confver.pack()
        self._github_btn.pack(pady=(20,0))
        self._about_tab_frm.place(anchor="c", relx=.5, rely=.4)

    def _editor_tab_ui(self):
        self._controlbtn_frm = ttk.Frame(self._editor_tab)
        self._controlbtn_frm.grid(row=0, column=0, padx=10, pady=10)

        self._createlist_btn = ttk.Button(self._controlbtn_frm, text="Create New List")
        self._editlist_btn = ttk.Button(self._controlbtn_frm, text="Edit Selected List")
        self._removelist_btn = ttk.Button(self._controlbtn_frm, text="Remove Selected List")
        
        self._createlist_btn.grid(row=0, column=0, padx=5)
        self._editlist_btn.grid(row=0, column=1, padx=5)
        self._removelist_btn.grid(row=0, column=2, padx=5)

    def _save_tab_ui(self):
        self._savecontrols_frm = ttk.Frame(self._save_tab)
        self._savecontrols_frm.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self._save_config_btn = ttk.Button(self._savecontrols_frm, text="Save configuration...", style="Accent.TButton", takefocus=0, state="disabled")
        self._save_lbl = ttk.Label(self._savecontrols_frm, text="Check your configuration options before saving!")
        
        self._config_preview_frm = ttk.LabelFrame(self._save_tab, text=" Configuration Preview ")
        self._config_preview = ttk.Label(self._config_preview_frm, font='TkFixedFont', foreground='gray64', text=lorem, wraplength=700)

        self._save_config_btn.grid(row=0, column=0, padx=5)
        self._save_lbl.grid(row=0, column=1, padx=(10,0))
        self._config_preview_frm.grid(row=1, column=0, sticky="NESW", padx=5, pady=(0, 5))
        self._config_preview.grid(row=1, column=0, sticky="NESW", padx=10, pady=10)
        self._save_tab.grid_columnconfigure(0, weight=1)
        self._save_tab.grid_rowconfigure(1, weight=1)


    def _preference_tab_ui(self):
        self._preference_container = ttk.LabelFrame(self._preference_tab, text=" Preferences ")
        self._colselect_container = ttk.LabelFrame(self._preference_tab, text=" Colour Selection ")
        self._font_preview_container = ttk.LabelFrame(self._preference_tab, text=" Font Preview ")

        values = ("Fixed","Random","Off")
        self._ontop_lbl = ttk.Label(self._preference_container, text="Always on top", anchor="e")
        self._ontop_chk = ttk.Checkbutton(self._preference_container, text="", variable=self._alwaysontop)
        self._sound_lbl = ttk.Label(self._preference_container, text="Sound mode", anchor="e")
        self._sound_dropdwn = ttk.OptionMenu(self._preference_container, self._soundmode, values[0], *values)
        self._font_lbl = ttk.Label(self._preference_container, text="Font Face", anchor="e")
        self._font_dropdwn = ttk.OptionMenu(self._preference_container, self._fontselect, values[0], *values)

        self._color_lbl = ttk.Label(self._preference_container, text="Random Colours")
        self._color_frm = ttk.Frame(self._preference_container)
        self._color_list = ttk.Treeview(self._color_frm, show="tree")
        self._color_scrl = ttk.Scrollbar(self._color_frm, command=self._color_list.yview)
        self._color_list.configure(yscrollcommand=self._color_scrl.set)

        # Placeholder items for the random colours treeview (TO BE REMOVED)
        for i in range(100):
            text = f"Item #{i+1}"
            self._color_list.insert("", "end", text=text)


        self._colselect_frm = ttk.Frame(self._colselect_container)
        self._colpreview = tk.Frame(self._colselect_container, background="black", width=40, highlightbackground="black", highlightthickness=1)

        # Colour Mixer Controls
        for color in ("r", "g", "b"):
            setattr(self, f"_label_{color}", ttk.Label(
                self._colselect_frm, text=color.upper())
            )
            setattr(self, f"_slider_{color}", Limiter(
                self._colselect_frm, variable=self._slidervals[color], to=255, precision=0)
            )
            setattr(self, f"_minus_{color}", ttk.Button(
                self._colselect_frm, text="-", 
                command=lambda color=color: self._change_intvar_by_amount(self._slidervals[color], -1))
            )
            setattr(self, f"_sliderval_lbl_{color}", ttk.Label(
                self._colselect_frm, textvariable=self._slidervals[color], anchor="center")
            )
            setattr(self, f"_plus_{color}", ttk.Button(
                self._colselect_frm, text="+",
                command=lambda color=color: self._change_intvar_by_amount(self._slidervals[color], 1))
            )

        self._preference_tab_ui_grid()

    def _preference_tab_ui_grid(self):
        self._preference_tab.grid_columnconfigure(0, weight=1, uniform="column")
        self._preference_tab.grid_columnconfigure(1, weight=1, uniform="column")
        for x in range(2):
            self._preference_tab.grid_rowconfigure(x, weight=1, uniform="row")
        for x in range(2):
            self._preference_container.grid_columnconfigure(x, weight=1, uniform="column")
        for x in range (3):
            self._preference_container.grid_rowconfigure(x, minsize=35)
        self._colselect_frm.grid_columnconfigure(4, minsize=40)

        self._ontop_lbl.grid(row=0, column=0, sticky="e")
        self._sound_lbl.grid(row=1, column=0, sticky="e")
        self._font_lbl.grid(row=2, column=0, sticky="e")
        self._color_lbl.grid(row=3, column=0, sticky="ne", pady=10)

        self._ontop_chk.grid(row=0, column=1, sticky="w", padx=10, pady=2)
        self._sound_dropdwn.grid(row=1, column=1, sticky="ew", padx=10, pady=2)
        self._font_dropdwn.grid(row=2, column=1, sticky="ew", padx=10, pady=2)
        self._color_frm.grid(row=3, column=1, sticky="NEWS", padx=10, pady=2)
        self._color_list.pack(side="left", fill="both", expand=True)
        self._color_scrl.pack(side="right", fill="y")

        self._label_r.grid(row=0, column=1, sticky="ew", padx=10)
        self._label_g.grid(row=1, column=1, sticky="ew", padx=10)
        self._label_b.grid(row=2, column=1, sticky="ew", padx=10)

        self._slider_r.grid(row=0, column=2, sticky="ew", padx=5)
        self._slider_g.grid(row=1, column=2, sticky="ew", padx=5)
        self._slider_b.grid(row=2, column=2, sticky="ew", padx=5)

        self._minus_r.grid(row=0, column=3, sticky="ew")
        self._minus_g.grid(row=1, column=3, sticky="ew")
        self._minus_b.grid(row=2, column=3, sticky="ew")

        self._sliderval_lbl_r.grid(row=0, column=4, sticky="ew", padx=5)
        self._sliderval_lbl_g.grid(row=1, column=4, sticky="ew", padx=5)
        self._sliderval_lbl_b.grid(row=2, column=4, sticky="ew", padx=5)

        self._plus_r.grid(row=0, column=5, sticky="ew")
        self._plus_g.grid(row=1, column=5, sticky="ew")
        self._plus_b.grid(row=2, column=5, sticky="ew")

        self._colselect_frm.grid(row=1, column=0, sticky="NESW", padx=10, pady=5)
        self._colpreview.grid(row=0, column=0, sticky="NESW", padx=10, pady=(5,0))
        
        # Add container instances to Window UI
        self._preference_container.grid(row=0, column=0, rowspan=2, sticky="NESW", padx=5, pady=5, ipadx=50, ipady=50)
        self._colselect_container.grid(row=0, column=1, sticky="NESW", padx=5, pady=(5,2), ipadx=20, ipady=20)
        self._font_preview_container.grid(row=1, column=1, sticky="NESW", padx=5, pady=(2,5), ipadx=20, ipady=20)

        # Column configurations
        self._colselect_container.grid_columnconfigure(0, weight=1)
        self._colselect_container.grid_rowconfigure(0, weight=1)
        self._colselect_frm.grid_columnconfigure(2, weight=1)
        for x in range (3):
            self._colselect_frm.grid_rowconfigure(x, minsize=35)

    def _cleanup(self):
        pass



if __name__ == "__main__":
    APP_CONFIG = EditorAppSettings("_configuration/app_config.json")
    instance = ConfigurationUtility(APP_CONFIG)
