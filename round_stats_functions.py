import myglobals as g

match_started = False
ranks_done = False
game_mode_done = False
round_current = 1
round_switch = 0
round_switch_found = False
team_score = {2: 0, 3: 0}
game_mode = 0
max_players = 0
actual_players = 0
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
        self.ttr = player.team_this_round


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
        self.team_this_round = team
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
    global match_started, round_current, team_score, max_players, PLAYERS, BOTS, takeovers, STATS, kills_round_list, game_mode, ranks_done, game_mode_done
    match_started = False
    ranks_done = False
    game_mode_done = False
    round_current = 1
    team_score = {2: 0, 3: 0}
    max_players = 0
    kills_round_list.clear()
    PLAYERS.clear()
    BOTS.clear()
    takeovers.clear()
    RANK_STATS.clear()
    STATS = {
        "otherdata": {
            "kills": {},
            "PFN": {}
        }
    }
    STATS["otherdata"].update({"header": data})


def player_team(data):
    global BOTS, PLAYERS, max_players, round_current, game_mode
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
        if round_current < round_switch or (round_current > ((round_switch - 1) * 2) and round_current % 6 in {1, 2, 3}):
            if data["team"] in (2, 3):
                rp.start_team = data["team"]
        else:
            if data["team"] == 2:
                rp.start_team = 3
            elif data["team"] == 3:
                rp.start_team = 2
    if rp and rp.start_team:
        rp.team_this_round = data["team"]


def player_death(data):
    global match_started, PLAYERS, BOTS, takeovers, STATS, round_current, kills_round_list, game_mode
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
        # print(data)
        krl_d = d
        if not d:
            if not(round_current < round_switch or (round_current > ((round_switch - 1) * 2) and round_current % 6 in {1, 2, 3})):
                df = 2 if df == 3 else 3
            krl_d = MyPlayer(data=g.demo_stats._players_by_uid[data["userid"]], ui=True, team=df)
            krl_d.name = f"BOT {krl_d.name}"
        krl_k = k
        if not k:
            if not(round_current < round_switch or (round_current > ((round_switch - 1) * 2) and round_current % 6 in {1, 2, 3})):
                kf = 2 if kf == 3 else 3
            if data["attacker"] == 0:
                krl_k = krl_d
            else:
                krl_k = MyPlayer(data=g.demo_stats._players_by_uid[data["attacker"]], ui=True, team=kf)
            krl_k.name = f"BOT {krl_k.name}"
        if data["weapon"].find("knife") != -1:
            data["weapon"] = "knife"
        if not g.WEAPON_TRANSLATE.get(data["weapon"]):
            print(data)
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
    global PLAYERS, max_players, round_current, game_mode
    # trying to find out player teams since i'm not parsing entities
    if data["teamnum"] == 0:
        return
    rp = PLAYERS.get(data["userid"])
    # if rp:
    #     print(f"  BGN: {rp.name} - s: {rp.start_team} // ttr: {rp.team_this_round} // teamnum: {data['teamnum']}")
    # print(data["userid"], bp, rp)
    # print("inside")
    # print(round_current, ">", bp, rp.start_team if rp else None)
    if rp and rp.start_team is None:
        if round_current < round_switch or (round_current > ((round_switch - 1) * 2) and round_current % 6 in {1, 2, 3}):
            if data["teamnum"] in (2, 3):
                rp.start_team = data["teamnum"]
        else:
            if data["teamnum"] == 2:
                rp.start_team = 3
            elif data["teamnum"] == 3:
                rp.start_team = 2
    if rp and rp.start_team:
        rp.team_this_round = data["teamnum"]
    # if rp:
    #     print(f"  END: {rp.name} - s: {rp.start_team} // ttr: {rp.team_this_round} // teamnum: {data['teamnum']}\n")
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
    print("MATCH STARTED.....................................................................")


def round_end(data):
    global match_started, round_current, team_score, game_mode
    if match_started:
        if round_current < round_switch or (round_current > ((round_switch - 1) * 2) and round_current % 6 in {1, 2, 3}):
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
    global match_started, STATS, round_current, team_score, PLAYERS, takeovers, kills_round_list, round_switch, round_switch_found
    if match_started:
        STATS.update({round_current: MyRoundStats(team_score[2], team_score[3], PLAYERS)})
        STATS["otherdata"]["kills"].update({round_current: kills_round_list})
        round_current += 1
        kills_round_list = list()
        takeovers.clear()
        if not round_switch_found:
            round_switch = round_current + 1
        for p2 in PLAYERS.values():
            p2.team_this_round = None
    print("ROUND {}..........................................................".format(round_current))


def cmd_dem_stop(data):
    global STATS, round_current, team_score, PLAYERS, max_players, game_mode, round_switch
    STATS.update({round_current: MyRoundStats(team_score[2], team_score[3], PLAYERS)})
    STATS["otherdata"]["kills"].update({round_current: kills_round_list})
    STATS["otherdata"].update({"nrplayers": max_players})
    STATS["otherdata"].update({"expectedplayers": 4 if max_players <= 4 else 10})
    STATS["otherdata"].update({"gamemode": game_mode})
    STATS["otherdata"].update({"round_switch": round_switch})
    for rnd, sts in STATS.items():
        if rnd == "otherdata":
            continue
        for p2 in sts.pscore:
            if not p2.ttr:
                rnd = int(rnd)
                if rnd < round_switch or (rnd > ((round_switch - 1) * 2) and rnd % 6 in {1, 2, 3}):
                    p2.ttr = p2.player.start_team
                else:
                    p2.ttr = 2 if p2.player.start_team == 3 else 3


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


