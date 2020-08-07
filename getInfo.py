import requests
import time
import glob, os
import re
from bs4 import BeautifulSoup

def getText(element):
    return element.getText()

class JAVInfoGetter:
    def __init__(self):
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


class FileNameParser:
    def __init__(self, fileExts):
        self.fileExts = fileExts

    def Parse(self, fileDir):
        os.chdir(fileDir)
        fileList = []
        for fileExt in self.fileExts:
            fileList.extend(glob.glob(fileExt, recursive = True)) # TODO: test recursive

        fileNames = []
        bangous = []
        for fileName in fileList:
            fileNames.append(os.path.join(fileDir, fileName))
            bangou = re.search("\w+\-\d+", fileName)
            bangous.append(bangou.group(0))

        print("fileNames" + str(fileNames))
        print("bangous" + str(bangous))
        return fileNames, bangous

if __name__ == "__main__":
    fileExts = ["*.mp4", "*.avi", "*.mkv", "*.avi", "*.flv", "*.rmvb", "*.rm"] # TODO: extensions
    filePath = "."
    getInterval = 5

    fileNameParser = FileNameParser(fileExts)
    fileNames, bangous = fileNameParser.Parse(filePath)

    infoGetter = JAVInfoGetter()
    for bangou in bangous:
        info = infoGetter.Get(bangou)
        print(info)
        # save info.json in the same directory

        # rename file
        
        exit(0)
        time.sleep(getInterval)
