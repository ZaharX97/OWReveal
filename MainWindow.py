import datetime as dt
import tkinter as tk
import subprocess as sp
import webbrowser as web

import scapy.all as scpa
import scapy.layers.http as scplh

import myglobals as g
import functions as f
import AlertWindow as AW
import WatchPlayer as WP
import WatchListWindow as WW
import LinksWindow as LW
import SettingsWindow as SW
import blackTkClasses as btk


class MainAppWindow:
    def start_stop(self):
        # global g.thread_sniff
        if f.check_npcap(self) is False:
            return
        if self.btn1_interfaces.text.get() == "Select one interface":
            AW.MyAlertWindow(self.window, "You need to select one network interface")
            return
        if self.btn2_start.text.get() == "Start":
            g.thread_sniff = scpa.AsyncSniffer(iface=f.return_interface(self),
                                               lfilter=lambda y: y.haslayer(scplh.HTTPRequest),
                                               prn=f.process_packet(self), store=False)
            g.thread_sniff.start()
            self.label1_dynamic.text.set("Looking for OW DEMO link")
            self.label1_dynamic.frame.config(fg="green")
            self.btn2_start.text.set("Stop")
            self.entry1_url.frame.delete(0, tk.END)
        else:
            g.thread_sniff.stop(join=False)
            self.label1_dynamic.text.set("Not looking for anything")
            self.label1_dynamic.frame.config(fg="red")
            self.btn2_start.text.set("Start")

    def update_stats(self, stats=None):
        # self.btn6_round.update([])
        self._reset_chekcs()
        if stats:
            # self.label_map.text.set(g.demo_stats["map"])
            indext = 0
            indexct = 0
            if (g.demo_nrplayers == 10 and stats <= 15) or (g.demo_nrplayers == 4 and stats <= 8):
                self.label_scorect.text.set(g.demo_stats[stats].score_team3)
                self.label_scoret.text.set(g.demo_stats[stats].score_team2)
                indext = 6
                indexct = 1
            else:
                self.label_scorect.text.set(g.demo_stats[stats].score_team2)
                self.label_scoret.text.set(g.demo_stats[stats].score_team3)
                indext = 1
                indexct = 6
            if indext == 0:
                AW.MyAlertWindow(g.app.window, "error reading players, max= {}".format(g.demo_nrplayers))
                return
            for p in range(g.demo_nrplayers):
                pname = g.demo_stats[stats].pscore[p].player.name
                # pname = "alongassstringtoseehowplayerswithlongnameslook"
                kda = "{} / {} / {}".format(g.demo_stats[stats].pscore[p].k, g.demo_stats[stats].pscore[p].a,
                                            g.demo_stats[stats].pscore[p].d)
                if g.demo_stats[stats].pscore[p].player.start_team == 2:
                    if (g.demo_nrplayers == 10 and stats <= 15) or (g.demo_nrplayers == 4 and stats <= 8):
                        if len(pname) > 20:
                            getattr(self, "label_player" + str(indext)).frame.config(anchor=tk.W)
                        else:
                            getattr(self, "label_player" + str(indext)).frame.config(anchor=tk.E)
                    getattr(self, "label_player" + str(indext)).text.set(pname)
                    g.profile_links.update(
                        {getattr(self, "label_player" + str(indext)).frame: g.demo_stats[stats].pscore[
                            p].player.profile})
                    getattr(self, "label_scorep" + str(indext)).text.set(kda)
                    indext += 1
                elif g.demo_stats[stats].pscore[p].player.start_team == 3:
                    if (g.demo_nrplayers == 10 and stats > 15) or (g.demo_nrplayers == 4 and stats > 8):
                        if len(pname) > 20:
                            getattr(self, "label_player" + str(indexct)).frame.config(anchor=tk.W)
                        else:
                            getattr(self, "label_player" + str(indexct)).frame.config(anchor=tk.E)
                    getattr(self, "label_player" + str(indexct)).text.set(pname)
                    g.profile_links.update(
                        {getattr(self, "label_player" + str(indexct)).frame: g.demo_stats[stats].pscore[
                            p].player.profile})
                    getattr(self, "label_scorep" + str(indexct)).text.set(kda)
                    indexct += 1
            if g.demo_nrplayers == 4:
                for p in range(3):
                    getattr(self, "label_player" + str(indext)).text.set("")
                    getattr(self, "label_scorep" + str(indext)).text.set("")
                    getattr(self, "label_player" + str(indexct)).text.set("")
                    getattr(self, "label_scorep" + str(indexct)).text.set("")
                    getattr(self, "btn_rad" + str(indext)).btn.grid_remove()
                    getattr(self, "btn_rad" + str(indexct)).btn.grid_remove()
                    indext += 1
                    indexct += 1
        else:
            self.btn6_round.update([])
            self.btn6_round.text.set("Select a round")
            # self.label_map.text.set("-")
            self.label_scorect.text.set(0)
            self.label_scoret.text.set(0)
            for p in range(1, 11):
                g.profile_links.update({getattr(self, "label_player" + str(p)).frame: ""})
                getattr(self, "label_player" + str(p)).text.set("???")
                getattr(self, "label_scorep" + str(p)).text.set("0 / 0 / 0")
                getattr(self, "btn_rad" + str(p)).btn.grid()
                if p > 5:
                    getattr(self, "label_player" + str(p)).frame.config(anchor=tk.E)
        self.window.update_idletasks()

    def _reset_chekcs(self):
        for i2 in range(10):
            getattr(self, "btn_rad" + str(i2 + 1)).btn.deselect()

    def _addto_watchlist(self):
        if g.thread_check_vac.is_alive():
            AW.MyAlertWindow(self.window, "VAC checking in progress, please wait!\n1 player / sec")
            return
        for i2 in range(1, 11):
            if getattr(self, "btn_rad" + str(i2)).value.get() == tk.TRUE:
                name = getattr(self, "label_player" + str(i2)).text.get()
                link = g.profile_links[getattr(self, "label_player" + str(i2)).frame]
                if link == "":
                    return
                try:
                    exist = False
                    wfile = open(g.exec_path + "watchlist", "r", encoding="utf-8")
                    for line in wfile:
                        player = WP.MyWatchPlayer(line)
                        if player.link == link:
                            exist = True
                            wfile.close()
                            break
                    if exist:
                        continue
                except Exception:
                    # the file probably doesnt exist
                    pass
                dtt = dt.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
                for player in g.demo_stats[len(g.demo_stats) - 1].pscore:
                    if player.player.profile == link:
                        kad = "{} / {} / {}".format(player.k, player.a, player.d)
                        break
                map = g.demo_stats["otherdata"]["map"]
                if g.demo_nrplayers == 4:
                    map += "_2v2"
                link = link[link.rfind("/") + 1:]
                # total = len(name) + len(link) + len(map) + len(kad) + len(dtt) + 6  # 5 spaces + banned
                try:
                    wfile = open(g.exec_path + "watchlist", "a", encoding="utf-8")
                    # wfile.write("{}={} ".format(len(str(total)), total))
                    wfile.write("{} {} {} {}={} ".format(link, "N", dtt, len(name), name))
                    wfile.write("{}={} {}={}\n".format(len(kad), kad, len(map), map))
                except Exception:
                    AW.MyAlertWindow(self.window, "Error3 opening WatchList")
                    return
        try:
            wfile.close()
        except Exception:
            pass

    def _open_watchlist(self):
        if g.thread_check_vac.is_alive():
            AW.MyAlertWindow(self.window, "VAC checking in progress, please wait!\n1 player / sec")
            return
        WW.WatchListWindow(self.window)

    def __init__(self, title, sizex, sizey):
        self.window = tk.Tk()
        self.window.title(title)
        self.window.minsize(sizex, sizey)
        # self.window.maxsize(sizex, sizey)
        # self.window.resizable(False, False)
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

        self.btn1_interfaces = btk.MyOptMenuStyle(self.window, "Select one interface", f.get_interfaces())
        self.btn1_interfaces.btn.grid(row=0, column=0, sticky=tk.W + tk.E, columnspan=7, pady=5, padx=5)

        self.btn2_start = btk.MyButtonStyle(self.window, "Start", self.start_stop)
        self.btn2_start.btn.config(font=("", 16, ""))
        self.btn2_start.btn.grid(row=0, column=7, columnspan=2, rowspan=2, sticky=tk.NSEW, padx=5, pady=5)

        self.label1_dynamic = btk.MyLabelStyle(self.window, "Not looking for anything")
        self.label1_dynamic.frame.config(borderwidth=10, font=("", 14, "bold"), fg="red")
        self.label1_dynamic.frame.grid(row=1, column=0, columnspan=7)

        self.entry1_url = btk.MyEntryStyle(self.window, "")
        self.entry1_url.frame.grid(row=2, column=0, sticky=tk.W + tk.E, columnspan=9, ipady=3, padx=5, pady=2)
        self.menu1_entry1_copy = btk.MyMenuStyle(self.window)
        self.menu1_entry1_copy.menu.add_command(label="Copy", command=lambda: f.copy_to_clipboard(
            self.entry1_url.frame, "http://" + self.entry1_url.text.get()))

        def rc_event1(event):
            self.menu1_entry1_copy.menu.post(event.x_root, event.y_root)

        self.entry1_url.frame.bind("<Button-3>", rc_event1)

        self.label2_count = btk.MyLabelStyle(self.window, "Total DEMOs: 0")
        self.label2_count.frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=5)

        self.label3_time = btk.MyLabelStyle(self.window, "No LINK found")
        self.label3_time.frame.grid(row=3, column=2, columnspan=4, sticky=tk.W + tk.E, padx=5)

        self.btn3_download = btk.MyButtonStyle(self.window, "Download DEMO",
                                               lambda: f.open_link(self.entry1_url.text.get(), self.btn3_download))
        self.btn3_download.btn.grid(row=3, column=7, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn4_link_list = btk.MyButtonStyle(self.window, "LINK List", lambda: LW.LinkListWindow(self.window))
        self.btn4_link_list.btn.grid(row=9, column=7, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn5_settings = btk.MyButtonStyle(self.window, "Settings", lambda: SW.SettingsWindow(self.window))
        self.btn5_settings.btn.grid(row=9, column=8, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn6_round = btk.MyOptMenuStyle(self.window, "Select a round", [])
        self.btn6_round.btn.grid(row=4, column=7, sticky=tk.W + tk.E, columnspan=2, pady=5, padx=5)

        self.btn7_add_wl = btk.MyButtonStyle(self.window, "Add to Watchlist", self._addto_watchlist)
        self.btn7_add_wl.btn.grid(row=6, column=7, columnspan=2, sticky=tk.W + tk.E, padx=5)

        self.btn8_watchlist = btk.MyButtonStyle(self.window, "WatchList", self._open_watchlist)
        self.btn8_watchlist.btn.grid(row=7, column=7, columnspan=2, sticky=tk.W + tk.E, padx=5)

        self.label_teamct = btk.MyLabelStyle(self.window, "CT")
        self.label_teamct.frame.config(font=("", 16, "bold"), fg="#00bfff")
        self.label_teamct.frame.grid(row=4, column=0, columnspan=2, sticky=tk.NSEW, padx=5)
        self.label_scorect = btk.MyLabelStyle(self.window, "0")
        self.label_scorect.frame.config(font=("", 16, ""))
        self.label_scorect.frame.grid(row=4, column=2, sticky=tk.NSEW, padx=5)
        # self.label_map = btk.MyLabelStyle(self.window, "-")
        # self.label_map.frame.grid(row=4, column=3, sticky=tk.W + tk.E, padx=5)
        self.label_scoresep = btk.MyLabelStyle(self.window, "-")
        self.label_scoresep.frame.config(font=("", 14, ""))
        self.label_scoresep.frame.grid(row=4, column=3)
        self.label_scoret = btk.MyLabelStyle(self.window, "0")
        self.label_scoret.frame.config(font=("", 16, ""))
        self.label_scoret.frame.grid(row=4, column=4, sticky=tk.NSEW, padx=5)
        self.label_teamt = btk.MyLabelStyle(self.window, "T")
        self.label_teamt.frame.config(font=("", 16, "bold"), fg="#df2020")
        self.label_teamt.frame.grid(row=4, column=5, columnspan=2, sticky=tk.NSEW, padx=5)

        self.label_player1 = btk.MyLabelStyle(self.window, "???")
        self.label_player1.frame.grid(row=5, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player2 = btk.MyLabelStyle(self.window, "???")
        self.label_player2.frame.grid(row=6, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player3 = btk.MyLabelStyle(self.window, "???")
        self.label_player3.frame.grid(row=7, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player4 = btk.MyLabelStyle(self.window, "???")
        self.label_player4.frame.grid(row=8, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player5 = btk.MyLabelStyle(self.window, "???")
        self.label_player5.frame.grid(row=9, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player6 = btk.MyLabelStyle(self.window, "???")
        self.label_player6.frame.grid(row=5, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_player7 = btk.MyLabelStyle(self.window, "???")
        self.label_player7.frame.grid(row=6, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_player8 = btk.MyLabelStyle(self.window, "???")
        self.label_player8.frame.grid(row=7, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_player9 = btk.MyLabelStyle(self.window, "???")
        self.label_player9.frame.grid(row=8, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_player10 = btk.MyLabelStyle(self.window, "???")
        self.label_player10.frame.grid(row=9, column=5, sticky=tk.W + tk.E, padx=5)

        def lc_event1(event):
            link = g.profile_links[event.widget]
            if len(link) == 0:
                return
            if g.browser_path is None:
                web.open_new_tab(link)
            else:
                sp.Popen(g.browser_path + " " + link)

        self.btn_rad1 = btk.MyCheckButtonStyle(self.window)
        self.btn_rad1.btn.grid(row=5, column=0, padx=5)
        self.btn_rad2 = btk.MyCheckButtonStyle(self.window)
        self.btn_rad2.btn.grid(row=6, column=0, padx=5)
        self.btn_rad3 = btk.MyCheckButtonStyle(self.window)
        self.btn_rad3.btn.grid(row=7, column=0, padx=5)
        self.btn_rad4 = btk.MyCheckButtonStyle(self.window)
        self.btn_rad4.btn.grid(row=8, column=0, padx=5)
        self.btn_rad5 = btk.MyCheckButtonStyle(self.window)
        self.btn_rad5.btn.grid(row=9, column=0, padx=5)
        self.btn_rad6 = btk.MyCheckButtonStyle(self.window)
        self.btn_rad6.btn.grid(row=5, column=6, padx=5)
        self.btn_rad7 = btk.MyCheckButtonStyle(self.window)
        self.btn_rad7.btn.grid(row=6, column=6, padx=5)
        self.btn_rad8 = btk.MyCheckButtonStyle(self.window)
        self.btn_rad8.btn.grid(row=7, column=6, padx=5)
        self.btn_rad9 = btk.MyCheckButtonStyle(self.window)
        self.btn_rad9.btn.grid(row=8, column=6, padx=5)
        self.btn_rad10 = btk.MyCheckButtonStyle(self.window)
        self.btn_rad10.btn.grid(row=9, column=6, padx=5)
        self._reset_chekcs()

        self.label_scorep1 = btk.MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep1.frame.grid(row=5, column=2, sticky=tk.W, padx=5)
        self.label_scorep2 = btk.MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep2.frame.grid(row=6, column=2, sticky=tk.W, padx=5)
        self.label_scorep3 = btk.MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep3.frame.grid(row=7, column=2, sticky=tk.W, padx=5)
        self.label_scorep4 = btk.MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep4.frame.grid(row=8, column=2, sticky=tk.W, padx=5)
        self.label_scorep5 = btk.MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep5.frame.grid(row=9, column=2, sticky=tk.W, padx=5)
        self.label_scorep6 = btk.MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep6.frame.grid(row=5, column=4, sticky=tk.E, padx=5)
        self.label_scorep7 = btk.MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep7.frame.grid(row=6, column=4, sticky=tk.E, padx=5)
        self.label_scorep8 = btk.MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep8.frame.grid(row=7, column=4, sticky=tk.E, padx=5)
        self.label_scorep9 = btk.MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep9.frame.grid(row=8, column=4, sticky=tk.E, padx=5)
        self.label_scorep10 = btk.MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep10.frame.grid(row=9, column=4, sticky=tk.E, padx=5)

        # self.label_sep1 = btk.MyLabelStyle(self.window, "|")
        # self.label_sep1.frame.grid(row=5, column=3, sticky=tk.W + tk.E, padx=5)
        # self.label_sep2 = btk.MyLabelStyle(self.window, "|")
        # self.label_sep2.frame.grid(row=6, column=3, sticky=tk.W + tk.E, padx=5)
        # self.label_sep3 = btk.MyLabelStyle(self.window, "|")
        # self.label_sep3.frame.grid(row=7, column=3, sticky=tk.W + tk.E, padx=5)
        # self.label_sep4 = btk.MyLabelStyle(self.window, "|")
        # self.label_sep4.frame.grid(row=8, column=3, sticky=tk.W + tk.E, padx=5)
        # self.label_sep5 = btk.MyLabelStyle(self.window, "|")
        # self.label_sep5.frame.grid(row=9, column=3, sticky=tk.W + tk.E, padx=5)

        for i2 in range(1, 11):
            g.profile_links.update({getattr(self, "label_player" + str(i2)).frame: ""})
            if i2 < 6:
                getattr(self, "label_player" + str(i2)).frame.config(cursor="hand2", anchor=tk.W)
            else:
                getattr(self, "label_player" + str(i2)).frame.config(cursor="hand2", anchor=tk.E)
            getattr(self, "label_player" + str(i2)).frame.bind("<Button-1>", lc_event1)
            getattr(self, "label_scorep" + str(i2)).frame.config(font=("", 12, ""))

        self.window.grid_columnconfigure(0, minsize=0.05 * sizex, weight=1)
        self.window.grid_columnconfigure(1, minsize=0.2 * sizex, weight=1)
        self.window.grid_columnconfigure(2, minsize=0.12 * sizex, weight=1)
        self.window.grid_columnconfigure(3, minsize=0.02 * sizex, weight=1)
        self.window.grid_columnconfigure(4, minsize=0.12 * sizex, weight=1)
        self.window.grid_columnconfigure(5, minsize=0.2 * sizex, weight=1)
        self.window.grid_columnconfigure(6, minsize=0.05 * sizex, weight=1)  # 0.7
        self.window.grid_columnconfigure(7, minsize=0.12 * sizex, weight=1)
        self.window.grid_columnconfigure(8, minsize=0.12 * sizex, weight=1)
        self.window.grid_propagate(False)

        # self.window.grid_rowconfigure(0, minsize=0.06 * sizey, weight=1)
        # self.window.grid_rowconfigure(1, minsize=0.14 * sizey, weight=1)
        # self.window.grid_rowconfigure(2, minsize=0.1 * sizey, weight=1)
        # self.window.grid_rowconfigure(3, minsize=0.05 * sizey, weight=1)
        # self.window.grid_rowconfigure(4, minsize=0.1 * sizey, weight=1)
        self.window.grid_rowconfigure(5, minsize=30, weight=0)
        self.window.grid_rowconfigure(6, minsize=30, weight=0)
        self.window.grid_rowconfigure(7, minsize=30, weight=0)
        self.window.grid_rowconfigure(8, minsize=30, weight=0)
        self.window.grid_rowconfigure(9, minsize=30, weight=0)
        self.window.update_idletasks()
