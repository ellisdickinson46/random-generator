import json
import tkinter as tk

class DictVar(tk.Variable):
    def __init__(self, master=None, value=None, name=None):
        super().__init__(master, name)
        if value is None:
            value = {}
        self.set(value)

    def get(self):
        value = super().get()
        if isinstance(value, str):
            if not value.strip():
                return {}
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {}
        return value

    def set(self, value):
        if isinstance(value, dict):
            value = json.dumps(value)
        super().set(value)

    def find(self, keys, default=None):
        """
        Find a value using a string (for flat keys) or a tuple (for nested keys).
        Example:
            find("theme") --> Flat key lookup
            find(("user", "details", "age")) --> Nested key lookup
        """
        current = self.get()

        # Handle single string key lookup
        if isinstance(keys, str):
            return current.get(keys, default)

        # Handle tuple for nested key lookup
        elif isinstance(keys, tuple):
            try:
                for key in keys:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return default
                return current
            except (KeyError, TypeError):
                return default

        else:
            raise TypeError("Keys must be a string or a tuple of strings")

    # ---- New methods for handling nested keys ----

    def get_nested(self, keys, default=None):
        """
        Get a value from nested dictionary keys.
        keys: Tuple of keys representing the path.
        """
        current = self.get()
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

    def set_nested(self, keys, value):
        """
        Set a value in a nested dictionary structure.
        keys: Tuple of keys representing the path.
        """
        if not keys:
            raise ValueError("Keys cannot be empty")

        current = self.get()
        target = current
        for key in keys[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]

        target[keys[-1]] = value
        self.set(current)

    def remove_nested(self, keys):
        """
        Remove a value from nested dictionary keys.
        keys: Tuple of keys representing the path.
        """
        if not keys:
            raise ValueError("Keys cannot be empty")

        current = self.get()
        target = current
        for key in keys[:-1]:
            if key in target and isinstance(target[key], dict):
                target = target[key]
            else:
                return

        if keys[-1] in target:
            del target[keys[-1]]
            self.set(current)

    def pop_nested(self, keys, default=None):
        """
        Pop a value from nested dictionary keys.
        keys: Tuple of keys representing the path.
        """
        if not keys:
            raise ValueError("Keys cannot be empty")

        current = self.get()
        target = current
        for key in keys[:-1]:
            if key in target and isinstance(target[key], dict):
                target = target[key]
            else:
                return default

        value = target.pop(keys[-1], default)
        self.set(current)
        return value

    # ---- Existing methods for flat dictionaries ----

    def update(self, key, value):
        current = self.get()
        current[key] = value
        self.set(current)

    def remove(self, key):
        current = self.get()
        if key in current:
            del current[key]
            self.set(current)

    def clear(self):
        self.set({})

    def pop(self, key, default=None):
        current = self.get()
        value = current.pop(key, default)
        self.set(current)
        return value

    def keys(self):
        return list(self.get().keys())

    def values(self):
        return list(self.get().values())

    def items(self):
        return list(self.get().items())

    def __repr__(self):
        return repr(self.get())