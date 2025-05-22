import tkinter as tk
from tkinter import ttk

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
