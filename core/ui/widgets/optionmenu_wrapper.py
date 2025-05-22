from tkinter import ttk

class OptionMenuWrapper(ttk.OptionMenu):
    def __init__(self, parent, variable, values=None, default_index=0, **kwargs):
        self._variable = variable
        self._value_map = {}  # Renamed to avoid conflict with internal OptionMenu attributes

        if isinstance(values, dict):
            self._value_map = values
            display_values = list(values.keys())
        elif isinstance(values, list):
            self._value_map = {value: value for value in values}
            display_values = values
        else:
            display_values = []

        if display_values:
            initial_value = display_values[default_index]
        else:
            initial_value = ""

        # Extract the state if provided
        state = kwargs.pop('state', 'normal')

        # Remove any keys from kwargs that are not supported by ttk.OptionMenu
        kwargs = {k: v for k, v in kwargs.items() if k not in ['options']}

        # Initialize OptionMenu correctly
        super().__init__(parent, variable, initial_value, *display_values or [""], **kwargs)

        # Set the initial value in the variable
        if display_values:
            variable.set(initial_value)
        else:
            variable.set("")

        # Set the state if provided
        self.configure(state=state)

    def get_backend_value(self):
        """
        Get the backend value corresponding to the selected display value.
        """
        selected_display_value = self._variable.get()
        return self._value_map.get(selected_display_value, None)

    def set_backend_value(self, backend_value):
        """
        Set the display value based on the backend value.
        """
        for display_value, value in self._value_map.items():
            if value == backend_value:
                self._variable.set(display_value)
                break