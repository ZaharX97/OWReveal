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
# count stats in warmup? why bother
# bind arrowkeys to change rounds in the program while in csgo, so you dont have to alt tab
