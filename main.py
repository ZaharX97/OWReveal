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

list_settings = [
    ["stop_label", False],
    ["browser_dl", False],
    ["rename_dl", False]
]
list_links = list()
# browser_path = None
# download_path = None
# exec_path = None
npcap_link = "https://nmap.org/npcap/dist/npcap-0.9988.exe"
found_time = None
thread_sniff = None
thread_download = t.Thread()
event_pkt_found = t.Event()
event_dl_finished = t.Event()


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
            r = req.get("http://" + url)
            size_total = int(r.headers["Content-Length"])
            size_total_mb = str(int(size_total / (1 << 20))) + "MB"
            window.btn3_download.text.set("Download DEMO  " + size_total_mb)
            window.label2_count.text.set("Total DEMOs: " + str(len(list_links)))
            event_pkt_found.set()
            if list_settings[0][1] is True:
                window.start_stop()

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
    global list_settings, exec_path, download_path
    file = open(exec_path + "ow_config", "w")
    file.write(download_path + "\n")
    for x in list_settings:
        file.write(str(x) + "\n")
    file.close()


def import_settings():
    global list_settings, exec_path, download_path
    try:
        file = open(exec_path + "ow_config", "r")
    except FileNotFoundError:
        return
    download_path = file.readline().strip("\n")
    index = 0
    for line in file:
        text = line[line.find(",") + 2:line.find("]")]
        if text == "True":
            list_settings[index][1] = True
        elif text == "False":
            list_settings[index][1] = False
        else:
            list_settings[index][1] = text[1:-1]
        index += 1
    file.close()


def change_setting(button, value=None):
    for item in list_settings:
        if item[0] == button.btn.winfo_name():
            if value is not None:
                if bool(item[1]) is True:
                    item[1] = False
                else:
                    item[1] = value
            else:
                item[1] = not item[1]
            break
    update_buttons(button)


def update_buttons(button):
    for item in list_settings:
        if item[0] == button.btn.winfo_name():
            if bool(item[1]) is True:
                button.text.set("ON")
                button.btn.config(relief=tk.SUNKEN, bg="#404040", activebackground="#808080")
            else:
                button.text.set("OFF")
                button.btn.config(relief=tk.RAISED, bg="#101010", activebackground="#404040")


def download_from_link(link, button):
    global list_settings
    r = req.get(link, stream=True)
    chunk_size = 16384
    size_total = int(r.headers["Content-Length"])
    size_total_mb = str(int(size_total / (1 << 20))) + "MB"
    size_curr = 0
    btn_name = button.text.get()
    if list_settings[2][1] is False:
        name = list_links[-1][list_links[-1].rfind("/") + 1:]
    else:
        name = list_settings[2][1]
    with open(download_path + name, "wb") as dest:
        for chunk in r.iter_content(chunk_size=chunk_size):
            dest.write(chunk)
            percent = int(size_curr / size_total * 100)
            button.text.set(str(percent) + "%  of  " + size_total_mb)
            size_curr += chunk_size
    button.text.set("extracting..")
    name = name[:name.rfind(".")]
    with bz2.BZ2File(download_path + name + ".bz2") as file, open(download_path + name, "wb") as dest:
        shutil.copyfileobj(file, dest, chunk_size)
    os.remove(download_path + name + ".bz2")
    button.text.set(btn_name)


