import threading as t


settings_dict = {
    "dl_loc": "",
    "rename": "OW_replay",
    "stop_label": False,
    "browser_dl": False,
    "rename_dl": False,
    "auto_dl": True,
    "delete_after": True
}
list_links = list()
profile_links = dict()
browser_path = None
exec_path = None
demo_stats = None
demo_nrplayers = 10
npcap_link = "https://nmap.org/npcap/dist/npcap-0.9988.exe"
found_time = None
thread_sniff = t.Thread()
thread_download = t.Thread()
thread_analyze = t.Thread()
thread_check_vac = t.Thread()
event_pkt_found = t.Event()
event_check_vac = t.Event()
app = None
