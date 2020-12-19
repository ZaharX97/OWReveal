import datetime as dt


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
                                  self.dtt.strftime("%d-%b-%Y %H:%M:%S"))
        ret += "{}={} ".format(len(self.name), self.name)
        ret += "{}={} {}={} ".format(len(self.kad), self.kad, len(self.map), self.map)
        ret += "{}={} {}={} ".format(len(str(self.rank)), self.rank, len(self.server), self.server)
        ret += "{}={}".format(len(str(self.mode)), self.mode)
        if len(self.comm):
            ret += " {}\n".format(self.comm)
        else:
            ret += "\n"
        return ret

    def __init__(self, data=None):
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

        if data:
            self.data = data
            # length = self.data[:self.data.find("=")]
            # self._read(2 + len(length))
            self._get_player()
            del self.data

    def _get_player(self):
        self.link = "https://steamcommunity.com/profiles/" + self._read(17, string=False)
        self._read(1)
        self.banned = self._read(1)
        self._read(1)
        self.dtt = dt.datetime.strptime(self._read(20), "%d-%b-%Y %H:%M:%S")
        self.date = self.dtt.strftime("%d-%b-%Y %H:%M:%S")[:11]
        self._read(1)
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
        if self.data == "\n" or self.data == " \n":
            self.comm = ""
        else:
            self.comm = self.data[1:-1]
