import json


class Setting:
    def __init__(self):
        with open("config.json", encoding="utf-8") as configFile:
            settingJson = json.load(configFile)

        try:
            self.fileDirs = settingJson["fileDirs"]
            self.getInfoInterval = settingJson["getInfoInterval"]
            self.fileNameFormat = settingJson["fileNameFormat"]
            self.language = settingJson["language"]
            self.saveAlbum = settingJson["saveAlbum"]
            self.dryRun = settingJson["dryRun"]
            self.maxFileLength = settingJson["maxFileLength"]
            self.minFileSizeMB = settingJson["minFileSizeMB"]
            self.renameCheck = settingJson["renameCheck"]
            self.saveThumb = settingJson["saveThumb"]
            self.ignoreWords = settingJson["ignoreWords"]
            self.retryFailedDB = settingJson["retryFailedDB"]
            self.javlibraryCookieFilePath = settingJson["javlibraryCookieFilePath"]
            self.javdbCookieFilePath = settingJson["javdbCookieFilePath"]
            # TODO: enable db or not
        except:
            print("read config file failed")
            exit(0)
