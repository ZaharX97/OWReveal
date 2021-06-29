import tkinter as tk

import functions as f
import blackTkClasses as btk


class MyWlextraWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root.window)
        self.window.transient(root.window)
        self.window.title("Extra Stuff")
        # self.window.minsize(100, 50)
        self.window.resizable(False, False)
        self.window.attributes("-topmost")
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.btn_close = btk.MyButtonStyle(self.window, "More Stats", lambda: [root._open_more_stats(), self.window.destroy()])
        self.btn_close.btn.pack(padx=5, pady=5)
        self.btn_close = btk.MyButtonStyle(self.window, "Export WL (CSV)", lambda: [root.close_and_update(), f.export_wl_csv(self.window), self.window.destroy()])
        self.btn_close.btn.pack(padx=5, pady=5)
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (f.calc_window_pos(root.window, self.window)))
        self.window.grab_set()
        self.window.focus_set()
