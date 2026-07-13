import time
import shutil
from pathlib import Path

from http import cookiejar
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from seleniumbase import Driver


def resolveChromeBinary():
    """
    Selenium picks chrome.exe from PATH. If that is a Scoop shim, it forks the
    real Chrome and exits, which ChromeDriver misreports as "Chrome instance
    exited". Resolve the real binary from the shim's sidecar .shim file.
    Returns None when Chrome is not a Scoop shim (leave Selenium to auto-detect).
    """
    chrome = shutil.which("chrome")
    if not chrome:
        return None
    shim = Path(chrome).with_suffix(".shim")
    if not shim.exists():
        return None
    for line in shim.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("path"):
            return line.split("=", 1)[1].strip().strip('"')
    return None


class WebPageGetter(object):
    # Seconds to wait for a page element to appear. Kept separate from the
    # rate-limit interval (waitTime) so a small polite delay does not become a
    # too-short page-load timeout.
    PAGE_WAIT_TIMEOUT = 15

    def __init__(self, cookieFilePath, waitTime):
        """
        Put correct version of ChromeDriver.exe at path from https://chromedriver.chromium.org/downloads
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--ignore-certificate-errors-spki-list")
        chromeBinary = resolveChromeBinary()
        if chromeBinary:
            options.binary_location = chromeBinary
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
        browser = getattr(self, "browser", None)
        if browser:
            try:
                browser.quit()
            except Exception:
                pass


class WebPageGetter_JavLibrary(WebPageGetter):
    # javlibrary sits behind Cloudflare's JS challenge, which blocks plain
    # Selenium. SeleniumBase UC mode (undetected + disconnect/reconnect) slips
    # past it. Seconds to stay disconnected during each open:
    RECONNECT_TIME = 8

    def __init__(self, cookieFilePath, waitTime):
        self.baseUrl = "https://www.javlibrary.com/"
        chromeBinary = resolveChromeBinary()
        driverArgs = {"uc": True, "headless": True}
        if chromeBinary:
            driverArgs["binary_location"] = chromeBinary
        self.browser = Driver(**driverArgs)
        self.cookies = cookiejar.MozillaCookieJar(cookieFilePath)
        self.cookies.load()
        self.waitTime = waitTime

    def getPage(self, url):
        print(f"Get page {url}")
        # Clear Cloudflare on the base domain, add the login cookies, then open
        # the target the same way.
        self.browser.uc_open_with_reconnect(
            self.baseUrl, reconnect_time=self.RECONNECT_TIME)
        self.addCookies()
        for _ in range(2):
            self.browser.uc_open_with_reconnect(
                url, reconnect_time=self.RECONNECT_TIME)
            time.sleep(self.waitTime)
            if not self.isBlockedByCloudflare():
                break
            print("javlibrary: Cloudflare challenge detected, retrying...")
        else:
            print("javlibrary: blocked by Cloudflare challenge, no data returned")

        button = self.browser.find_elements(
            by=By.CLASS_NAME, value="btnAdultAgree")
        if button:
            button[0].click()
            time.sleep(self.waitTime)

        return self.browser.page_source

    def isBlockedByCloudflare(self):
        title = self.browser.title or ""
        return "cf_chl" in self.browser.page_source.lower() or "請稍候" in title


class WebPageGetter_JavDB(WebPageGetter):
    def __init__(self, cookieFilePath, waitTime):
        super().__init__(cookieFilePath, waitTime)
        self.baseUrl = "https://javdb.com"

    def getPage(self, url):
        self.simpleGetPage(url)
        try:
            WebDriverWait(self.browser, self.PAGE_WAIT_TIMEOUT).until(
                lambda x: x.find_element(By.CLASS_NAME, "movie-list"))
        except Exception as e:
            print("get page failed")
            return "", ""

        firstResult = self.browser.find_element(
            By.CSS_SELECTOR, ".movie-list .item a")
        videolink = "http://javdb.com/" + \
            firstResult.get_attribute("pathname") + "?locale=en"
        try:
            simpletitle = firstResult.find_element(
                By.CSS_SELECTOR, ".video-title").text
        except Exception:
            simpletitle = ""

        self.simpleGetPage(videolink)

        return self.browser.page_source, simpletitle
