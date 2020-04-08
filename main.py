import os
import inspect as i
import shutil
import tkinter as tk
import tkinter.filedialog as tkfd
import scapy.all as scpa
import scapy.layers.http as scplh
import datetime as dt
import threading as t
import winreg as wr
import subprocess as sp
import webbrowser as web
import platform
import requests as req
import bz2
from csgo_demoparser.DemoParser import DemoParser

settings_dict = {
    "dl_loc": "",
    "rename": "OW_replay",
    "stop_label": False,
    "browser_dl": False,
    "rename_dl": False,
    "auto_dl": True,
    "delete_after": True
}
list_links = []
profile_links = {}
# browser_path = None
# exec_path = None
demo_stats = None
demo_nrplayers = 10
npcap_link = "https://nmap.org/npcap/dist/npcap-0.9988.exe"
found_time = None
thread_sniff = t.Thread()
thread_download = t.Thread()
thread_analyze = t.Thread()
event_pkt_found = t.Event()


def update_time_label(label):
    global event_pkt_found, found_time
    while True:
        if found_time is not None:
            minutes = dt.datetime.now() - found_time
            label.text.set("LINK found {} minutes ago".format(int(minutes.total_seconds() / 60)))
            event_pkt_found.clear()
        event_pkt_found.wait(60)


def process_packet(window):
    def find_url(pkt):
        global event_pkt_found, found_time
        url = pkt[scplh.HTTPRequest].Host.decode() + pkt[scplh.HTTPRequest].Path.decode()
        if url.find("/730/") != -1 and url != window.entry1_url.text.get():
            found_time = dt.datetime.now()
            list_links.append(url)
            window.entry1_url.text.set(url)
            window.label2_count.text.set("Total DEMOs: " + str(len(list_links)))
            event_pkt_found.set()
            window.update_stats()
            if settings_dict["stop_label"] is True:
                window.start_stop()
            if settings_dict["auto_dl"] is True:
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


def find_file_path(exe=None):
    temp = os.path.abspath(i.getsourcefile(lambda: 0))
    temp = temp[:temp.rfind("\\")]
    if exe is not None:
        return temp + "\\"
    temp = temp + r"\replays" + "\\"
    return temp


def get_interfaces():
    interfaces_list = ["None  (select this if not sure)"]
    for x in scpa.IFACES.data.values():
        if str(x).find("Unknown") != -1:
            continue
        interfaces_list.append(str(x)[19:str(x).find("{") - 2])
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
        MyAlertWindow(window.window,
                      "Can't find npcap. Get it from  " + npcap_link + "\nPress the DOWNLOAD button to go to the link")
        window.entry1_url.text.set(npcap_link)
        window.label3_time.text.set("npcap error")
        return False


def save_settings():
    global settings_dict, exec_path
    try:
        file = open(exec_path + "ow_config", "w")
    except Exception:
        MyAlertWindow(app.window, "Error saving settings to file")
        return
    for x in settings_dict.items():
        file.write(str(x) + "\n")
    file.close()


def import_settings():
    global settings_dict, exec_path
    try:
        file = open(exec_path + "ow_config", "r")
    except Exception:
        return
    for line in file:
        sett = line[2:line.find(",") - 1]
        val = line[line.find(",") + 2:-2]
        if sett == "dl_loc":
            val = val.replace(r"\\", "\\")
        if val == "True":
            settings_dict[sett] = True
        elif val == "False":
            settings_dict[sett] = False
        else:
            if sett not in ("dl_loc", "rename"):
                continue
            settings_dict[sett] = val[1:-1]
    file.close()