def open_link(link, button):
    global browser_path, download_path, thread_download
    if link == "":
        return
    link = "http://" + link
    if thread_download.is_alive() is True:
        return
    if list_settings[1][1] is True:
        if len(link) == 0:
            return
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
        self.menu.delete(0, tk.END)
        if len(options) > 0:
            for opt in options:
                self.menu.add_command(label=opt, command=lambda label2=opt: self.text.set(label2))
        self.menu.config(font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040")


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
        update_buttons(self.btn_set1)
        update_buttons(self.btn_set2)
        update_buttons(self.btn_set3)
        if list_settings[2][1] is not False:
            self.entry_demo.text.set(list_settings[2][1])
        else:
            self.entry_demo.text.set("OW_replay")
        self._check_get_name()

    def _set_download_path(self):
        global download_path
        path = tkfd.askdirectory() + "/"
        if path == "/":
            return
        self.entry_browse.text.set(path)
        download_path = path

    def _check_get_name(self):
        name = ""
        list1 = " \n\\/"
        for letter in self.entry_demo.text.get():
            if list1.find(letter) == -1:
                name += letter
        if name == "":
            self.entry_demo.text.set("OW_replay")
            return "OW_replay"
        if len(name) > 45:
            self.entry_demo.text.set(name[:45])
            return name[:45]
        self.entry_demo.text.set(name)
        return name

    def _update_on_save(self):
        global list_settings
        self._check_get_name()
        if list_settings[2][1] is not False:
            list_settings[2][1] = self.entry_demo.text.get()
        save_settings()

    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Settings")
        self.window.minsize(330, 80)
        sizex = self.window.minsize()[0]
        # sizey = self.window.minsize()[1]
        # self.window.resizable(False, False)
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

        self.label_set1 = MyLabelStyle(self.window, "Stop scanning after a DEMO LINK is found")
        self.label_set1.frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set1 = MyButtonStyle(self.window, "OFF", lambda: change_setting(self.btn_set1), "stop_label")
        self.btn_set1.btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.label_set2 = MyLabelStyle(self.window, "Use the browser to download")
        self.label_set2.frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5, columnspan=2)
        self.btn_set2 = MyButtonStyle(self.window, "ON", lambda: change_setting(self.btn_set2), "browser_dl")
        self.btn_set2.btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=5, pady=5)

        self.label_set3 = MyLabelStyle(self.window,
                                       "*" * 30 + "Download location when not using the browser" + "*" * 30)
        self.label_set3.frame.config(width=45)
        self.label_set3.frame.grid(row=2, column=0, sticky=tk.W + tk.E, pady=5, columnspan=4)
        self.btn_browse = MyButtonStyle(self.window, "Browse", self._set_download_path)
        self.btn_browse.btn.grid(row=3, column=0, sticky=tk.W + tk.E, padx=5)
        self.entry_browse = MyEntryStyle(self.window, download_path)
        self.entry_browse.frame.grid(row=3, column=1, sticky=tk.W + tk.E, padx=5, columnspan=2)
        self.btn_opendl = MyButtonStyle(self.window, "Open", lambda: os.system(f"start {download_path}"))
        self.btn_opendl.btn.grid(row=3, column=3, sticky=tk.E, padx=5, pady=5)
        self.label_set3_1 = MyLabelStyle(self.window, "*" * 100)
        self.label_set3_1.frame.config(width=45)
        self.label_set3_1.frame.grid(row=4, column=0, sticky=tk.W + tk.E, columnspan=4)

        self.label_set4 = MyLabelStyle(self.window, "Rename downloaded demos to ")
        self.label_set4.frame.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        self.btn_set3 = MyButtonStyle(self.window, "ON",
                                      lambda: change_setting(self.btn_set3, self._check_get_name()), "rename_dl")
        self.btn_set3.btn.grid(row=5, column=0, sticky=tk.W + tk.E, padx=5, pady=5)
        self.entry_demo = MyEntryStyle(self.window, "")
        self.entry_demo.frame.config(state="normal")
        self.entry_demo.frame.grid(row=5, column=2, sticky=tk.W + tk.E, padx=5, columnspan=2)

        self.btn_save = MyButtonStyle(self.window, "Save to file", self._update_on_save)
        self.btn_save.btn.grid(row=6, column=3, sticky=tk.E, padx=5, pady=5)

        self._update_all_settings()
        self.window.grid_columnconfigure(0, minsize=0.15 * sizex, weight=1)
        self.window.grid_columnconfigure(1, minsize=0.5 * sizex, weight=1)
        self.window.grid_columnconfigure(2, minsize=0.15 * sizex, weight=1)
        self.window.grid_columnconfigure(3, minsize=0.2 * sizex, weight=1)
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

    def __init__(self, title, sizex, sizey):
        self.window = tk.Tk()
        self.window.title(title)
        self.window.minsize(sizex, sizey)
        # self.window.maxsize(512, 288)
        # self.window.resizable(False, False)
        self.window.config(bg="#101010")
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

        self.btn1_interfaces = MyOptMenuStyle(self.window, "Select one interface", get_interfaces())
        self.btn1_interfaces.btn.grid(row=0, column=0, sticky=tk.W + tk.E, columnspan=3, pady=5, padx=5)

        self.btn2_start = MyButtonStyle(self.window, "Start", self.start_stop)
        self.btn2_start.btn.config(font=("", 14, ""))
        self.btn2_start.btn.grid(row=0, column=3, columnspan=2, rowspan=2, sticky=tk.NSEW, padx=5, pady=5)

        self.label1_dynamic = MyLabelStyle(self.window, "Not looking for anything")
        self.label1_dynamic.frame.config(borderwidth=10, font=("", 14, "bold"), fg="red")
        self.label1_dynamic.frame.grid(row=1, column=0, columnspan=3)

        self.entry1_url = MyEntryStyle(self.window, "")
        self.entry1_url.frame.grid(row=2, column=0, sticky=tk.W + tk.E, columnspan=5, ipady=3, padx=5, pady=2)
        self.menu1_entry1_copy = MyMenuStyle(self.window)
        self.menu1_entry1_copy.menu.add_command(label="Copy",
                                                command=lambda: copy_to_clipboard(self.entry1_url.frame,
                                                                                  self.entry1_url.text.get()))

        def rc_event1(event):
            self.menu1_entry1_copy.menu.post(event.x_root, event.y_root)

        self.entry1_url.frame.bind("<Button-3>", rc_event1)

        self.label2_count = MyLabelStyle(self.window, "Total DEMOs: 0")
        self.label2_count.frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5)

        self.label3_time = MyLabelStyle(self.window, "No LINK found")
        self.label3_time.frame.grid(row=3, column=1, columnspan=2, sticky=tk.W + tk.E, padx=5)

        self.btn3_download = MyButtonStyle(self.window, "Download DEMO",
                                           lambda: open_link(self.entry1_url.text.get(), self.btn3_download))
        self.btn3_download.btn.grid(row=3, column=3, columnspan=2, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn4_link_list = MyButtonStyle(self.window, "LINK List", lambda: LinkListWindow(self.window))
        self.btn4_link_list.btn.grid(row=4, column=3, sticky=tk.W + tk.E, padx=5, pady=1)

        self.btn5_settings = MyButtonStyle(self.window, "Settings", lambda: SettingsWindow(self.window))
        self.btn5_settings.btn.grid(row=4, column=4, sticky=tk.NSEW, padx=5, pady=1)

        self.window.grid_columnconfigure(0, minsize=0.3 * sizex, weight=1)
        self.window.grid_columnconfigure(1, minsize=0.2 * sizex, weight=1)
        self.window.grid_columnconfigure(2, minsize=0.15 * sizex, weight=1)
        self.window.grid_columnconfigure(3, minsize=0.2 * sizex, weight=1)
        self.window.grid_columnconfigure(4, minsize=0.15 * sizex, weight=1)
        self.window.update_idletasks()


if __name__ == "__main__":
    app = MainAppWindow("Another OW Revealer 2", 500, 185)
    thread_time = t.Thread(target=lambda: update_time_label(app.label3_time), daemon=True)
    thread_time.start()
    browser_path = find_browser_path()
    download_path = find_file_path()
    exec_path = find_file_path(True)
    import_settings()

    app.window.mainloop()
