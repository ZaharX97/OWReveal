import struct
import copy

import csgo_demoparser.consts as c
from csgo_demoparser.ByteReader import Bytebuffer


class DemoHeader:
    """1072 Byte header for .DEM file.

    This header has the following format:

    +-----------+---------------------------------------+
    | Byte      | Description                           |
    +===========+=======================================+
    | 0-7       | Fixed string 'HL2DEMO\0'.             |
    +-----------+---------------------------------------+
    | 8-11      | Demo file protocol version.           |
    +-----------+---------------------------------------+
    | 12-15     | Network protocol version.             |
    +-----------+---------------------------------------+
    | 16-275    | Server name.                          |
    +-----------+---------------------------------------+
    | 276-535   | Name of client who recorded the demo. |
    +-----------+---------------------------------------+
    | 536-795   | Map name.                             |
    +-----------+---------------------------------------+
    | 796-1055  | Game directory.                       |
    +-----------+---------------------------------------+
    | 1056-1059 | Playback time in seconds.             |
    +-----------+---------------------------------------+
    | 1060-1063 | Number of ticks in demo.              |
    +-----------+---------------------------------------+
    | 1064-1067 | Number of frames in demo.             |
    +-----------+---------------------------------------+
    | 1068-1071 | Length of signon data.                |
    +-----------+---------------------------------------+
    """

    def __init__(self, data):
        buf = Bytebuffer(data)
        self.header = struct.unpack("8s", buf.read(8))[0].strip(b"\0").decode()
        self.demo_protocol = struct.unpack("<I", buf.read(4))[0]
        self.network_protocol = struct.unpack("<I", buf.read(4))[0]
        self.server_name = struct.unpack("260s", buf.read(c.MAX_PATH))[0].strip(b"\0").decode()
        self.client_name = struct.unpack("260s", buf.read(c.MAX_PATH))[0].strip(b"\0").decode()
        self.map_name = struct.unpack("260s", buf.read(c.MAX_PATH))[0].strip(b"\0").decode()
        self.game_directory = struct.unpack("260s", buf.read(c.MAX_PATH))[0].strip(b"\0").decode()
        self.playback_time = struct.unpack("<f", buf.read(4))[0]
        self.ticks = struct.unpack("<I", buf.read(4))[0]
        self.frames = struct.unpack("<I", buf.read(4))[0]
        self.signon_length = struct.unpack("<I", buf.read(4))[0]
        del buf


class CommandHeader:
    """Header for each command packet.

    .. _header-format:

    The header has the following format:

    +------+--------------+
    | Byte | Description  |
    +======+==============+
    | 0    | Command ID   |
    +------+--------------+
    | 1-4  | Current tick |
    +------+--------------+
    | 5    | Player ID    |
    +------+--------------+
    """

    def __init__(self, data):
        buf = Bytebuffer(data)
        self.command = struct.unpack("<B", buf.read(1))[0]
        self.tick = struct.unpack("<I", buf.read(4))[0]
        self.player = struct.unpack("<B", buf.read(1))[0]
        del buf


# class QAngle(Structure):
#     pitch = SLFloat32()
#     yaw = SLFloat32()
#     roll = SLFloat32()
#
#
# class Vector(Structure):
#     x = SLFloat32()
#     y = SLFloat32()
#     z = SLFloat32()
#
#
# class OriginViewAngles(Structure):
#     view_origin = SubstructureField(Vector)
#     view_angles = SubstructureField(QAngle)
#     local_view_angles = SubstructureField(QAngle)
#
#
# class SplitCommandInfo(Structure):
#     flags = ULInt32()
#     original = SubstructureField(OriginViewAngles)
#     resampled = SubstructureField(OriginViewAngles)
#
#
# class CommandInfo(Structure):
#     commands = FieldArray(SplitCommandInfo)


