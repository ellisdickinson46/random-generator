import tkinter as tk

class ListVar(tk.Variable):
    def __init__(self, master=None, value=None, name=None):
        super().__init__(master, name)
        if value is None:
            value = []
        self.set(value)
    
    def get(self):
        # Convert stored string to list
        value = super().get()
        if isinstance(value, str):
            # Handle the special case for an empty string
            if value == '':
                return []
            return value.split(' ')
        return value
    
    def set(self, value):
        if isinstance(value, list):
            if not value:
                # Store an empty string for an empty list
                value = ''
            else:
                # Use list comprehension for better clarity
                value = ' '.join([str(item) for item in value])
        super().set(value)
    
    def append(self, item):
        current = self.get()
        current.append(item)
        self.set(current)
    
    def remove(self, item):
        current = self.get()
        if item in current:
            current.remove(item)
            self.set(current)
    
    def clear(self):
        self.set([])
    
    def pop(self, index=-1):
        current = self.get()
        if current:
            item = current.pop(index)
            self.set(current)
            return item
    
    def __repr__(self):
        return repr(self.get())
