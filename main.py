# main.py
# Entry point — creates the window and starts the event loop.

import tkinter as tk
from tkinter import ttk
from gui import OrganizerApp


def main():
    root = tk.Tk()
    # Use the 'vista' theme for a native Windows look (falls back gracefully).
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    OrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()