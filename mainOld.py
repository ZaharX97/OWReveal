from tkinter import *
from scapy.all import *
from scapy.layers.http import HTTPRequest
from datetime import datetime
from threading import Thread, Event
from winreg import *
import subprocess
import platform
import webbrowser
import requests

set1_btn_value = False
found_packet = False
found_packet_event = Event()
mainWinW = 500
mainWinH = 190
sniff_thread = None
link_time = None
link_list = list()
keyp = None
npcap_found = True


def sniff_packets(xiface=None):
    global sniff_thread
    # Sniff packets with `iface`, if None (default), then the
    # Scapy's default interface is used
    if xiface is None or xiface == b01_opt_list[0]:
        sniff_thread = AsyncSniffer(lfilter=lambda y: y.haslayer(HTTPRequest), prn=process_packet, store=False)
        sniff_thread.start()
        # sniff(prn=process_packet, store=False, stop_filter=check_stop_sniff)
    else:
        sniff_thread = AsyncSniffer(iface=xiface, lfilter=lambda y: y.haslayer(HTTPRequest), prn=process_packet,
                                    store=False)
        sniff_thread.start()
        # sniff(prn=process_packet, iface=xiface, store=False, stop_filter=check_stop_sniff)


def process_packet(pkt):
    global found_packet, link_time, link_list
    # This function is executed whenever a packet is sniffed
    # if pkt.haslayer(HTTPRequest):
    # if this packet is an HTTP Request
    # get the requested URL
    url = pkt[HTTPRequest].Host.decode() + pkt[HTTPRequest].Path.decode()
    # get the requester's IP Address
    # ip = packet[IP].src
    # get the request method
    # method = packet[HTTPRequest].Method.decode()
    # print("\n{}".format(url))
    if url.find(".dem.bz2") != -1 and url != b12_text.get():
        found_packet = True
        link_time = datetime.now()
        link_list.append(url)
        b12_text.set(url)
        found_packet_event.set()
        if set1_btn_value is True:
            b02_func()


def get_interfaces():
    interfaces_list = list()
    for x in IFACES.data.values():
        if str(x).find("Unknown") != -1:
            continue
        interfaces_list.append(str(x)[19:str(x).find("{") - 2])
    return interfaces_list


def check_npcap():
    global npcap_found
    try:
        sniff(count=1, store=False)
    except RuntimeError:
        npcap_found = False
        return
    npcap_found = True


def calc_geo(x, y):
    # print("root = " + str(x.winfo_width()) + " / " + str(x.winfo_height()))
    # print("child = " + str(y.winfo_width()) + " / " + str(y.winfo_height()))
    return x.winfo_x() + (x.winfo_width() - y.winfo_width()) / 2, x.winfo_y() + (
            x.winfo_height() - y.winfo_height()) / 2


def invert_set1(x):
    global set1_btn_value
    set1_btn_value = not set1_btn_value
    if set1_btn_value is True:
        x.config(text="ON", relief=SUNKEN, bg="#404040", activebackground="#808080")
    else:
        x.config(text="OFF", relief=RAISED, bg="#101010", activebackground="#404040")


def wtf():
    print("wtf")
    print(sniff_thread.running)


