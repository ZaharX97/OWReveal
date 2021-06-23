import datetime as dt
import tkinter as tk
import subprocess as sp
import webbrowser as web
import re

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
        if f.check_npcap(self) is False:
            return
        if self.btn1_interfaces.text.get() == "Select one interface":
            AW.MyAlertWindow(self.window, "You need to select one network interface")
            return
        g.settings_dict.update({"net_interface": f.return_interface(self)})
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
        self._reset_chekcs()
        if stats:
            indext = 6
            indexct = 1
            if (g.demo_mode in (0, 6) and (stats <= 15 or (stats > 30 and stats % 6 in {1, 2, 3}))) or (g.demo_mode in (-7, 7) and stats <= 8):
                self.label_scorect.text.set(g.demo_stats[stats].score_team3)
                self.label_scoret.text.set(g.demo_stats[stats].score_team2)
                # indext = 6
                # indexct = 1
            else:
                self.label_scorect.text.set(g.demo_stats[stats].score_team2)
                self.label_scoret.text.set(g.demo_stats[stats].score_team3)
                # indext = 1
                # indexct = 6
            for p in range(len(g.demo_stats[stats].pscore)):
                # test = g.demo_stats
                pname = g.demo_stats[stats].pscore[p].player.name
                prank = g.demo_stats[stats].pscore[p].player.rank
                # pname = "alongassstringtoseehowplayerswithlongnameslook"
                # prank = 18
                kda = "{} / {} / {}".format(g.demo_stats[stats].pscore[p].k, g.demo_stats[stats].pscore[p].a,
                                            g.demo_stats[stats].pscore[p].d)
                # kda = "66 / 66 / 66"
                if g.demo_stats[stats].pscore[p].ttr == 2:
                    index_to_use = indext
                    if len(pname) >= g.NAME_CUTOUT_MAIN:
                        getattr(self, "label_player" + str(index_to_use)).frame.config(anchor=tk.W)
                    else:
                        getattr(self, "label_player" + str(index_to_use)).frame.config(anchor=tk.E)
                    indext += 1
                elif g.demo_stats[stats].pscore[p].ttr == 3:
                    index_to_use = indexct
                    indexct += 1
                getattr(self, "label_player" + str(index_to_use)).text.set(pname)
                g.profile_links.update(
                    {getattr(self, "label_player" + str(index_to_use)).frame: g.demo_stats[stats].pscore[
                        p].player.profile})
                # getattr(self, "label_rank" + str(index_to_use)).text.set(g.RANK_TRANSLATE[prank])
                getattr(self, "label_rank" + str(index_to_use)).frame.config(image=g.RANK_TRANSLATE_IMG[prank])
                getattr(self, "label_scorep" + str(index_to_use)).text.set(kda)
                getattr(self, "btn_rad" + str(index_to_use)).btn.grid()
            if g.demo_mode in (0, 6) and (indext % 5 != 1 or indexct % 5 != 1):
                while indext % 5 != 1 or indexct % 5 != 1:
                    if indext % 5 != 1:
                        getattr(self, "label_player" + str(indext)).text.set("")
                        # getattr(self, "label_rank" + str(indext)).text.set("")
                        getattr(self, "label_rank" + str(indext)).frame.config(image="")
                        getattr(self, "label_scorep" + str(indext)).text.set("")
                        getattr(self, "btn_rad" + str(indext)).btn.grid_remove()
                        indext += 1
                    if indexct % 5 != 1:
                        getattr(self, "label_player" + str(indexct)).text.set("")
                        # getattr(self, "label_rank" + str(indexct)).text.set("")
                        getattr(self, "label_rank" + str(indexct)).frame.config(image="")
                        getattr(self, "label_scorep" + str(indexct)).text.set("")
                        getattr(self, "btn_rad" + str(indexct)).btn.grid_remove()
                        indexct += 1
            elif g.demo_mode in (-7, 7) and (indext % 5 != 3 or indexct % 5 != 3):
                while indext % 5 != 3 or indexct % 5 != 3:
                    if indext % 5 != 3:
                        getattr(self, "label_player" + str(indext)).text.set("")
                        # getattr(self, "label_rank" + str(indext)).text.set("")
                        getattr(self, "label_rank" + str(indext)).frame.config(image="")
                        getattr(self, "label_scorep" + str(indext)).text.set("")
                        indext += 1
                    if indexct % 5 != 3:
                        getattr(self, "label_player" + str(indexct)).text.set("")
                        # getattr(self, "label_rank" + str(indexct)).text.set("")
                        getattr(self, "label_rank" + str(indexct)).frame.config(image="")
                        getattr(self, "label_scorep" + str(indexct)).text.set("")
                        indexct += 1
            if g.demo_mode in (-7, 7) and self.after_reset is True:
                self.after_reset = False
                for p in range(3):
                    getattr(self, "label_player" + str(indext)).text.set("")
                    # getattr(self, "label_rank" + str(indext)).text.set("")
                    getattr(self, "label_rank" + str(indext)).frame.config(image="")
                    getattr(self, "label_scorep" + str(indext)).text.set("")
                    getattr(self, "label_player" + str(indexct)).text.set("")
                    # getattr(self, "label_rank" + str(indexct)).text.set("")
                    getattr(self, "label_rank" + str(indexct)).frame.config(image="")
                    getattr(self, "label_scorep" + str(indexct)).text.set("")
                    getattr(self, "btn_rad" + str(indext)).btn.grid_remove()
                    getattr(self, "btn_rad" + str(indexct)).btn.grid_remove()
                    indext += 1
                    indexct += 1
            kills = 0
            for kills in range(len(g.demo_stats["otherdata"]["kills"][stats])):
                atk = g.demo_stats["otherdata"]["kills"][stats][kills][0]
                ass = g.demo_stats["otherdata"]["kills"][stats][kills][1]
                ded = g.demo_stats["otherdata"]["kills"][stats][kills][2]
                data = g.demo_stats["otherdata"]["kills"][stats][kills][3]
                tempdata = g.demo_stats["otherdata"]["kills"][stats][kills]
                # print(data)
                # T = fg="#df2020" // CT = fg="#00bfff"
                # 2 = "T" // 3 = "CT"
                if (g.demo_mode in (0, 6) and stats <= 15) or (g.demo_mode in (-7, 7) and stats <= 8):
                    color = "#00bfff" if atk.start_team == 3 else "#df2020"
                else:
                    color = "#00bfff" if atk.start_team == 2 else "#df2020"
                getattr(self, "label_atk{}".format(str(kills + 1))).frame.config(fg=color)
                getattr(self, "label_atk{}".format(str(kills+1))).text.set(atk.name)
                if len(atk.name) > g.NAME_CUTOUT_KILLS:
                    getattr(self, f"label_atk{str(kills + 1)}").frame.config(anchor=tk.W)
                else:
                    getattr(self, f"label_atk{str(kills + 1)}").frame.config(anchor=tk.CENTER)
                # data["weapon"] = "sawedoff"
                getattr(self, "label_weapon{}".format(str(kills + 1))).text.set(g.WEAPON_TRANSLATE.get(data["weapon"], "unknown"))
                if (g.demo_mode in (0, 6) and stats <= 15) or (g.demo_mode in (-7, 7) and stats <= 8):
                    color = "#00bfff" if ded.start_team == 3 else "#df2020"
                else:
                    color = "#00bfff" if ded.start_team == 2 else "#df2020"
                getattr(self, "label_ded{}".format(str(kills + 1))).frame.config(fg=color)
                getattr(self, "label_ded{}".format(str(kills + 1))).text.set(ded.name)
                if len(ded.name) > g.NAME_CUTOUT_KILLS:
                    getattr(self, f"label_ded{str(kills + 1)}").frame.config(anchor=tk.W)
                else:
                    getattr(self, f"label_ded{str(kills + 1)}").frame.config(anchor=tk.CENTER)
            while kills < 9:
                kills += 1
                getattr(self, "label_atk{}".format(str(kills + 1))).text.set("")
                getattr(self, "label_weapon{}".format(str(kills + 1))).text.set("")
                getattr(self, "label_ded{}".format(str(kills + 1))).text.set("")
        else:
            self.btn6_round.update([])
            self.btn6_round.text.set("Round ??")
            # self.label_map.text.set("-")
            self.label_scorect.text.set(0)
            self.label_scoret.text.set(0)
            for p in range(1, 11):
                g.profile_links.update({getattr(self, "label_player" + str(p)).frame: ""})
                getattr(self, "label_player" + str(p)).text.set("???")
                # getattr(self, "label_rank" + str(p)).text.set("???")
                getattr(self, "label_rank" + str(p)).frame.config(image=g.RANK_TRANSLATE_IMG[0])
                getattr(self, "label_scorep" + str(p)).text.set("0 / 0 / 0")
                getattr(self, "btn_rad" + str(p)).btn.grid()
                if p > 5:
                    getattr(self, "label_player" + str(p)).frame.config(anchor=tk.E)
                getattr(self, "label_atk{}".format(str(p))).text.set("")
                getattr(self, "label_weapon{}".format(str(p))).text.set("")
                getattr(self, "label_ded{}".format(str(p))).text.set("")
            self.label4_map.text.set("Map")
            self.label4_map.frame.config(anchor=tk.CENTER)
            self.label5_server.text.set("Server")
            self.label5_server.frame.config(anchor=tk.CENTER)
            self.after_reset = True
        self.window.update_idletasks()

    def _reset_chekcs(self):
        for i2 in range(10):
            getattr(self, "btn_rad" + str(i2 + 1)).btn.deselect()

    def _addto_watchlist(self):
        if g.thread_check_vac.is_alive():
            AW.MyAlertWindow(self.window, "VAC checking in progress, please wait!\n1 player / sec")
            return
        to_add = set()
        for i2 in range(1, 11):
            if getattr(self, "btn_rad" + str(i2)).value.get() == tk.TRUE:
                link = g.profile_links[getattr(self, "label_player" + str(i2)).frame]
                if link == "":
                    continue
                to_add.add(link)
        if len(to_add):
            try:
                rfile = open(g.path_exec_folder + "watchlist", "r", encoding="utf-8")
            except FileNotFoundError:
                tempwrite = open(g.path_exec_folder + "watchlist", "w", encoding="utf-8")
                tempwrite.close()
                try:
                    rfile = open(g.path_exec_folder + "watchlist", "r", encoding="utf-8")
                except:
                    AW.MyAlertWindow(self.window, "Error opening WatchList (read)")
                    return
            except Exception:
                AW.MyAlertWindow(self.window, "Error opening WatchList (read)")
                return
            for line in rfile:
                player = WP.MyWatchPlayer(line)
                if player.link in to_add:
                    to_add.remove(player.link)
                    if not len(to_add):
                        break
            try:
                rfile.close()
            except Exception:
                pass
            try:
                wfile = open(g.path_exec_folder + "watchlist", "a", encoding="utf-8")
            except Exception:
                AW.MyAlertWindow(self.window, "Error opening WatchList (append)")
                return
            dtt = g.demo_date.astimezone().strftime("%d-%b-%Y %H:%M:%S%z")
            qdtt_demo = g.demo_date.strftime("%Y-%m-%d %H:%M:%S")
            qdtt_now = dt.datetime.now().astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            map2 = g.demo_stats["otherdata"]["header"].map_name
            # if g.demo_nrplayers == 4:
            #     map2 += "_2v2"
            for player in g.demo_stats[len(g.demo_stats) - 1].pscore:
                if player.player.profile in to_add:
                    name = player.player.name
                    rank = player.player.rank
                    mode = g.demo_mode
                    link = player.player.profile[player.player.profile.rfind("/") + 1:]
                    # if not len(name):
                    #     name = g.demo_stats["otherdata"]["PFN"][link]
                    if not len(name):
                        name = "unnamed"
                    kad = "{} / {} / {}".format(player.k, player.a, player.d)
                    wfile.write("{} {} {} {}={} ".format(link, "N", dtt, len(name), name))
                    wfile.write("{}={} {}={} ".format(len(kad), kad, len(map2), map2))
                    wfile.write("{}={} {}={} ".format(len(str(rank)), rank, len(g.last_server), g.last_server))
                    wfile.write("{}={} 2=-1\n".format(len(str(mode)), mode))
                    to_add.remove(player.player.profile)
                    if g.settings_dict["add_to_db"] and self.entry1_url.text.get() != "":
                        # delta = dt.timedelta(hours=g.DEMOS_AGE)
                        # if (dt.datetime.now().astimezone(dt.timezone.utc) - g.demo_date) > delta or g.demo_stats["otherdata"]["header"].server_name.upper().find("VALVE") == -1:
                        #     if not len(to_add):
                        #         break
                        #     continue
                        if g.demo_stats["otherdata"]["header"].server_name.upper().find("VALVE") == -1:
                            if not len(to_add):
                                break
                            continue
                        g.list_add_db.append((link, name, rank, kad, map2, mode, g.last_server, qdtt_now, qdtt_demo, 0))
                        if not g.thread_add_to_db.is_alive():
                            g.thread_add_to_db.start()
                        g.event_add_db.set()
                    if not len(to_add):
                        break
            try:
                wfile.close()
            except Exception:
                pass

    def _open_watchlist(self):
        if g.thread_check_vac.is_alive():
            AW.MyAlertWindow(self.window, "VAC checking in progress, please wait!\n1 player / sec")
            return
        WW.WatchListWindow(self.window)

    def _toggle_stats_frame(self):
        if g.stats_active:
            self.frame_stats.grid_remove()
            self.frame_kills.grid()
            self.btn7_add_wl.btn.grid_remove()
            self.btn_toggle.text.set("Show Stats")
        else:
            self.frame_kills.grid_remove()
            self.frame_stats.grid()
            self.btn7_add_wl.btn.grid()
            self.btn_toggle.text.set("Show Kills")
        g.stats_active = not g.stats_active
        self.window.update_idletasks()

    def _prev_next_round(self, prev=False):
        roundd = self.btn6_round.text.get()[6:]
        try:
            roundd = int(roundd)
        except ValueError:
            return
        if prev and roundd > 1:
            self.btn6_round.text.set(f"Round {roundd - 1}")
            self.update_stats(roundd - 1)
            return
        if not prev and roundd < (len(g.demo_stats) - 1):
            self.btn6_round.text.set(f"Round {roundd + 1}")
            self.update_stats(roundd + 1)

    def __init__(self, title, sizex, sizey):
        self.after_reset = False
        self.window = tk.Tk()
        self.window.title(title)
        self.window.minsize(sizex, sizey)
        # self.window.maxsize(sizex, sizey)
        # self.window.resizable(False, False)
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

        self.btn1_interfaces = btk.MyOptMenuStyle(self.window, "Select one interface", f.get_interfaces())
        self.btn1_interfaces.btn.grid(row=0, column=0, sticky=tk.W + tk.E, columnspan=3, pady=5, padx=5)

        self.btn2_start = btk.MyButtonStyle(self.window, "Start", self.start_stop)
        self.btn2_start.btn.config(font=("", 16, ""))
        self.btn2_start.btn.grid(row=0, column=3, columnspan=2, rowspan=2, sticky=tk.NSEW, padx=5, pady=5)

        self.label1_dynamic = btk.MyLabelStyle(self.window, "Not looking for anything")
        self.label1_dynamic.frame.config(borderwidth=10, font=("", 14, "bold"), fg="red")
        self.label1_dynamic.frame.grid(row=1, column=0, columnspan=3)

        self.entry1_url = btk.MyEntryStyle(self.window, "")
        self.entry1_url.frame.grid(row=2, column=0, sticky=tk.W + tk.E, columnspan=5, ipady=3, padx=5, pady=2)
        self.menu1_entry1_copy = btk.MyMenuStyle(self.window)
        self.menu1_entry1_copy.menu.add_command(label="Copy", command=lambda: f.copy_to_clipboard(
            self.entry1_url.frame, self.entry1_url.text.get()))

        def rc_event1(event):
            self.menu1_entry1_copy.menu.post(event.x_root, event.y_root)

        self.entry1_url.frame.bind("<Button-3>", rc_event1)

        self.label2_count = btk.MyLabelStyle(self.window, "Total DEMOs: 0")
        self.label2_count.frame.grid(row=3, column=0, sticky=tk.W, padx=5)

        self.label3_time = btk.MyLabelStyle(self.window, "No LINK found")
        self.label3_time.frame.grid(row=3, column=1, sticky=tk.W, padx=5)

        self.btn_toggle = btk.MyButtonStyle(self.window, "Show Kills", self._toggle_stats_frame)
        self.btn_toggle.btn.grid(row=3, column=2, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn3_download = btk.MyButtonStyle(self.window, "Download DEMO",
                                               lambda: f.open_link(self.entry1_url.text.get(), self.btn3_download))
        self.btn3_download.btn.grid(row=3, column=3, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn4_link_list = btk.MyButtonStyle(self.window, "LINK List", lambda: LW.LinkListWindow(self.window))
        self.btn4_link_list.btn.grid(row=9, column=3, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn5_settings = btk.MyButtonStyle(self.window, "Settings", lambda: SW.SettingsWindow(self.window))
        self.btn5_settings.btn.grid(row=9, column=4, sticky=tk.W + tk.E, padx=5, pady=1)

        self.rounds_frame = tk.Frame(self.window, bg="#101010", bd=0, padx=5, pady=1)
        self.rounds_frame.grid(row=4, column=3, sticky=tk.W + tk.E, columnspan=2)

        btn = btk.MyButtonStyle(self.rounds_frame, "<", lambda: self._prev_next_round(True))
        # btn.btn.config()
        btn.btn.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.btn6_round = btk.MyOptMenuStyle(self.rounds_frame, "Round ??", [])
        self.btn6_round.btn.config(width=1)
        self.btn6_round.btn.grid(row=0, column=1, sticky=tk.W + tk.E)
        btn = btk.MyButtonStyle(self.rounds_frame, ">", lambda: self._prev_next_round())
        btn.btn.grid(row=0, column=2, sticky=tk.W + tk.E)
        # btn.btn.config()

        self.rounds_frame.grid_columnconfigure(0, minsize=0.15 * 0.2 * sizex, weight=1)
        self.rounds_frame.grid_columnconfigure(1, minsize=0.6 * 0.2 * sizex, weight=1)
        self.rounds_frame.grid_columnconfigure(2, minsize=0.15 * 0.2 * sizex, weight=1)
        self.rounds_frame.grid_propagate(False)

        self.label4_map = btk.MyLabelStyle(self.window, "Map")
        self.label4_map.frame.config(font=("", 11, "bold"), fg="green")
        self.label4_map.frame.grid(row=5, column=3, columnspan=2, sticky=tk.W + tk.E, padx=5)
        self.label5_server = btk.MyLabelStyle(self.window, "Server")
        self.label5_server.frame.config(font=("", 11, "bold"), fg="pink")
        self.label5_server.frame.grid(row=6, column=3, columnspan=2, sticky=tk.W + tk.E, padx=5)

        self.btn7_add_wl = btk.MyButtonStyle(self.window, "Add to WatchList", self._addto_watchlist)
        self.btn7_add_wl.btn.grid(row=7, column=3, columnspan=2, sticky=tk.W + tk.E, padx=5)

        self.btn8_watchlist = btk.MyButtonStyle(self.window, "WatchList", self._open_watchlist)
        self.btn8_watchlist.btn.grid(row=8, column=3, columnspan=2, sticky=tk.W + tk.E, padx=5)

        self.frame_scorehead = tk.Frame(self.window, bg="#101010", bd=0)  # width=sizex, height=20
        self.frame_scorehead.grid(row=4, column=0, columnspan=3, rowspan=6, sticky=tk.NSEW)

        self.label_teamct = btk.MyLabelStyle(self.frame_scorehead, "CT")
        self.label_teamct.frame.config(font=("", 16, "bold"), fg="#00bfff")
        self.label_teamct.frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        self.label_scorect = btk.MyLabelStyle(self.frame_scorehead, "0")
        self.label_scorect.frame.config(font=("", 16, ""))
        self.label_scorect.frame.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        # self.label_map = btk.MyLabelStyle(self.window, "-")
        # self.label_map.frame.grid(row=4, column=3, sticky=tk.W + tk.E, padx=5)
        self.label_scoresep = btk.MyLabelStyle(self.frame_scorehead, "-")
        self.label_scoresep.frame.config(font=("", 14, ""))
        self.label_scoresep.frame.grid(row=0, column=2)
        self.label_scoret = btk.MyLabelStyle(self.frame_scorehead, "0")
        self.label_scoret.frame.config(font=("", 16, ""))
        self.label_scoret.frame.grid(row=0, column=3, sticky=tk.NSEW, padx=5)
        self.label_teamt = btk.MyLabelStyle(self.frame_scorehead, "T")
        self.label_teamt.frame.config(font=("", 16, "bold"), fg="#df2020")
        self.label_teamt.frame.grid(row=0, column=4, sticky=tk.NSEW, padx=5)

        self.frame_scorehead.grid_columnconfigure(0, minsize=0.35 * 0.8 * sizex, weight=1)
        self.frame_scorehead.grid_columnconfigure(1, minsize=0.1375 * 0.8 * sizex, weight=1)
        self.frame_scorehead.grid_columnconfigure(2, minsize=0.025 * 0.8 * sizex, weight=1)
        self.frame_scorehead.grid_columnconfigure(3, minsize=0.1375 * 0.8 * sizex, weight=1)
        self.frame_scorehead.grid_columnconfigure(4, minsize=0.35 * 0.8 * sizex, weight=1)

        self.frame_stats = tk.Frame(self.window, bg="#101010", bd=0)  # width=sizex, height=20
        self.frame_stats.grid(row=5, column=0, columnspan=3, rowspan=6, sticky=tk.NSEW, pady=2)

        self.label_player1 = btk.MyLabelStyle(self.frame_stats, "???")
        self.label_player1.frame.grid(row=0, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player2 = btk.MyLabelStyle(self.frame_stats, "???")
        self.label_player2.frame.grid(row=1, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player3 = btk.MyLabelStyle(self.frame_stats, "???")
        self.label_player3.frame.grid(row=2, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player4 = btk.MyLabelStyle(self.frame_stats, "???")
        self.label_player4.frame.grid(row=3, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player5 = btk.MyLabelStyle(self.frame_stats, "???")
        self.label_player5.frame.grid(row=4, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player6 = btk.MyLabelStyle(self.frame_stats, "???")
        self.label_player6.frame.grid(row=0, column=7, sticky=tk.W + tk.E, padx=5)
        self.label_player7 = btk.MyLabelStyle(self.frame_stats, "???")
        self.label_player7.frame.grid(row=1, column=7, sticky=tk.W + tk.E, padx=5)
        self.label_player8 = btk.MyLabelStyle(self.frame_stats, "???")
        self.label_player8.frame.grid(row=2, column=7, sticky=tk.W + tk.E, padx=5)
        self.label_player9 = btk.MyLabelStyle(self.frame_stats, "???")
        self.label_player9.frame.grid(row=3, column=7, sticky=tk.W + tk.E, padx=5)
        self.label_player10 = btk.MyLabelStyle(self.frame_stats, "???")
        self.label_player10.frame.grid(row=4, column=7, sticky=tk.W + tk.E, padx=5)

        self.label_rank1 = btk.MyLabelStyle(self.frame_stats, "")
        self.label_rank1.frame.grid(row=0, column=2, sticky=tk.W + tk.E, padx=5)
        self.label_rank2 = btk.MyLabelStyle(self.frame_stats, "")
        self.label_rank2.frame.grid(row=1, column=2, sticky=tk.W + tk.E, padx=5)
        self.label_rank3 = btk.MyLabelStyle(self.frame_stats, "")
        self.label_rank3.frame.grid(row=2, column=2, sticky=tk.W + tk.E, padx=5)
        self.label_rank4 = btk.MyLabelStyle(self.frame_stats, "")
        self.label_rank4.frame.grid(row=3, column=2, sticky=tk.W + tk.E, padx=5)
        self.label_rank5 = btk.MyLabelStyle(self.frame_stats, "")
        self.label_rank5.frame.grid(row=4, column=2, sticky=tk.W + tk.E, padx=5)
        self.label_rank6 = btk.MyLabelStyle(self.frame_stats, "")
        self.label_rank6.frame.grid(row=0, column=6, sticky=tk.W + tk.E, padx=5)
        self.label_rank7 = btk.MyLabelStyle(self.frame_stats, "")
        self.label_rank7.frame.grid(row=1, column=6, sticky=tk.W + tk.E, padx=5)
        self.label_rank8 = btk.MyLabelStyle(self.frame_stats, "")
        self.label_rank8.frame.grid(row=2, column=6, sticky=tk.W + tk.E, padx=5)
        self.label_rank9 = btk.MyLabelStyle(self.frame_stats, "")
        self.label_rank9.frame.grid(row=3, column=6, sticky=tk.W + tk.E, padx=5)
        self.label_rank10 = btk.MyLabelStyle(self.frame_stats, "")
        self.label_rank10.frame.grid(row=4, column=6, sticky=tk.W + tk.E, padx=5)

        def lc_event1(event):
            link = g.profile_links[event.widget]
            if len(link) == 0:
                return
            if g.browser_path is None:
                web.open_new_tab(link)
            else:
                sp.Popen(g.browser_path + " " + link)

        def rc_event2(event):
            link = g.profile_links[event.widget]
            if len(link) == 0:
                return
            psteam64 = re.search(".*steamcommunity[.]com/profiles/(\d+)", link)
            psteam64 = psteam64.groups()[0]
            f.copy_to_clipboard(event.widget, psteam64)

        self.btn_rad1 = btk.MyCheckButtonStyle(self.frame_stats)
        self.btn_rad1.btn.grid(row=0, column=0, padx=5)
        self.btn_rad2 = btk.MyCheckButtonStyle(self.frame_stats)
        self.btn_rad2.btn.grid(row=1, column=0, padx=5)
        self.btn_rad3 = btk.MyCheckButtonStyle(self.frame_stats)
        self.btn_rad3.btn.grid(row=2, column=0, padx=5)
        self.btn_rad4 = btk.MyCheckButtonStyle(self.frame_stats)
        self.btn_rad4.btn.grid(row=3, column=0, padx=5)
        self.btn_rad5 = btk.MyCheckButtonStyle(self.frame_stats)
        self.btn_rad5.btn.grid(row=4, column=0, padx=5)
        self.btn_rad6 = btk.MyCheckButtonStyle(self.frame_stats)
        self.btn_rad6.btn.grid(row=0, column=8, padx=5)
        self.btn_rad7 = btk.MyCheckButtonStyle(self.frame_stats)
        self.btn_rad7.btn.grid(row=1, column=8, padx=5)
        self.btn_rad8 = btk.MyCheckButtonStyle(self.frame_stats)
        self.btn_rad8.btn.grid(row=2, column=8, padx=5)
        self.btn_rad9 = btk.MyCheckButtonStyle(self.frame_stats)
        self.btn_rad9.btn.grid(row=3, column=8, padx=5)
        self.btn_rad10 = btk.MyCheckButtonStyle(self.frame_stats)
        self.btn_rad10.btn.grid(row=4, column=8, padx=5)
        self._reset_chekcs()

        self.label_scorep1 = btk.MyLabelStyle(self.frame_stats, "0 / 0 / 0")
        self.label_scorep1.frame.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.label_scorep2 = btk.MyLabelStyle(self.frame_stats, "0 / 0 / 0")
        self.label_scorep2.frame.grid(row=1, column=3, sticky=tk.W, padx=5)
        self.label_scorep3 = btk.MyLabelStyle(self.frame_stats, "0 / 0 / 0")
        self.label_scorep3.frame.grid(row=2, column=3, sticky=tk.W, padx=5)
        self.label_scorep4 = btk.MyLabelStyle(self.frame_stats, "0 / 0 / 0")
        self.label_scorep4.frame.grid(row=3, column=3, sticky=tk.W, padx=5)
        self.label_scorep5 = btk.MyLabelStyle(self.frame_stats, "0 / 0 / 0")
        self.label_scorep5.frame.grid(row=4, column=3, sticky=tk.W, padx=5)
        self.label_scorep6 = btk.MyLabelStyle(self.frame_stats, "0 / 0 / 0")
        self.label_scorep6.frame.grid(row=0, column=5, sticky=tk.E, padx=5)
        self.label_scorep7 = btk.MyLabelStyle(self.frame_stats, "0 / 0 / 0")
        self.label_scorep7.frame.grid(row=1, column=5, sticky=tk.E, padx=5)
        self.label_scorep8 = btk.MyLabelStyle(self.frame_stats, "0 / 0 / 0")
        self.label_scorep8.frame.grid(row=2, column=5, sticky=tk.E, padx=5)
        self.label_scorep9 = btk.MyLabelStyle(self.frame_stats, "0 / 0 / 0")
        self.label_scorep9.frame.grid(row=3, column=5, sticky=tk.E, padx=5)
        self.label_scorep10 = btk.MyLabelStyle(self.frame_stats, "0 / 0 / 0")
        self.label_scorep10.frame.grid(row=4, column=5, sticky=tk.E, padx=5)

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

        self.frame_stats.grid_columnconfigure(0, minsize=0.05 * 0.8 * sizex, weight=1)
        self.frame_stats.grid_columnconfigure(1, minsize=0.2125 * 0.8 * sizex, weight=1)
        self.frame_stats.grid_columnconfigure(2, minsize=0.0875 * 0.8 * sizex, weight=1)
        self.frame_stats.grid_columnconfigure(3, minsize=0.1375 * 0.8 * sizex, weight=1)
        self.frame_stats.grid_columnconfigure(4, minsize=0.025 * 0.8 * sizex, weight=1)
        self.frame_stats.grid_columnconfigure(5, minsize=0.1375 * 0.8 * sizex, weight=1)
        self.frame_stats.grid_columnconfigure(6, minsize=0.0875 * 0.8 * sizex, weight=1)
        self.frame_stats.grid_columnconfigure(7, minsize=0.2125 * 0.8 * sizex, weight=1)
        self.frame_stats.grid_columnconfigure(8, minsize=0.05 * 0.8 * sizex, weight=1)

        self.frame_stats.grid_rowconfigure(0, minsize=30, weight=1)
        self.frame_stats.grid_rowconfigure(1, minsize=30, weight=1)
        self.frame_stats.grid_rowconfigure(2, minsize=30, weight=1)
        self.frame_stats.grid_rowconfigure(3, minsize=30, weight=1)
        self.frame_stats.grid_rowconfigure(4, minsize=30, weight=1)
        self.frame_stats.grid_propagate(False)

        self.frame_kills = tk.Frame(self.window, bg="#101010", bd=0)  # width=sizex, height=20
        self.frame_kills.grid(row=5, column=0, columnspan=3, rowspan=6, sticky=tk.NSEW, pady=2)
        self.frame_kills.grid_remove()

        self.label_atk1 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_atk1.frame.grid(row=0, column=0, sticky=tk.W + tk.E, padx=5)
        self.label_atk2 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_atk2.frame.grid(row=1, column=0, sticky=tk.W + tk.E, padx=5)
        self.label_atk3 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_atk3.frame.grid(row=2, column=0, sticky=tk.W + tk.E, padx=5)
        self.label_atk4 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_atk4.frame.grid(row=3, column=0, sticky=tk.W + tk.E, padx=5)
        self.label_atk5 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_atk5.frame.grid(row=4, column=0, sticky=tk.W + tk.E, padx=5)
        self.label_atk6 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_atk6.frame.grid(row=0, column=4, sticky=tk.W + tk.E, padx=5)
        self.label_atk7 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_atk7.frame.grid(row=1, column=4, sticky=tk.W + tk.E, padx=5)
        self.label_atk8 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_atk8.frame.grid(row=2, column=4, sticky=tk.W + tk.E, padx=5)
        self.label_atk9 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_atk9.frame.grid(row=3, column=4, sticky=tk.W + tk.E, padx=5)
        self.label_atk10 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_atk10.frame.grid(row=4, column=4, sticky=tk.W + tk.E, padx=5)

        self.label_weapon1 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_weapon1.frame.grid(row=0, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_weapon2 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_weapon2.frame.grid(row=1, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_weapon3 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_weapon3.frame.grid(row=2, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_weapon4 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_weapon4.frame.grid(row=3, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_weapon5 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_weapon5.frame.grid(row=4, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_weapon6 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_weapon6.frame.grid(row=0, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_weapon7 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_weapon7.frame.grid(row=1, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_weapon8 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_weapon8.frame.grid(row=2, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_weapon9 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_weapon9.frame.grid(row=3, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_weapon10 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_weapon10.frame.grid(row=4, column=5, sticky=tk.W + tk.E, padx=5)

        self.label_ded1 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_ded1.frame.grid(row=0, column=2, sticky=tk.W + tk.E, padx=5)
        self.label_ded2 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_ded2.frame.grid(row=1, column=2, sticky=tk.W + tk.E, padx=5)
        self.label_ded3 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_ded3.frame.grid(row=2, column=2, sticky=tk.W + tk.E, padx=5)
        self.label_ded4 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_ded4.frame.grid(row=3, column=2, sticky=tk.W + tk.E, padx=5)
        self.label_ded5 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_ded5.frame.grid(row=4, column=2, sticky=tk.W + tk.E, padx=5)
        self.label_ded6 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_ded6.frame.grid(row=0, column=6, sticky=tk.W + tk.E, padx=5)
        self.label_ded7 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_ded7.frame.grid(row=1, column=6, sticky=tk.W + tk.E, padx=5)
        self.label_ded8 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_ded8.frame.grid(row=2, column=6, sticky=tk.W + tk.E, padx=5)
        self.label_ded9 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_ded9.frame.grid(row=3, column=6, sticky=tk.W + tk.E, padx=5)
        self.label_ded10 = btk.MyLabelStyle(self.frame_kills, "")
        self.label_ded10.frame.grid(row=4, column=6, sticky=tk.W + tk.E, padx=5)

        self.frame_kills.grid_columnconfigure(0, minsize=0.2 * 0.8 * sizex, weight=1)
        self.frame_kills.grid_columnconfigure(1, minsize=0.09 * 0.8 * sizex, weight=1)
        self.frame_kills.grid_columnconfigure(2, minsize=0.2 * 0.8 * sizex, weight=1)
        self.frame_kills.grid_columnconfigure(3, minsize=0.02 * 0.8 * sizex, weight=1)
        self.frame_kills.grid_columnconfigure(4, minsize=0.2 * 0.8 * sizex, weight=1)
        self.frame_kills.grid_columnconfigure(5, minsize=0.09 * 0.8 * sizex, weight=1)
        self.frame_kills.grid_columnconfigure(6, minsize=0.2 * 0.8 * sizex, weight=1)

        self.frame_kills.grid_rowconfigure(0, minsize=30, weight=1)
        self.frame_kills.grid_rowconfigure(1, minsize=30, weight=1)
        self.frame_kills.grid_rowconfigure(2, minsize=30, weight=1)
        self.frame_kills.grid_rowconfigure(3, minsize=30, weight=1)
        self.frame_kills.grid_rowconfigure(4, minsize=30, weight=1)
        self.frame_kills.grid_propagate(False)

        for i2 in range(1, 11):
            g.profile_links.update({getattr(self, "label_player" + str(i2)).frame: ""})
            if i2 < 6:
                getattr(self, "label_player" + str(i2)).frame.config(cursor="hand2", anchor=tk.W, fg="#00bfff")
            else:
                getattr(self, "label_player" + str(i2)).frame.config(cursor="hand2", anchor=tk.E, fg="#df2020")
            getattr(self, "label_player" + str(i2)).frame.bind("<Button-1>", lc_event1)
            getattr(self, "label_player" + str(i2)).frame.bind("<Button-3>", rc_event2)
            getattr(self, "label_scorep" + str(i2)).frame.config(font=("", 12, ""))
            getattr(self, "label_rank" + str(i2)).frame.config(fg="#aaff00")

        self.window.grid_columnconfigure(0, minsize=0.34 * sizex, weight=1)
        self.window.grid_columnconfigure(1, minsize=0.31 * sizex, weight=1)
        self.window.grid_columnconfigure(2, minsize=0.15 * sizex, weight=1)
        self.window.grid_columnconfigure(3, minsize=0.1 * sizex, weight=1)
        self.window.grid_columnconfigure(4, minsize=0.1 * sizex, weight=1)
        self.window.grid_propagate(False)

        # self.window.grid_rowconfigure(0, minsize=0.06 * sizey, weight=1)
        # self.window.grid_rowconfigure(1, minsize=0.14 * sizey, weight=1)
        # self.window.grid_rowconfigure(2, minsize=0.1 * sizey, weight=1)
        # self.window.grid_rowconfigure(3, minsize=0.05 * sizey, weight=1)
        # self.window.grid_rowconfigure(4, minsize=0.1 * sizey, weight=1)
        self.window.grid_rowconfigure(5, minsize=30, weight=1)
        self.window.grid_rowconfigure(6, minsize=30, weight=1)
        self.window.grid_rowconfigure(7, minsize=30, weight=1)
        self.window.grid_rowconfigure(8, minsize=30, weight=1)
        self.window.grid_rowconfigure(9, minsize=30, weight=1)

        self.window.update_idletasks()
