import tkinter as tk
from tkinter import ttk


class Limiter(ttk.Scale):
    """ ttk.Scale sublass that limits the precision of values. """

    def __init__(self, *args, **kwargs):
        self.precision = kwargs.pop('precision')  # Remove non-std kwarg.
        self.chain = kwargs.pop('command', lambda *a: None)  # Save if present.
        super(Limiter, self).__init__(*args, command=self._value_changed, **kwargs)

    def _value_changed(self, newvalue):
        newvalue = round(float(newvalue), self.precision)
        if self.precision == 0:
            newvalue = int(newvalue)
        self.winfo_toplevel().globalsetvar(self.cget('variable'), (newvalue))
        self.chain(newvalue)  # Call user specified function.


class ReadOnlyTextWithVar(tk.Frame):
    def __init__(self, parent, textvariable=None, **kwargs):
        super().__init__(parent)

        self.text_widget = tk.Text(self, **kwargs, state="disabled")
        self.text_widget.pack(expand=True, fill="both")

        self.textvariable = textvariable
        self.yview = self.text_widget.yview

        # Initialize text from textvariable
        if self.textvariable is not None:
            self.update_text_widget()
            self.textvariable.trace_add("write", lambda *_: self.update_text_widget())

    def update_text_widget(self):
        """Update the Text widget when the StringVar changes."""
        if self.textvariable is not None:
            new_text = self.textvariable.get()
            
            # Enable text widget temporarily to modify text
            self.text_widget.config(state="normal")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", new_text)
            self.text_widget.config(state="disabled")  # Re-disable input


class OptionMenuWrapper(ttk.OptionMenu):
    def __init__(self, parent, variable, values=None, default_index=0, **kwargs):
        """Wrapper for ttk.OptionMenu to allow `values` as a keyword argument."""
        values = values or []  # Ensure values is always a list
        
        if values:
            initial_value = values[default_index]
        else:
            initial_value = ""  # Use an empty string if no values are provided
        
        super().__init__(parent, variable, initial_value, *values, **kwargs)

        # If values is empty, clear the variable to avoid showing an unintended value
        if not values:
            variable.set("")


class ScrollableListbox(tk.Frame):
    def __init__(self, parent, header="", **kwargs):
        super().__init__(parent)
        kwargs.pop("show", None)
        show = "tree"
        if header:
            show = "tree headings"

        self._treeview = ttk.Treeview(self, show=show, **kwargs)
        self._scrollbar = ttk.Scrollbar(self, command=self._treeview.yview)
        self._treeview.configure(yscrollcommand=self._scrollbar.set)
        
        self._treeview.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")

        self._treeview.column("#0", width=0)
        self._treeview.heading('#0', text=header)
        # Placeholder items for the random colours treeview (TO BE REMOVED)
        for i in range(100):
            text = f"Item #{i+1}"
            self._treeview.insert("", "end", text=text)
