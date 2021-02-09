import myglobals as g

match_started = False
round_current = 1
team_score = {2: 0, 3: 0}
max_players = 0
kills_round_list = list()
PLAYERS = dict()
BOTS = dict()
takeovers = dict()
STATS = {
    "otherdata": {
        "kills": {},
        "PFN": {}
    }
}
RANK_STATS = dict()


class MiniStats:
    def __init__(self, player):
        self.player = player
        self.k = player.k
        self.d = player.d
        self.a = player.a


class MyRoundStats:
    # stats at the end of the round
    def __init__(self, t2, t3, players):
        # 2 = "T" // 3 = "CT"
        self.score_team2 = t2
        self.score_team3 = t3
        self.pscore = []
        for p in players.values():
            self.pscore.append(MiniStats(p))
        self.pscore = sorted(self.pscore, key=lambda p2: p2.k, reverse=True)


class MyPlayer:
    def __init__(self, data=None, ui=False, team=None):
        self.id = None
        self.eid = None
        self.name = None
        # self.steamid = None
        self.profile = None
        self.k = 0
        self.d = 0
        self.a = 0
        # 2 = "T" // 3 = "CT"
        self.rank = None
        self.start_team = team
        self.userinfo = None
        self.data = None
        if data:
            self.update(data, ui)

    def update(self, data, ui):
        if ui:
            self.userinfo = data
            self.id = data.user_id
            self.name = data.name
            # self.steamid = data.guid
            self.profile = "https://steamcommunity.com/profiles/" + str(data.xuid)
            # self.profile += str(c.PROFILE_NR + int(self.steamid[8]) + 2 * int(self.steamid[10:]))


def new_demo(data):
    global match_started, round_current, team_score, max_players, PLAYERS, BOTS, takeovers, STATS, kills_round_list
    match_started = False
    round_current = 1
    team_score = {2: 0, 3: 0}
    max_players = 0
    kills_round_list = list()
    PLAYERS = dict()
    BOTS = dict()
    takeovers = dict()
    STATS = {
        "otherdata": {
            "kills": {},
            "PFN": {}
        }
    }
    STATS["otherdata"].update({"map": data.map_name})


def player_team(data):
    global BOTS, PLAYERS, max_players, round_current
    # trying to find out player teams (and bots, mainly bots here) since i'm not parsing entities
    # if data["isbot"]:
    #     print("bot {} joined team {} / disc= {}".format(data["userid"], data["team"], data["disconnect"]))
    # else:
    #     print("player {} joined team {} / disc= {}".format(data["userid"], data["team"], data["disconnect"]))
    if data["team"] == 0:
        if data["isbot"] and BOTS.get(data["userid"]):
            BOTS.pop(data["userid"])
        return
    if data["isbot"] and not BOTS.get(data["userid"]):
        BOTS.update({data["userid"]: data["team"]})
        return
    rp = PLAYERS.get(data["userid"])
    if rp and rp.start_team is None:
        if max_players == 10:
            if round_current <= 15:
                if data["team"] in (2, 3):
                    rp.start_team = data["team"]
            else:
                if data["team"] == 2:
                    rp.start_team = 3
                elif data["team"] == 3:
                    rp.start_team = 2
        elif max_players == 4:
            if round_current <= 8:
                if data["team"] in (2, 3):
                    rp.start_team = data["team"]
            else:
                if data["team"] == 2:
                    rp.start_team = 3
                elif data["team"] == 3:
                    rp.start_team = 2


