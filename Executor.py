import requests
from getch import getch
from pathlib import Path
import utils
import re
from utils import lenInBytes
import sys


class Executor:
    def __init__(self, setting):
        self.setting = setting
        self.renameRecords = open("renameHistory.txt", "a", encoding="utf-8")

    def HandleFiles(self, info, bangou, fileNames):
        print(
            f"===== 2/3: handle bangou {utils.yellowStr(bangou)} =====")
        self.HandleBangou(info, fileNames[bangou][0])

        if len(fileNames[bangou]) > 1:  # need to rename files with index
            for index, fileName in enumerate(fileNames[bangou]):
                self.HandleFile(info, fileName, index)
        else:
            self.HandleFile(info, fileNames[bangou][0])

    def HandleBangou(self, info, path):  # only save one copy of album and thumb
        if self.setting.saveAlbum:
            self.SaveAlbum(info, path)
        if self.setting.saveThumb:
            self.SaveThumb(info, path)

    def HandleFile(self, info, path, index=-1):
        print(
            f"===== 3/3: handle file {utils.yellowStr(str(path))} =====")
        self.Rename(info, path, index)
        # optional TODO: fill video meta description in video file
        # TODO: option: new folder for all video file, for the same actor, for the same tag # create link

    def getValidWindowsFileName(self, fileName):
        """
        https://docs.microsoft.com/zh-tw/windows/win32/fileio/naming-a-file?redirectedfrom=MSDN
        """
        return re.sub(r"[><:\"/\\\|\?*]", "_", fileName)

    def Rename(self, info, path, index):
        newFileName = self.setting.fileNameFormat
        for key in info:
            infokey = "{" + key + "}"
            infovalue = info[key]
            if type(infovalue) is list:
                infovalue = ""
                for element in info[key]:
                    infovalue = infovalue + "[" + element + "]"
            newFileName = newFileName.replace(infokey, infovalue)

        if "win" in sys.platform:
            newFileName = self.getValidWindowsFileName(newFileName)

        # handle multiple files with the same bangou
        numberStr = ("_" + str(index+1)) if (index != -1) else ""
        # handle file name too long error
        if lenInBytes(newFileName) + lenInBytes(numberStr) + lenInBytes(path.suffix) > self.setting.maxFileLength:
            print(utils.redBackStr(f"File name too long: {newFileName}"))
            maxFileLength = self.setting.maxFileLength - \
                lenInBytes(path.suffix) - lenInBytes(numberStr)
            while lenInBytes(newFileName) > maxFileLength:
                newFileName = newFileName[0:-1]
            print(
                f"After truncate file name: {utils.blueBackStr(newFileName)}")
        newName = newFileName + numberStr + path.suffix

        if path.name == newName:
            print(
                f"File {utils.blueBackStr(str(path))} no need to rename")
            return

        self.DoRename(path, newName)

    def DoRename(self, path, newName):
        newPath = path.parents[0] / newName

        print(f"Rename {utils.blueBackStr(str(path))}\n" +
              f"To     {utils.greenBackStr(str(newPath))}")

        if self.setting.dryRun:
            return

        if self.setting.renameCheck:
            print(utils.blueBackStr(f"Do you want to execute rename?(Y/n)"))
            response = getch()
            print(response)
            if response.lower() == "n":
                print("User cancel rename")
                return

        try:
            self.renameRecords.write(f"{path} -> {newPath}\n")
            self.renameRecords.flush()
            path.rename(newPath)
        except Exception as e:
            print(
                utils.redBackStr(f"Rename [{str(path)}] to [{str(newPath)}] failed"))
            print(e)

    def SaveAlbum(self, info, path):
        if not info["album"]:
            print("Album link not found")
            return

        albumFileName = info["bangou"] + ".jpg"
        albumPath = Path(path.parents[0] / albumFileName)

        if albumPath.exists():
            print(
                f"Album {utils.blueBackStr(str(albumPath))} already exists")
            return
        self.DoSaveAlbum(info["album"], albumPath)

    def DoSaveAlbum(self, fileURL, albumPath):
        print(
            f"Save album {utils.greenBackStr(str(albumPath))}")

        if self.setting.dryRun:
            return

        with open(albumPath, 'wb') as albumFile:
            fileObject = requests.get(fileURL)
            albumFile.write(fileObject.content)

    def SaveThumb(self, info, path):
        if not info["thumbs"]:
            print("Thumbnail link not found")
            return

        for index, thumb in enumerate(info["thumbs"]):
            fileName = info["bangou"] + "_thumb" + \
                str(index) + ".jpg"  # TODO: fill leading 0 of index
            filePath = Path(path.parents[0] / fileName)

            if filePath.exists():
                print(
                    f"Thumbnail {utils.blueBackStr(str(filePath))} already exists")
                continue

            self.DoSaveThumb(thumb, filePath)

    def DoSaveThumb(self, fileURL, filePath):
        print(
            f"Save thumbnail {utils.greenBackStr(str(filePath))}")

        if self.setting.dryRun:
            return

        with open(filePath, 'wb') as thumbFile:
            fileObject = requests.get(fileURL)
            thumbFile.write(fileObject.content)
