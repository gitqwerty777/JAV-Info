import requests
import time
import glob, os
import re
import json
import pprint
from pathlib import Path
from bs4 import BeautifulSoup
import colorama # TODO: from import or import

def getText(element):
    return element.getText()

def CreatePrettyPrinter():
    return pprint.PrettyPrinter(indent=0, width=60)

class JAVInfoGetter:
    def __init__(self, setting):
        self.setting = setting
        self.dbpath = Path("db.json") # TODO: db should seperate by language

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
            return self.dbdata[bangou], True

        response = requests.get("http://www.javlibrary.com/" + self.setting.language + "/vl_searchbyid.php?keyword=" + bangou)
        self.soup = BeautifulSoup(response.text, "html.parser")
        info = dict()

        #print(soup.prettify())
        info["bangou"] = bangou
        info["title"] = self.ParseTitle() # TODO: remove bangou info in title # title may include actor name
        info["tags"] = self.ParseTag()
        info["director"] = self.ParseDirector()
        info["maker"] = self.ParseMaker()
        info["actors"] = self.ParseActor()
        info["album"] = self.ParseAlbum()
        info["length"] = self.ParseLength()
        info["date"] = self.ParseDate()
        info["thumbs"] = self.ParseThumbs()
        info["rate"] = self.ParseRate()

        if not info["title"]:
            print(f"Parse {bangou} failed")
            return info, False

        print(json.dumps(info, indent=4, ensure_ascii=False))
        self.AddData(info)
        time.sleep(setting.getInfoInterval)

        return info, True

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

    def ParseThumbs(self):
        try:
            return self.soup.select(".previewthumbs") #TODO:
        except:
            return ""

    def ParseRate(self):
        try:
            return self.soup.select_one("#video_review") #TODO:
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
            return bangou
        except:
            return ""

class Setting:
    def __init__(self):
        with open("config.json") as configFile:
            settingJson = json.load(configFile)

        try:
            self.fileExts = settingJson["fileExts"]
            self.fileDir = settingJson["fileDir"]
            self.getInfoInterval = settingJson["getInfoInterval"]
            self.fileNameFormat = settingJson["fileNameFormat"]
            self.language = settingJson["language"]
            self.saveAlbum = settingJson["saveAlbum"]
            self.dryRun = settingJson["dryRun"]
        except:
            print("read config file failed")
            exit(1)

class Executor:
    def __init__(self, setting):
        self.setting = setting

    def HandleFile(self, info, path):
        print(f"============== handle bangou {info['bangou']} ==================")
        self.Rename(info, path)
        if self.setting.saveAlbum:
           self.SaveAlbum(info, path)

    def Rename(self, info, path):
        newFileName = self.setting.fileNameFormat
        for key in info:
            infokey = "{" + key + "}"
            infovalue = info[key]
            if type(infovalue) is list:
                infovalue = ""
                for element in info[key]:
                    infovalue = infovalue + "[" + element + "]"
            newFileName = newFileName.replace(infokey, infovalue)

        newName = newFileName + path.suffix
        if path.name == newName:
            print(f"File [{str(path)}] no need to rename")
            return

        self.DoRename(path, newName)
        
    def DoRename(self, path, newName):
        newPath = path.parents[0] / newName
        print(f"Rename {colorama.Back.BLUE}[{str(path)}]{colorama.Back.RESET}\n"+
              f"To     {colorama.Back.GREEN}[{str(newPath)}]{colorama.Back.RESET}")

        if self.setting.dryRun:
            return

        try:
            path.rename(newPath)
        except: #TODO: print error reason
            print(f"{colorama.Back.RED}Rename [{str(path)}] to [{str(newPath)}] failed{colorama.Back.RESET}")

    def SaveAlbum(self, info, path):
        albumFileName = info["bangou"] + ".jpg"
        albumPath = Path(path.parents[0] / albumFileName)

        if albumPath.exists():
            print(f"Album {colorama.Back.GREEN}[{str(albumPath)}]{colorama.Back.RESET} already exists, do nothing")
            return
        self.DoSaveAlbum(info, albumPath)

    def DoSaveAlbum(self, info, albumPath):
        print(f"Save album as [{str(albumPath)}]")
        
        if self.setting.dryRun:
            return

        with open(albumPath, 'wb') as albumFile:
            fileURL = "http:" + info["album"]
            fileObject = requests.get(fileURL)
            albumFile.write(fileObject.content)

if __name__ == "__main__": # TODO: move to main.py
    colorama.init()
    setting = Setting()
    fileNameParser = FileNameParser(setting.fileExts)
    infoGetter = JAVInfoGetter(setting)
    executor = Executor(setting)

    fileNames, bangous = fileNameParser.Parse(setting.fileDir)
    # TODO: option: new folder for all video file, for the same actor, for the same tag # create link
    # TODO: deal with multiple part files of the same bangou, should ask user to overwrite or rename
    for bangou in bangous:
        info, success = infoGetter.Get(bangou)
        if not success:
            continue
        executor.HandleFile(info, fileNames[bangou])

    infoGetter.SaveData()
