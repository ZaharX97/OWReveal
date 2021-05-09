import threading as t
import tkinter as tk

import myglobals as g
import functions as f
import MainWindow as MW

if __name__ == "__main__":
    g.app = MW.MainAppWindow("Another OW Revealer 2", 805, 350)

    thread_time = t.Thread(target=lambda: f.update_time_label(g.app.label3_time), daemon=True)
    thread_time.start()

    f.import_settings()

    g.app.window.iconphoto(True, tk.PhotoImage(file=fr"{g.path_resources}resources\app_icon.png"))
    g.app.window.mainloop()

# todo
# get rank mode from the demo
# new function to count stats in warmup
