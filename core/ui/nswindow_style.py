import tkinter as tk
import uuid

def set_nswindow_style(root: tk.Tk, window_size, original_title=""):
    # Assign a unique identifier to find the window and force its creation
    unique_tag = str(uuid.uuid4())
    root.title(unique_tag)
    root.update()

    from AppKit import (
        NSApplication,
        NSWindowStyleMaskFullSizeContentView
    )
    app = NSApplication.sharedApplication()

    # Find the NSWindow by exact title‐string match
    nswin = next(
        (w for w in app.windows() if w.title() == unique_tag),
        None
    )
    if nswin is None:
        raise RuntimeError("Could not find the NSWindow instance")

    # Calculate the title bar height and store this for later use
    winFrame     = nswin.frame()                # NSRect
    contentFrame = nswin.contentView().frame()  # NSRect
    title_h      = int(winFrame.size.height - contentFrame.size.height)
    root._titlebar_height = title_h

    # Do the full-bleed magic
    nswin.setTitlebarAppearsTransparent_(True)
    mask = nswin.styleMask()
    mask |= NSWindowStyleMaskFullSizeContentView
    nswin.setStyleMask_(mask)

    # Modify the window geometry to accomodate the lack of a title bar
    root.geometry(f"{window_size[0]}x{window_size[1] + root._titlebar_height}")
    root.title(original_title)
