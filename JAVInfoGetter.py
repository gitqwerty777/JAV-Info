import re
import json
import requests
from bs4 import BeautifulSoup
from webpage_getter import WebPageGetter_JavLibrary, WebPageGetter_JavDB

# TODO: find chinese title source website


def getText(element):
    return element.getText()


class JAVInfoGetter:
    def __init__(self, setting, dataManager):
        self.setting = setting
        self.dataManager = dataManager

    def GetInfo(self, bangou, fileName):
        # TODO: move search database out of there
        print(f"Try to get info from {self.__class__.__name__}")
        info = self.dataManager.Search(bangou)
        if info:
            if "title" in info and info["title"]:
                print(f"Find complete info of {bangou} in db")
                return info, True
            elif not self.setting.retryFailedDB:  # directly use incomplete info, no retry
                print(f"Find incomplete info of {bangou} in db")
                return info, False

        info = dict()
        link = self.GetWebContent(bangou)

        if not link:
            print("Get Webpage Failed")
            info["bangou"] = bangou
            return info, False

        # print(self.soup.prettify())
        info["bangou"] = self.ParseBangou()
        info["title"] = self.ParseTitle(info["bangou"])
        info["tags"] = self.ParseTag()
        info["director"] = self.ParseDirector()
        info["maker"] = self.ParseMaker()
        info["actors"] = self.ParseActor()
        info["album"] = self.ParseAlbum()
        info["duration"] = self.ParseDuration()
        info["date"] = self.ParseDate()
        info["thumbs"] = self.ParseThumbs()
        info["rating"] = self.ParseRating()
        info["link"] = link

        self.dataManager.AddRecord(info)

        if not info["title"]:
            info["bangou"] = bangou
            return info, False
        else:
            info["title"] = info["title"].replace(
                info["bangou"], "").strip(" ")

        print(json.dumps(info, indent=4, ensure_ascii=False))

        # BUG: Weird, there are two bangous, maybe it's a bug
        if bangou != info["bangou"]:
            info2 = info.copy()
            info2["bangou"] = bangou
            print(f"two bangous: {bangou} {info['bangou']}")

        return info, True


class JAVInfoGetter_javlibrary(JAVInfoGetter):
    def __init__(self, setting, dataManager):
        super().__init__(setting, dataManager)
        self.webPageGetter = WebPageGetter_JavLibrary(
            cookieFilePath=self.setting.javlibraryCookieFilePath, waitTime=self.setting.getInfoInterval)  # TODO: move cookie and waittime to config

    def GetWebContent(self, bangou):
        link = "http://www.javlibrary.com/" + self.setting.language + \
            "/vl_searchbyid.php?keyword=" + bangou

        source = self.webPageGetter.getPage(link)
        self.soup = BeautifulSoup(source, "html.parser")

        # has multiple search result
        if self.soup.select_one(".videothumblist"):
            try:
                link = "http://www.javlibrary.com/" + self.setting.language + "/" + \
                    self.soup.select_one(".videothumblist").select_one(
                        ".video").select_one("a")["href"]
                response = requests.get(link)
                self.soup = BeautifulSoup(response.text, "html.parser")
            except:
                link = ""

        return link

    def ParseBangou(self):
        try:
            return self.soup.select_one("#video_id").select_one(".text").getText()
        except:
            return ""

    def ParseTitle(self, bangou):
        try:
            return self.soup.select_one(
                "#video_title").select_one("a").getText()
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
            return "http:" + self.soup.select_one("#video_jacket").select_one("img").get("src")
        except:
            return ""

    def ParseDuration(self):
        try:
            return self.soup.select_one("#video_length").select_one(".text").getText()
        except:
            return ""

    def ParseDate(self):
        try:
            return self.soup.select_one("#video_date").select_one(".text").getText()
        except:
            return ""

    def ParseThumbs(self):  # FIXME: sometimes no thumb
        try:
            imgs = self.soup.select_one(".previewthumbs").select("img")
            imgs = imgs[1:]  # remove "../img/player.gif"
            imgs = [img["src"] for img in imgs]
            return imgs
        except:
            return ""

    def ParseRating(self):
        try:
            text = self.soup.select_one(
                "#video_review").select_one(".score").getText()
            rate = re.search("(\d+.*\d)", text).group(0)
            return str(float(rate))
        except:
            return ""


# TODO: now only support english version
class JAVInfoGetter_javdb(JAVInfoGetter):
    def __init__(self, setting, dataManager):
        super().__init__(setting, dataManager)
        self.webPageGetter = WebPageGetter_JavDB(
            cookieFilePath=self.setting.javdbCookieFilePath, waitTime=self.setting.getInfoInterval)

    def GetWebContent(self, bangou):
        link = "http://javdb.com/search?q=" + bangou
        print(link)
        source, simpletitle = self.webPageGetter.getPage(link)
        if not source and not simpletitle:
            return ""

        self.soup = BeautifulSoup(source, "html.parser")
        try:
            infos = self.soup.select_one(
                ".movie-panel-info").select(".panel-block")
        except:
            # not found, use simple title as info
            print("Detail page not found, use simple title")
            self.infoDict = dict()
            self.infoDict["title"] = simpletitle
            self.infoDict["ID"] = bangou
            return link

        self.infoDict = dict()
        for info in infos:
            key = info.select_one("strong")
            if not key:
                continue
            key = key.getText().strip(":")
            value = info.select_one("span").getText()
            self.infoDict[key] = value
        return link

    def ParseBangou(self):
        try:
            return self.infoDict["ID"]
        except:
            return ""

    def ParseTitle(self, bangou):
        try:
            return self.infoDict["title"]
        except:
            pass
        try:
            return self.soup.select_one(".title").select_one("strong").getText()
        except:
            return ""

    def ParseTag(self):
        try:
            tags = self.infoDict["Tags"].split(",")
            tags = [tag.strip(u"\xa0").strip(" ") for tag in tags]
            return tags
        except:
            return ""

    def ParseMaker(self):
        try:
            return self.infoDict["Maker"]
        except:
            return ""

    def ParseDirector(self):
        try:
            return self.infoDict["Director"]
        except:
            return ""

    def ParseActor(self):
        try:
            return self.infoDict["Actor(s)"]
        except:
            return ""

    def ParseAlbum(self):
        try:
            return self.soup.select_one(".video-cover")["src"]
        except:
            return ""

    def ParseDuration(self):
        try:
            duration = self.infoDict["Duration"]
            duration = re.search("\d+", duration).group(0)
            return duration
        except:
            return ""

    def ParseDate(self):
        try:
            return self.infoDict["Date"]
        except:
            return ""

    def ParseThumbs(self):
        try:
            imgs = self.soup.select_one(".preview-images").select("a")
            imgs = [img["href"] for img in imgs]
            return imgs
        except:
            return ""

    def ParseRating(self):
        try:
            rating = self.infoDict["Rating"]
            rating = re.search("\d+.\d+", rating).group(0)
            return rating
        except:
            return ""
