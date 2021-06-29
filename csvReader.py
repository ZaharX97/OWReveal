import csv


class myCSV:
    def get_next(self):
        try:
            return self.reader.__next__()
        except Exception:
            return None

    def reset(self):
        self.file.seek(0, 0)
        self.get_next()

    def __init__(self, file):
        self.reader = csv.reader(file)
        self.file = file
