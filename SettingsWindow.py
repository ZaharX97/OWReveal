import os
import threading as t
import tkinter as tk
import tkinter.filedialog as tkfd
import subprocess as sp
import webbrowser as web

import myglobals as g
import functions as f
import AlertWindow as AW
import blackTkClasses as btk


class SettingsWindow:
    def _update_all_settings(self):
        self._update_buttons(self.btn_set1)
        self._update_buttons(self.btn_set2)
        self._update_buttons(self.btn_set3)
        self._update_buttons(self.btn_set5)
        self._update_buttons(self.btn_set6)
        self._update_buttons(self.btn_set7)
        if g.settings_dict["auto_dl"] and g.settings_dict["browser_dl"]:
            self._change_setting(self.btn_set2)
            self._change_setting(self.btn_set5)
        self._check_get_name(self.entry_demo)

    def _change_setting(self, button):
        if button.btn.winfo_name() == "auto_dl" and not g.settings_dict["auto_dl"] and g.settings_dict["browser_dl"]:
            self._change_setting(self.btn_set2)
        elif button.btn.winfo_name() == "browser_dl" and not g.settings_dict["browser_dl"] and g.settings_dict[
            "auto_dl"]:
            self._change_setting(self.btn_set5)
        elif button.btn.winfo_name() == "rename_dl":
            self._check_get_name(self.entry_demo)
        elif button.btn.winfo_name() == "rank_doodles":
            g.RANK_TRANSLATE = g.RANK_TRANSLATE_1 if g.settings_dict["rank_doodles"] else g.RANK_TRANSLATE_2
        g.settings_dict[button.btn.winfo_name()] = not g.settings_dict[button.btn.winfo_name()]
        self._update_buttons(button)

    def _update_buttons(self, button):
        if g.settings_dict[button.btn.winfo_name()]:
            button.text.set("ON")
            button.btn.config(relief=tk.SUNKEN, bg="#404040", activebackground="#808080")
        else:
            button.text.set("OFF")
            button.btn.config(relief=tk.RAISED, bg="#101010", activebackground="#404040")

    def _set_download_path(self):
        # global g.settings_dict
        path = tkfd.askdirectory() + "/"
        if path == "/":
            return
        self.entry_browse.text.set(path)
        g.settings_dict["dl_loc"] = path

    def _analyze_demo(self):
        # global g.settings_dict, g.thread_analyze
        path = tkfd.askopenfilename()
        if path == "":
            return
        if g.thread_download.is_alive() or g.thread_analyze.is_alive():
            AW.MyAlertWindow(g.app.window, "A demo is already being analyzed, please wait!")
            return
        g.app.update_stats()
        g.thread_analyze = t.Thread(target=lambda: f.analyze_demo(path, g.app.btn3_download), daemon=True)
        g.thread_analyze.start()
        self._destroy_checkname()

    def _check_get_name(self, button):
        # global g.settings_dict
        name = ""
        list1 = "\n\"*/:<>?\\|"
        for letter in button.text.get():
            if list1.find(letter) == -1:
                if len(name) and letter == " " and name[-1] == " ":
                    continue
                name += letter
        name = name.replace(" ", "_")
        if name == "":
            name = "OW_replay"
        if len(name) > 45:
            name = name[:45]
        button.text.set(name)
        g.settings_dict["rename"] = name

    def _update_on_save(self):
        # global g.settings_dict
        self._check_get_name(self.entry_demo)
        f.save_settings()

    def _destroy_checkname(self):
        self._check_get_name(self.entry_demo)
        self.window.destroy()

    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.transient(root)
        self.window.title("Settings")
        self.window.minsize(580, 375)
        sizex = self.window.minsize()[0]
        # sizey = self.window.minsize()[1]
        self.window.resizable(False, False)
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self._destroy_checkname)

        self.label_set1 = btk.MyLabelStyle(self.window, "Stop scanning after a DEMO LINK is found")
        self.label_set1.frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set1 = btk.MyButtonStyle(self.window, "OFF", lambda: self._change_setting(self.btn_set1), "stop_label")
        self.btn_set1.btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.label_set5 = btk.MyLabelStyle(self.window, "Auto download DEMO after a LINK is found")
        self.label_set5.frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set5 = btk.MyButtonStyle(self.window, "ON", lambda: self._change_setting(self.btn_set5), "auto_dl")
        self.btn_set5.btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.label_set2 = btk.MyLabelStyle(self.window, "Use the browser to download (doesn't work with auto download)")
        self.label_set2.frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set2 = btk.MyButtonStyle(self.window, "OFF", lambda: self._change_setting(self.btn_set2), "browser_dl")
        self.btn_set2.btn.grid(row=2, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.label_set3 = btk.MyLabelStyle(self.window,
                                           "*" * 50 + "Download location when not using the browser" + "*" * 50)
        self.label_set3.frame.config(width=45)
        self.label_set3.frame.grid(row=3, column=0, sticky=tk.W + tk.E, pady=5, columnspan=4)
        self.btn_browse = btk.MyButtonStyle(self.window, "Browse", self._set_download_path)
        self.btn_browse.btn.grid(row=4, column=0, sticky=tk.W + tk.E, padx=5)
        self.entry_browse = btk.MyEntryStyle(self.window, g.settings_dict["dl_loc"])
        self.entry_browse.frame.grid(row=4, column=1, sticky=tk.W + tk.E, padx=5, columnspan=2)
        self.btn_opendl = btk.MyButtonStyle(self.window, "Open",
                                            lambda: os.system("start {}".format(g.settings_dict["dl_loc"])))
        self.btn_opendl.btn.grid(row=4, column=3, sticky=tk.E, padx=5, pady=5)
        self.label_set3_1 = btk.MyLabelStyle(self.window, "*" * 200)
        self.label_set3_1.frame.config(width=45)
        self.label_set3_1.frame.grid(row=5, column=0, sticky=tk.W + tk.E, columnspan=4)

        self.label_set4 = btk.MyLabelStyle(self.window, "Rename downloaded demos to ")
        self.label_set4.frame.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        self.btn_set3 = btk.MyButtonStyle(self.window, "ON", lambda: self._change_setting(self.btn_set3), "rename_dl")
        self.btn_set3.btn.grid(row=6, column=0, sticky=tk.W + tk.E, padx=5, pady=5)
        self.entry_demo = btk.MyEntryStyle(self.window, g.settings_dict["rename"])
        self.entry_demo.frame.config(state="normal")
        self.entry_demo.frame.grid(row=6, column=2, sticky=tk.W + tk.E, padx=5, columnspan=2)

        self.label_set6 = btk.MyLabelStyle(self.window, "Auto delete DEMO after it is analyzed")
        self.label_set6.frame.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set6 = btk.MyButtonStyle(self.window, "ON", lambda: self._change_setting(self.btn_set6),
                                          "delete_after")
        self.btn_set6.btn.grid(row=7, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.label_set7 = btk.MyLabelStyle(self.window, "Rank doodles")
        self.label_set7.frame.grid(row=8, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set7 = btk.MyButtonStyle(self.window, "OFF", lambda: self._change_setting(self.btn_set7),
                                          "rank_doodles")
        self.btn_set7.btn.grid(row=8, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.btn_save = btk.MyButtonStyle(self.window, "Save to file", self._update_on_save)
        self.btn_save.btn.grid(row=9, column=3, sticky=tk.E, padx=5, pady=5)

        self.btn_analyze = btk.MyButtonStyle(self.window, "Analyze a demo", self._analyze_demo)
        self.btn_analyze.btn.grid(row=9, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        def lc_event1(event):
            if g.browser_path is None:
                web.open_new_tab(g.PROJECT_LINK)
            else:
                sp.Popen(g.browser_path + " " + g.PROJECT_LINK)

        self.label_github = btk.MyLabelStyle(self.window, "v{}   {}".format(g.VERSION, g.PROJECT_LINK))
        self.label_github.frame.config(cursor="hand2")
        self.label_github.frame.grid(row=9, column=1, padx=5, pady=5, columnspan=2)
        self.label_github.frame.bind("<Button-1>", lc_event1)

        self._update_all_settings()
        self.window.grid_columnconfigure(0, minsize=0.15 * sizex, weight=1)
        self.window.grid_columnconfigure(1, minsize=0.5 * sizex, weight=1)
        self.window.grid_columnconfigure(2, minsize=0.15 * sizex, weight=1)
        self.window.grid_columnconfigure(3, minsize=0.2 * sizex, weight=1)
        self.window.grid_propagate(False)
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (f.calc_window_pos(root, self.window)))
        self.window.grab_set()
        self.window.focus_set()