def download_from_link(link, button):
    global settings_dict
    if not len(link):
        return
    r = req.get(link, stream=True)
    chunk_size = 16384
    size_total = int(r.headers["Content-Length"])
    size_total_mb = str(int(size_total / (1 << 20))) + "MB"
    size_curr = 0
    btn_name = button.text.get()
    if settings_dict["rename_dl"] is False:
        name = list_links[-1][list_links[-1].rfind("/") + 1:]
    else:
        name = settings_dict["rename"] + ".dem.bz2"
    try:
        os.makedirs(settings_dict["dl_loc"], exist_ok=True)
        i2 = 1
        while os.path.isfile(settings_dict["dl_loc"] + name[:-4]):
            if i2 == 1:
                name = name[:-8] + str(i2) + ".dem.bz2"
            else:
                name = name[:-(8 + len(str(i2)))] + str(i2) + ".dem.bz2"
            i2 += 1
        dest1 = open(settings_dict["dl_loc"] + name, "wb")
    except Exception:
        MyAlertWindow(app.window, "Error downloading file")
        button.text.set(btn_name)
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
        file1 = bz2.BZ2File(settings_dict["dl_loc"] + name + ".bz2")
        dest1 = open(settings_dict["dl_loc"] + name, "wb")
    except Exception:
        MyAlertWindow(app.window, "Error extracting file")
        button.text.set(btn_name)
        return
    with file1 as file, dest1 as dest:
        shutil.copyfileobj(file, dest, chunk_size)
    os.remove(settings_dict["dl_loc"] + name + ".bz2")
    try:
        analyze_demo(settings_dict["dl_loc"] + name, button, btn_name)
    except:
        MyAlertWindow(app.window, "Error parsing demo")
    if settings_dict["delete_after"] is True:
        os.remove(settings_dict["dl_loc"] + name)


def analyze_demo(path, button, btn_name):
    global demo_stats, demo_nrplayers
    button.text.set("analyzing...")
    demo_stats = DemoParser(path)
    demo_stats = demo_stats.parse()
    demo_nrplayers = demo_stats["nrplayers"]
    rounds_list = [None] * (len(demo_stats) - 2)
    for i2 in range(1, len(demo_stats) - 1):
        rounds_list[i2 - 1] = "Round " + str(i2)
    app.btn6_round.update(rounds_list, cmd=app.update_stats)
    # app.btn6_round.text.set("Round " + str(len(demo_stats) - 2))
    app.update_stats(len(demo_stats) - 2)
    button.text.set(btn_name)


def open_link(link, button):
    global browser_path, thread_download
    if link == "":
        return
    link = "http://" + link
    if thread_download.is_alive() or thread_analyze.is_alive():
        MyAlertWindow(app.window, "Download or analyze in progress, please wait!")
        return
    if settings_dict["browser_dl"] is True:
        if browser_path is None:
            web.open_new_tab(link)
        else:
            sp.Popen(browser_path + " " + link)
    else:
        thread_download = t.Thread(target=lambda: download_from_link(link, button), daemon=True)
        thread_download.start()


def copy_to_clipboard(root, text: str or list):
    root.clipboard_clear()
    if type(text) is str:
        root.clipboard_append(text)
    elif len(text) > 0:
        nice_list = ""
        for x in text:
            nice_list = nice_list + root.get(x) + "\n"
        root.clipboard_append(nice_list)


def calc_window_pos(x, y):
    return x.winfo_x() + (x.winfo_width() - y.winfo_width()) / 2, x.winfo_y() + (
            x.winfo_height() - y.winfo_height()) / 2


def placeholder():
    print("test")


