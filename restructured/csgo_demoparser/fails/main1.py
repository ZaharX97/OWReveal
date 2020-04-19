import struct
import NETMSG_pb2 as Pbuf
# copied the whole bitreader class from https://github.com/holosiek/csgodemo-python/blob/master/csgo.py
import BitReader as br
import math


class DEM:
    SIGNON = 1
    PACKET = 2
    SYNCTICK = 3
    CONSOLECMD = 4
    USERCMD = 5
    DATATABLES = 6
    STOP = 7
    CUSTOMDATA = 8
    STRINGTABLES = 9


demo_path2 = r"C:\Users\Zahar\Desktop\asd\demo.dem"


# valve demo parser https://github.com/ValveSoftware/csgo-demoinfo
#
# the projects below have comments and explain what some methods do
#
# useful demo parser project https://github.com/ibm-dev-incubator/demoparser
# another one https://github.com/holosiek/csgodemo-python
# and another one https://github.com/markus-wa/demoinfocs-golang
#
# csgo unpacked files? https://github.com/SteamDatabase/GameTracking-CSGO

# i'll write here how i understand csgo demos work
#
# first 1072 bytes = demo header
# repeat until end >
# read 1 + 4 + 1 bytes for (_command / _tick / _playerslot)
#       if _command is 1 or 2 (SIGNON, PACKET) >
#           read 160 bytes (useless?)
#           read 4 bytes (length of packet)
#           repeat until length end >
#               read variable bytes (_message) (can't figure out how)
#                   _message is a SVC or NET number defined in netmessages.proto
#               read variable bytes (_size)
#               read _size bytes (_data)
#       if _command is 3 (SYNCTICK) > pass
#       if _command is 4 (CONSOLECMD) > pass?
#       if _command is 5 (USERCMD) > pass?
#       if _command is 6 (DATATABLES) >
#           read 4 bytes (_length)
#           repeat until last DATA TABLE (or SEND TABLE?) >
#               read variable bytes (_type) (useless?)
#               read variable bytes (_size)
#               read _size bytes (_data)
#               use protobuf class to decode _data
#           read 2 bytes (_nr of server classes) (idk what is this)
#           for every sv_class >
#               read 2 bytes (_classid)
#               read 1 byte at a time until 0 is reached (_name)
#               read 1 byte at a time until 0 is reached (_DATA_TABLE_name)
#               the data tables can be (should be?) linked to server classes
#       if _command is 7 (STOP) > that's the whole demo
#       if _command is 8 (CUSTOMDATA) > pass?
#       if _command is 9 (STRINGTABLES) > idk
#
# use _message to get data (list of game events, event ids, names)
# ex: _message #30 is a list of all game events and id's and variable names for each event
# _message #25 is an actual event (ex: player_death, where you can get info about killer and other)
# _message #12 (not sure yet) lists of data (ex: userinfo > info about players)
# todo figure out how to use this
# _message #13 (not sure yet) updated data throughout the game for the lists at _message #12


def placeholder():
    print("wtf")


