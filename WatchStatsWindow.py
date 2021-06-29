import tkinter as tk
import math

import myglobals as g
import functions as f
import WatchPlayer as WP
import AlertWindow as AW
import blackTkClasses as btk
import csvReader as mycsv


class WatchStatsWindow:
    def _switch_stats(self):
        if self._all_stats:
            self._show_stats(self.nrbanned, True)
            self._all_stats = False
            self.btn1.text.set("Show all players")
        else:
            self._show_stats(self.nrall)
            self._all_stats = True
            self.btn1.text.set("Show only banned players")
        # self._scroll_func(tk.SCROLL, -120, tk.UNITS)

    def _show_stats(self, nrplayers, banned=False):
        # if len(self.labels_list):
        #     for label in self.labels_list:
        #         label.frame.destroy()
        #         del label
        #     self.labels_list.clear()
        if banned:
            rank_list = self.rank_dict_b
            map_list = self.map_dict_b
            server_list = self.server_dict_b
            mode_list = self.mode_dict_b
        else:
            rank_list = self.rank_dict
            map_list = self.map_dict
            server_list = self.server_dict
            mode_list = self.mode_dict
        length_ranks = len(rank_list)
        length_maps = len(map_list)
        length_servers = len(server_list)
        length_mode = len(mode_list)
        maxim = max(length_ranks, length_maps, length_servers, length_mode)
        self.rank_box.box.delete(0, tk.END)
        self.map_box.box.delete(0, tk.END)
        self.server_box.box.delete(0, tk.END)
        self.mode_box.box.delete(0, tk.END)
        for val in range(0, maxim):
            if val < length_ranks:
                text = g.RANK_TRANSLATE_TEXT[rank_list[val][0]] + " = " + str(round(rank_list[val][1] / nrplayers * 100, 2)) + "% (" + str(rank_list[val][1]) + ")"
                self.rank_box.box.insert(tk.END, text)
                # rank_list_text.append(text)
                # label = btk.MyLabelStyle(self.stats_frame, text)
                # label.frame.grid(row=val, column=0, padx=5, pady=3, sticky=tk.W + tk.E)
                # self.labels_list.append(label)
            if val < length_maps:
                text = map_list[val][0] + " = " + str(round(map_list[val][1] / nrplayers * 100, 2)) + "% (" + str(map_list[val][1]) + ")"
                self.map_box.box.insert(tk.END, text)
                # map_list_text.append(text)
                # label = btk.MyLabelStyle(self.stats_frame, text)
                # label.frame.grid(row=val, column=1, padx=5, pady=3, sticky=tk.W + tk.E)
                # self.labels_list.append(label)
            if val < length_servers:
                text = server_list[val][0] + " = " + str(round(server_list[val][1] / nrplayers * 100, 2)) + "% (" + str(server_list[val][1]) + ")"
                self.server_box.box.insert(tk.END, text)
                # server_list_text.append(text)
                # label = btk.MyLabelStyle(self.stats_frame, text)
                # label.frame.grid(row=val, column=2, padx=5, pady=3, sticky=tk.W + tk.E)
                # self.labels_list.append(label)
            if val < length_mode:
                text = g.MODE_TRANSLATE[mode_list[val][0]] + " = " + str(round(mode_list[val][1] / nrplayers * 100, 2)) + "% (" + str(mode_list[val][1]) + ")"
                self.mode_box.box.insert(tk.END, text)
                # mode_list_text.append(text)
                # label = btk.MyLabelStyle(self.stats_frame, text)
                # label.frame.grid(row=val, column=3, padx=5, pady=3, sticky=tk.W + tk.E)
                # self.labels_list.append(label)

    def _check_more_stats(self):
        try:
            rfile = open(g.path_exec_folder + "watchlist", "r", encoding="utf-8")
            rdr = mycsv.myCSV(rfile)
            rdr.get_next()
        except:
            AW.MyAlertWindow(self.window, "Cannot read Watchlist")
            return
        for line in rdr.reader:
            player = WP.MyWatchPlayer(line)
            if player.banned == "Y":
                self.map_dict_b[player.map] = self.map_dict_b[player.map] + 1 if self.map_dict_b.get(player.map) else 1
                self.rank_dict_b[player.rank] = self.rank_dict_b[player.rank] + 1 if self.rank_dict_b.get(player.rank) else 1
                self.server_dict_b[player.server] = self.server_dict_b[player.server] + 1 if self.server_dict_b.get(
                    player.server) else 1
                self.mode_dict_b[player.mode] = self.mode_dict_b[player.mode] + 1 if self.mode_dict_b.get(player.mode) else 1
            self.map_dict[player.map] = self.map_dict[player.map] + 1 if self.map_dict.get(player.map) else 1
            self.rank_dict[player.rank] = self.rank_dict[player.rank] + 1 if self.rank_dict.get(player.rank) else 1
            self.server_dict[player.server] = self.server_dict[player.server] + 1 if self.server_dict.get(
                player.server) else 1
            self.mode_dict[player.mode] = self.mode_dict[player.mode] + 1 if self.mode_dict.get(player.mode) else 1
        rfile.close()
        self.map_dict = sorted(self.map_dict.items(), key=lambda item: item[1], reverse=True)
        self.rank_dict = sorted(self.rank_dict.items(), key=lambda item: item[1], reverse=True)
        self.server_dict = sorted(self.server_dict.items(), key=lambda item: item[1], reverse=True)
        self.mode_dict = sorted(self.mode_dict.items(), key=lambda item: item[1], reverse=True)
        self.map_dict_b = sorted(self.map_dict_b.items(), key=lambda item: item[1], reverse=True)
        self.rank_dict_b = sorted(self.rank_dict_b.items(), key=lambda item: item[1], reverse=True)
        self.server_dict_b = sorted(self.server_dict_b.items(), key=lambda item: item[1], reverse=True)
        self.mode_dict_b = sorted(self.mode_dict_b.items(), key=lambda item: item[1], reverse=True)

    def _scroll_func(self, *args):
        self.rank_box.box.yview(*args)
        self.map_box.box.yview(*args)
        self.server_box.box.yview(*args)
        self.mode_box.box.yview(*args)

    def _scroll_func_mwheel(self, event):
        self.rank_box.box.yview(tk.SCROLL, -event.delta, tk.UNITS)
        self.map_box.box.yview(tk.SCROLL, -event.delta, tk.UNITS)
        self.server_box.box.yview(tk.SCROLL, -event.delta, tk.UNITS)
        self.mode_box.box.yview(tk.SCROLL, -event.delta, tk.UNITS)
        return "break"

    def __init__(self, root, nrplayers, nrbanned):
        self.window = tk.Toplevel(root)
        self.window.transient(root)
        self.window.title("WatchList Extra Stats")
        self.window.minsize(750, 350)
        sizex = self.window.minsize()[0]
        # sizey = self.window.minsize()[1]
        self.window.resizable(False, False)
        # self.window.attributes("-topmost")
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.window.bind("<MouseWheel>", self._scroll_func_mwheel)

        self.map_dict = dict()
        self.rank_dict = dict()
        self.server_dict = dict()
        self.mode_dict = dict()
        self.map_dict_b = dict()
        self.rank_dict_b = dict()
        self.server_dict_b = dict()
        self.mode_dict_b = dict()
        self.nrall = nrplayers
        self.nrbanned = nrbanned
        self._all_stats = True
        # self.labels_list = list()
        self._check_more_stats()

        frame = tk.Frame(self.window, bg="#101010", width=sizex, height=20)
        label = btk.MyLabelStyle(frame, "RANKS")
        label.frame.config(font=("", math.ceil(12 * g.settings_dict["scaling"]), "bold"))
        label.frame.grid(row=0, column=0, padx=5, sticky=tk.W + tk.E)
        label = btk.MyLabelStyle(frame, "MAPS")
        label.frame.config(font=("", math.ceil(12 * g.settings_dict["scaling"]), "bold"))
        label.frame.grid(row=0, column=1, padx=5, sticky=tk.W + tk.E)
        label = btk.MyLabelStyle(frame, "SERVERS")
        label.frame.config(font=("", math.ceil(12 * g.settings_dict["scaling"]), "bold"))
        label.frame.grid(row=0, column=2, padx=5, sticky=tk.W + tk.E)
        label = btk.MyLabelStyle(frame, "MODES")
        label.frame.config(font=("", math.ceil(12 * g.settings_dict["scaling"]), "bold"))
        label.frame.grid(row=0, column=3, padx=5, sticky=tk.W + tk.E)

        frame.grid_columnconfigure(0, minsize=0.1 * sizex * g.settings_dict["scaling"], weight=1)
        frame.grid_columnconfigure(1, minsize=0.15 * sizex * g.settings_dict["scaling"], weight=1)
        frame.grid_columnconfigure(2, minsize=0.25 * sizex * g.settings_dict["scaling"], weight=1)
        frame.grid_columnconfigure(3, minsize=0.2 * sizex * g.settings_dict["scaling"], weight=1)

        frame.grid_propagate(False)
        frame.pack(fill=tk.X)
        frame = tk.Frame(self.window, bg="#101010", width=sizex, height=20)
        label = btk.MyLabelStyle(frame, "_" * 300)
        label.frame.pack()
        frame.pack_propagate(False)
        frame.pack(fill=tk.X)

        self.stats_frame = tk.Frame(self.window, bg="#101010", width=sizex, height=20)

        self.scrollbar = tk.Scrollbar(self.stats_frame, orient=tk.VERTICAL, command=self._scroll_func)
        self.scrollbar.grid(row=0, column=4, padx=3, sticky=tk.N + tk.S)
        # self.scrollbar.config(bd=5, highlightthickness=0, bg="#101010", activebackground="#101010", troughcolor="#101010",
        #                       activerelief=tk.FLAT)

        self.rank_box = btk.MyListboxStyle(self.stats_frame, [], addmenu=False)
        self.rank_box.box.config(selectmode=tk.BROWSE, height=15, highlightthickness=0, relief=tk.FLAT, yscrollcommand=self.scrollbar.set)
        # self.rank_box.box.bind("<MouseWheel>", self._scroll_func_mwheel)
        self.map_box = btk.MyListboxStyle(self.stats_frame, [], addmenu=False)
        self.map_box.box.config(selectmode=tk.BROWSE, height=15, highlightthickness=0, relief=tk.FLAT, yscrollcommand=self.scrollbar.set)
        # self.map_box.box.bind("<MouseWheel>", self._scroll_func_mwheel)
        self.server_box = btk.MyListboxStyle(self.stats_frame, [], addmenu=False)
        self.server_box.box.config(selectmode=tk.BROWSE, height=15, highlightthickness=0, relief=tk.FLAT, yscrollcommand=self.scrollbar.set)
        # self.server_box.box.bind("<MouseWheel>", self._scroll_func_mwheel)
        self.mode_box = btk.MyListboxStyle(self.stats_frame, [], addmenu=False)
        self.mode_box.box.config(selectmode=tk.BROWSE, height=15, highlightthickness=0, relief=tk.FLAT, yscrollcommand=self.scrollbar.set)
        # self.mode_box.box.bind("<MouseWheel>", self._scroll_func_mwheel)
        self.rank_box.box.grid(row=0, column=0, sticky=tk.NSEW)
        self.map_box.box.grid(row=0, column=1, sticky=tk.NSEW)
        self.server_box.box.grid(row=0, column=2, sticky=tk.NSEW)
        self.mode_box.box.grid(row=0, column=3, sticky=tk.NSEW)

        self._show_stats(nrplayers)

        self.stats_frame.grid_columnconfigure(0, minsize=0.16 * sizex * g.settings_dict["scaling"], weight=1)
        self.stats_frame.grid_columnconfigure(1, minsize=0.31 * sizex * g.settings_dict["scaling"], weight=1)
        self.stats_frame.grid_columnconfigure(2, minsize=0.24 * sizex * g.settings_dict["scaling"], weight=1)
        self.stats_frame.grid_columnconfigure(3, minsize=0.22 * sizex * g.settings_dict["scaling"], weight=1)
        # self.stats_frame.grid_columnconfigure(4, minsize=0.06 * sizex, weight=1)

        # frame.grid_propagate(False)
        self.stats_frame.pack(fill=tk.BOTH)

        frame = tk.Frame(self.window, bg="#101010", width=sizex, height=20)
        self.btn1 = btk.MyButtonStyle(frame, "Show only banned players", self._switch_stats)
        self.btn1.btn.pack(padx=5, pady=5)
        frame.pack(pady=10, fill=tk.X)

        # self.window.pack_propagate(False)
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (f.calc_window_pos(root, self.window)))
        self.window.grab_set()
        self.window.focus_set()
