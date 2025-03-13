# Random Generator
This project is a Python-based portable script for picking items from a pre-defined list of options, spinning wheel of sorts.

## Features
* Modern graphical interface design, built using `tkinter`
* A visual configuration tool to allow the easy modification of settings
* Completely portable, useful in restricted environments where command line access to `pip` isn't available
* No external dependencies.
* Expandable Multi-language localisation (currently English, Spanish, French, German)


## Local Dependencies
* `aiofiles` for asyncronous file operations
* `darkdetect` for detecting system dark mode
* `logbook` for detailed logging
* `polib` for on-the-fly compiling of localisation files
* `pywinstyles` for extended theming (Windows only)
* `sv_ttk` _(modified)_ for interface element theming