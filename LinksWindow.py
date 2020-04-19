import tkinter as tk

import myglobals as g
import functions as f
import blackTkClasses as btk


class LinkListWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.transient(root)
        self.window.title("Past LINKs")
        self.window.minsize(150, 150)
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.label1_top = btk.MyLabelStyle(self.window, "Oldest LINK on TOP")
        self.label1_top.frame.pack()
        self.box = btk.MyListboxStyle(self.window, g.list_links)
        self.box.box.pack(fill=tk.BOTH, expand=1)
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (f.calc_window_pos(root, self.window)))
        self.window.grab_set()
        self.window.focus_set()
        self.box.box.selection_set(0)
