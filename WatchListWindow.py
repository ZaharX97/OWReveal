import os
import tkinter as tk
import subprocess as sp
import webbrowser as web

import myglobals as g
import functions as f
import AlertWindow as AW
import WatchPlayer as WP
import blackTkClasses as btk


class WatchListWindow:
    def _remove_pl(self):
        for i2 in range(10):
            if self.watchlist[i2]["btn"].value.get() == tk.TRUE and self.watchlist[i2]["kad"].text.get() != "":
                val = self.watchlist[i2]["nr"].text.get()[:self.watchlist[i2]["nr"].text.get().find(".")]
                val = int(val)
                if val not in self.to_remove:
                    self.to_remove.add(val)
                    self.watchlist[i2]["name"].text.set("TO REMOVE")
                    self.watchlist[i2]["kad"].text.set("TO REMOVE")
                    self.watchlist[i2]["map"].text.set("TO REMOVE")
                    self.watchlist[i2]["date"].text.set("TO REMOVE")
                else:
                    self.to_remove.discard(val)
                    self.watchlist[i2]["name"].text.set("TO UPDATE")
                    self.watchlist[i2]["kad"].text.set("TO UPDATE")
                    self.watchlist[i2]["map"].text.set("TO UPDATE")
                    self.watchlist[i2]["date"].text.set("TO UPDATE")

    def _mark_ban(self):
        for i2 in range(10):
            if self.watchlist[i2]["btn"].value.get() == tk.TRUE and self.watchlist[i2]["kad"].text.get() != "":
                val = self.watchlist[i2]["nr"].text.get()[:self.watchlist[i2]["nr"].text.get().find(".")]
                val = int(val)
                if val not in self.to_ban:
                    self.to_ban.add(val)
                    if self.watchlist[i2]["player"].banned == "Y":
                        self.watchlist[i2]["name"].frame.config(bg="#101010")
                    else:
                        self.watchlist[i2]["name"].frame.config(bg="#ff6666")
                else:
                    self.to_ban.discard(val)
                    if self.watchlist[i2]["player"].banned == "N":
                        self.watchlist[i2]["name"].frame.config(bg="#101010")
                    else:
                        self.watchlist[i2]["name"].frame.config(bg="#ff6666")

    def _update_page(self, page):
        if page is None or page < 1 or page == self._lastpage or page > self._maxpages:
            return
        if self._lastpage != 0:
            self._check_comm()
        if page < self._lastpage:
            self.rfile.seek(0, 0)
            self.findex = 1
        self.entry_page.text.set(str(page))
        self._lastpage = page
        while self.findex < page * 10 - 9:
            self.rfile.readline()
            self.findex += 1
        for i2 in range(10):
            line = self.rfile.readline()
            if not line:
                break
            player = WP.MyWatchPlayer(line)
            if self.findex in self.to_remove:
                player = None
            self.watchlist[i2].update({"player": player})
            self.watchlist[i2]["btn"].btn.grid()
            self.watchlist[i2]["btn"].btn.deselect()
            self.watchlist[i2]["nr"].text.set(str(self.findex) + ".")
            self.watchlist[i2]["name"].text.set(player.name if player else "TO REMOVE")
            if player:
                if len(player.name) > 25:
                    self.watchlist[i2]["name"].frame.config(anchor=tk.W)
                else:
                    self.watchlist[i2]["name"].frame.config(anchor=tk.CENTER)
                if self.findex in self.to_ban:
                    if player.banned == "Y":
                        self.watchlist[i2]["name"].frame.config(bg="#101010")
                    else:
                        self.watchlist[i2]["name"].frame.config(bg="#ff6666")
                else:
                    if player.banned == "Y":
                        self.watchlist[i2]["name"].frame.config(bg="#ff6666")
                    else:
                        self.watchlist[i2]["name"].frame.config(bg="#101010")
            self.watchlist[i2]["kad"].text.set(player.kad if player else "TO REMOVE")
            self.watchlist[i2]["map"].text.set(player.map if player else "TO REMOVE")
            if len(self.watchlist[i2]["map"].text.get()) > 15:
                self.watchlist[i2]["map"].frame.config(anchor=tk.W)
            else:
                self.watchlist[i2]["map"].frame.config(anchor=tk.CENTER)
            self.watchlist[i2]["date"].text.set(player.date if player else "TO REMOVE")
            self.watchlist[i2]["comm"].frame.grid()
            self.watchlist[i2]["comm"].text.set(
                self.comm_dict[self.findex] if self.comm_dict.get(self.findex) else player.comm)
            self.findex += 1
        i2 = (self.findex - 1) % 10
        if i2 != 0:
            while i2 <= 9:
                self.watchlist[i2]["btn"].btn.grid_remove()
                self.watchlist[i2]["nr"].text.set("")
                self.watchlist[i2]["name"].text.set("")
                self.watchlist[i2]["name"].frame.config(bg="#101010")
                self.watchlist[i2]["kad"].text.set("")
                self.watchlist[i2]["map"].text.set("")
                self.watchlist[i2]["date"].text.set("")
                self.watchlist[i2]["comm"].frame.grid_remove()
                self.watchlist[i2]["player"] = None
                i2 += 1

    def _elect_btns(self):
        if not len(self.watchlist):
            return
        if self.watchlist[0]["btn"].value.get() == tk.TRUE:
            for btn in self.watchlist:
                btn["btn"].btn.deselect()
        else:
            for btn in self.watchlist:
                btn["btn"].btn.select()

    def _check_int(self, var, offset=0):
        try:
            var = int(var)
        except Exception:
            AW.MyAlertWindow(self.window, "Page is not a number")
            return None
        return var + offset

    def _enter_event(self, event):
        self._update_page(self._check_int(self.entry_page.text.get()))
        self.window.focus_set()

    def close_and_update(self):
        self._check_comm()
        if not len(self.to_remove) and not len(self.to_ban) and not len(self.to_comm):
            self.window.destroy()
            return
        self.rfile.seek(0, 0)
        self.findex = 1
        try:
            wfile = open(g.exec_path + "watchlist.temp", "w", encoding="utf-8")
        except Exception:
            AW.MyAlertWindow(self.window, "Cannot update WatchList")
            return
        for line in self.rfile:
            if self.findex in self.to_remove:
                self.findex += 1
                continue
            to_change = False
            if self.findex in self.to_ban or self.findex in self.to_comm:
                player = WP.MyWatchPlayer(line)
                to_change = True
            if self.findex in self.to_ban:
                player.banned = "Y" if player.banned == "N" else "N"
            if self.findex in self.to_comm:
                player.comm = self.comm_dict[self.findex]
            if to_change:
                line = player.ret_string()
            wfile.write(line)
            self.findex += 1
        wfile.close()
        self.rfile.close()
        os.remove(g.exec_path + "watchlist")
        os.rename(g.exec_path + "watchlist.temp", g.exec_path + "watchlist")
        self.window.destroy()

    def _check_stats(self):
        nrplayers = 0
        banned = 0
        for line in self.rfile:
            player = WP.MyWatchPlayer(line)
            nrplayers += 1
            if player.banned == "Y":
                banned += 1
        self.rfile.seek(0, 0)
        self._stats.update({"nrpl": nrplayers, "ban": banned})
        if nrplayers % 10 == 0:
            self._maxpages = int(nrplayers / 10)
        else:
            self._maxpages = int(nrplayers / 10) + 1

    def _check_comm(self):
        for i2 in range(10):
            player = self.watchlist[i2]["player"]
            if player and self.watchlist[i2]["comm"].text.get() != player.comm:
                val = self.watchlist[i2]["nr"].text.get()[:self.watchlist[i2]["nr"].text.get().find(".")]
                val = int(val)
                if val not in self.to_comm:
                    self.to_comm.add(val)
                self.comm_dict.update({val: self.watchlist[i2]["comm"].text.get()})

    def __init__(self, root):
        try:
            self.rfile = open(g.exec_path + "watchlist", "r", encoding="utf-8")
        except FileNotFoundError:
            self.rfile = open(g.exec_path + "watchlist", "w", encoding="utf-8")
            self.rfile.close()
            self.rfile = open(g.exec_path + "watchlist", "r", encoding="utf-8")
        self.findex = 1
        self._lastpage = 0
        self._maxpages = 0
        self._stats = {}
        self.watchlist = []
        self.to_remove = set()
        self.to_ban = set()
        self.to_comm = set()
        self.comm_dict = {}
        self.window = tk.Toplevel(root)
        self.window.transient(root)
        self.window.title("WatchList")
        self.window.minsize(750, 410)
        # self.window.resizable(False, False)
        sizex = self.window.minsize()[0]
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.close_and_update)
        frame = tk.Frame(self.window, bg="#101010", width=sizex, height=20)
        label = btk.MyLabelStyle(frame, " \\")
        label.frame.config(font=("", 12, "bold"))
        label.frame.grid(row=0, column=0, sticky=tk.W + tk.E)
        label = btk.MyLabelStyle(frame, "   ##")
        label.frame.config(font=("", 12, "bold"))
        label.frame.grid(row=0, column=1, sticky=tk.W + tk.E)
        label = btk.MyLabelStyle(frame, "NAME")
        label.frame.config(font=("", 12, "bold"))
        label.frame.grid(row=0, column=2, padx=5, sticky=tk.W + tk.E)
        label = btk.MyLabelStyle(frame, "KAD")
        label.frame.config(font=("", 12, "bold"))
        label.frame.grid(row=0, column=3, padx=5, sticky=tk.W + tk.E)
        label = btk.MyLabelStyle(frame, "MAP")
        label.frame.config(font=("", 12, "bold"))
        label.frame.grid(row=0, column=4, padx=5, sticky=tk.W + tk.E)
        label = btk.MyLabelStyle(frame, "DATE ADDED")
        label.frame.config(font=("", 12, "bold"))
        label.frame.grid(row=0, column=5, padx=5, sticky=tk.W + tk.E)
        label = btk.MyLabelStyle(frame, "COMMENTS")
        label.frame.config(font=("", 12, "bold"))
        label.frame.grid(row=0, column=6, padx=5, sticky=tk.W + tk.E)
        # frame.grid_columnconfigure(0, minsize=0.002 * sizex, weight=1)
        # frame.grid_columnconfigure(1, minsize=0.002 * sizex, weight=1)
        frame.grid_columnconfigure(2, minsize=0.27 * sizex, weight=1)
        frame.grid_columnconfigure(3, minsize=0.15 * sizex, weight=1)
        frame.grid_columnconfigure(4, minsize=0.15 * sizex, weight=1)
        frame.grid_columnconfigure(5, minsize=0.15 * sizex, weight=1)
        frame.grid_columnconfigure(6, minsize=0.2 * sizex, weight=1)
        frame.grid_propagate(False)
        frame.pack(fill=tk.X)
        frame = tk.Frame(self.window, bg="#101010", width=sizex, height=20)
        label = btk.MyLabelStyle(frame, "_" * 300)
        label.frame.pack()
        frame.pack_propagate(False)
        frame.pack(fill=tk.X)
        frame = tk.Frame(self.window, bg="#101010", width=sizex, height=300)

        def lc_event1(event):
            for item in self.watchlist:
                if item["name"].frame == event.widget:
                    link = item["player"].link if item["player"] is not None else None
                    break
            if link is None or len(link) == 0:
                return
            if g.browser_path is None:
                web.open_new_tab(link)
            else:
                sp.Popen(g.browser_path + " " + link)

        for i2 in range(1, 11):
            check = btk.MyCheckButtonStyle(frame)
            check.btn.grid(row=i2 - 1, column=0)
            numberr = btk.MyLabelStyle(frame, "")
            numberr.frame.config(anchor=tk.W)
            numberr.frame.grid(row=i2 - 1, column=1, sticky=tk.W + tk.E)
            name = btk.MyLabelStyle(frame, "")
            name.frame.grid(row=i2 - 1, column=2, padx=5, sticky=tk.W + tk.E)
            name.frame.config(cursor="hand2")
            name.frame.bind("<Button-1>", lc_event1)
            kad = btk.MyLabelStyle(frame, "")
            kad.frame.grid(row=i2 - 1, column=3, padx=5, sticky=tk.W + tk.E)
            mapp = btk.MyLabelStyle(frame, "")
            mapp.frame.grid(row=i2 - 1, column=4, padx=5, sticky=tk.W + tk.E)
            date = btk.MyLabelStyle(frame, "")
            date.frame.grid(row=i2 - 1, column=5, padx=5, sticky=tk.W + tk.E)
            comm = btk.MyEntryStyle(frame, "")
            comm.frame.config(state=tk.NORMAL, bg="#101010", fg="white", insertbackground="white")
            comm.frame.grid(row=i2 - 1, column=6, padx=5, pady=2, sticky=tk.W + tk.E)
            self.watchlist.append(
                {"btn": check, "nr": numberr, "name": name, "kad": kad, "map": mapp, "date": date,
                 "comm": comm, "player": None})
        # self.sf.inner.grid_columnconfigure(0, minsize=0.05 * sizex, weight=1)
        # self.sf.inner.grid_columnconfigure(1, minsize=0.05 * sizex, weight=1)
        frame.grid_columnconfigure(2, minsize=0.27 * sizex, weight=1)
        frame.grid_columnconfigure(3, minsize=0.15 * sizex, weight=1)
        frame.grid_columnconfigure(4, minsize=0.15 * sizex, weight=1)
        frame.grid_columnconfigure(5, minsize=0.15 * sizex, weight=1)
        frame.grid_columnconfigure(6, minsize=0.2 * sizex, weight=1)
        # self.sf.inner.grid_propagate(False)
        # self.frame.update_idletasks()
        frame.pack(fill=tk.BOTH)
        # frame = tk.Frame(self.window, bg="#101010", width=sizex, height=20)
        # label = btk.MyLabelStyle(frame, "_" * 300)
        # label.frame.pack()
        # frame.pack_propagate(False)
        # frame.pack(fill=tk.X)
        frame = tk.Frame(self.window, bg="#101010", width=sizex, height=15)
        btn = btk.MyButtonStyle(frame, "1 <<", lambda: self._update_page(1))
        btn.btn.config(width=5)
        btn.btn.pack(side=tk.LEFT, padx=5)
        btn = btk.MyButtonStyle(frame, "<", lambda: self._update_page(self._check_int(self.entry_page.text.get(), -1)))
        btn.btn.config(width=5)
        btn.btn.pack(side=tk.LEFT, padx=5)
        self.entry_page = btk.MyEntryStyle(frame, "0")
        self.entry_page.frame.config(width=5, state=tk.NORMAL)
        self.entry_page.frame.pack(side=tk.LEFT, padx=5)
        self.entry_page.frame.bind("<Return>", self._enter_event)
        btn = btk.MyButtonStyle(frame, ">", lambda: self._update_page(self._check_int(self.entry_page.text.get(), 1)))
        btn.btn.config(width=5)
        btn.btn.pack(side=tk.LEFT, padx=5)
        self.btn_lastpage = btk.MyButtonStyle(frame, ">>", lambda: self._update_page(self._maxpages))
        self.btn_lastpage.btn.config(width=5)
        self.btn_lastpage.btn.pack(side=tk.LEFT, padx=5)
        frame.pack()
        frame = tk.Frame(self.window, bg="#101010", width=sizex, height=15)
        btn = btk.MyButtonStyle(frame, "(De) Select All", self._elect_btns)
        btn.btn.grid(row=0, column=0, padx=5)
        btn = btk.MyButtonStyle(frame, "Remove selected", self._remove_pl)
        btn.btn.grid(row=0, column=1, padx=5)
        btn = btk.MyButtonStyle(frame, "(Un) Mark Banned", self._mark_ban)
        btn.btn.grid(row=0, column=2, padx=5)
        btn = btk.MyButtonStyle(frame, "Check VAC", lambda: f.check_vac(self))
        btn.btn.grid(row=0, column=3, padx=5)
        frame.pack(side=tk.LEFT)
        self._check_stats()
        frame = tk.Frame(self.window, bg="#101010", width=sizex, height=20)
        self.stats_players = btk.MyLabelStyle(frame, "Total players: " + str(self._stats["nrpl"]))
        self.stats_players.frame.config(font=("", 12, "bold"))
        self.stats_players.frame.grid(row=0, column=0, sticky=tk.W)
        self.stats_banned = btk.MyLabelStyle(frame, "Banned players: " + str(self._stats["ban"]))
        self.stats_banned.frame.config(font=("", 12, "bold"))
        self.stats_banned.frame.grid(row=1, column=0, sticky=tk.W)
        if self._stats["nrpl"] == 0:
            percent = "--.--"
        else:
            percent = round(self._stats["ban"] / self._stats["nrpl"] * 100, 2)
        self.percent = btk.MyLabelStyle(frame, "Percent: " + str(percent) + " %")
        self.percent.frame.config(font=("", 12, "bold"))
        self.percent.frame.grid(row=2, column=0, sticky=tk.W)
        self.btn_lastpage.text.set(">> " + str(self._maxpages))
        frame.pack(side=tk.RIGHT)
        self._update_page(self._maxpages)
        self.window.pack_propagate(False)
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (f.calc_window_pos(root, self.window)))
        self.window.grab_set()
        self.window.focus_set()
