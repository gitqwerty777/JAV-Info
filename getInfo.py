import requests
import time
import glob, os
import re
from pathlib import Path
from bs4 import BeautifulSoup

def getText(element):
    return element.getText()

class JAVInfoGetter:
    def __init__(self):
        # TODO: save this entry into info.json in the same directory
        pass

    def Get(self, bangou):
        response = requests.get('http://www.javlibrary.com/tw/vl_searchbyid.php?keyword=' + bangou)
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

        # TODO: save info into json

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

class FileNameParser:
    def __init__(self, fileExts):
        self.fileExts = fileExts

    def Parse(self, fileDir):
        os.chdir(fileDir)

        videoFileList = []
        for fileExt in self.fileExts:
            videoFileList.extend(glob.glob(fileExt))

        fileNames = dict()
        bangous = []
        for fileName in videoFileList:
            bangou = self.ParseBangou(fileName)
            if not bangou:
                continue
            
            bangous.append(bangou)
            fileNames[bangou] = fileName

        print("fileNames : " + str(fileNames))
        print("bangous : " + str(bangous))
        return fileNames, bangous

    def ParseBangou(self, fileName):
        try:
            bangou = re.search("\w+\-\d+", fileName).group(0)
        except:
            try:
                bangou = re.search("\w+\d+", fileName).group(0)
            except:
                return ""
        return bangou

if __name__ == "__main__":
    # TODO: do real test
    # TODO: move to config
    fileExts = ["*.mp4", "*.avi", "*.mkv", "*.avi", "*.flv", "*.rmvb", "*.rm", "*.m4v", "*.asf", "*.wmv", "*.webm"]
    fileDir = "original/"
    getInterval = 5

    fileNameParser = FileNameParser(fileExts)
    fileNames, bangous = fileNameParser.Parse(fileDir)

    infoGetter = JAVInfoGetter()

    # TODO: option: new folder for all xxx
    # TODO: option: new folder for the same actor
    # TODO: option: new folder for the same tag # create link
    for bangou in bangous:
        info = infoGetter.Get(bangou)
        print(info)
        # TODO: specify rename file name
        oldName = fileNames[bangou]
        newName = info["title"] + Path(fileNames[bangou]).suffix
        os.rename(oldName, newName)
        print(f"Rename [{oldName}] to [{newName}]")

        time.sleep(getInterval)