def player_death(data):
    global match_started, PLAYERS, BOTS, takeovers, STATS, round_current, kills_round_list
    if match_started:
        k = PLAYERS.get(data["attacker"])
        a = PLAYERS.get(data["assister"])
        d = PLAYERS.get(data["userid"])
        kf = BOTS.get(data["attacker"])
        af = BOTS.get(data["assister"])
        df = BOTS.get(data["userid"])
        kto = takeovers.get(data["attacker"])
        ato = takeovers.get(data["assister"])
        dto = takeovers.get(data["userid"])
        # if round_current == 7:
        #     print(data)
        # if not d:
        #     temp = g.demo_stats._players_by_uid[data["userid"]]
        #     randommm = 1
        krl_d = d
        if not d:
            if not((max_players == 10 and round_current <= 15) or (max_players == 4 and round_current <= 8)):
                df = 2 if df == 3 else 3
            krl_d = MyPlayer(data=g.demo_stats._players_by_uid[data["userid"]], ui=True, team=df)
            krl_d.name = f"BOT {krl_d.name}"
        krl_k = k
        if not k:
            if not ((max_players == 10 and round_current <= 15) or (max_players == 4 and round_current <= 8)):
                kf = 2 if kf == 3 else 3
            if data["attacker"] == 0:
                krl_k = krl_d
            else:
                krl_k = MyPlayer(data=g.demo_stats._players_by_uid[data["attacker"]], ui=True, team=kf)
            krl_k.name = f"BOT {krl_k.name}"
        kills_round_list.append([krl_k, a, krl_d, data])
        if data["assister"] and not data["assistedflash"]:
            if a and not ato:  # asd
                a.a += 1
                # print("ass", d.userinfo.xuid, d.start_team, a.start_team, df, af)
                if d and a.start_team and d.start_team and a.start_team == d.start_team:
                    a.a -= 1
                elif not df and a.start_team and a.start_team == df:
                    a.a -= 1
        if k and not kto:
            k.k += 1
        if d and not dto and data["weapon"] != "planted_c4":
            d.d += 1
        if d and not dto and data["userid"] == data["attacker"]:
            d.k -= 2
        else:
            if k and not kto and d and k.start_team and d.start_team and k.start_team == d.start_team:
                k.k -= 2
            elif k and not kto and not df and k.start_team and k.start_team == df:
                k.k -= 2


def player_spawn(data):
    global PLAYERS, max_players, round_current
    # trying to find out player teams since i'm not parsing entities
    if data["teamnum"] == 0:
        return
    rp = PLAYERS.get(data["userid"])
    # print(data["userid"], bp, rp)
    # print("inside")
    # print(round_current, ">", bp, rp.start_team if rp else None)
    if rp and rp.start_team is None:
        if max_players == 10:
            if round_current <= 15:
                if data["teamnum"] in (2, 3):
                    rp.start_team = data["teamnum"]
            else:
                if data["teamnum"] == 2:
                    rp.start_team = 3
                elif data["teamnum"] == 3:
                    rp.start_team = 2
        elif max_players == 4:
            if round_current <= 8:
                if data["teamnum"] in (2, 3):
                    rp.start_team = data["teamnum"]
            else:
                if data["teamnum"] == 2:
                    rp.start_team = 3
                elif data["teamnum"] == 3:
                    rp.start_team = 2
    # print(">>", BOTS.get(data["userid"]), rp.start_team if rp else None)
    # print(".................................................")


def bot_takeover(data):
    global match_started, takeovers
    if match_started:
        takeovers.update({data["userid"]: 1})


def begin_new_match(data):
    global match_started
    if match_started:
        _reset_pstats()
    match_started = True
    # print("MATCH STARTED.....................................................................")


def round_end(data):
    global match_started, round_current, team_score
    if match_started:
        if max_players == 10:
            if round_current <= 15:
                if data["winner"] == 2:
                    team_score[2] += 1
                elif data["winner"] == 3:
                    team_score[3] += 1
            else:
                if data["winner"] == 2:
                    team_score[3] += 1
                elif data["winner"] == 3:
                    team_score[2] += 1
        elif max_players == 4:
            if round_current <= 8:
                if data["winner"] == 2:
                    team_score[2] += 1
                elif data["winner"] == 3:
                    team_score[3] += 1
            else:
                if data["winner"] == 2:
                    team_score[3] += 1
                elif data["winner"] == 3:
                    team_score[2] += 1
        # print("    {} / {}".format(data["reason"], data["message"]))


