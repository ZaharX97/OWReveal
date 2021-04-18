import tkinter as tk

import functions as f
import blackTkClasses as btk


class MyAlertWindow:
    def __init__(self, root, message, title="error"):
        self.window = tk.Toplevel(root)
        self.window.transient(root)
        self.window.title(title)
        self.window.minsize(100, 50)
        self.window.resizable(False, False)
        self.window.attributes("-topmost")
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.label = btk.MyLabelStyle(self.window, message)
        self.label.frame.pack()
        self.btn_close = btk.MyButtonStyle(self.window, "Close", self.window.destroy)
        self.btn_close.btn.pack()
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (f.calc_window_pos(root, self.window)))
        self.window.grab_set()
        self.window.focus_set()
