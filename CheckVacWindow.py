import tkinter as tk

import myglobals as g
import functions as f
import blackTkClasses as btk


class MyVacWindow:
    def checkk(self, root, count):
        delay = self.entry_speed.text.get()
        try:
            delay = int(delay)
        except ValueError:
            delay = 1000
        g.settings_dict["vac_delay"] = delay
        delay = round(delay / 1000, 3)
        f.check_vac(root, delay, count)

    def __init__(self, root):
        self.window = tk.Toplevel(root.window)
        self.window.transient(root.window)
        self.window.title("Check Vac")
        self.window.minsize(150, 80)
        self.window.resizable(False, False)
        self.window.attributes("-topmost")
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.label = btk.MyLabelStyle(self.window, "What to check?")
        self.label.frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.btn_30 = btk.MyButtonStyle(self.window, "Last 30 players", lambda: self.checkk(root, 30))
        self.btn_30.btn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.E + tk.W)
        self.btn_all = btk.MyButtonStyle(self.window, "Check all", lambda: self.checkk(root, 0))
        self.btn_all.btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E + tk.W)
        self.label2 = btk.MyLabelStyle(self.window, "Delay in ms:")
        self.label2.frame.grid(row=2, column=0, padx=5, pady=5)
        self.entry_speed = btk.MyEntryStyle(self.window, str(g.settings_dict["vac_delay"]))
        self.entry_speed.frame.config(state="normal")
        self.entry_speed.frame.grid(row=2, column=1, sticky=tk.W + tk.E, padx=5)
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (f.calc_window_pos(root.window, self.window)))
        self.window.grab_set()
        self.window.focus_set()
