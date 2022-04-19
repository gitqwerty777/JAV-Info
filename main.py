import colorama
import utils
from Setting import Setting
from FileNameParser import FileNameParser
from DataManager import DataManager
from JAVInfoGetter import JAVInfoGetter_javlibrary, JAVInfoGetter_javdb
from Executor import Executor
from getch import getch


class JAVInfoGetter:
    def __init__(self, setting, fileNameParser, dataManager, infoGetters, executor):
        self.setting = setting
        self.fileNameParser = fileNameParser
        self.dataManager = dataManager
        self.infoGetters = infoGetters
        self.executor = executor
        self.renameFailedFile = open(
            "renameFailedHistory.txt", "a", encoding="utf-8")  # TODO: filename to config

    def getInfo(self):
        try:
            for fileDir in self.setting.fileDirs:
                fileNames = fileNameParser.GetFiles(fileDir)
                for bangou in fileNames:
                    self.renameByBangou(bangou, fileNames)
        except Exception as e:
            print(e)
        finally:
            self.dataManager.Save()

    def renameByBangou(self, bangou, fileNames):
        info = None
        success = False
        print(
            f"===== 1/3: get bangou info {utils.yellowStr(bangou)}")
        for infoGetter in self.infoGetters:
            # Get the first complete info
            info, success = infoGetter.GetInfo(
                bangou, str(fileNames[bangou]))
            if success:
                break
        if not success:
            utils.logError(
                f"Get Info from bangou {bangou} failed. File name {str(fileNames[bangou])}")
            utils.writeText(self.renameFailedFile,
                            f"{bangou} {fileNames[bangou]}\n")
            self.dataManager.AddRecord(info)
            return
        assert info
        self.executor.HandleFiles(info, bangou, fileNames)


def checkDryRun(setting):
    if setting.dryRun:
        utils.logError(
            f"This is dry run version.\nSet dryRun to false in config.json to execute")
    else:
        utils.logError(
            f"This is not dry run version.\nDry run is recommended before execution.\nDo you want to continue?(y/N)")
        response = getch()
        if response.lower() != "y":
            exit(0)


if __name__ == "__main__":
    colorama.init()

    setting = Setting()
    checkDryRun(setting)

    fileNameParser = FileNameParser(setting.minFileSizeMB, setting.ignoreWords)
    dataManager = DataManager(setting)
    infoGetters = [JAVInfoGetter_javlibrary(setting, dataManager), JAVInfoGetter_javdb(
        setting, dataManager)]
    executor = Executor(setting)
    javInfoGetter = JAVInfoGetter(
        setting, fileNameParser, dataManager, infoGetters, executor)

    javInfoGetter.getInfo()