class MsgHandler:
    # use classes from .proto file
    def msg12(self):
        data = Pbuf.CSVCMsg_CreateStringTable()
        data.ParseFromString(self.data)
        self.target.fdump.write("\nCRSTRTBL> " + str(data) + "\n")
        # if data.name == "userinfo":
        #     print("x")
        table = [[data.name, data.max_entries, data.user_data_fixed_size, data.user_data_size_bits]]
        for i in range(data.max_entries):
            table.append([None, None])
        self.parseStringTable(data, table, 0)
        self.target.string_tables_list.append(table)

    def msg13(self):
        data = Pbuf.CSVCMsg_UpdateStringTable()
        data.ParseFromString(self.data)
        # if self.target.string_tables_list[data.table_id][0][0] == "instancebaseline":
            # print("da")
        if self.target.string_tables_list[data.table_id][0][0] == "userinfo":
            self.parseStringTable(data, self.target.string_tables_list[data.table_id])

    def msg25(self):
        data = Pbuf.CSVCMsg_GameEvent()
        data.ParseFromString(self.data)
        self.target.fdump.write("\nGEVNT> " + str(data) + "\n")
        # self.event2dict(data)
        if data.eventid == 7:
            self.player_connect(self.event2dict(data))
        elif data.eventid == 51:
            self.start_match()
        elif self.target.match_started is True and data.eventid == 24:
            self.player_death(self.event2dict(data))
        elif self.target.match_started is True and data.eventid == 45:
            self.round_ended()

    def msg26(self):
        print("ONCE")
        data = Pbuf.CSVCMsg_PacketEntities()
        data.ParseFromString(self.data)
        actual_data = br.CBitRead(data.entity_data)
        index = 0
        entity_index = -1
        for index in range(data.updated_entries):
            entity_index += 1 + actual_data.readUBitVar()
            if actual_data.readBit():
                if actual_data.readBit():
                    print("delete entity ", entity_index)
                    self.target.entity_dict.update({entity_index: None})
            elif actual_data.readBit():
                class_id = actual_data.readUBitLong(self.target.class_bits)
                print("clsid= ", class_id)
                serial = actual_data.readUBitLong(10)
                print("ei= {} / clsid= {}".format(entity_index, self.target.serv_class_dict[class_id].name))
                res = br.parse_entity_update(actual_data, self.target.serv_class_dict[class_id], [])
                print(res)
                self.target.entity_dict.update({entity_index: [class_id, res]})
            else:
                class_id = self.target.entity_dict.get(entity_index, None)
                res = br.parse_entity_update(actual_data, class_id, [])
                print("2= {}".format(res))
        self.target.fdump.write("\n{}\n".format(str(data)))

    def msg30(self):
        data = Pbuf.CSVCMsg_GameEventList()
        data.ParseFromString(self.data)
        for field in data.descriptors:
            keylist = []
            for key in field.keys:
                keylist.append([key.type, key.name])
            self.target.game_events_dict.update({field.eventid: [field.name, keylist]})
        # print(self.target.game_events_dict)

    def start_match(self):
        self.target.match_started = True

    def round_ended(self):
        # todo add score/round
        self.target.round_current += 1
        # print("\nROUND ENDED\n")

    def player_death(self, event):
        killed = ""
        killer = ""
        helper = ""
        if self.target.scoreboard_dict.get(event["userid"]) is not None:
            killed = self.target.scoreboard_dict[event["userid"]]
            killed.deaths += 1
            # self.target.scoreboard_dict[event["userid"]].deaths += 1
        if self.target.scoreboard_dict.get(event["attacker"]) is not None:
            killer = self.target.scoreboard_dict[event["attacker"]]
            killer.kills += 1
            # self.target.scoreboard_dict[event["attacker"]].kills += 1
        if self.target.scoreboard_dict.get(event["assister"]) is not None:
            helper = self.target.scoreboard_dict[event["assister"]]
            helper.assists += 1
            # self.target.scoreboard_dict[event["assister"]].assists += 1
        # if killer.steam_id == killed.steam_id:
        #     print("\nSUICIDE\n")
        #     killer.kills -= 2
        # if killed != "":
        #     killed = killed.name
        # if killer != "":
        #     killer = killer.name
        # if helper != "":
        #     helper = helper.name
        # print(killer + " + " + helper + " > " + killed)

    def player_connect(self, event):
        if event["networkid"] == "BOT":
            return
        for player in self.target.scoreboard_dict.values():
            if player.steam_id == event["networkid"]:
                self.target.scoreboard_dict.update({event["userid"]: player})
                self.target.scoreboard_dict.pop(player.userid)
                self.target.scoreboard_dict[event["userid"]].name = event["name"]
                self.target.scoreboard_dict[event["userid"]].index = event["index"]
                self.target.scoreboard_dict[event["userid"]].userid = event["userid"]
                return
        newPlayer = DemoFile.Player()
        newPlayer.name = event["name"]
        newPlayer.index = event["index"]
        newPlayer.userid = event["userid"]
        newPlayer.steam_id = event["networkid"]
        self.target.scoreboard_dict.update({event["userid"]: newPlayer})

    def event2dict(self, event):
        result = {event.eventid: self.target.game_events_dict[event.eventid][0]}
        for i in range(len(event.keys)):
            name = self.target.game_events_dict[event.eventid][1][i][1]
            result.update({name: self.get_right_val(event.keys[i])})
        return result

    def get_right_val(self, key):
        if key.type == 1:
            return key.val_string
        if key.type == 2:
            return key.val_float
        if key.type == 3:
            return key.val_long
        if key.type == 4:
            return key.val_short
        if key.type == 5:
            return key.val_byte
        if key.type == 6:
            return key.val_bool
        return key.val_uint64

    def parseStringTable(self, data, table, update=1):
        # i dont understand what's happening here
        lastEntry = -1
        string_data = br.CBitRead(data.string_data)
        stringo = ""
        entryBits = int(math.log2(table[0][1]))
        if string_data.readBit():
            return
        if update == 1:
            x2 = data.num_changed_entries
            name = table[0][0]
        else:
            x2 = data.num_entries
            name = data.name
        for i in range(x2):
            entryIndex = lastEntry + 1
            if not string_data.readBit():
                entryIndex = int(string_data.readUBitLong(entryBits))
            lastEntry = entryIndex
            if string_data.readBit():
                if string_data.readBit():
                    index = string_data.readUBitLong(5)
                    bytestocpy = string_data.readUBitLong(5)
                    stringo = string_data.readString()
                else:
                    stringo = string_data.readString()
                # print("1 ", stringo)
                table[entryIndex + 1][0] = stringo
            userData = ""
            if string_data.readBit():
                if table[0][2]:
                    userData = string_data.readBits(table[0][3])
                else:
                    bytez = string_data.readUBitLong(14)
                    userData = string_data.readBytes(bytez)
                table[entryIndex + 1][1] = userData
            if name == "instancebaseline" and len(userData):
                class_id = int(stringo)
                if len(self.target.serv_class_dict):
                    self.target.baseline_list.append([class_id, userData])
                    br.parseBaselines(self.target.baseline_list, self.target.serv_class_dict[class_id],
                                      self.target.data_tables_dict)
                else:
                    self.target.baseline_list.append([class_id, userData])
            if name == "userinfo" and len(userData):
                playerInfo = DemoFile.PlayerInfo()
                playerInfo.add_info(userData, entryIndex)
                # if playerInfo.guid == "BOT":
                #     continue
                # print("name= {} / entity_id= {}".format(playerInfo.name, playerInfo.entityID))
                if self.target.scoreboard_dict.get(entryIndex) is None and playerInfo.guid != "BOT":
                    newPlayer = DemoFile.Player()
                    newPlayer.name = playerInfo.name
                    newPlayer.userid = entryIndex
                    newPlayer.steam_id = playerInfo.guid
                    self.target.scoreboard_dict.update({entryIndex: newPlayer})
                exist = False
                # for item in self.target.player_info_list:
                #     if item.entityID == entryIndex:
                #         exist = True
                if exist is False:
                    self.target.player_info_list.append(playerInfo)

    def __init__(self, number, data, target):
        self.target = target
        self.data = data
        name = "msg" + str(number)
        getattr(self, name)()
        # try:
        #     getattr(self, name)()
        # except AttributeError:
        #     print("msg({}) not handled".format(number))


