import colorama
from Setting import Setting
from FileNameParser import FileNameParser
from DataManager import DataManager
from JAVInfoGetter import JAVInfoGetter_javlibrary, JAVInfoGetter_javdb
from Executor import Executor
from getch import getch

if __name__ == "__main__":
    colorama.init()
    setting = Setting()
    fileNameParser = FileNameParser(
        setting.fileExts, setting.minFileSizeMB, setting.ignoreWords)
    dataManager = DataManager(setting)
    infoGetters = [JAVInfoGetter_javlibrary(setting, dataManager), JAVInfoGetter_javdb(
        setting, dataManager)]
    executor = Executor(setting)

    if setting.dryRun:
        print(f"{colorama.Back.RED}This is dry run version.\nSet dryRun to false in config.json to execute{colorama.Back.RESET}")
    else:
        print(f"{colorama.Back.RED}This is not dry run version.\nDry run is recommended before execution.\nDo you want to continue?(y/N){colorama.Back.RESET}")
        response = getch()
        print(response)
        if response.lower() != "y":
            exit(0)

    fileNames = fileNameParser.GetFiles(setting.fileDir)
    for bangou in fileNames:
        for infoGetter in infoGetters:
            info, success = infoGetter.GetInfo(bangou, str(fileNames[bangou]))
            if success:
                # TODO: add to database at here
                break
            else:
                continue
        if not success:
            print(
                f"{colorama.Back.RED}Get Info from bangou {bangou} failed. File name {str(fileNames[bangou])}{colorama.Back.RESET}")
            dataManager.Add(info)
            continue
        executor.HandleFiles(info, bangou, fileNames)

    dataManager.Save()
    print("Press Any Button to Exit")
    getch()
