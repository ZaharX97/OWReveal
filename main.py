import threading as t
import tkinter as tk

import myglobals as g
import functions as f
import MainWindow as MW

if __name__ == "__main__":
    f.find_set_scaling()
    g.app = MW.MainAppWindow("Another OW Revealer 2", 805, 350)

    new_ver_thread = t.Thread(target=f.check_new_version)
    new_ver_thread.start()

    thread_time = t.Thread(target=lambda: f.update_time_label(g.app.label3_time), daemon=True)
    thread_time.start()

    f.import_settings()

    g.app.init_hotkeys()

    g.app.window.iconphoto(True, tk.PhotoImage(file=fr"{g.path_resources}resources\app_icon.png"))
    g.app.window.mainloop()

# todo
# count stats in warmup? why bother
