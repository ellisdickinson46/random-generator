import builtins
import gettext
import os
import threading
import tkinter as tk
from contextlib import contextmanager
from typing import Optional, Dict, List

from libs.polib import polib
from libs.logbook import Logger


class LocaleManager:
    """
    A manager for compiling, installing, loading, and unloading locale files dynamically,
    with support for Tkinter UI bindings via tk.StringVar.

    Parameters:
        domain: The gettext message domain (e.g., 'messages' for 'messages.po').
        localedir: Directory containing locale subfolders (default 'locales').
        default_locale: Optional locale to load on init (e.g., 'en').
        logger: Logger instance for internal logging.
    """

    def __init__(self,
                 domain: str,
                 logger_instance: Logger,
                 localedir: str = 'locales',
                 default_locale: Optional[str] = None):
        self.domain = domain
        self.localedir = localedir
        self.default_locale = default_locale
        self.logger = logger_instance

        self._translations: Dict[str, gettext.GNUTranslations] = {}
        self._current_locale: Optional[str] = None
        self._lock = threading.RLock()

        # UI-bound StringVars: key -> tk.StringVar
        self._ui_vars: Dict[str, tk.StringVar] = {}

        self.logger.debug(f"Initialized LocaleManager(domain={domain}, localedir={localedir})")

        # Compile all .po -> .mo on startup
        try:
            self.compile_all()
        except Exception as e:
            self.logger.error(f"Error compiling locales on init: {e}")

        # Null translation fallback
        self._null_trans = gettext.NullTranslations()
        self._null_trans.install()
        builtins._ = self._null_trans.gettext

        # Load default if provided
        if default_locale:
            self.load_locale(default_locale)

    def compile_locale(self, locale: str) -> None:
        po_path = os.path.join(self.localedir, locale, 'LC_MESSAGES', f'{self.domain}.po')
        mo_path = os.path.join(self.localedir, locale, 'LC_MESSAGES', f'{self.domain}.mo')

        if not os.path.isfile(po_path):
            self.logger.error(f"PO file not found: {po_path}")
            raise FileNotFoundError(f"PO file not found: {po_path}")

        po = polib.pofile(po_path)
        mo_data = po.to_binary()

        # Skip unchanged
        if os.path.isfile(mo_path):
            with open(mo_path, 'rb') as f:
                if f.read() == mo_data:
                    self.logger.debug(f"Skipping compile for '{locale}': no changes detected.")
                    return

        os.makedirs(os.path.dirname(mo_path), exist_ok=True)
        with open(mo_path, 'wb') as f:
            f.write(mo_data)
        self.logger.info(f"Compiled locale '{locale}' -> {mo_path}")

    def compile_all(self) -> None:
        self.logger.info("Starting bulk compilation of locales...")
        for loc in self.available_locales():
            try:
                self.compile_locale(loc)
            except Exception as e:
                self.logger.error(f"Failed to compile '{loc}': {e}")
        self.logger.info("Bulk compilation complete.")

    def available_locales(self) -> List[str]:
        dirs: List[str] = []
        if not os.path.isdir(self.localedir):
            self.logger.warning(f"Locale directory not found: {self.localedir}")
            return dirs
        for name in os.listdir(self.localedir):
            if os.path.isdir(os.path.join(self.localedir, name, 'LC_MESSAGES')):
                dirs.append(name)
        self.logger.debug(f"Available locales: {dirs}")
        return dirs

    def load_locale(self, locale: str) -> None:
        """
        Load and install the specified locale, updating all UI StringVars.
        """
        with self._lock:
            try:
                trans = gettext.translation(
                    domain=self.domain,
                    localedir=self.localedir,
                    languages=[locale],
                    fallback=True
                )
                trans.install()
                builtins._ = trans.gettext
                self._translations[locale] = trans
                self._current_locale = locale
                self.logger.info(f"Loaded locale '{locale}' and installed translations.")

                # Update all registered UI variables
                for key, sv in self._ui_vars.items():
                    sv.set(builtins._(key))
            except Exception as e:
                self.logger.error(f"Could not load locale '{locale}': {e}")
                self.unload_locale()

    def unload_locale(self) -> None:
        """
        Revert to null translations and update UI variables.
        """
        with self._lock:
            self._null_trans.install()
            builtins._ = self._null_trans.gettext
            old = self._current_locale
            self._current_locale = None
            self.logger.info(f"Unloaded locale '{old}', reverted to default.")

            # Refresh UI
            for key, sv in self._ui_vars.items():
                sv.set(builtins._(key))

    @contextmanager
    def switch_locale(self, locale: str):
        """
        Temporarily switch locale within context, restoring afterward.
        """
        old = self._current_locale
        self.logger.debug(f"Switching locale from '{old}' to '{locale}'")
        self.load_locale(locale)
        try:
            yield
        finally:
            if old:
                self.load_locale(old)
            else:
                self.unload_locale()
            self.logger.debug(f"Restored locale back to '{old}'")

    def register_ui(self, key: str) -> tk.StringVar:
        """
        Create or retrieve a tk.StringVar bound to a translation key.
        The variable updates automatically on locale changes.
        """
        if key in self._ui_vars:
            return self._ui_vars[key]
        sv = tk.StringVar()
        sv.set(builtins._(key))
        self._ui_vars[key] = sv
        return sv

    @property
    def current_locale(self) -> Optional[str]:
        return self._current_locale


# Example UI integration
if __name__ == '__main__':
    root = tk.Tk()
    logger = Logger()
    lm = LocaleManager(domain='messages', logger_instance=logger, default_locale='en')

    # UI elements
    hello_var = lm.register_ui('Hello, world!')
    label = tk.Label(root, textvariable=hello_var)
    label.pack(pady=10)

    def switch_to_es():
        lm.set_locale('es')  # alias to load_locale

    btn = tk.Button(root, text='Switch to Español', command=lambda: lm.load_locale('es'))
    btn.pack(pady=10)

    root.mainloop()
