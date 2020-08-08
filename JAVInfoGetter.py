import time
import json
import requests
import colorama
from bs4 import BeautifulSoup


def getText(element):
    return element.getText()


class JAVInfoGetter:
    def __init__(self, setting, dataManager):
        self.setting = setting
        self.dataManager = dataManager

    def GetWebContent(self, bangou):
        link = "http://www.javlibrary.com/" + self.setting.language + \
            "/vl_searchbyid.php?keyword=" + bangou  # TODO: add another source to get info
        response = requests.get(link)
        self.soup = BeautifulSoup(response.text, "html.parser")

        if self.soup.select_one(".videothumblist"):  # has multiple search result
            try:
                link = "http://www.javlibrary.com/" + self.setting.language + "/" + \
                    self.soup.select_one(".videothumblist").select_one(
                        ".video").select_one("a")["href"]
                print(link)
                response = requests.get(link)
                self.soup = BeautifulSoup(response.text, "html.parser")
            except:
                pass

        return link

    def GetInfo(self, bangou, fileName):
        info = self.dataManager.Search(bangou)
        if info:
            if info["title"]:
                print(f"Find success info of {bangou} in db")
                return info, True
            else:
                print(f"Find failed info of {bangou} in db")
                return info, False

        info = dict()
        link = self.GetWebContent(bangou)

        # print(self.soup.prettify())
        # TODO: make sure different bangou has one copy. e.g, mum-130, mum130
        info["bangou"] = self.ParseBangou()
        info["title"] = self.ParseTitle(info["bangou"])
        info["tags"] = self.ParseTag()
        info["director"] = self.ParseDirector()
        info["maker"] = self.ParseMaker()
        info["actors"] = self.ParseActor()
        info["album"] = self.ParseAlbum()
        info["length"] = self.ParseLength()
        info["date"] = self.ParseDate()
        info["thumbs"] = self.ParseThumbs()
        info["rate"] = self.ParseRate()
        info["link"] = link

        if not info["title"]:
            print(
                f"{colorama.Back.RED}Get Info from bangou {bangou} failed. File name {fileName}{colorama.Back.RESET}")
            info["bangou"] = bangou
            self.dataManager.Add(info)
            return info, False

        self.dataManager.Add(info)
        print(json.dumps(info, indent=4, ensure_ascii=False))

        if bangou != info["bangou"]:
            info2 = info.copy()
            info2["bangou"] = bangou
            self.dataManager.Add(info2)
        # XXX: use timer instead sleep
        time.sleep(self.setting.getInfoInterval)

        return info, True

    def ParseBangou(self):
        try:
            return self.soup.select_one("#video_id").select_one(".text").getText()
        except:
            return ""

    def ParseTitle(self, bangou):
        try:
            title = self.soup.select_one(
                "#video_title").select_one("a").getText()
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
            imgs = imgs[1:]  # remove "../img/player.gif"
            imgs = [img["src"] for img in imgs]
            return imgs
        except:
            return ""

    def ParseRate(self):
        try:
            text = self.soup.select_one(
                "#video_review").select_one(".score").getText()
            rate = re.search("(\d+.*\d)", text).group(0)
            return str(float(rate))
        except:
            return ""
