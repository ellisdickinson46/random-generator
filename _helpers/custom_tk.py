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
        kwargs.pop("state", None) # Prevent double calling of state in Text Widget
        self.textvariable = textvariable

        self.text_widget = tk.Text(self, **kwargs, state="disabled")
        self.scrollbar = ttk.Scrollbar(self, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)

        self.text_widget.grid(row=0, column=0, sticky="nesw")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

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

        self.treeview = ttk.Treeview(self, show=show, **kwargs)
        self.scrollbar = ttk.Scrollbar(self, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)

        self.treeview.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.treeview.column("#0", width=0)
        self.treeview.heading('#0', text=header)
    
    def add_item(self, item):
        if item:
            # Get all existing items in the treeview
            existing_items = [self.treeview.item(child, 'text') for child in self.treeview.get_children()]
            
            if item not in existing_items:
                # Capture the ID of the newly inserted item
                new_item_id = self.treeview.insert("", "end", text=item)
                
                # Select the newly inserted item
                self.treeview.selection_set(new_item_id)
                self.treeview.focus(new_item_id)  # Optional: Set focus to the new item
                self.treeview.yview_moveto(1.0)
            else:
                print(f"Item '{item}' already exists.")

    def rem_item(self):
        selection = self.treeview.selection()
        for item in selection:
            self.treeview.delete(item)
    
    def add_sample_items(self):
        for i in range(100):
            text = f"Item #{i + 1}"
            self.treeview.insert("", "end", text=text)
