import threading as t

import myglobals as g
import functions as f
import MainWindow as MW

if __name__ == "__main__":
    g.app = MW.MainAppWindow("Another OW Revealer 2", 805, 350)

    thread_time = t.Thread(target=lambda: f.update_time_label(g.app.label3_time), daemon=True)
    thread_time.start()

    f.import_settings()

    g.app.window.mainloop()
