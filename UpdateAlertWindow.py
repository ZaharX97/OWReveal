import tkinter as tk

import myglobals as g
import functions as f
import blackTkClasses as btk


class MyUpdateWindow:
    def __init__(self, root, newver, oldver):
        self.window = tk.Toplevel(root)
        self.window.transient(root)
        self.window.title("New Version Available")
        self.window.minsize(150, 80)
        self.window.resizable(False, False)
        self.window.attributes("-topmost")
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.label = btk.MyLabelStyle(self.window, "Newer version (v{}) available!\nYou have v{}".format(newver, oldver))
        self.label.frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.btn_close = btk.MyButtonStyle(self.window, "Ignore", self.window.destroy)
        self.btn_close.btn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.E + tk.W)
        self.btn_close = btk.MyButtonStyle(self.window, "Download", lambda: [f.open_link(g.PROJECT_LINK_LATEST, None, True), self.window.destroy()])
        self.btn_close.btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E + tk.W)
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (f.calc_window_pos(root, self.window)))
        self.window.grab_set()
        self.window.focus_set()
