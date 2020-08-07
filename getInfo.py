import requests
import time
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
    def __init__(self):
        pass

    def Parse(self, filePath):
        fileNames = ["EBOD-704", "MUM-130", "STARS-234"]
        # TODO:
        return fileNames

if __name__ == "__main__":
    
    getInterval = 5

    fileNameParser = FileNameParser()
    bangous = fileNameParser.Parse(filePath)

    infoGetter = JAVInfoGetter()
    for bangou in bangous:
        info = infoGetter.Get(bangou)
        print(info)
        exit(0)
        time.sleep(getInterval)