class UserInfo:
    """Player data.

    This structure has the following format:

    +---------+---------------------------------------+
    | Byte    | Description                           |
    +=========+=======================================+
    | 0-7     | Version. Same for all players.        |
    +---------+---------------------------------------+
    | 8-15    | xuid. Some sort of unique ID.         |
    +---------+---------------------------------------+
    | 15-142  | Player name.                          |
    +---------+---------------------------------------+
    | 143-146 | Local server user ID.                 |
    +---------+---------------------------------------+
    | 147-179 | GUID                                  |
    +---------+---------------------------------------+
    | 180-183 | Friend's ID.                          |
    +---------+---------------------------------------+
    | 184-312 | Friend's Name.                        |
    +---------+---------------------------------------+
    | 313     | Is player a bot?                      |
    +---------+---------------------------------------+
    | 314     | Is player an HLTV proxy?              |
    +---------+---------------------------------------+
    | 314-329 | Custom files CRC.                     |
    +---------+---------------------------------------+
    | 330     | Numbre of files downloaded by server. |
    +---------+---------------------------------------+
    | 331-335 | Entity index.                         |
    +---------+---------------------------------------+
    | 336-340 | No idea.                              |
    +---------+---------------------------------------+
    """

    def __init__(self, data):
        buf = Bytebuffer(data)
        self.version = struct.unpack(">Q", buf.read(8))[0]
        self.xuid = struct.unpack(">Q", buf.read(8))[0]
        self.name = struct.unpack("128s", buf.read(c.MAX_PLAYER_NAME_LENGTH))[0].strip(b"\0").decode(
            errors="replace").strip("\n")
        self.user_id = struct.unpack(">I", buf.read(4))[0]
        self.guid = struct.unpack("33s", buf.read(c.SIGNED_GUID_LEN))[0].strip(b"\0").decode(errors="replace")
        self.friends_id = struct.unpack(">I", buf.read(4))[0]
        self.friends_name = struct.unpack("128s", buf.read(c.MAX_PLAYER_NAME_LENGTH))[0].strip(b"\0").decode(
            errors="replace").strip("\n")
        self.fake_player = struct.unpack(">B", buf.read(1))[0]
        self.is_hltv = struct.unpack(">B", buf.read(1))[0]
        self.custom_files = struct.unpack(">IIII", buf.read(c.MAX_CUSTOM_FILES * 4))
        self.files_downloaded = struct.unpack(">B", buf.read(1))[0]
        self.entity_id = struct.unpack(">I", buf.read(4))[0]
        self.tbd = struct.unpack(">I", buf.read(4))[0]
        del buf


class StringTable:
    def __init__(self, msg):
        self.name = msg.name
        self.max_entries = msg.max_entries
        self.udfs = msg.user_data_fixed_size
        self.uds = msg.user_data_size
        self.udsb = msg.user_data_size_bits
        self.data = []
        for i in range(self.max_entries):
            self.data.append({"entry": None, "user_data": None})


class ServerClass:
    def __init__(self, id2, name, dt_name):
        self.id = id2
        self.name = name
        self.dt = dt_name
        self.fprops = None


class Entity:
    def __init__(self, parser, entity_id, cls_id, serial, parse=True):
        self.class_id = cls_id
        self.class_name = parser._serv_class_dict[cls_id].name
        self.parse = parse
        if parse:
            self.parser = parser
            self.entity_id = entity_id
            self.serial = serial
            self.props = dict()
            self.props = copy.deepcopy(parser._baselines_dict[cls_id])

    def update(self, table, key, value):
        # if self.parse and self.props.get(table) and self.props[table].get(key):
        self.props[table][key] = value

    def find(self, name: str):
        name = name.upper()
        ret = dict()
        for table in self.props.items():
            if table[0].upper().find(name) != -1:
                ret.update({table[0]: table[1]})
            for prop in table[1].items():
                if prop[0].upper().find(name) != -1:
                    ret.update({prop[0]: prop[1]})
        if len(ret.items()):
            return ret
        else:
            return None

    def get_table(self, name: str):
        if self.props.get(name):
            return self.props[name]
        else:
            return None

    def get_prop(self, name: str):
        for keyd in self.props.values():
            for key in keyd.items():
                if key[0] == name:
                    return key[1]
        return None

# EVENT
# name
# eventid
# keys
#     name
#     type
