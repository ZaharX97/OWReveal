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
        ret += "{}={} {}={} {}\n".format(len(self.kad), self.kad, len(self.map), self.map, self.comm)
        return ret

    def __init__(self, data=None):
        if data is None:
            self.name = None
            self.link = None
            self.datetime = None
            self.date = None
            self.comm = None
        else:
            self.data = data
            # length = self.data[:self.data.find("=")]
            # self._read(2 + len(length))
            self.link = "https://steamcommunity.com/profiles/" + self._read(17, string=False)
            self._read(1)
            self.banned = self._read(1)
            self._read(1)
            self.dtt = dt.datetime.strptime(self._read(20, string=False), "%d-%b-%Y %H:%M:%S")
            self.date = self.dtt.strftime("%d-%b-%Y %H:%M:%S")[:11]
            self._read(1)
            length = self.data[:self.data.find("=")]
            self._read(1 + len(length))
            self.name = self._read(int(length), string=False)
            self._read(1)
            length = self.data[:self.data.find("=")]
            self._read(1 + len(length))
            self.kad = self._read(int(length), string=False)
            self._read(1)
            length = self.data[:self.data.find("=")]
            self._read(1 + len(length))
            self.map = self._read(int(length), string=False)
            if self.data == "\n":
                self.comm = ""
            else:
                self.comm = self.data[1:-1]
            del self.data
            del length
