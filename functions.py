import os
import sys
import inspect as i
import shutil
import datetime as dt
import threading as t
import platform
import winreg as wr
import bz2
import subprocess as sp
import webbrowser as web
import tkinter as tk

import scapy.all as scpa
import scapy.layers.http as scplh
import requests as req
import PIL.Image as pili
import PIL.ImageTk as piltk

import myglobals as g
import AlertWindow as AW
import UpdateAlertWindow as UW
import WatchPlayer as WP
import csgo_demoparser.DemoParser as dp
import round_stats_functions as my


def check_new_version():
    resp = req.get(g.PROJECT_LINK_LATEST)
    if resp.status_code == req.codes.ok:
        last_ver = resp.url[resp.url.find("/releases/tag/") + 14:]
        last_ver_list = last_ver.split(".")
        this_ver = g.VERSION.split(".")
        for idx in range(max(len(this_ver), len(last_ver_list))):
            try:
                this_int = int(this_ver[idx])
            except IndexError:
                UW.MyUpdateWindow(g.app.window, last_ver, g.VERSION)
                return
            try:
                last_int = int(last_ver_list[idx])
            except IndexError:
                print("You have a newer version than on Github")
                return
            if last_int > this_int:
                UW.MyUpdateWindow(g.app.window, last_ver, g.VERSION)
                return
            elif last_int < this_int:
                print("You have a newer version than on Github")
                return


def update_time_label(label):
    # global g.event_pkt_found, g.found_time
    while True:
        if g.found_time is not None:
            minutes = dt.datetime.now() - g.found_time
            label.text.set("LINK found {} minutes ago".format(int(minutes.total_seconds() / 60)))
            g.event_pkt_found.clear()
        g.event_pkt_found.wait(60)


def process_packet(window):
    def find_url(pkt):
        # global g.event_pkt_found, g.found_time
        url = pkt[scplh.HTTPRequest].Host.decode() + pkt[scplh.HTTPRequest].Path.decode()
        if url.find("/730/") != -1 and url.find(".dem.bz2") != -1 and url != window.entry1_url.text.get():
            g.found_time = dt.datetime.now()
            g.list_links.append(url)
            window.entry1_url.text.set(url)
            window.label2_count.text.set("Total DEMOs: " + str(len(g.list_links)))
            g.event_pkt_found.set()
            window.update_stats()
            if g.settings_dict["stop_label"] is True:
                window.start_stop()
            if g.settings_dict["auto_dl"] is True:
                open_link(window.entry1_url.text.get(), window.btn3_download)
            else:
                r = req.get("http://" + url)
                size_total = int(r.headers["Content-Length"])
                size_total_mb = str(int(size_total / (1 << 20))) + "MB"
                window.btn3_download.text.set("Download DEMO  " + size_total_mb)

    return find_url


