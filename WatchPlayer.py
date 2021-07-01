import datetime as dt
import myglobals as g


class MyWatchPlayer:
    def _read(self, amount, string=False):
        if amount <= 0:
            return
        if string:
            ret = self.data[1:amount + 2]
            self.data = self.data[amount + 2:]
        else:
            ret = self.data[:amount]
            self.data = self.data[amount:]
        return ret

    def update(self, name, link, datetime: str):
        self.name = name
        self.link = link
        self.datetime = datetime
        self.date = datetime[:10]

    def ret_string(self):
        ret = ""
        ret += "{} {} {} ".format(self.link[self.link.rfind("/") + 1:], self.banned,
                                  self.dtt.strftime("%d-%b-%Y %H:%M:%S%z"))
        ret += "{}={} ".format(len(self.name), self.name)
        ret += "{}={} {}={} ".format(len(self.kad), self.kad, len(self.map), self.map)
        ret += "{}={} {}={} ".format(len(str(self.rank)), self.rank, len(self.server), self.server)
        ret += "{}={} {}={}".format(len(str(self.mode)), self.mode, len(str(self.ban_speed)), self.ban_speed)
        if len(self.comm):
            ret += " {}\n".format(self.comm)
        else:
            ret += "\n"
        return ret

    def ret_csv(self):
        return self.link[36:], self.banned, self.dtt.strftime("%d-%b-%Y %H:%M:%S%z"), self.name, self.kad, self.map, self.rank, self.server, self.mode, self.ban_speed, self.comm

    def __init__(self, data=None, old=False):
        self.name = None
        self.rank = None
        self.link = None
        self.datetime = None
        self.date = None
        self.comm = None
        self.banned = None
        self.dtt = None
        self.kad = None
        self.map = None
        self.server = None
        self.mode = None
        self.ban_speed = None

        if data:
            self.data = data
            # length = self.data[:self.data.find("=")]
            # self._read(2 + len(length))
            if old:
                self._get_player_old()
            else:
                self._get_player()
            del self.data

    def _get_player(self):
        self.link = "https://steamcommunity.com/profiles/" + self.data[0]
        self.banned = self.data[1]
        try:
            self.dtt = dt.datetime.strptime(self.data[2], "%d-%b-%Y %H:%M:%S%z")
        except ValueError:
            self.dtt = dt.datetime.strptime(self.data[2], "%d-%b-%Y %H:%M:%S").astimezone()
        self.date = self.dtt.strftime("%d-%b-%Y %H:%M:%S%z")[:11]
        self.name = self.data[3]
        self.kad = self.data[4]
        self.map = self.data[5]
        try:
            self.rank = int(self.data[6])
            self.server = self.data[7]
            self.mode = int(self.data[8])
        except IndexError:
            self.rank = 0
            self.server = "Unknown"
            self.mode = 0
            self.comm = self.data[6]
        try:
            self.ban_speed = int(self.data[9])
        except IndexError:
            self.ban_speed = -1
        try:
            self.comm = self.data[10]
        except IndexError:
            self.comm = ""

    def _get_player_old(self):
        self.link = "https://steamcommunity.com/profiles/" + self._read(17, string=False)
        self._read(1)
        self.banned = self._read(1)
        self._read(1)
        self.dtt = self._read(20)
        length = self._read(1)
        if length != " ":
            self.dtt += length
            length = self.data.index(" ")
            self.dtt += self._read(length)
            self._read(1)
            self.dtt = dt.datetime.strptime(self.dtt, "%d-%b-%Y %H:%M:%S%z")
            self.date = self.dtt.strftime("%d-%b-%Y %H:%M:%S%z")[:11]
        else:
            self.dtt = dt.datetime.strptime(self.dtt, "%d-%b-%Y %H:%M:%S").astimezone()
            self.date = self.dtt.strftime("%d-%b-%Y %H:%M:%S%z")[:11]
        length = self.data[:self.data.find("=")]
        self._read(1 + len(length))
        self.name = self._read(int(length))
        self._read(1)
        length = self.data[:self.data.find("=")]
        self._read(1 + len(length))
        self.kad = self._read(int(length))
        self._read(1)
        length = self.data[:self.data.find("=")]
        self._read(1 + len(length))
        self.map = self._read(int(length))
        length = self.data.find("=")
        if length != -1:
            self._read(1)
            length = self.data[:length-1]
            self._read(1 + len(length))
            self.rank = int(self._read(int(length)))
            self._read(1)
            length = self.data[:self.data.find("=")]
            self._read(1 + len(length))
            self.server = self._read(int(length))
            self._read(1)
            length = self.data[:self.data.find("=")]
            self._read(1 + len(length))
            self.mode = int(self._read(int(length)))
        else:
            self.rank = 0
            self.server = "Unknown"
            self.mode = 0
        length = self.data.find("=")
        if length != -1:
            self._read(1)
            length = self.data[:length - 1]
            self._read(1 + len(length))
            self.ban_speed = self._read(int(length))
        else:
            self.ban_speed = -1
        if self.data == "\n" or self.data == " \n":
            self.comm = ""
        else:
            self.comm = self.data[1:-1]
