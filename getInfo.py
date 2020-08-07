import requests
import time
import glob, os
import re
import json
import pprint
from pathlib import Path
from bs4 import BeautifulSoup

def getText(element):
    return element.getText()

def CreatePrettyPrinter():
    return pprint.PrettyPrinter(indent=0, width=60)

class JAVInfoGetter:
    def __init__(self):
        self.dbpath = Path("db.json")

        if not self.dbpath.exists(): # XXX: move db out of infogetter
            self.dbpath.touch()
            self.dbdata = {}
        else:
            with open(self.dbpath) as self.dbfile:
                self.dbdata = json.load(self.dbfile)

        print("read db")
        #print(self.dbdata)

    def Get(self, bangou):
        if bangou in self.dbdata:
            print(f"find [{bangou}] info in db")
            return self.dbdata[bangou]

        response = requests.get('http://www.javlibrary.com/tw/vl_searchbyid.php?keyword=' + bangou) # TODO: different lang
        self.soup = BeautifulSoup(response.text, "html.parser")
        info = dict()

        #print(soup.prettify())
        info["bangou"] = bangou
        info["title"] = self.ParseTitle()
        info["tags"] = self.ParseTag()
        info["director"] = self.ParseDirector()
        info["maker"] = self.ParseMaker()
        info["actors"] = self.ParseActor()
        info["album"] = self.ParseAlbum()
        info["length"] = self.ParseLength()
        info["date"] = self.ParseDate()

        print(json.dumps(info, indent=4, ensure_ascii=False))
        self.AddData(info)
        time.sleep(setting.getInfoInterval)

        return info

    def ParseTitle(self):
        try:
            return self.soup.select_one("#video_title").select_one("a").getText()
        except:
            return ""

    def ParseTag(self):
        try:
            return list(map(getText, self.soup.select_one("#video_genres").select("a")))
        except:
            return ""

    def ParseMaker(self):
        try:
            return self.soup.select_one("#video_maker").select_one("a").getText()
        except:
            return ""

    def ParseDirector(self):
        try:
            return self.soup.select_one("#video_director").select_one("a").getText()
        except:
            return ""

    def ParseActor(self):
        try:
            return list(map(getText, self.soup.select_one("#video_cast").select("a")))
        except:
            return ""

    def ParseAlbum(self):
        try:
            return self.soup.select_one("#video_jacket").select_one("img").get("src")
        except:
            return ""

    def ParseLength(self):
        try:
            return self.soup.select_one("#video_length").select_one(".text").getText()
        except:
            return ""

    def ParseDate(self):
        try:
            return self.soup.select_one("#video_date").select_one(".text").getText()
        except:
            return ""

    def AddData(self, info):
        self.dbdata.update({info["bangou"]: info})

    def SaveData(self):
        print("save db")
        with open(self.dbpath, "w") as self.dbfile:
            json.dump(self.dbdata, self.dbfile)
            self.dbfile.close()

class FileNameParser:
    def __init__(self, fileExts):
        self.fileExts = fileExts

    def Parse(self, fileDir):
        videoFileList = []
        path = Path(fileDir)
        for fileExt in self.fileExts:
            videoFileList.extend(path.rglob(fileExt))

        fileNames = dict()
        bangous = []
        for fileName in videoFileList:
            bangou = self.ParseBangou(fileName.name)
            if not bangou:
                continue
            
            bangous.append(bangou)
            fileNames[bangou] = fileName

        pp = CreatePrettyPrinter()
        print("find video files")
        pp.pprint(fileNames)

        return fileNames, bangous

    def ParseBangou(self, fileName):
        try:
            bangou = re.search("\w+\-*\d+", fileName).group(0)
        except:
            return ""
        return bangou

class Setting:
    def __init__(self):
        with open("config.json") as configFile:
            settingText = configFile.read()
            settingJson = json.loads(settingText)

            try:
                self.fileExts = settingJson["fileExts"]
                self.fileDir = settingJson["fileDir"]
                self.getInfoInterval = int(settingJson["getInfoInterval"])
                self.fileNameFormat = settingJson["fileNameFormat"]
            except:
                print("read config file failed")
                exit(1)

    def Rename(self, info, path):
        newFileNameFormat = self.fileNameFormat
        for key in info:
            infokey = "{" + key + "}"
            infovalue = info[key]
            if type(infovalue) is list:
                infovalue = ""
                for element in info[key]:
                    infovalue = infovalue + "["+element+"]"
            newFileNameFormat = newFileNameFormat.replace(infokey, infovalue)

        oldName = str(path)
        newName = newFileNameFormat + path.suffix
        if path.name == newName:
            print(f"File [{oldName}] no need to rename")
            return
        path = path.rename(path.parents[0] / newName)
        newName = str(path)
        print(f"Rename [{oldName}] to [{newName}]")

if __name__ == "__main__":
    # TODO: do real file test
    setting = Setting()
    fileNameParser = FileNameParser(setting.fileExts)
    fileNames, bangous = fileNameParser.Parse(setting.fileDir)

    infoGetter = JAVInfoGetter()

    # TODO: option: new folder for all video file, for the same actor, for the same tag # create link
    # TODO: save album
    for bangou in bangous:
        info = infoGetter.Get(bangou)
        setting.Rename(info, fileNames[bangou])

    infoGetter.SaveData()
