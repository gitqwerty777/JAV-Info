import requests
import time, os
import re
import json
import pprint
import colorama
from pathlib import Path
from bs4 import BeautifulSoup

def getText(element):
    return element.getText()

def CreatePrettyPrinter():
    return pprint.PrettyPrinter(indent=0, width=60)

def lenInBytes(string):
    return len(string.encode("utf-8"))

class JAVInfoGetter:
    def __init__(self, setting):
        self.setting = setting
        self.dbpath = Path("db-" + self.setting.language + ".json")

        if not self.dbpath.exists(): # XXX: move db out of infogetter
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
        #print(self.dbdata)

    def Get(self, bangou, fileName):
        if bangou in self.dbdata:
            print(f"find [{bangou}] info in db")
            return self.dbdata[bangou], True

        response = requests.get("http://www.javlibrary.com/" + self.setting.language + "/vl_searchbyid.php?keyword=" + bangou)
        self.soup = BeautifulSoup(response.text, "html.parser")
        info = dict()

        #print(soup.prettify())
        info["bangou"] = bangou # TODO: normalize bangou, and change filenames' key
        info["title"] = self.ParseTitle(bangou)
        info["tags"] = self.ParseTag()
        info["director"] = self.ParseDirector()
        info["maker"] = self.ParseMaker()
        info["actors"] = self.ParseActor()
        info["album"] = self.ParseAlbum()
        info["length"] = self.ParseLength()
        info["date"] = self.ParseDate()
        info["thumbs"] = self.ParseThumbs() # TODO: save thumbs
        info["rate"] = self.ParseRate()

        if not info["title"]:
            print(f"{colorama.Back.RED}Parse {bangou} failed. File name {fileName}{colorama.Back.RESET}")
            return info, False

        print(json.dumps(info, indent=4, ensure_ascii=False))
        self.AddData(info)
        time.sleep(setting.getInfoInterval) # XXX: use timer instead sleep

        return info, True

    def ParseTitle(self, bangou):
        try:
            title = self.soup.select_one("#video_title").select_one("a").getText()
            title = title.replace(bangou, "")
            return title.strip(" ")
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
            imgs = self.soup.select_one(".previewthumbs").select("img")
            imgs = imgs[1:] # remove "../img/player.gif"
            imgs = [img["src"] for img in imgs]
            return imgs
        except:
            return ""

    def ParseRate(self):
        try:
            text = self.soup.select_one("#video_review").select_one(".score").getText()
            rate = re.search("(\d+.*\d)", text).group(0)
            return str(float(rate))
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
            self.maxFileLength = settingJson["maxFileLength"]
        except:
            print("read config file failed")
            exit(1)

class Executor:
    def __init__(self, setting):
        self.setting = setting

    def HandleFile(self, info, path):
        print(f"============== handle bangou {colorama.Back.YELLOW}{info['bangou']}{colorama.Back.RESET} ==================")
        self.Rename(info, path)
        if self.setting.saveAlbum:
           self.SaveAlbum(info, path)
        # TODO: fill video description in video file

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

        if lenInBytes(newFileName) + lenInBytes(path.suffix) > self.setting.maxFileLength:
            print(f"File name too long: {newFileName}")
            maxFileLength = self.setting.maxFileLength - lenInBytes(path.suffix)
            while lenInBytes(newFileName) > maxFileLength:
                newFileName = newFileName[0:-1]
            print(f"After truncate file name: {newFileName}")

        newName = newFileName + path.suffix

        if path.name == newName:
            print(f"File {colorama.Back.BLUE}[{str(path)}]{colorama.Back.RESET} no need to rename")
            return

        self.DoRename(path, newName)
        
    def DoRename(self, path, newName):
        newPath = path.parents[0] / newName
        if newPath.exists(): # TODO: test multiple files with the same bangou
            number = 1
            newPath = path.parents[0] / (newName + str(number))
            while newPath.exists():
                number += 1
                newPath = path.parents[0] / (newName + str(number))

        print(f"Rename {colorama.Back.BLUE}{str(path)}{colorama.Back.RESET}\n"+
              f"To     {colorama.Back.GREEN}{str(newPath)}{colorama.Back.RESET}")

        # TODO: option to ask before rename

        if self.setting.dryRun:
            return

        try:
            path.rename(newPath)
        except Exception as e:
            print(f"{colorama.Back.RED}Rename [{str(path)}] to [{str(newPath)}] failed{colorama.Back.RESET}")
            print(e)
            # TODO: file name too long

    def SaveAlbum(self, info, path):
        albumFileName = info["bangou"] + ".jpg"
        albumPath = Path(path.parents[0] / albumFileName)

        if albumPath.exists():
            print(f"Album {colorama.Back.BLUE}{str(albumPath)}{colorama.Back.RESET} already exists")
            return
        self.DoSaveAlbum(info, albumPath)

    def DoSaveAlbum(self, info, albumPath):
        print(f"Save album image {colorama.Back.GREEN}{str(albumPath)}{colorama.Back.RESET}")
        
        if self.setting.dryRun:
            return

        with open(albumPath, 'wb') as albumFile:
            fileURL = "http:" + info["album"]
            fileObject = requests.get(fileURL)
            albumFile.write(fileObject.content)

if __name__ == "__main__": # XXX: move to main.py
    colorama.init()
    setting = Setting()
    fileNameParser = FileNameParser(setting.fileExts)
    infoGetter = JAVInfoGetter(setting)
    executor = Executor(setting)

    if setting.dryRun:
        print(f"{colorama.Back.RED}This is dry run version.\nSet dryRun to false in config.json to execute{colorama.Back.RESET}")

    fileNames, bangous = fileNameParser.Parse(setting.fileDir)
    # TODO: option: new folder for all video file, for the same actor, for the same tag # create link
    for bangou in bangous:
        info, success = infoGetter.Get(bangou, str(fileNames[bangou]))
        if not success:
            continue
        executor.HandleFile(info, fileNames[bangou])

    infoGetter.SaveData()
