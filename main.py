import colorama
import utils
from Setting import Setting
from FileNameParser import FileNameParser
from DataManager import DataManager
from JAVInfoGetter import JAVInfoGetter_javlibrary, JAVInfoGetter_javdb
from Executor import Executor
from getch import getch

if __name__ == "__main__":
    colorama.init()
    setting = Setting()
    fileNameParser = FileNameParser(setting.minFileSizeMB, setting.ignoreWords)
    dataManager = DataManager(setting)
    infoGetters = [JAVInfoGetter_javlibrary(setting, dataManager), JAVInfoGetter_javdb(
        setting, dataManager)]
    executor = Executor(setting)

    if setting.dryRun:
        utils.logError(
            f"This is dry run version.\nSet dryRun to false in config.json to execute")
    else:
        utils.logError(
            f"This is not dry run version.\nDry run is recommended before execution.\nDo you want to continue?(y/N)")
        response = getch()
        if response.lower() != "y":
            exit(0)

    try:
        fileNames = fileNameParser.GetFiles(setting.fileDir)
        for bangou in fileNames:
            info = None
            success = False
            print(
                f"===== 1/2: get bangou info {utils.yellowStr(bangou)} =====")
            for infoGetter in infoGetters:
                info, success = infoGetter.GetInfo(
                    bangou, str(fileNames[bangou]))
                if success:
                    dataManager.AddRecord(info)
                    break
                else:
                    continue
            if not success:
                utils.logError(
                    f"Get Info from bangou {bangou} failed. File name {str(fileNames[bangou])}")
                continue
            assert info
            executor.HandleFiles(info, bangou, fileNames)
    except Exception as e:
        print(e)
    finally:
        dataManager.Save()
