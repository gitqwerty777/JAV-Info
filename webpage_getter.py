import time
from pathlib import Path

from http import cookiejar
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class WebPageGetter(object):
    def __init__(self, cookieFilePath, waitTime):
        """
        Put correct version of ChromeDriver.exe at path from https://chromedriver.chromium.org/downloads
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--ignore-certificate-errors-spki-list")
        self.browser = webdriver.Chrome(options=options)
        self.cookies = cookiejar.MozillaCookieJar(cookieFilePath)
        self.cookies.load()
        self.waitTime = waitTime

    def addCookies(self):
        # https://stackoverflow.com/questions/41906704/selenium-add-cookies-from-cookiejar
        for cookie in self.cookies:
            cookie_dict = {'domain': cookie.domain, 'name': cookie.name,
                           'value': cookie.value, 'secure': cookie.secure}
            if cookie.expires:
                cookie_dict['expiry'] = cookie.expires
            if cookie.path_specified:
                cookie_dict['path'] = cookie.path
            self.browser.add_cookie(cookie_dict)

    def getPage(self, url):
        raise NotImplementedError

    def simpleGetPage(self, url):
        print(f"Get page {url}")
        self.browser.get(self.baseUrl)
        self.addCookies()
        self.browser.get(url)
        time.sleep(self.waitTime)

    def __del__(self):
        self.browser.close()


class WebPageGetter_JavLibrary(WebPageGetter):
    def __init__(self, cookieFilePath, waitTime):
        super().__init__(cookieFilePath, waitTime)
        self.baseUrl = "https://www.javlibrary.com/"

    def getPage(self, url):
        self.simpleGetPage(url)
        button = self.browser.find_elements(
            by=By.CLASS_NAME, value="btnAdultAgree")
        if button:
            button[0].click()
            time.sleep(self.waitTime)

        return self.browser.page_source


class WebPageGetter_JavDB(WebPageGetter):
    def __init__(self, cookieFilePath, waitTime):
        super().__init__(cookieFilePath, waitTime)
        self.baseUrl = "https://javdb.com"

    def getPage(self, url):
        self.simpleGetPage(url)
        try:
            WebDriverWait(self.browser, self.waitTime).until(
                lambda x: x.find_element(By.ID, "videos"))
        except Exception as e:
            return "", ""

        videolink = "http://javdb.com/" + \
            self.browser.find_element(
                by=By.XPATH, value='//*[@id="videos"]/div/div[1]/a').get_attribute('pathname') + "?locale=en"
        simpletitle = self.browser.find_element(
            by=By.XPATH, value='//*[@id="videos"]/div/div[1]/a/div[3]').text
        #print(f"videolink {videolink}")
        #print(f"simpletitle {simpletitle}")

        self.simpleGetPage(videolink)

        # with open(url.split("=")[-1]+".html", "w", encoding="utf-8") as f:
        # f.write(self.browser.page_source)

        return self.browser.page_source, simpletitle