def find_browser_path():
    if platform.platform().lower().find("windows") != -1:
        key = wr.OpenKey(wr.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.html\UserChoice")
        key2 = wr.QueryValueEx(key, "ProgId")[0]
        key.Close()
        key = wr.OpenKey(wr.HKEY_CLASSES_ROOT, key2 + r"\shell\open\command")
        key2 = wr.QueryValueEx(key, None)[0]
        key.Close()
        return key2[:key2[1:].find("\"") + 2]
    else:
        print("you are not using windows")
        return None


def find_file_path(exe=False):
    if getattr(sys, "frozen", False):
        temp = sys.executable
        g.path_resources = sys._MEIPASS + "\\"
        return os.path.dirname(temp) + "\\" if exe else os.path.dirname(temp) + r"\replays" + "\\"
    else:
        temp = os.path.abspath(i.getsourcefile(lambda: 0))
        temp = temp[:temp.rfind("\\")]
        g.path_resources = temp + "\\"
        return temp + "\\" if exe else temp + r"\replays" + "\\"


def get_interfaces():
    if platform.platform().lower().find("windows") != -1:
        res = scpa.get_windows_if_list()
    else:
        res = scpa.get_if_list()
    interfaces_list = ["None  (select this if not sure)"]
    for x in res:
        interfaces_list.append(x["name"])
    return interfaces_list


def return_interface(window):
    if window.btn1_interfaces.text.get() == window.btn1_interfaces.menu.entrycget(0, "label"):
        return None
    else:
        return window.btn1_interfaces.text.get()


def check_npcap(window):
    try:
        scpa.sniff(count=1, iface=None, store=False)
        return True
    except RuntimeError:
        AW.MyAlertWindow(window.window,
                         "Can't find npcap. Get it from: " + g.npcap_link +
                         "\nPress the DOWNLOAD button to go to the link")
        window.entry1_url.text.set(g.npcap_link)
        window.label3_time.text.set("npcap error")
        return False
    except:
        AW.MyAlertWindow(window.window,
                         "Unknown npcap error. Try to reinstall or get the latest version from: \n" + g.npcap_link +
                         "\nPress the DOWNLOAD button to go to the link")
        window.entry1_url.text.set(g.npcap_link)
        window.label3_time.text.set("npcap error")
        return False


def save_settings():
    # global g.settings_dict, g.exec_path
    try:
        file = open(g.path_exec_folder + "ow_config", "w")
    except Exception:
        AW.MyAlertWindow(g.app.window, "Error saving settings to file")
        return
    for x in g.settings_dict.items():
        file.write(str(x) + "\n")
    file.close()


def import_settings():
    # global g.settings_dict, g.exec_path
    g.browser_path = find_browser_path()
    g.path_exec_folder = find_file_path(True)
    try:
        file = open(g.path_exec_folder + "ow_config", "r")
    except Exception:
        import_settings_extra()
        return
    for line in file:
        sett = line[2:line.find(",") - 1]
        if g.settings_dict.get(sett) is None:
            continue
        val = line[line.find(",") + 2:-2]
        if sett == "dl_loc":
            val = val.replace(r"\\", "\\")
        if val == "True":
            g.settings_dict[sett] = True
        elif val == "False":
            g.settings_dict[sett] = False
        else:
            if sett not in ("dl_loc", "rename"):
                continue
            g.settings_dict[sett] = val[1:-1]
    import_settings_extra()
    file.close()


def import_settings_extra():
    if not len(g.settings_dict["dl_loc"]):
        g.settings_dict["dl_loc"] = find_file_path()
    label_size = (g.app.label_rank1.frame.winfo_width(), g.app.label_rank1.frame.winfo_height())
    g.RANK_TRANSLATE_IMG = {
        0: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\0.png").resize(label_size, pili.ANTIALIAS)),
        1: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\1.png").resize(label_size, pili.ANTIALIAS)),
        2: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\2.png").resize(label_size, pili.ANTIALIAS)),
        3: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\3.png").resize(label_size, pili.ANTIALIAS)),
        4: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\4.png").resize(label_size, pili.ANTIALIAS)),
        5: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\5.png").resize(label_size, pili.ANTIALIAS)),
        6: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\6.png").resize(label_size, pili.ANTIALIAS)),
        7: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\7.png").resize(label_size, pili.ANTIALIAS)),
        8: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\8.png").resize(label_size, pili.ANTIALIAS)),
        9: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\9.png").resize(label_size, pili.ANTIALIAS)),
        10: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\10.png").resize(label_size, pili.ANTIALIAS)),
        11: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\11.png").resize(label_size, pili.ANTIALIAS)),
        12: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\12.png").resize(label_size, pili.ANTIALIAS)),
        13: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\13.png").resize(label_size, pili.ANTIALIAS)),
        14: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\14.png").resize(label_size, pili.ANTIALIAS)),
        15: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\15.png").resize(label_size, pili.ANTIALIAS)),
        16: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\16.png").resize(label_size, pili.ANTIALIAS)),
        17: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\17.png").resize(label_size, pili.ANTIALIAS)),
        18: piltk.PhotoImage(pili.open(fr"{g.path_resources}resources\csgo_rank_icons\18.png").resize(label_size, pili.ANTIALIAS)),
    }
    for i2 in range(1, 11):
        getattr(g.app, "label_rank" + str(i2)).frame.config(image=g.RANK_TRANSLATE_IMG[0])
    g.RANK_TRANSLATE_WL = g.RANK_TRANSLATE_IMG


def download_from_link(link, button):
    # global g.settings_dict
    if not len(link):
        return
    r = req.get(link, stream=True)
    chunk_size = 16384
    size_total = int(r.headers["Content-Length"])
    size_total_mb = str(int(size_total / (1 << 20))) + "MB"
    size_curr = 0
    if g.settings_dict["rename_dl"] is False:
        name = g.list_links[-1][g.list_links[-1].rfind("/") + 1:]
    else:
        name = g.settings_dict["rename"] + ".dem.bz2"
    try:
        os.makedirs(g.settings_dict["dl_loc"], exist_ok=True)
        i2 = 1
        while os.path.isfile(g.settings_dict["dl_loc"] + name[:-4]):
            if i2 == 1:
                name = name[:-8] + str(i2) + ".dem.bz2"
            else:
                name = name[:-(8 + len(str(i2)))] + str(i2) + ".dem.bz2"
            i2 += 1
        dest1 = open(g.settings_dict["dl_loc"] + name, "wb")
    except Exception:
        AW.MyAlertWindow(g.app.window, "Error downloading file")
        button.text.set("Download DEMO")
        return
    with dest1 as dest:
        for chunk in r.iter_content(chunk_size=chunk_size):
            dest.write(chunk)
            percent = int(size_curr / size_total * 100)
            button.text.set(str(percent) + "%  of  " + size_total_mb)
            size_curr += chunk_size
    button.text.set("extracting...")
    name = name[:name.rfind(".")]
    try:
        file1 = bz2.BZ2File(g.settings_dict["dl_loc"] + name + ".bz2")
        dest1 = open(g.settings_dict["dl_loc"] + name, "wb")
    except Exception:
        AW.MyAlertWindow(g.app.window, "Error extracting file")
        button.text.set("Download DEMO")
        return
    with file1 as file, dest1 as dest:
        shutil.copyfileobj(file, dest, chunk_size)
    os.remove(g.settings_dict["dl_loc"] + name + ".bz2")
    analyze_demo(g.settings_dict["dl_loc"] + name, button)
    if g.settings_dict["delete_after"] is True:
        os.remove(g.settings_dict["dl_loc"] + name)


def analyze_demo(path, button):
    # global g.demo_stats, g.demo_nrplayers
    button.text.set("analyzing...")
    g.demo_stats = dp.DemoParser(path, ent="NONE")
    g.demo_stats.subscribe_to_event("parser_start", my.new_demo)
    g.demo_stats.subscribe_to_event("gevent_player_team", my.player_team)
    g.demo_stats.subscribe_to_event("gevent_player_death", my.player_death)
    g.demo_stats.subscribe_to_event("gevent_player_spawn", my.player_spawn)
    g.demo_stats.subscribe_to_event("gevent_bot_takeover", my.bot_takeover)
    g.demo_stats.subscribe_to_event("gevent_begin_new_match", my.begin_new_match)
    g.demo_stats.subscribe_to_event("gevent_round_end", my.round_end)
    g.demo_stats.subscribe_to_event("gevent_round_officially_ended", my.round_officially_ended)
    g.demo_stats.subscribe_to_event("parser_update_pinfo", my.update_pinfo)
    g.demo_stats.subscribe_to_event("cmd_dem_stop", my.cmd_dem_stop)
    # g.demo_stats.subscribe_to_event("parser_new_tick", analyze_progress(button))
    # try:
    g.demo_stats.parse()
    # except Exception as err:
    #     AW.MyAlertWindow(g.app.window, f"Error parsing demo!\n{err}\nPlease open a new issue with the download link for the demo")
    #     button.text.set("Download DEMO")
    #     return
    g.demo_ranks = dp.DemoParser(path, ent="STATS")
    g.demo_ranks.subscribe_to_event("parser_start", my.new_demo_ranks)
    g.demo_ranks.subscribe_to_event("parser_new_tick", my.get_ranks)
    try:
        g.demo_ranks.parse()
    except Exception:
        AW.MyAlertWindow(g.app.window, "Error parsing demo ranks\nStats are OK")
        for player in my.PLAYERS.values():
            player.rank = 0
    g.last_server = g.demo_ranks.header.server_name[:g.demo_ranks.header.server_name.find("(")-1]
    if g.last_server.find("Valve CS:GO ") != -1:
        g.last_server = g.last_server[12:]
    stringsearch = g.last_server.find(" Server")
    if stringsearch != -1:
        g.last_server = g.last_server[:stringsearch]
    g.demo_ranks = my.RANK_STATS
    for xuid, rank in g.demo_ranks.items():
        for player in my.PLAYERS.values():
            if xuid == player.userinfo.xuid:
                player.rank = rank
                break

    g.demo_stats = my.STATS
    g.demo_nrplayers = g.demo_stats["otherdata"]["nrplayers"]
    rounds_list = [None] * (len(g.demo_stats) - 1)
    for i2 in range(1, len(g.demo_stats)):
        rounds_list[i2 - 1] = "Round " + str(i2)
    g.app.btn6_round.update(rounds_list, cmd=g.app.update_stats)
    # g.app.btn6_round.text.set("Round " + str(len(g.demo_stats) - 2))
    tempmap = g.demo_stats["otherdata"]["map"]
    tempmapidx = tempmap.find("_scrimmagemap")
    if tempmapidx != -1:
        tempmap = tempmap[:tempmapidx]
    g.app.label4_map.text.set(tempmap)
    g.app.label5_server.text.set(g.last_server)
    if len(tempmap) > g.TEXT_CUTOUT_MAPSERV:
        g.app.label4_map.frame.config(anchor=tk.W)
    if len(g.last_server) > g.TEXT_CUTOUT_MAPSERV:
        g.app.label5_server.frame.config(anchor=tk.W)
    # swapping player names for the one they used on first join
    for xuid, pfname in g.demo_stats["otherdata"]["PFN"].items():
        for player in my.PLAYERS.values():
            if xuid == str(player.userinfo.xuid):
                # print(f"{player.name} <=> {pfname}")
                player.name = pfname
                break
    g.app.btn6_round.text.set(f"Round {len(g.demo_stats) - 1}")
    g.app.update_stats(len(g.demo_stats) - 1)
    button.text.set("Download DEMO")


def open_link(link, button, nodemo=False):
    # global g.browser_path, g.thread_download
    if link == "":
        return
    if link == g.npcap_link or nodemo:
        if g.browser_path is None:
            web.open_new_tab(link)
        else:
            sp.Popen(g.browser_path + " " + link)
        return
    link = "http://" + link
    if g.thread_download.is_alive() or g.thread_analyze.is_alive():
        AW.MyAlertWindow(g.app.window, "Download or analyze in progress, please wait!")
        return
    if g.settings_dict["browser_dl"] is True:
        if g.browser_path is None:
            web.open_new_tab(link)
        else:
            sp.Popen(g.browser_path + " " + link)
    else:
        g.thread_download = t.Thread(target=lambda: download_from_link(link, button), daemon=True)
        g.thread_download.start()


def copy_to_clipboard(root, text: str or list):
    if len(text) == 0:
        return
    root.clipboard_clear()
    if type(text) is str:
        root.clipboard_append(text)
    else:
        nice_list = ""
        for x in text:
            nice_list = nice_list + root.get(x) + "\n"
        root.clipboard_append(nice_list)


def calc_window_pos(x, y):
    if x.winfo_height() - y.winfo_height() < 0:
        return x.winfo_x() + (x.winfo_width() - y.winfo_width()) / 2, x.winfo_y()
    return x.winfo_x() + (x.winfo_width() - y.winfo_width()) / 2, x.winfo_y() + (
            x.winfo_height() - y.winfo_height()) / 2


def check_vac(window):
    # global g.thread_check_vac
    window.close_and_update()
    g.thread_check_vac = t.Thread(target=actual_check_vac, daemon=True)
    g.thread_check_vac.start()
    AW.MyAlertWindow(g.app.window, "Started checking for new VAC bans\n1 player / sec")


def actual_check_vac():
    # global g.event_check_vac
    newbans = 0
    newpb = ""
    failed = 0
    try:
        rfile = open(g.path_exec_folder + "watchlist", "r", encoding="utf-8")
        wfile = open(g.path_exec_folder + "watchlist.temp", "w", encoding="utf-8")
    except Exception:
        AW.MyAlertWindow(g.app.window, "Error4 opening WatchList")
        return
    for line in rfile:
        player = WP.MyWatchPlayer(line)
        if player.banned == "Y":
            wfile.write(player.ret_string())
            continue
        r = req.get(player.link)
        if r.status_code == req.codes.ok:
            i3 = r.content.find(b" day(s) since last ban")
            if i3 == -1:
                wfile.write(player.ret_string())
                continue
            data = r.content[:i3]
            days = data[data.rfind(b"\t") + 1:i3].decode("utf-8")
            delta = str(dt.datetime.now() - player.dtt)
            delta = delta[:delta.find(" day")]
            try:
                days = int(days)
                delta = int(delta)
            except Exception:
                delta = 0
            if days in (0, 1) or days <= delta:
                newbans += 1
                player.banned = "Y"
                newpb += player.name + "\n"
            wfile.write(player.ret_string())
        else:
            failed += 1
            wfile.write(player.ret_string())
        g.event_check_vac.wait(1)
    wfile.close()
    rfile.close()
    g.event_check_vac.wait(3)
    os.remove(g.path_exec_folder + "watchlist")
    os.rename(g.path_exec_folder + "watchlist.temp", g.path_exec_folder + "watchlist")
    text = "{} new bans.\n".format(newbans)
    text += newpb
    if failed > 0:
        text += "Failed to check {} players".format(failed)
    AW.MyAlertWindow(g.app.window, text)


def analyze_progress(btn):
    def analyze_progress2(data):
        btn.text.set("analyzing... {} %".format(int(data)))
    return analyze_progress2


def placeholder():
    print("test", g.app.window.winfo_width(), g.app.window.winfo_height())
