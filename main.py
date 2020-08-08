import colorama
from Setting import Setting
from FileNameParser import FileNameParser
from DataManager import DataManager
from JAVInfoGetter import JAVInfoGetter
from Executor import Executor

if __name__ == "__main__":
    colorama.init()
    setting = Setting()
    fileNameParser = FileNameParser(setting.fileExts, setting.minFileSizeMB)
    dataManager = DataManager(setting)
    infoGetter = JAVInfoGetter(setting, dataManager)
    executor = Executor(setting)

    if setting.dryRun:
        print(f"{colorama.Back.RED}This is dry run version.\nSet dryRun to false in config.json to execute{colorama.Back.RESET}")
    else:
        print(f"{colorama.Back.RED}This is not dry run version.\nDry run is recommended before execution.\nDo you want to continue?(y/N){colorama.Back.RESET}")
        response = input()
        if response.lower() != "y":
            exit(0)

    fileNames = fileNameParser.GetFiles(setting.fileDir)
    for bangou in fileNames:
        info, success = infoGetter.GetInfo(bangou, str(fileNames[bangou]))
        if not success:
            continue
        executor.HandleFiles(info, bangou, fileNames)

    dataManager.Save()