def get_ranks(data):
    global ranks_done, PLAYERS, actual_players
    if ranks_done:
        g.demo_stats.unsubscribe_from_event("parser_new_tick", get_ranks)
        if game_mode_done:
            g.demo_stats.unsubscribe_from_event("packet_svc_PacketEntities")
    else:
        res_table = g.demo_stats.get_resource_table()
        if not res_table:
            return
        else:
            res_table = res_table.props
        for player in PLAYERS.values():
            if player.userinfo.xuid == 0:
                continue
            if not RANK_STATS.get(player.userinfo.xuid):
                RANK_STATS.update({player.userinfo.xuid: None})
            if RANK_STATS[player.userinfo.xuid] is None:
                key = str(player.userinfo.entity_id).zfill(3)
                connected = res_table["m_bConnected"][key]
                in_team = res_table["m_iTeam"][key]
                if not (in_team == 2 or in_team == 3) or not connected:
                    RANK_STATS.pop(player.userinfo.xuid)
                    continue
                if connected:
                    rank = res_table["m_iCompetitiveRanking"][key]
                    RANK_STATS.update({player.userinfo.xuid: rank})
        if len(RANK_STATS) == actual_players:
            ranks_done = True
            for ranks in RANK_STATS.values():
                if ranks is None:
                    ranks_done = False
                    break


def get_game_mode(data):
    global game_mode, PLAYERS, game_mode_done
    gmd = dict()
    if game_mode in (-7, 0, 0.1):
        if g.demo_stats.header.server_name.upper().find("VALVE") == -1:
            game_mode_done = True
            if ranks_done:
                g.demo_stats.unsubscribe_from_event("packet_svc_PacketEntities")
            g.demo_stats.unsubscribe_from_event("parser_new_tick", get_game_mode)
            return
        res_table = g.demo_stats.get_resource_table()
        if res_table and len(PLAYERS) >= actual_players - 1:
            for player in PLAYERS.values():
                game_mode2 = res_table.props["m_iCompetitiveRankType"][str(player.userinfo.entity_id).zfill(3)]
                gmd.update({game_mode2: 1 if not gmd.get(game_mode2) else gmd.get(game_mode2) + 1})
                # if game_mode != -1:
                #     g.demo_stats.unsubscribe_from_event("packet_svc_PacketEntities")
                #     g.demo_stats.unsubscribe_from_event("parser_new_tick", get_game_mode)
                #     break
            # print(gmd)
            for x in sorted(gmd.keys(), reverse=True):
                # print(x, len(PLAYERS.values()))
                game_mode2 = x
                if game_mode2 != 0:
                    game_mode = game_mode + game_mode2 * 2 if game_mode2 == 7 else game_mode + game_mode2
                    game_mode_done = True
                    if ranks_done:
                        g.demo_stats.unsubscribe_from_event("packet_svc_PacketEntities")
                    g.demo_stats.unsubscribe_from_event("parser_new_tick", get_game_mode)
                else:
                    if not match_started:
                        g.demo_stats.unsubscribe_from_event("parser_new_tick", get_game_mode)
                        g.demo_stats.subscribe_to_event("gevent_begin_new_match", get_game_mode)
                    elif match_started:
                        game_mode_done = True
                        if ranks_done:
                            g.demo_stats.unsubscribe_from_event("packet_svc_PacketEntities")
                        g.demo_stats.unsubscribe_from_event("parser_new_tick", get_game_mode)
                        g.demo_stats.unsubscribe_from_event("gevent_begin_new_match", get_game_mode)
                break

#   first passing > looking for round switch and max players to determine game mode


def new_demo_gamemode(data):
    global round_switch, game_mode, max_players, PLAYERS, BOTS, match_started, round_current, actual_players, round_switch_found
    match_started = False
    round_current = 1
    round_switch = 0
    round_switch_found = False
    game_mode = 0
    max_players = 0
    actual_players = 0
    PLAYERS.clear()
    BOTS.clear()


def round_announce_last_round_half(data):
    global round_switch, round_current, match_started, round_switch_found
    if match_started:
        round_switch_found = True
        round_switch = round_current + 1


def cmd_dem_stop_gm(data):
    global max_players, actual_players, game_mode, round_switch
    actual_players = max_players
    if max_players <= 4:
        game_mode = -7
    elif max_players > 4:
        if round_switch == 9:
            game_mode += 0.1
        elif round_switch == 16:
            game_mode = 0
        elif 9 < round_switch < 16:
            game_mode = 0
        elif 0 < round_switch < 9:
            # could be ranked long/short and surrender before round 9....
            # todo find a way to find out
            game_mode = 0
    # wingman = 7
    # wingman unranked = -7
    # ranked long match = 6
    # ranked short match = 6.1
    # unranked long match = 0
    # unranked short match = 0.1


def _reset_pstats():
    global PLAYERS, team_score, kills_round_list
    for p2 in PLAYERS.values():
        team_score[2] = 0
        team_score[3] = 0
        p2.k = 0
        p2.a = 0
        p2.d = 0
        p2.start_team = None
        p2.team_this_round = None
    kills_round_list.clear()


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
