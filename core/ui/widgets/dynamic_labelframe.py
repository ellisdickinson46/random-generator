from tkinter import ttk

class DynamicLabelframe(ttk.Labelframe):
    def __init__(self, master=None, **kwargs):
        # Pop off static text and/or textvariable
        text = kwargs.pop('text', '')
        textvar = kwargs.pop('textvariable', None)

        # Initialize as usual, with any other Labelframe options
        super().__init__(master, text=text, **kwargs)

        # If they passed a variable-like for the label…
        self._textvar = None
        if textvar is not None:
            # Real tk Variable? wire up trace
            if hasattr(textvar, 'trace_add'):
                self._textvar = textvar
                def _on_var_change(*_, var=textvar, widget=self):
                    widget.configure(text=var.get())
                textvar.trace_add('write', _on_var_change)
                # keep the callback ref so we can remove it later
                self._textvar_callback = _on_var_change
                # initialize label to current value
                self.configure(text=textvar.get())
            else:
                # Not a Variable—treat it as static text
                self.configure(text=str(textvar))

    def destroy(self):
        # Clean up the trace if we set one
        if self._textvar is not None:
            try:
                self._textvar.trace_remove('write', self._textvar_callback)
            except Exception:
                pass
        super().destroy()
