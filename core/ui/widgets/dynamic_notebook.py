from tkinter import ttk

class DynamicNotebook(ttk.Notebook):
    # Alias all inherited Notebook methods
    hide = ttk.Notebook.hide
    index = ttk.Notebook.index
    insert = ttk.Notebook.insert
    select = ttk.Notebook.select
    tab = ttk.Notebook.tab
    tabs = ttk.Notebook.tabs
    enable_traversal = ttk.Notebook.enable_traversal

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._tab_textvars = {}

    def add(self, child, **kw):
        """
        notebook.add(child,
                     text="Static Title",
                     textvariable=StringVar(...) OR any tk.Variable,
                     **other_kwargs)
        """
        # Pull out both text and textvariable if provided
        text = kw.pop('text', '')
        textvar = kw.pop('textvariable', None)

        # First, add the tab with whichever static text we have
        super().add(child, text=text, **kw)

        # If they passed something for textvariable...
        if textvar is not None:
            # If it looks like a Tk Variable, wire up the trace
            if hasattr(textvar, 'trace_add'):
                def _on_var_change(*_, child=child, var=textvar):
                    self.tab(child, text=var.get())

                # Store to allow cleanup
                self._tab_textvars[child] = (textvar, _on_var_change)
                textvar.trace_add('write', _on_var_change)

                # Initialize to current value
                self.tab(child, text=textvar.get())

            else:
                # Not a Variable: treat it as static text
                # (this covers if someone mistakenly passed a str)
                self.tab(child, text=str(textvar))

    def forget(self, tab_id):
        """Remove the tab and clean up any StringVar traces."""
        # Resolve the child widget
        if isinstance(tab_id, int):
            child = self.tabs()[tab_id]
        else:
            child = tab_id

        # If we set up a trace on it, remove that now
        if child in self._tab_textvars:
            var, callback = self._tab_textvars.pop(child)
            try:
                var.trace_remove('write', callback)
            except Exception:
                pass

        super().forget(tab_id)