def browser_find():
    global keyp
    if platform.platform().lower().find("windows") != -1:
        key = OpenKey(HKEY_CURRENT_USER,
                      r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.html\UserChoice")
        keyp = QueryValueEx(key, "ProgId")[0]
        key.Close()
        key = OpenKey(HKEY_CLASSES_ROOT, keyp + r"\shell\open\command")
        keyp = QueryValueEx(key, None)[0]
        key.Close()
        keyp = keyp[:keyp[1:].find("\"") + 2]
    else:
        print("you are not using windows")
        keyp = "1"


def open_link2(linkk):
    if len(linkk) == 0:
        return
    global keyp
    if keyp is None:
        browser_find()
    if keyp == "1":
        webbrowser.open_new_tab(linkk)
    else:
        subprocess.Popen(keyp + " " + linkk)


def open_link3(linkk):
    r = requests.get(linkk, stream=True)
    with open(r"C:\Users\Zahar\Desktop\asd\1.dem.gz", "wb") as dest:
        for chunk in r.iter_content(chunk_size=128):
            dest.write(chunk)


def time_elapsed():
    global link_time, found_packet_event
    while True:
        if link_time is not None:
            time_in_minutes = datetime.now() - link_time
            b10_text.set("LINK found {} minutes ago".format(int(time_in_minutes.total_seconds() / 60)))
            found_packet_event.clear()
        found_packet_event.wait(60)


def copy_entry(root_window, this_window):
    root_window.clipboard_clear()
    if type(this_window) is str:
        root_window.clipboard_append(this_window)
    else:
        w = ""
        for z in this_window:
            w = w + root_window.get(z) + "\n"
        root_window.clipboard_append(w)


def alert_small_error(root, message):
    alert = Toplevel(root)
    alert.title("error")
    alert.minsize(100, 50)
    alert.resizable(False, False)
    alert.attributes("-topmost")
    alert.config(bg="#101010")
    msg = Label(alert, text=message)
    msg.config(font=("arial", 10, ""), fg="white", bg="#101010")
    msg.pack()
    button = Button(alert, text="Close", command=alert.destroy)
    button.config(font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040", bd=3)
    button.pack()
    alert.update_idletasks()
    alert.geometry("+%d+%d" % (calc_geo(root, alert)))
    alert.grab_set()
    alert.focus_set()


def link_list_func(root):
    global link_list
    if len(link_list) == 0:
        alert_small_error(mainWindow, "No LINKs found yet")
        return

    def copy_ev(event):
        copy_menu.post(event.x_root, event.y_root)

    link_listbox_main = Toplevel(root)
    link_listbox_main.title("Past LINKs")
    # link_listbox_main.resizable(False, False)
    link_listbox_main.config(bg="#101010")
    link_listbox_main.protocol("WM_DELETE_WINDOW", link_listbox_main.destroy)
    link_listbox_main.grab_set()
    link_listbox_main.focus_set()
    link_listbox_msg = Label(link_listbox_main, text="Oldest LINK at TOP")
    link_listbox_msg.config(font=("arial", 10, ""), fg="white", bg="#101010")
    link_listbox_msg.pack()
    link_list2 = StringVar(value=link_list)
    link_listbox = Listbox(link_listbox_main)
    link_listbox.config(activestyle=NONE, listvariable=link_list2, width=len(link_list[-1]) + 2,
                        height=len(link_list) + 1, selectmode=MULTIPLE, font=("arial", 10, ""), fg="white",
                        bg="#101010", borderwidth=5)
    link_listbox.pack(fill=BOTH, expand=1)
    copy_menu = Menu(link_listbox)
    copy_menu.add_command(label="Copy selected",
                          command=lambda: copy_entry(link_listbox, link_listbox.curselection()))
    copy_menu.add_command(label="Select all",
                          command=lambda: link_listbox.selection_set(0, END))
    copy_menu.add_command(label="Deselect all",
                          command=lambda: link_listbox.selection_clear(0, END))
    copy_menu.config(tearoff=0, font=("arial", 10, ""), fg="white", bg="#101010")
    link_listbox.bind("<Button-3>", copy_ev)
    link_listbox_main.update_idletasks()
    link_listbox_main.geometry("+%d+%d" % (calc_geo(root, link_listbox_main)))
    link_listbox_main.grab_set()
    link_listbox_main.focus_set()
    link_listbox.selection_set(0)


def b02_func():
    global found_packet, sniff_thread, npcap_found
    if npcap_found is False:
        alert_small_error(mainWindow,
                          "Couldn't find npcap. Get it from  https://nmap.org/npcap/dist/npcap-0.9988.exe  \n Press the DOWNLOAD button to go to the link")
        b12_text.set("https://nmap.org/npcap/dist/npcap-0.9988.exe")
        b10_text.set("npcap error")

        return
    if b01_text.get() == "Select one interface":
        alert_small_error(mainWindow, "You need to select one network interface")
        return
    if b02_text.get() == "Start":
        found_packet = False
        b12.delete(0, END)
        b02_text.set("Stop")
        b00_text.set("Looking for OW DEMO link")
        b00.config(fg="green")
        sniff_packets(b01_text.get())
    else:
        b02_text.set("Start")
        b00_text.set("Not looking for anything")
        b00.config(fg="red")
        sniff_thread.stop(join=False)


def settings_win(root):
    global set1_btn_value
    settings_window = Toplevel(root)
    settings_window.title("yay settings")
    settings_window.minsize(300, 80)
    settings_window.resizable(False, False)
    settings_window.config(bg="#101010")
    settings_window.protocol("WM_DELETE_WINDOW", settings_window.destroy)
    settings_window.grid_columnconfigure(0, minsize=25)
    settings_window.grid_columnconfigure(1, minsize=225)
    settings_window.grid_columnconfigure(2, minsize=50)
    set1_desc = Label(settings_window, text="Stop scanning after a DEMO LINK is found")
    set1_desc.config(font=("arial", 10, ""), fg="white", bg="#101010")
    set1_desc.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
    set1_btn = Button(settings_window, text="OFF", command=lambda: invert_set1(set1_btn))
    set1_btn.config(anchor=CENTER, font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040", bd=3)
    set1_btn.grid(row=0, column=0, padx=5, pady=5)
    if set1_btn_value is True:
        set1_btn.config(text="ON", relief=SUNKEN, bg="#404040", activebackground="#808080")
    else:
        set1_btn.config(text="OFF", relief=RAISED, bg="#101010", activebackground="#404040")
    save_btn = Button(settings_window, text="Save", command=wtf)
    save_btn.config(font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040", bd=3)
    save_btn.grid(row=5, column=2, sticky=W + E, padx=5, pady=5)
    settings_window.update_idletasks()
    settings_window.geometry("+%d+%d" % (calc_geo(root, settings_window)))
    settings_window.grab_set()
    settings_window.focus_set()


mainWindow = Tk()
mainWindow.title("Another OW Revealer 2")
mainWindow.minsize(mainWinW, mainWinH)
# mainWindow.maxsize(512, 288)
mainWindow.resizable(False, False)
mainWindow.config(bg="#101010")
mainWindow.protocol("WM_DELETE_WINDOW", mainWindow.destroy)
mainWindow.grid_columnconfigure(0, minsize=0.3 * mainWinW)
mainWindow.grid_columnconfigure(1, minsize=0.2 * mainWinW)
mainWindow.grid_columnconfigure(2, minsize=0.15 * mainWinW)
mainWindow.grid_columnconfigure(3, minsize=0.15 * mainWinW)
mainWindow.grid_columnconfigure(4, minsize=0.2 * mainWinW)

# ratio = mainWindow.winfo_screenwidth()/mainWindow.winfo_screenheight()
# print(ratio)

b01_opt_list = ["None  (select this if not sure)"]
b01_opt_list.extend(get_interfaces())
b01_text = StringVar()
b01_text.set("Select one interface")
b01 = OptionMenu(mainWindow, b01_text, "")
b01["menu"].delete(0, END)
for opt_list in b01_opt_list:
    b01["menu"].add_command(label=opt_list, command=lambda value=opt_list: b01_text.set(value))
b01["menu"].config(font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040")
b01.config(anchor=W, font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040")
b01.grid(row=0, column=0, sticky=W + E, columnspan=3, pady=5, padx=5)

b02_text = StringVar()
b02_text.set("Start")
b02 = Button(mainWindow, textvariable=b02_text, command=b02_func)
b02.config(bd=5, font=("arial", 14, ""), fg="white", bg="#101010", activebackground="#404040")
b02.grid(row=0, column=3, columnspan=2, rowspan=2, sticky=NSEW, padx=5, pady=5)

b00_text = StringVar()
b00_text.set("Not looking for anything")
b00 = Label(mainWindow, textvariable=b00_text)
b00.config(borderwidth=10, font=("", 14, "bold"), fg="red", bg="#101010")
b00.grid(row=1, column=0, columnspan=3)

b12_text = StringVar()
b12_text.set("")
b12 = Entry(mainWindow, textvariable=b12_text, state="readonly")
b12.config(justify=CENTER, font=("arial", 10, ""), borderwidth=2, readonlybackground="#f0f0f0")
b12.grid(row=2, column=0, sticky=W + E, columnspan=5, ipady=3, padx=5, pady=2)

b12_menu = Menu(b12)
b12_menu.add_command(label="Copy", command=lambda: copy_entry(b12, b12_text.get()))
b12_menu.config(tearoff=0, font=("arial", 10, ""), fg="white", bg="#101010")


def b12event(event):
    b12_menu.post(event.x_root, event.y_root)


b12.bind("<Button-3>", b12event)

b10_text = StringVar()
b10_text.set("No LINK found")
b10 = Label(mainWindow, textvariable=b10_text)
b10.config(anchor=W, font=("arial", 10, ""), fg="white", bg="#101010")
b10.grid(row=3, column=1, columnspan=2, sticky=W + E, padx=5)

b11 = Button(mainWindow, text="Download DEMO", command=lambda: open_link2(b12_text.get()))
b11.config(font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040", bd=3)
b11.grid(row=3, column=3, columnspan=2, sticky=W + E, padx=5, pady=1)

button_link_list = Button(mainWindow, text="LINK List", command=lambda: link_list_func(mainWindow))
button_link_list.config(font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040", bd=3)
button_link_list.grid(row=4, column=3, sticky=W + E, padx=5, pady=1)

# icon_settings = PhotoImage(file="resources/icon_settings.png")
button_settings = Button(mainWindow, text="Settings", command=lambda: settings_win(mainWindow))
button_settings.config(compound=LEFT, font=("arial", 10, ""), fg="white", bg="#101010", activebackground="#404040",
                       bd=3)
button_settings.grid(row=4, column=4, sticky=NSEW, padx=5, pady=1)

time_thread = Thread(target=time_elapsed, daemon=True)
time_thread.start()
# check_npcap()

mainWindow.mainloop()
