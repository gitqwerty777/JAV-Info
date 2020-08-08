import json

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
            self.minFileSizeMB = settingJson["minFileSizeMB"]
        except:
            print("read config file failed")
            exit(1)
