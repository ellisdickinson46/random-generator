import builtins
import gettext
import os
import threading
from contextlib import contextmanager
from typing import Optional, Dict, List

from libs.polib import polib
from libs.logbook import Logger


class LocaleManager:
    """
    A manager for compiling, installing, loading, and unloading locale files dynamically.
    Uses smart compilation: only writes .mo if source .po content differs.
    Offers a logging hook to track compilation and locale switches.

    Parameters:
        domain: The gettext message domain (the base filename for your .po/.mo files, e.g., 'messages' for 'messages.po').
        localedir: Root directory containing locale subfolders (default 'locales').
        default_locale: Optional locale to load on init (e.g., 'en').
        logger: Optional Logger instance for internal logging.
    """

    def __init__(self, domain: str, logger_instance: Logger, localedir: str = 'locales', 
        default_locale: Optional[str] = None
    ):
        self.domain = domain
        self.localedir = localedir
        self.default_locale = default_locale
        self._translations: Dict[str, gettext.GNUTranslations] = {}
        self._current_locale: Optional[str] = None
        self._lock = threading.RLock()
        self.logger = logger_instance

        self.logger.debug(f"Initialized LocaleManager(domain={domain}, localedir={localedir})")

        # Ensure all .po files are compiled to .mo before use
        try:
            self.compile_all()
        except Exception as e:
            self.logger.error(f"Error compiling locales on init: {e}")

        # Install default/null translation
        self._null_trans = gettext.NullTranslations()
        self._null_trans.install()
        builtins._ = self._null_trans.gettext

        if default_locale:
            self.load_locale(default_locale)

    def compile_locale(self, locale: str) -> None:
        """
        Compile a .po file to .mo using polib, but only if the content changed.
        """
        po_path = os.path.join(self.localedir, locale, 'LC_MESSAGES', f'{self.domain}.po')
        mo_path = os.path.join(self.localedir, locale, 'LC_MESSAGES', f'{self.domain}.mo')

        if not os.path.isfile(po_path):
            self.logger.error(f"PO file not found: {po_path}")
            raise FileNotFoundError(f"PO file not found: {po_path}")

        # Parse and generate binary .mo data
        po = polib.pofile(po_path)
        mo_data = po.to_binary()

        # Skip if up-to-date
        if os.path.isfile(mo_path):
            with open(mo_path, 'rb') as existing:
                if existing.read() == mo_data:
                    self.logger.debug(f"Skipping compile for '{locale}': no changes detected.")
                    return

        # Ensure target directory
        os.makedirs(os.path.dirname(mo_path), exist_ok=True)

        # Write compiled .mo
        with open(mo_path, 'wb') as mo_file:
            mo_file.write(mo_data)
        self.logger.info(f"Compiled locale '{locale}' -> {mo_path}")

    def compile_all(self) -> None:
        """
        Compile all available locale .po files in localedir, skipping unchanged ones.
        """
        self.logger.info("Starting bulk compilation of locales...")
        for locale in self.available_locales():
            try:
                self.compile_locale(locale)
            except Exception as e:
                self.logger.error(f"Failed to compile '{locale}': {e}")
        self.logger.info("Bulk compilation complete.")

    def available_locales(self) -> List[str]:
        """
        List all locale directories under localedir.
        """
        dirs: List[str] = []
        if not os.path.isdir(self.localedir):
            self.logger.warning(f"Locale directory not found: {self.localedir}")
            return dirs
        for name in os.listdir(self.localedir):
            path = os.path.join(self.localedir, name, 'LC_MESSAGES')
            if os.path.isdir(path):
                dirs.append(name)
        self.logger.debug(f"Available locales: {dirs}")
        return dirs

    def load_locale(self, locale: str) -> None:
        """
        Load and install the specified locale. Falls back to NullTranslations if not found.
        This also updates the global '_' alias.
        """
        with self._lock:
            try:
                trans = gettext.translation(
                    domain=self.domain,
                    localedir=self.localedir,
                    languages=[locale],
                    fallback=True,
                )
                trans.install()
                builtins._ = trans.gettext
                self._translations[locale] = trans
                self._current_locale = locale
                self.logger.info(f"Loaded locale '{locale}' and assigned '_' global alias.")
            except Exception as e:
                self.logger.error(f"Could not load locale '{locale}': {e}")
                self.unload_locale()

    def unload_locale(self) -> None:
        """
        Uninstall current locale and revert to null translations.
        Updates the global '_' alias accordingly.
        """
        with self._lock:
            self._null_trans.install()
            builtins._ = self._null_trans.gettext
            old = self._current_locale
            self._current_locale = None
            self.logger.info(f"Unloaded locale '{old}', reverted '_' to default.")

    @contextmanager
    def switch_locale(self, locale: str):
        """
        Context manager to temporarily switch locale.
        Usage:
            with manager.switch_locale('es'):
                ...
        Updates and restores the global '_' alias.
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
            self.logger.debug(f"Restored locale back to '{old}' and '_' alias updated.")

    @property
    def current_locale(self) -> Optional[str]:
        """
        Return the currently active locale.
        """
        return self._current_locale


# Example Usage
# manager = LocaleManager(
#     domain='messages',
#     localedir='locales',
#     default_locale='en',
#     logger=logger
# )
# manager.compile_all()                 # Compile all .po to .mo as needed
# manager.load_locale('fr')            # Switch to French translations
# print(_('Hello'))                    # Translated output
# manager.unload_locale()              # Revert to default (NullTranslations)
# with manager.switch_locale('de'):
#     print(_('Goodbye'))              # Temporarily switch to German