class DemoFile:
    class Header:
        def __init__(self, data: tuple):
            self.stamp = data[0].decode()
            self.protocol = data[1]
            self.network_protocol = data[2]
            self.server_name = data[3].decode()
            self.client_name = data[4].decode()
            self.map_name = data[5].decode()
            self.game_dir = data[6].decode()
            self.play_time = data[7]
            self.play_ticks = data[8]
            self.play_frames = data[9]
            self.signon = data[10]

    class Player:
        def update(self, k=None, a=None, d=None, t=None, index=None, userid=None):
            if k is not None:
                self.kills += k
            if a is not None:
                self.assists += a
            if d is not None:
                self.deaths += d
            if t is not None:
                self.startTeam = t
            if index is not None:
                self.index = index
            if userid is not None:
                self.userid = userid

        def __init__(self):
            self.name = ""
            self.steam_id = ""
            self.index = 0
            self.userid = 0
            self.kills = 0
            self.assists = 0
            self.deaths = 0
            self.startTeam = None

    class PlayerInfo:
        def add_info(self, data, id2):
            data = struct.unpack("2Q128si33sI128s2?3LBi", data)
            self.version = data[0]
            self.xuid = data[1]
            self.name = data[2].split(b"\0", 1)[0].decode()
            self.userID = data[3]
            self.guid = data[4].split(b"\0", 1)[0].decode()
            self.friendsID = data[5]
            self.friendsName = data[6].split(b"\0", 1)[0].decode()
            self.fakeplayer = data[7]
            self.ishltv = data[8]
            self.customFiles = data[9]
            self.filesDownloaded = [data[10], data[11], data[12], data[13]]
            self.entityID = id2

        def __init__(self):
            self.version = 0
            self.xuid = 0
            self.name = ""
            self.userID = 0
            self.guid = ""
            self.friendsID = 0
            self.friendsName = ""
            self.fakeplayer = False
            self.ishltv = False
            self.customFiles = []
            self.filesDownloaded = 0
            self.entityID = 0

    class ServerClass:
        def show(self, file):
            file.write("    classID={}".format(self.classID))
            file.write("    name={}".format(self.name))
            file.write("    DTname={}".format(self.DTname))
            file.write("    valuess=\n{}\n".format(self.valuess))
            # file.write("     dataTable={}".format(self.dataTable))

        def __init__(self):
            self.classID = 0
            self.name = ""
            self.DTname = ""
            # self.dataTable = ""
            self.propss = list()
            self.valuess = dict()

    def read_next_cmd(self):
        cmd = self.read_byte()
        tick = self.read_int()
        player_slot = self.read_byte()
        self.fdump.write("cmd= {} / tick= {} / pslot= {} \n".format(cmd, tick, player_slot))
        return cmd, tick, player_slot

    def read_cmd_data(self):
        # useless data? idk
        return self.file.read(152)

    def read_seq_data(self):
        # two ints
        data = self.file.read(8)
        return struct.unpack("ii", data)

    def cmd_read_packet_data(self):
        length = self.read_int()
        index = 0
        while index < length:
            # so cmd and size are not always exactly 4 bytes /
            # we need to read bits? 4 bytes = 32 bits
            msg = self.read_varint()
            size = self.read_varint()
            data = self.file.read(size)
            index += self._varint_size(msg) + self._varint_size(size) + size
            self.update_cmd_counter(msg, False)
            self.fdump.write("....msg= {} / size= {} \n".format(msg, size))
            if msg in (12, 13, 25, 26, 30):
                MsgHandler(msg, data, self)
                # todo
            else:
                pass
                # print("cmd out of range")

    def cmd_read_data_tables(self):
        length = self.read_int()
        # index = 0
        while True:
            typed = self.read_varint()
            size = self.read_varint()
            table = Pbuf.CSVCMsg_SendTable()
            table.ParseFromString(self.file.read(size))
            # index += self._varint_size(typed) + self._varint_size(size) + size
            # self.fdump.write("DatTbl  " + str(table) + "\n")
            if table.is_end is True:
                break
            self.data_tables_dict.update({table.net_table_name: table})
        sv_classes = self.read_shortint()
        self.class_bits = int(math.ceil(math.log2(sv_classes)))
        # index += 2
        for i in range(sv_classes):
            data = DemoFile.ServerClass()
            data.classID = self.read_shortint()
            data.name = self.read_string()
            data.DTname = self.read_string()
            data.dataTable = self.data_tables_dict[data.DTname]
            self.serv_class_dict.update({data.classID: data})
            # self.fdump.write("\nServCls  ")
            # data.show(self.fdump)
            data.propss.extend(br.flatten(data.DTname, self.data_tables_dict))
        br.parseBaselines(self.baseline_list, self.serv_class_dict, self.data_tables_dict)

    def cmd_read_next_packet(self):
        self.read_cmd_data()
        self.read_seq_data()
        self.cmd_read_packet_data()

    def read_until_end(self):
        while True:
            cmd_data = self.read_next_cmd()
            self.update_cmd_counter(cmd_data[0])
            if cmd_data[0] in (DEM.SIGNON, DEM.PACKET):
                self.cmd_read_next_packet()
            elif cmd_data[0] == DEM.SYNCTICK:
                pass
            elif cmd_data[0] in (DEM.CONSOLECMD, DEM.USERCMD, DEM.CUSTOMDATA):
                # i've never met this and it's skipped in valve's reader
                # if encountered, check first link for potential fix
                print("cmd: " + cmd_data[0] + " shouldnt be met")
                pass
            elif cmd_data[0] == DEM.DATATABLES:
                self.cmd_read_data_tables()
            elif cmd_data[0] == DEM.STRINGTABLES:
                # didnt encounter this yet
                length = self.read_int()
                data = self.file.read(length)
                data = br.CBitRead(data)
                num_tables = data.readUBitLong(8)
                for item in range(num_tables):
                    print("table_name= {}".format(data.readString()))
                # todo
                # pass
            elif cmd_data[0] == DEM.STOP:
                print("\nDEMO ENDED\n")
                break
            else:
                print("cmd: " + cmd_data[0] + " not recognised")
                break
        # todo
        self.fdump.write("\nDataTablesx  \n")
        for item in self.data_tables_dict.items():
            self.fdump.write(str(item))
            self.fdump.write("\n")
        self.fdump.write("\nServCls  \n")
        for item in self.serv_class_dict.values():
            item.show(self.fdump)
        self.fdump.write("\n GEVLIST: \n")
        for item in self.game_events_dict.items():
            self.fdump.write(str(item))
            self.fdump.write("\n")
        self.string_tables_print()
        self.players_print()
        self.fdump.write("\nheader total ticks: " + str(self.header.play_ticks) + "\n")
        self.cmd_counter_print()
        self.players_print2()

    def read_byte(self):
        data = self.file.read(1)
        data = struct.unpack("B", data)[0]
        return data

    def read_string(self):
        string = ""
        while True:
            data = self.file.read(1)
            data = struct.unpack("B", data)[0]
            if data == 0:
                break
            string += chr(data)
        return string

    def read_int(self):
        data = self.file.read(4)
        data = struct.unpack("i", data)[0]
        return data

    def read_shortint(self):
        data = self.file.read(2)
        data = struct.unpack("h", data)[0]
        return data

    def read_varint(self):
        count = 0
        result = 0
        cont = True
        while cont:
            b = self.read_byte()
            if count < 5:
                result |= (b & 0x7F) << (7 * count)
            count += 1
            cont = b & 0x80
        return result

    def _varint_size(self, value):
        if value < 1 << 7:
            return 1
        elif value < 1 << 14:
            return 2
        elif value < 1 << 21:
            return 3
        elif value < 1 << 28:
            return 4
        else:
            return 5

    def update_cmd_counter(self, value, cmd=True):
        if cmd is True:
            for item in self.cmd_msg_counter[0]:
                if item[0] == value:
                    item[1] += 1
                    return
            self.cmd_msg_counter[0].append([value, 1])
            return
        else:
            for item in self.cmd_msg_counter[1]:
                if item[0] == value:
                    item[1] += 1
                    return
            self.cmd_msg_counter[1].append([value, 1])
            return

    def cmd_counter_print(self):
        print("CMDS:")
        for item in self.cmd_msg_counter[0]:
            print("cmd= {} / count= {}".format(item[0], item[1]))
        print("MSGS:")
        for item in self.cmd_msg_counter[1]:
            print("msg= {} / count= {}".format(item[0], item[1]))

    def string_tables_print(self):
        self.fdump.write("DATA TABLESS>\n")
        for item in self.string_tables_list:
            self.fdump.write("{}\n".format(item))

    def players_print(self):
        self.fdump.write("PLAYER USERINFO>\n")
        for item in self.player_info_list:
            self.fdump.write("{} / {} / ".format(item.version, item.xuid))
            self.fdump.write(item.name)
            self.fdump.write(" / {} / {} / {} / {} / ".format(item.userID, item.guid, item.friendsID, item.friendsName))
            self.fdump.write("{} / {} / {} /".format(item.fakeplayer, item.ishltv, item.customFiles))
            self.fdump.write("{} / {}\n".format(item.filesDownloaded, item.entityID))

    def players_print2(self):
        for player in self.scoreboard_dict.values():
            print("{} / {} / {} / {}".format(player.name, player.index, player.userid, player.steam_id))
            print("K: {} / A: {} / D: {}\n".format(player.kills, player.assists, player.deaths))

    def __init__(self, demo_path):
        self.match_started = False
        self.path = demo_path
        self.file = open(self.path, "rb")
        self.fdump = open(r"C:\Users\Zahar\Desktop\asd\demodump.txt", "w", encoding="utf-8")
        self.cmd_msg_counter = [[], []]
        data = self.file.read(1072)
        self.header = DemoFile.Header(struct.unpack("8sii260s260s260s260sfiii", data))
        self.game_events_dict = dict()
        self.serv_class_dict = dict()
        self.baseline_list = list()
        self.data_tables_dict = dict()
        self.string_tables_list = list()
        self.player_info_list = list()
        self.entity_dict = dict()
        self.scoreboard_dict = dict()
        self.round_current = 1
        self.class_bits = 0


x = DemoFile(demo_path2)
x.read_until_end()
# x.read_until_cmd()
# x.read_next_packet()
