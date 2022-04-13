import json
from pathlib import Path
import utils


class DataManager:
    def __init__(self, setting):
        self.setting = setting
        self.dbpath = Path("db-" + self.setting.language + ".json")

        if not self.dbpath.exists():
            self.dbpath.touch()
            self.dbdata = {}

        with open(self.dbpath) as self.dbfile:
            dbtext = self.dbfile.read()
            if not dbtext:
                self.dbdata = {}
            else:
                self.dbdata = json.loads(dbtext)

    def AddRecord(self, info):
        self.dbdata.update({info["bangou"]: info})

    def Save(self):
        print(utils.whiteBackStr("save db"))
        with open(self.dbpath, "w") as self.dbfile:
            json.dump(self.dbdata, self.dbfile)
            self.dbfile.close()

    def Search(self, bangou):
        if bangou in self.dbdata:
            return self.dbdata[bangou]
        else:
            return None
