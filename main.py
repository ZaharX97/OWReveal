import threading as t

import myglobals as g
import functions as f
import MainWindow as MW

if __name__ == "__main__":
    g.app = MW.MainAppWindow("Another OW Revealer 2", 760, 350)
    thread_time = t.Thread(target=lambda: f.update_time_label(g.app.label3_time), daemon=True)
    thread_time.start()
    g.browser_path = f.find_browser_path()
    g.exec_path = f.find_file_path(True)
    f.import_settings()
    if not len(g.settings_dict["dl_loc"]):
        g.settings_dict["dl_loc"] = f.find_file_path()

    g.app.window.mainloop()
