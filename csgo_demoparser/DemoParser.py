import math
from csgo_demoparser import NETMSG_pb2 as pbuf, PrintStuff as p, consts as c
from csgo_demoparser.ByteReader import Bytebuffer
from csgo_demoparser.BitReader import Bitbuffer
from csgo_demoparser.structures import DemoHeader, CommandHeader, StringTable, UserInfo, MyPlayer, MyRoundStats


class DemoParser:
    def __init__(self, demo_path, dump=None):
        self._buf = Bytebuffer(open(demo_path, "rb").read())
        self.dump = None
        if dump:
            self.dump = open(dump, "w", encoding="utf-8")
            self._counter = [[], [], []]
        self.header = None
        self.game_events_dict = {}
        self._serv_class_dict = {}
        # self.baseline_list = list()
        self._data_tables_dict = {}
        self._string_tables_list = []
        self._class_bits = None
        self.match_started = False
        self.round_current = 1
        self.team_score = {2: 0, 3: 0}
        self._max_players = 0
        self.progress = 0
        self.PLAYERS = {}
        self._BOTS = {}
        self._takeovers = {}
        self.STATS = {}

    def parse(self):
        self.header = DemoHeader(self._buf.read(1072))
        assert self.header.header == "HL2DEMO"
        demo_finished = False
        while not demo_finished:
            command_header = CommandHeader(self._buf.read(6))
            tick = command_header.tick
            self.progress = round(tick / self.header.ticks * 100, 2)
            cmd = command_header.command
            # self.dump.write("cmd= {}\n".format(cmd))
            if self.dump:
                self._update_cmd_counter(cmd, cmd=True)
            if cmd in (c.DEM_SIGNON, c.DEM_PACKET):  # 1 and 2
                self._handle_packet()
            elif cmd in (c.DEM_SYNCTICK, c.DEM_CUSTOMDATA):  # 3 and 8
                pass
            elif cmd == c.DEM_CONSOLECMD:  # 4
                pass
                # self.read_raw_data(None, 0)
            elif cmd == c.DEM_USERCMD:  # 5
                pass
                # self.handle_usercmd(None, 0)
            elif cmd == c.DEM_DATATABLES:  # 6
                self._handle_datatables()
            elif cmd == c.DEM_STRINGTABLES:  # 9
                self._handle_stringtables()
            elif cmd == c.DEM_STOP:  # 7
                self.STATS.update(
                    {self.round_current: MyRoundStats(self.team_score[2], self.team_score[3],
                                                      self.PLAYERS)})
                self.STATS.update({"nrplayers": self._max_players})
                self.STATS.update({"map": self.header.map_name})
                # print(self.progress, "%  >DEMO ENDED<")
                # for p2 in self.PLAYERS.values():
                #     print("name= {} / team= {}".format(p2.name, p2.start_team))
                demo_finished = True
            else:
                demo_finished = True
                print("Demo command not recognised: ", cmd)
                return None
        self._demo_ended_stuff()
        return self.STATS

    def _handle_packet(self):
        self._buf.read(152 + 4 + 4)
        length = self._buf.read_int()
        index = 0
        while index < length:
            msg = self._buf.read_varint()
            size = self._buf.read_varint()
            data = self._buf.read(size)
            # self.dump.write("...msg= {} / size= {}\n".format(msg, size))
            index += self._buf.varint_size(msg) + self._buf.varint_size(size) + size
            if self.dump:
                self._update_cmd_counter(msg, msg=True)
            try:
                getattr(DemoParser, "_pkt_msg" + str(msg))(self, data)
            except AttributeError:
                pass

    def _handle_datatables(self):
        length = self._buf.read_int()
        while True:
            v_type = self._buf.read_varint()
            size = self._buf.read_varint()
            data = self._buf.read(size)
            table = pbuf.CSVCMsg_SendTable()
            table.ParseFromString(data)
            if table.is_end:
                break
            self._data_tables_dict.update({table.net_table_name: table})
        sv_classes = self._buf.read_short()
        self._class_bits = int(math.ceil(math.log2(sv_classes)))
        for i in range(sv_classes):
            my_id = self._buf.read_short()
            name = self._buf.read_string()
            dt = self._buf.read_string()
            # sv_cls = ServerClass()
            # self._serv_class_dict.update({my_id: sv_cls})

    def _handle_stringtables(self):
        length = self._buf.read_int()
        data = self._buf.read(length)

    # PACKET MESSAGES >

    def _pkt_msg12(self, data):
        msg = pbuf.CSVCMsg_CreateStringTable()
        msg.ParseFromString(data)
        msg2 = StringTable(msg)
        self._string_tables_list.append(msg2)
        # print(msg.max_entries, " ", msg.num_entries)
        uinfo = True if msg.name == "userinfo" else False
        self._update_string_table(msg.string_data, msg2.data, uinfo, msg.num_entries, msg.max_entries,
                                  msg.user_data_size_bits, msg.user_data_fixed_size)

    def _update_string_table(self, data, res, uinfo, num_entries, max_entries, user_data_size, user_data_fixsize):
        _buf = Bitbuffer(data)
        history = []
        # ret = []
        entry = None
        entry_bits = int(math.log2(max_entries))
        assert not _buf.read_bit()
        index = 0
        last_index = -1
        for i in range(num_entries):
            index = last_index + 1
            if not _buf.read_bit():
                index = _buf.read_uint_bits(entry_bits)
            last_index = index
            assert 0 <= index <= max_entries
            if _buf.read_bit():
                if _buf.read_bit():
                    idx = _buf.read_uint_bits(5)
                    assert 0 <= idx <= 32
                    btc = _buf.read_uint_bits(c.SUBSTRING_BITS)
                    substring = history[idx][:btc]
                    suffix = _buf.read_string()
                    entry = substring + suffix
                else:
                    entry = _buf.read_string()
                res[index]["entry"] = entry
            user_data = None
            if _buf.read_bit():
                if user_data_fixsize:
                    user_data = _buf.readBits(user_data_size)
                else:
                    size = _buf.read_uint_bits(c.MAX_USERDATA_BITS)
                    user_data = _buf.readBits(size * 8)
                if uinfo:
                    user_data = UserInfo(user_data)
                    self._update_pinfo(user_data)
                    # if user_data.guid == "BOT":
                    #     self._BOTS.update({user_data.user_id: {"team": "no", "name": user_data.name}})
                    #     print("bot {} connected".format(user_data.user_id))
                res[index]["user_data"] = user_data
            if len(history) == 32:
                history.pop(0)
            history.append(entry)

    def _pkt_msg13(self, data):
        msg = pbuf.CSVCMsg_UpdateStringTable()
        msg.ParseFromString(data)
        obj = self._string_tables_list[msg.table_id]
        uinfo = True if obj.name == "userinfo" else False
        if obj.name == "userinfo":  # "instancebaseline"
            self._update_string_table(msg.string_data, obj.data, uinfo, msg.num_changed_entries, obj.max_entries,
                                      obj.uds, obj.udfs)

    def _pkt_msg25(self, data):
        msg = pbuf.CSVCMsg_GameEvent()
        msg.ParseFromString(data)
        if self.dump:
            self._update_cmd_counter(msg.eventid, ev=True)
        args = {}
        for i in range(len(msg.keys)):
            key_name = self.game_events_dict[msg.eventid].keys[i].name
            typed = msg.keys[i].type
            if typed == 1:
                key_val = msg.keys[i].val_string
            elif typed == 2:
                key_val = msg.keys[i].val_float
            elif typed == 3:
                key_val = msg.keys[i].val_long
            elif typed == 4:
                key_val = msg.keys[i].val_short
            elif typed == 5:
                key_val = msg.keys[i].val_byte
            elif typed == 6:
                key_val = msg.keys[i].val_bool
            elif typed == 7:
                key_val = msg.keys[i].val_uint64
            # elif typed == 8:
            #     key_val = msg.keys[i].val_wstring
            else:
                key_val = None
                print("UNKNOWN >", msg.keys[i])
                assert key_val is not None
            args.update({key_name: key_val})
        try:
            getattr(DemoParser, "_my_" + self.game_events_dict[msg.eventid].name)(self, args)
        except AttributeError:
            pass

    def _pkt_msg30(self, data):
        msg = pbuf.CSVCMsg_GameEventList()
        msg.ParseFromString(data)
        for event in msg.descriptors:
            self.game_events_dict.update({event.eventid: event})

    # NO MORE PACKET MESSAGES <

    # EVENTS HANDLERS >

    def _my_player_team(self, data):
        # trying to find out player teams (and bots, mainly bots here) since i'm not parsing entities
        # if data["isbot"]:
        #     print("bot {} joined team {} / disc= {}".format(data["userid"], data["team"], data["disconnect"]))
        # else:
        #     print("player {} joined team {} / disc= {}".format(data["userid"], data["team"], data["disconnect"]))
        if data["team"] == 0:
            if data["isbot"] and self._BOTS.get(data["userid"]):
                self._BOTS.pop(data["userid"])
            return
        if data["isbot"] and not self._BOTS.get(data["userid"]):
            self._BOTS.update({data["userid"]: data["team"]})
            return
        rp = self.PLAYERS.get(data["userid"])
        if rp and rp.start_team is None:
            if self._max_players == 10:
                if self.round_current <= 15:
                    if data["team"] in (2, 3):
                        rp.start_team = data["team"]
                else:
                    if data["team"] == 2:
                        rp.start_team = 3
                    elif data["team"] == 3:
                        rp.start_team = 2
            elif self._max_players == 4:
                if self.round_current <= 8:
                    if data["team"] in (2, 3):
                        rp.start_team = data["team"]
                else:
                    if data["team"] == 2:
                        rp.start_team = 3
                    elif data["team"] == 3:
                        rp.start_team = 2

    def _my_player_death(self, data):
        if self.match_started:
            k = self.PLAYERS.get(data["attacker"])
            a = self.PLAYERS.get(data["assister"])
            d = self.PLAYERS.get(data["userid"])
            kf = self._BOTS.get(data["attacker"])
            af = self._BOTS.get(data["assister"])
            df = self._BOTS.get(data["userid"])
            kto = self._takeovers.get(data["attacker"])
            ato = self._takeovers.get(data["assister"])
            dto = self._takeovers.get(data["userid"])
            # if self.round_current == 7:
            #     print(data)
            if data["assister"] and not data["assistedflash"]:
                if a and not ato:  # asd
                    self.PLAYERS[data["assister"]].a += 1
                    # print("ass", d.userinfo.xuid, d.start_team, a.start_team, df, af)
                    if d and a.start_team and d.start_team and a.start_team == d.start_team:
                        self.PLAYERS[data["assister"]].a -= 1
                    elif not df and a.start_team and a.start_team == df:
                        self.PLAYERS[data["assister"]].a -= 1
            if k and not kto:
                self.PLAYERS[data["attacker"]].k += 1
            if d and not dto:
                self.PLAYERS[data["userid"]].d += 1
            if d and not dto and data["userid"] == data["attacker"]:
                self.PLAYERS[data["userid"]].k -= 2
            else:
                if k and not kto and d and k.start_team and d.start_team and k.start_team == d.start_team:
                    self.PLAYERS[data["attacker"]].k -= 2
                elif k and not kto and not df and k.start_team and k.start_team == df:
                    self.PLAYERS[data["attacker"]].k -= 2

    def _my_player_spawn(self, data):
        # trying to find out player teams since i'm not parsing entities
        if data["teamnum"] == 0:
            return
        rp = self.PLAYERS.get(data["userid"])
        # print(data["userid"], bp, rp)
        # print("inside")
        # print(self.round_current, ">", bp, rp.start_team if rp else None)
        if rp and rp.start_team is None:
            if self._max_players == 10:
                if self.round_current <= 15:
                    if data["teamnum"] in (2, 3):
                        rp.start_team = data["teamnum"]
                else:
                    if data["teamnum"] == 2:
                        rp.start_team = 3
                    elif data["teamnum"] == 3:
                        rp.start_team = 2
            elif self._max_players == 4:
                if self.round_current <= 8:
                    if data["teamnum"] in (2, 3):
                        rp.start_team = data["teamnum"]
                else:
                    if data["teamnum"] == 2:
                        rp.start_team = 3
                    elif data["teamnum"] == 3:
                        rp.start_team = 2
        # print(">>", self._BOTS.get(data["userid"]), rp.start_team if rp else None)
        # print(".................................................")

    def _my_bot_takeover(self, data):
        if self.match_started:
            self._takeovers.update({data["userid"]: 1})

    def _my_begin_new_match(self, data):
        if self.match_started:
            self._reset_pstats()
        self.match_started = True
        # print("MATCH STARTED.....................................................................")

    def _my_round_end(self, data):
        if self.match_started:
            if self.round_current > 15:
                if data["winner"] == 2:
                    data["winner"] = 3
                elif data["winner"] == 3:
                    data["winner"] = 2
            if data["winner"] == 2:
                self.team_score[2] += 1
            elif data["winner"] == 3:
                self.team_score[3] += 1
            # print("    {} / {}".format(data["reason"], data["message"]))

    def _my_round_officially_ended(self, data):
        if self.match_started:
            self.STATS.update(
                {self.round_current: MyRoundStats(self.team_score[2], self.team_score[3], self.PLAYERS)})
            self.round_current += 1
            self._takeovers.clear()
        # print("ROUND {}..........................................................".format(self.round_current))

    # NO MORE EVENTS HANDLERS <

    def _reset_pstats(self):
        for p2 in self.PLAYERS.values():
            self.team_score[2] = 0
            self.team_score[3] = 0
            p2.k = 0
            p2.a = 0
            p2.d = 0
            p2.start_team = None

    def _update_pinfo(self, data):
        if data.guid != "BOT":
            exist = None
            for x in self.PLAYERS.items():
                if data.xuid == x[1].userinfo.xuid:
                    exist = x[0]
                    break
            if exist:
                self.PLAYERS[exist].update(data, ui=True)
                if exist != data.user_id:
                    self.PLAYERS.update({data.user_id: self.PLAYERS[exist]})
                    self.PLAYERS.pop(exist)
            else:
                self.PLAYERS.update({data.user_id: MyPlayer(data, ui=True)})
            self._max_players = len(self.PLAYERS)

    def _update_cmd_counter(self, value, cmd=False, msg=False, ev=False):
        if cmd is True:
            for item in self._counter[0]:
                if item[0] == value:
                    item[1] += 1
                    return
            self._counter[0].append([value, 1])
            return
        elif msg is True:
            for item in self._counter[1]:
                if item[0] == value:
                    item[1] += 1
                    return
            self._counter[1].append([value, 1])
            return
        elif ev is True:
            for item in self._counter[2]:
                if item[0] == value:
                    item[1] += 1
                    return
            self._counter[2].append([value, 1])
            return

    def _demo_ended_stuff(self):
        if self.dump:
            p.print_header(self.dump, self.header)
            p.print_event_list(self.dump, self.game_events_dict)
            p.print_counter(self.dump, self._counter)
            # p.print_userinfo(self.dump, self._string_tables_list)
            p.print_players_userinfo(self.dump, self.PLAYERS)
            p.print_match_stats(self.dump, self.STATS)
            # for x in self.players_userinfo.items():
            #     print(x[0], x[1].name)
