import json
from pathlib import Path


class DataManager:
    def __init__(self, setting):
        self.setting = setting
        self.dbpath = Path("db-" + self.setting.language + ".json")

        if not self.dbpath.exists():
            self.dbpath.touch()
            self.dbdata = {}
        else:
            with open(self.dbpath) as self.dbfile:
                dbtext = self.dbfile.read()
                if not dbtext:
                    self.dbdata = {}
                else:
                    self.dbdata = json.loads(dbtext)

        print("read db")
        # print(self.dbdata)

    def Add(self, info):
        self.dbdata.update({info["bangou"]: info})

    def Save(self):
        print("save db")
        with open(self.dbpath, "w") as self.dbfile:
            json.dump(self.dbdata, self.dbfile)
            self.dbfile.close()

    def Search(self, bangou):
        if bangou in self.dbdata:
            return self.dbdata[bangou]
        else:
            return None