def round_officially_ended(data):
    global match_started, STATS, round_current, team_score, PLAYERS, takeovers, kills_round_list
    if match_started:
        STATS.update({round_current: MyRoundStats(team_score[2], team_score[3], PLAYERS)})
        STATS["otherdata"]["kills"].update({round_current: kills_round_list})
        round_current += 1
        kills_round_list = list()
        takeovers.clear()
    # print("ROUND {}..........................................................".format(round_current))


def cmd_dem_stop(data):
    global STATS, round_current, team_score, PLAYERS, max_players
    STATS.update({round_current: MyRoundStats(team_score[2], team_score[3], PLAYERS)})
    STATS["otherdata"]["kills"].update({round_current: kills_round_list})
    # if 0 < max_players < 4:
    #     max_players = 4
    # elif 6 < max_players < 10:
    #     max_players = 10
    STATS["otherdata"].update({"nrplayers": max_players})


def update_pinfo(data):
    global PLAYERS, max_players
    if data.guid != "BOT":
        if not STATS["otherdata"]["PFN"].get(str(data.xuid)):
            STATS["otherdata"]["PFN"].update({str(data.xuid): data.name})
        exist = None
        for x in PLAYERS.items():
            if data.xuid == x[1].userinfo.xuid:
                exist = x[0]
                break
        if exist:
            PLAYERS[exist].update(data, ui=True)
            if exist != data.user_id:
                PLAYERS.update({data.user_id: PLAYERS[exist]})
                PLAYERS.pop(exist)
        else:
            PLAYERS.update({data.user_id: MyPlayer(data, ui=True)})
        max_players = len(PLAYERS)


def new_demo_ranks(data):
    global RANK_STATS
    g.ranks_done = False
    RANK_STATS = dict()


def get_ranks(data):
    if g.ranks_done:
        g.ranks_done = False
        g.demo_ranks.demo_finished = True
    else:
        res_table = g.demo_ranks.get_resource_table()
        if not res_table:
            return
        else:
            res_table = res_table.props
        for player in g.demo_ranks._players_by_uid.values():
            if player.xuid == 0:
                continue
            if not RANK_STATS.get(player.xuid):
                RANK_STATS.update({player.xuid: None})
            if RANK_STATS[player.xuid] is None:
                key = str(player.entity_id).zfill(3)
                connected = res_table["m_bConnected"][key]
                in_team = res_table["m_iTeam"][key]
                if not (in_team == 2 or in_team == 3) or not connected:
                    RANK_STATS.pop(player.xuid)
                    continue
                if connected:
                    rank = res_table["m_iCompetitiveRanking"][key]
                    RANK_STATS.update({player.xuid: rank})
        if len(RANK_STATS) == STATS["otherdata"]["nrplayers"]:
            for ranks in RANK_STATS.values():
                if ranks is None:
                    break
                g.ranks_done = True


def _reset_pstats():
    global PLAYERS, team_score
    for p2 in PLAYERS.values():
        team_score[2] = 0
        team_score[3] = 0
        p2.k = 0
        p2.a = 0
        p2.d = 0
        p2.start_team = None


def print_match_stats(data):
    global STATS
    file = data
    if not file:
        return
    file.write("\nMATCH STATS:\n")
    for x in STATS.items():
        if x[0] == "otherdata":
            continue
        file.write("\nRound {}:\n".format(x[0]))
        file.write("team2= {} / team3= {}\n\n".format(x[1].score_team2, x[1].score_team3))
        file.write("        K / A / D\n")
        for i in range(len(x[1].pscore)):
            file.write("{} > {} / {} / {}, team= {} xuid= {}\n".format(x[1].pscore[i].player.name, x[1].pscore[i].k,
                                                                       x[1].pscore[i].a, x[1].pscore[i].d,
                                                                       x[1].pscore[i].player.start_team,
                                                                       x[1].pscore[i].player.userinfo.xuid))
        file.write("...............................................................\n")
