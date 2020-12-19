import threading as t


settings_dict = {
    "dl_loc": "",
    "rename": "OW_replay",
    "stop_label": False,
    "browser_dl": False,
    "rename_dl": False,
    "auto_dl": True,
    "delete_after": True,
    "rank_doodles": False
}
RANK_TRANSLATE_1 = {
    0: "N/A",
    1: "S1",
    2: "S2",
    3: "S3",
    4: "S4",
    5: "SE",
    6: "SEM",
    7: "GN1",
    8: "GN2",
    9: "GN3",
    10: "GNM",
    11: "MG1",
    12: "MG2",
    13: "MGE",
    14: "DMG",
    15: "LE",
    16: "LEM",
    17: "SMFC",
    18: "Global",
}
RANK_TRANSLATE_2 = {
    0: "⚠",
    1: ">",
    2: ">>",
    3: ">>>",
    4: ">>>>",
    5: "(>>>>",
    6: "(*>>>>",
    7: "(*)",
    8: "(**)",
    9: "(***)",
    10: "(****)",
    11: "︻╦╤─",
    12: "(︻╦╤─)",
    13: "*︻╦╤─*",
    14: "🌟",
    15: "*🦅*",
    16: "(*🦅*)",
    17: "*⚞◯⚟*",
    18: "(*☢*)",
}
MODE_TRANSLATE = {
    0: "Unknown",
    6: "Competitive",
    7: "Wingman"
}

NAME_CUTOUT_MAIN = 16
NAME_CUTOUT_WATCHLIST = 22
TEXT_CUTOUT_MAPSERV = 18
RANK_TRANSLATE = RANK_TRANSLATE_2

VERSION = "4.0.1"
PROJECT_LINK = "https://github.com/ZaharX97/OWReveal"
PROJECT_LINK_LATEST = PROJECT_LINK + "/releases/latest"

list_links = list()
profile_links = dict()
browser_path = None
exec_path = None
last_server = None
demo_stats = None
demo_nrplayers = 10
demo_ranks = None
ranks_done = False
npcap_link = "https://nmap.org/npcap/"
found_time = None
thread_sniff = t.Thread()
thread_download = t.Thread()
thread_analyze = t.Thread()
thread_check_vac = t.Thread()
event_pkt_found = t.Event()
event_check_vac = t.Event()
app = None