class MyButtonStyle:
    def __init__(self, root, label, cmd, name=None):
        self.text = tk.StringVar()
        self.text.set(label)
        self.btn = tk.Button(root, textvariable=self.text, command=cmd, name=name)
        self.btn.config(font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040", bd=3)


class MyOptMenuStyle:
    def __init__(self, root, label, options: list):
        self.text = tk.StringVar()
        self.text.set(label)
        self.btn = tk.OptionMenu(root, self.text, "")
        self.btn.config(anchor=tk.W, font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040")
        self.menu = self.btn["menu"]
        self.update(options)
        self.menu.config(font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040")

    def _cmd_new(self, cmd, value):
        self.text.set(value)
        cmd(int(value[6:]))

    def update(self, options, cmd=None):
        self.menu.delete(0, tk.END)
        if len(options) > 0:
            for opt in options:
                if cmd:
                    self.menu.add_command(label=opt, command=lambda label2=opt: self._cmd_new(cmd, label2))
                else:
                    self.menu.add_command(label=opt, command=lambda label2=opt: self.text.set(label2))
        self.menu.update_idletasks()


class MyListboxStyle:
    def __init__(self, root, items: list):
        self.box = tk.Listbox(root)
        self.items_box = tk.StringVar(value=items)
        if len(items) > 0:
            length = len(items[-1])
            vlength = len(items)
        else:
            length = 5
            vlength = 5
        self.box.config(activestyle=tk.NONE, listvariable=self.items_box, width=length + 2,
                        height=vlength + 1, selectmode=tk.MULTIPLE, font=("arial", 10, ""), fg="white",
                        bg="#101010", borderwidth=5)
        self.menu = MyMenuStyle(self.box)
        self.menu.menu.add_command(label="Copy selected",
                                   command=lambda: copy_to_clipboard(self.box, self.box.curselection()))
        self.menu.menu.add_command(label="Select all",
                                   command=lambda: self.box.selection_set(0, tk.END))
        self.menu.menu.add_command(label="Deselect all",
                                   command=lambda: self.box.selection_clear(0, tk.END))

        def rc_event2(event):
            self.menu.menu.post(event.x_root, event.y_root)

        self.box.bind("<Button-3>", rc_event2)


class MyLabelStyle:
    def __init__(self, root, label):
        self.text = tk.StringVar()
        self.text.set(label)
        self.frame = tk.Label(root, textvariable=self.text)
        self.frame.config(font=("arial", 10, ""), fg="white", bg="#101010")


class MyEntryStyle:
    def __init__(self, root, label):
        self.text = tk.StringVar()
        self.text.set(label)
        self.frame = tk.Entry(root, textvariable=self.text, state="readonly")
        self.frame.config(justify=tk.CENTER, font=("arial", 10, ""), borderwidth=2, bg="#f0f0f0",
                          readonlybackground="#f0f0f0")


class MyMenuStyle:
    def __init__(self, root):
        self.menu = tk.Menu(root)
        self.menu.config(tearoff=0, font=("arial", 10, ""), fg="white", bg="#101010")


class MyAlertWindow:
    def __init__(self, root, message):
        self.window = tk.Toplevel(root)
        self.window.title("error")
        self.window.minsize(100, 50)
        self.window.resizable(False, False)
        self.window.attributes("-topmost")
        self.window.config(bg="#101010")
        self.label = MyLabelStyle(self.window, message)
        self.label.frame.pack()
        self.btn_close = MyButtonStyle(self.window, "Close", self.window.destroy)
        self.btn_close.btn.pack()
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (calc_window_pos(root, self.window)))
        self.window.grab_set()
        self.window.focus_set()


class LinkListWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Past LINKs")
        self.window.minsize(150, 150)
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.label1_top = MyLabelStyle(self.window, "Oldest LINK on TOP")
        self.label1_top.frame.pack()
        self.box = MyListboxStyle(self.window, list_links)
        self.box.box.pack(fill=tk.BOTH, expand=1)
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (calc_window_pos(root, self.window)))
        self.window.grab_set()
        self.window.focus_set()
        self.box.box.selection_set(0)


class SettingsWindow:
    def _update_all_settings(self):
        self._update_buttons(self.btn_set1)
        self._update_buttons(self.btn_set2)
        self._update_buttons(self.btn_set3)
        self._update_buttons(self.btn_set5)
        self._update_buttons(self.btn_set6)
        if settings_dict["auto_dl"] and settings_dict["browser_dl"]:
            self._change_setting(self.btn_set2)
            self._change_setting(self.btn_set5)
        self._check_get_name(self.entry_demo)

    def _change_setting(self, button, value=None):
        if button.btn.winfo_name() == "auto_dl" and not settings_dict["auto_dl"] and settings_dict["browser_dl"]:
            self._change_setting(self.btn_set2)
        elif button.btn.winfo_name() == "browser_dl" and not settings_dict["browser_dl"] and settings_dict["auto_dl"]:
            self._change_setting(self.btn_set5)
        elif button.btn.winfo_name() == "rename_dl":
            self._check_get_name(self.entry_demo)
        # if value:
        #     if bool(settings_dict[button.btn.winfo_name()]) is True:
        #         settings_dict[button.btn.winfo_name()] = False
        #     else:
        #         settings_dict[button.btn.winfo_name()] = value
        # else:
        settings_dict[button.btn.winfo_name()] = not settings_dict[button.btn.winfo_name()]
        self._update_buttons(button)

    def _update_buttons(self, button):
        if settings_dict[button.btn.winfo_name()]:
            button.text.set("ON")
            button.btn.config(relief=tk.SUNKEN, bg="#404040", activebackground="#808080")
        else:
            button.text.set("OFF")
            button.btn.config(relief=tk.RAISED, bg="#101010", activebackground="#404040")

    def _set_download_path(self):
        global settings_dict
        path = tkfd.askdirectory() + "/"
        if path == "/":
            return
        self.entry_browse.text.set(path)
        settings_dict["dl_loc"] = path

    def _analyze_demo(self):
        global settings_dict, thread_analyze
        path = tkfd.askopenfilename()
        if path == "":
            return
        if thread_download.is_alive() or thread_analyze.is_alive():
            MyAlertWindow(app.window, "A demo is already being analyzed, please wait!")
            return
        app.update_stats()
        thread_analyze = t.Thread(target=lambda: analyze_demo(path, app.btn3_download, app.btn3_download.text.get()),
                                  daemon=True)
        thread_analyze.start()

    def _check_get_name(self, button):
        global settings_dict
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
        settings_dict["rename"] = name

    def _update_on_save(self):
        global settings_dict
        self._check_get_name(self.entry_demo)
        save_settings()

    def _destroy_checkname(self):
        self._check_get_name(self.entry_demo)
        self.window.destroy()

    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Settings")
        self.window.minsize(580, 330)
        sizex = self.window.minsize()[0]
        # sizey = self.window.minsize()[1]
        self.window.resizable(False, False)
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self._destroy_checkname)

        self.label_set1 = MyLabelStyle(self.window, "Stop scanning after a DEMO LINK is found")
        self.label_set1.frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set1 = MyButtonStyle(self.window, "OFF", lambda: self._change_setting(self.btn_set1), "stop_label")
        self.btn_set1.btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.label_set5 = MyLabelStyle(self.window, "Auto download DEMO after a LINK is found")
        self.label_set5.frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set5 = MyButtonStyle(self.window, "ON", lambda: self._change_setting(self.btn_set5), "auto_dl")
        self.btn_set5.btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.label_set2 = MyLabelStyle(self.window, "Use the browser to download (doesn't work with auto download)")
        self.label_set2.frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set2 = MyButtonStyle(self.window, "OFF", lambda: self._change_setting(self.btn_set2), "browser_dl")
        self.btn_set2.btn.grid(row=2, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.label_set3 = MyLabelStyle(self.window,
                                       "*" * 50 + "Download location when not using the browser" + "*" * 50)
        self.label_set3.frame.config(width=45)
        self.label_set3.frame.grid(row=3, column=0, sticky=tk.W + tk.E, pady=5, columnspan=4)
        self.btn_browse = MyButtonStyle(self.window, "Browse", self._set_download_path)
        self.btn_browse.btn.grid(row=4, column=0, sticky=tk.W + tk.E, padx=5)
        self.entry_browse = MyEntryStyle(self.window, settings_dict["dl_loc"])
        self.entry_browse.frame.grid(row=4, column=1, sticky=tk.W + tk.E, padx=5, columnspan=2)
        self.btn_opendl = MyButtonStyle(self.window, "Open",
                                        lambda: os.system("start {}".format(settings_dict["dl_loc"])))
        self.btn_opendl.btn.grid(row=4, column=3, sticky=tk.E, padx=5, pady=5)
        self.label_set3_1 = MyLabelStyle(self.window, "*" * 200)
        self.label_set3_1.frame.config(width=45)
        self.label_set3_1.frame.grid(row=5, column=0, sticky=tk.W + tk.E, columnspan=4)

        self.label_set4 = MyLabelStyle(self.window, "Rename downloaded demos to ")
        self.label_set4.frame.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        self.btn_set3 = MyButtonStyle(self.window, "ON", lambda: self._change_setting(self.btn_set3), "rename_dl")
        self.btn_set3.btn.grid(row=6, column=0, sticky=tk.W + tk.E, padx=5, pady=5)
        self.entry_demo = MyEntryStyle(self.window, settings_dict["rename"])
        self.entry_demo.frame.config(state="normal")
        self.entry_demo.frame.grid(row=6, column=2, sticky=tk.W + tk.E, padx=5, columnspan=2)

        self.label_set6 = MyLabelStyle(self.window, "Auto delete DEMO after it is analyzed")
        self.label_set6.frame.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set6 = MyButtonStyle(self.window, "ON", lambda: self._change_setting(self.btn_set6), "delete_after")
        self.btn_set6.btn.grid(row=7, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.btn_save = MyButtonStyle(self.window, "Save to file", self._update_on_save)
        self.btn_save.btn.grid(row=8, column=3, sticky=tk.E, padx=5, pady=5)

        self.btn_analyze = MyButtonStyle(self.window, "Analyze a demo", self._analyze_demo)
        self.btn_analyze.btn.grid(row=8, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        def lc_event1(event):
            link = self.label_github.text.get()
            if len(link) == 0:
                return
            if browser_path is None:
                web.open_new_tab(link)
            else:
                sp.Popen(browser_path + " " + link)
                
        self.label_github = MyLabelStyle(self.window, "https://github.com/ZaharX97/OWReveal")
        self.label_github.frame.config(cursor="hand2")
        self.label_github.frame.grid(row=8, column=1, padx=5, pady=5, columnspan=2)
        self.label_github.frame.bind("<Button-1>", lc_event1)

        self._update_all_settings()
        self.window.grid_columnconfigure(0, minsize=0.15 * sizex, weight=1)
        self.window.grid_columnconfigure(1, minsize=0.5 * sizex, weight=1)
        self.window.grid_columnconfigure(2, minsize=0.15 * sizex, weight=1)
        self.window.grid_columnconfigure(3, minsize=0.2 * sizex, weight=1)
        self.window.grid_propagate(False)
        self.window.update_idletasks()
        self.window.geometry("+%d+%d" % (calc_window_pos(root, self.window)))
        self.window.grab_set()
        self.window.focus_set()


class MainAppWindow:
    def start_stop(self):
        global thread_sniff
        if check_npcap(self) is False:
            return
        if self.btn1_interfaces.text.get() == "Select one interface":
            MyAlertWindow(self.window, "You need to select one network interface")
            return
        if self.btn2_start.text.get() == "Start":
            thread_sniff = scpa.AsyncSniffer(iface=return_interface(self),
                                             lfilter=lambda y: y.haslayer(scplh.HTTPRequest),
                                             prn=process_packet(self), store=False)
            thread_sniff.start()
            self.label1_dynamic.text.set("Looking for OW DEMO link")
            self.label1_dynamic.frame.config(fg="green")
            self.btn2_start.text.set("Stop")
            self.entry1_url.frame.delete(0, tk.END)
        else:
            thread_sniff.stop(join=False)
            self.label1_dynamic.text.set("Not looking for anything")
            self.label1_dynamic.frame.config(fg="red")
            self.btn2_start.text.set("Start")

    def update_stats(self, stats=None):
        # self.btn6_round.update([])
        if stats:
            # self.label_map.text.set(demo_stats["map"])
            indext = 0
            indexct = 0
            if demo_nrplayers == 10:
                if stats <= 15:
                    self.label_scorect.text.set(demo_stats[stats].score_team3)
                    self.label_scoret.text.set(demo_stats[stats].score_team2)
                    indext = 6
                    indexct = 1
                else:
                    self.label_scorect.text.set(demo_stats[stats].score_team2)
                    self.label_scoret.text.set(demo_stats[stats].score_team3)
                    indext = 1
                    indexct = 6
            elif demo_nrplayers == 4:
                if stats <= 8:
                    self.label_scorect.text.set(demo_stats[stats].score_team3)
                    self.label_scoret.text.set(demo_stats[stats].score_team2)
                    indext = 6
                    indexct = 1
                else:
                    self.label_scorect.text.set(demo_stats[stats].score_team2)
                    self.label_scoret.text.set(demo_stats[stats].score_team3)
                    indext = 1
                    indexct = 6
            if indext == 0:
                MyAlertWindow(app.window, "error reading players, max= {}".format(demo_nrplayers))
                return
            for p in range(demo_nrplayers):
                pname = demo_stats[stats].pscore[p].player.name
                # pname = "alongassstringtoseehowplayerswithlongnameslook"
                kda = "{} / {} / {}".format(demo_stats[stats].pscore[p].k, demo_stats[stats].pscore[p].a,
                                            demo_stats[stats].pscore[p].d)
                if demo_stats[stats].pscore[p].player.start_team == 2:
                    if (demo_nrplayers == 10 and stats <= 15) or (demo_nrplayers == 4 and stats <= 8):
                        if len(pname) > 24:
                            getattr(self, "label_player" + str(indext)).frame.config(anchor=tk.W)
                        else:
                            getattr(self, "label_player" + str(indext)).frame.config(anchor=tk.E)
                    getattr(self, "label_player" + str(indext)).text.set(pname)
                    profile_links.update(
                        {getattr(self, "label_player" + str(indext)).frame: demo_stats[stats].pscore[p].player.profile})
                    getattr(self, "label_scorep" + str(indext)).text.set(kda)
                    indext += 1
                elif demo_stats[stats].pscore[p].player.start_team == 3:
                    if (demo_nrplayers == 10 and stats > 15) or (demo_nrplayers == 4 and stats > 8):
                        if len(pname) > 24:
                            getattr(self, "label_player" + str(indexct)).frame.config(anchor=tk.W)
                        else:
                            getattr(self, "label_player" + str(indexct)).frame.config(anchor=tk.E)
                    getattr(self, "label_player" + str(indexct)).text.set(pname)
                    profile_links.update(
                        {getattr(self, "label_player" + str(indexct)).frame: demo_stats[stats].pscore[
                            p].player.profile})
                    getattr(self, "label_scorep" + str(indexct)).text.set(kda)
                    indexct += 1
            if indext == 3:
                for p in range(3):
                    getattr(self, "label_player" + str(indext)).text.set("")
                    getattr(self, "label_scorep" + str(indext)).text.set("")
                    getattr(self, "label_player" + str(indexct)).text.set("")
                    getattr(self, "label_scorep" + str(indexct)).text.set("")
                    indext += 1
                    indexct += 1
        else:
            self.btn6_round.update([])
            self.btn6_round.text.set("Select a round")
            # self.label_map.text.set("-")
            self.label_scorect.text.set(0)
            self.label_scoret.text.set(0)
            for p in range(1, 11):
                profile_links.update({getattr(self, "label_player" + str(p)).frame: ""})
                getattr(self, "label_player" + str(p)).text.set("???")
                getattr(self, "label_scorep" + str(p)).text.set("0 / 0 / 0")
                if p > 5:
                    getattr(self, "label_player" + str(p)).frame.config(anchor=tk.E)
        self.window.update_idletasks()

    def __init__(self, title, sizex, sizey):
        self.window = tk.Tk()
        self.window.title(title)
        self.window.minsize(sizex, sizey)
        # self.window.maxsize(sizex, sizey)
        # self.window.resizable(False, False)
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

        self.btn1_interfaces = MyOptMenuStyle(self.window, "Select one interface", get_interfaces())
        self.btn1_interfaces.btn.grid(row=0, column=0, sticky=tk.W + tk.E, columnspan=7, pady=5, padx=5)

        self.btn2_start = MyButtonStyle(self.window, "Start", self.start_stop)
        self.btn2_start.btn.config(font=("", 16, ""))
        self.btn2_start.btn.grid(row=0, column=7, columnspan=2, rowspan=2, sticky=tk.NSEW, padx=5, pady=5)

        self.label1_dynamic = MyLabelStyle(self.window, "Not looking for anything")
        self.label1_dynamic.frame.config(borderwidth=10, font=("", 14, "bold"), fg="red")
        self.label1_dynamic.frame.grid(row=1, column=0, columnspan=7)

        self.entry1_url = MyEntryStyle(self.window, "")
        self.entry1_url.frame.grid(row=2, column=0, sticky=tk.W + tk.E, columnspan=9, ipady=3, padx=5, pady=2)
        self.menu1_entry1_copy = MyMenuStyle(self.window)
        self.menu1_entry1_copy.menu.add_command(label="Copy",
                                                command=lambda: copy_to_clipboard(self.entry1_url.frame,
                                                                                  self.entry1_url.text.get()))

        def rc_event1(event):
            self.menu1_entry1_copy.menu.post(event.x_root, event.y_root)

        self.entry1_url.frame.bind("<Button-3>", rc_event1)

        self.label2_count = MyLabelStyle(self.window, "Total DEMOs: 0")
        self.label2_count.frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=5)

        self.label3_time = MyLabelStyle(self.window, "No LINK found")
        self.label3_time.frame.grid(row=3, column=2, columnspan=4, sticky=tk.W + tk.E, padx=5)

        self.btn3_download = MyButtonStyle(self.window, "Download DEMO",
                                           lambda: open_link(self.entry1_url.text.get(), self.btn3_download))
        self.btn3_download.btn.grid(row=3, column=7, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn4_link_list = MyButtonStyle(self.window, "LINK List", lambda: LinkListWindow(self.window))
        self.btn4_link_list.btn.grid(row=9, column=7, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn5_settings = MyButtonStyle(self.window, "Settings", lambda: SettingsWindow(self.window))
        self.btn5_settings.btn.grid(row=9, column=8, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn6_round = MyOptMenuStyle(self.window, "Select a round", [])
        self.btn6_round.btn.grid(row=4, column=7, sticky=tk.W + tk.E, columnspan=2, pady=5, padx=5)

        # self.btn7_add_wl = MyButtonStyle(self.window, "Add to Watchlist", placeholder)
        # self.btn7_add_wl.btn.grid(row=7, column=7, sticky=tk.W + tk.E, padx=5)

        self.label_teamct = MyLabelStyle(self.window, "CT")
        self.label_teamct.frame.config(font=("", 16, "bold"), fg="#00bfff")
        self.label_teamct.frame.grid(row=4, column=0, columnspan=2, sticky=tk.NSEW, padx=5)
        self.label_scorect = MyLabelStyle(self.window, "0")
        self.label_scorect.frame.config(font=("", 16, ""))
        self.label_scorect.frame.grid(row=4, column=2, sticky=tk.NSEW, padx=5)
        # self.label_map = MyLabelStyle(self.window, "-")
        # self.label_map.frame.grid(row=4, column=3, sticky=tk.W + tk.E, padx=5)
        self.label_scoresep = MyLabelStyle(self.window, "-")
        self.label_scoresep.frame.config(font=("", 14, ""))
        self.label_scoresep.frame.grid(row=4, column=3)
        self.label_scoret = MyLabelStyle(self.window, "0")
        self.label_scoret.frame.config(font=("", 16, ""))
        self.label_scoret.frame.grid(row=4, column=4, sticky=tk.NSEW, padx=5)
        self.label_teamt = MyLabelStyle(self.window, "T")
        self.label_teamt.frame.config(font=("", 16, "bold"), fg="#df2020")
        self.label_teamt.frame.grid(row=4, column=5, columnspan=2, sticky=tk.NSEW, padx=5)

        self.label_player1 = MyLabelStyle(self.window, "???")
        self.label_player1.frame.grid(row=5, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player2 = MyLabelStyle(self.window, "???")
        self.label_player2.frame.grid(row=6, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player3 = MyLabelStyle(self.window, "???")
        self.label_player3.frame.grid(row=7, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player4 = MyLabelStyle(self.window, "???")
        self.label_player4.frame.grid(row=8, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player5 = MyLabelStyle(self.window, "???")
        self.label_player5.frame.grid(row=9, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_player6 = MyLabelStyle(self.window, "???")
        self.label_player6.frame.grid(row=5, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_player7 = MyLabelStyle(self.window, "???")
        self.label_player7.frame.grid(row=6, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_player8 = MyLabelStyle(self.window, "???")
        self.label_player8.frame.grid(row=7, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_player9 = MyLabelStyle(self.window, "???")
        self.label_player9.frame.grid(row=8, column=5, sticky=tk.W + tk.E, padx=5)
        self.label_player10 = MyLabelStyle(self.window, "???")
        self.label_player10.frame.grid(row=9, column=5, sticky=tk.W + tk.E, padx=5)

        def lc_event1(event):
            link = profile_links[event.widget]
            if len(link) == 0:
                return
            if browser_path is None:
                web.open_new_tab(link)
            else:
                sp.Popen(browser_path + " " + link)

        self.label_scorep1 = MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep1.frame.grid(row=5, column=2, sticky=tk.W, padx=5)
        self.label_scorep2 = MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep2.frame.grid(row=6, column=2, sticky=tk.W, padx=5)
        self.label_scorep3 = MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep3.frame.grid(row=7, column=2, sticky=tk.W, padx=5)
        self.label_scorep4 = MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep4.frame.grid(row=8, column=2, sticky=tk.W, padx=5)
        self.label_scorep5 = MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep5.frame.grid(row=9, column=2, sticky=tk.W, padx=5)
        self.label_scorep6 = MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep6.frame.grid(row=5, column=4, sticky=tk.E, padx=5)
        self.label_scorep7 = MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep7.frame.grid(row=6, column=4, sticky=tk.E, padx=5)
        self.label_scorep8 = MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep8.frame.grid(row=7, column=4, sticky=tk.E, padx=5)
        self.label_scorep9 = MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep9.frame.grid(row=8, column=4, sticky=tk.E, padx=5)
        self.label_scorep10 = MyLabelStyle(self.window, "0 / 0 / 0")
        self.label_scorep10.frame.grid(row=9, column=4, sticky=tk.E, padx=5)

        # self.label_sep1 = MyLabelStyle(self.window, "|")
        # self.label_sep1.frame.grid(row=5, column=3, sticky=tk.W + tk.E, padx=5)
        # self.label_sep2 = MyLabelStyle(self.window, "|")
        # self.label_sep2.frame.grid(row=6, column=3, sticky=tk.W + tk.E, padx=5)
        # self.label_sep3 = MyLabelStyle(self.window, "|")
        # self.label_sep3.frame.grid(row=7, column=3, sticky=tk.W + tk.E, padx=5)
        # self.label_sep4 = MyLabelStyle(self.window, "|")
        # self.label_sep4.frame.grid(row=8, column=3, sticky=tk.W + tk.E, padx=5)
        # self.label_sep5 = MyLabelStyle(self.window, "|")
        # self.label_sep5.frame.grid(row=9, column=3, sticky=tk.W + tk.E, padx=5)

        for i2 in range(1, 11):
            profile_links.update({getattr(self, "label_player" + str(i2)).frame: ""})
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


if __name__ == "__main__":
    app = MainAppWindow("Another OW Revealer 2", 760, 350)
    thread_time = t.Thread(target=lambda: update_time_label(app.label3_time), daemon=True)
    thread_time.start()
    browser_path = find_browser_path()
    exec_path = find_file_path(True)
    import_settings()
    if not len(settings_dict["dl_loc"]):
        settings_dict["dl_loc"] = find_file_path()

    app.window.mainloop()
