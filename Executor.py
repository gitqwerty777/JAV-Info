import requests
import colorama
from getch import getch
from pathlib import Path


def lenInBytes(string):
    return len(string.encode("utf-8"))


class Executor:
    def __init__(self, setting):
        self.setting = setting

    def HandleFiles(self, info, bangou, fileNames):
        self.HandleBangou(info, fileNames[bangou][0])

        if len(fileNames[bangou]) > 1:  # need to rename files with index
            for index, fileName in enumerate(fileNames[bangou]):
                self.HandleFile(info, fileName, index)
        else:
            self.HandleFile(info, fileNames[bangou][0])

    def HandleBangou(self, info, path):  # only save one copy of album and thumb
        print(
            f"============== handle bangou {colorama.Back.YELLOW}{info['bangou']}{colorama.Back.RESET} ==================")
        if self.setting.saveAlbum:
            self.SaveAlbum(info, path)
        if self.setting.saveThumb:
            self.SaveThumb(info, path)

    def HandleFile(self, info, path, index=-1):
        print(
            f"============== handle file {colorama.Back.YELLOW}{str(path)}{colorama.Back.RESET} ==================")
        self.Rename(info, path, index)
        # TODO: fill video meta description in video file
        # TODO: option: new folder for all video file, for the same actor, for the same tag # create link

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

        # handle multiple files with the same bangou
        numberStr = ("_" + str(index+1)) if (index != -1) else ""
        # handle file name too long error
        if lenInBytes(newFileName) + lenInBytes(numberStr) + lenInBytes(path.suffix) > self.setting.maxFileLength:
            print(f"File name too long: {newFileName}")
            maxFileLength = self.setting.maxFileLength - \
                lenInBytes(path.suffix) - lenInBytes(numberStr)
            while lenInBytes(newFileName) > maxFileLength:
                newFileName = newFileName[0:-1]
            print(f"After truncate file name: {newFileName}")
        newName = newFileName + numberStr + path.suffix

        if path.name == newName:
            print(
                f"File {colorama.Back.BLUE}{str(path)}{colorama.Back.RESET} no need to rename")
            return

        self.DoRename(path, newName)

    def DoRename(self, path, newName):
        newPath = path.parents[0] / newName

        print(f"Rename {colorama.Back.BLUE}{str(path)}{colorama.Back.RESET}\n" +
              f"To     {colorama.Back.GREEN}{str(newPath)}{colorama.Back.RESET}")

        if self.setting.dryRun:
            return

        if self.setting.renameCheck:
            print(
                f"{colorama.Back.BLUE}Do you want to execute rename?(Y/n){colorama.Back.RESET}")
            response = getch()
            print(response)
            if response.lower() == "n":
                print("User cancel rename")
                return

        try:
            path.rename(newPath)
        except Exception as e:
            print(
                f"{colorama.Back.RED}Rename [{str(path)}] to [{str(newPath)}] failed{colorama.Back.RESET}")
            print(e)

    def SaveAlbum(self, info, path):
        if not info["album"]:
            print("Album link not found")
            return

        albumFileName = info["bangou"] + ".jpg"
        albumPath = Path(path.parents[0] / albumFileName)

        if albumPath.exists():
            print(
                f"Album {colorama.Back.BLUE}{str(albumPath)}{colorama.Back.RESET} already exists")
            return
        self.DoSaveAlbum(info["album"], albumPath)

    def DoSaveAlbum(self, fileURL, albumPath):
        print(
            f"Save album {colorama.Back.GREEN}{str(albumPath)}{colorama.Back.RESET}")

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
                    f"Thumbnail {colorama.Back.BLUE}{str(filePath)}{colorama.Back.RESET} already exists")
                continue

            self.DoSaveThumb(thumb, filePath)

    def DoSaveThumb(self, fileURL, filePath):
        print(
            f"Save thumbnail {colorama.Back.GREEN}{str(filePath)}{colorama.Back.RESET}")

        if self.setting.dryRun:
            return

        with open(filePath, 'wb') as thumbFile:
            fileObject = requests.get(fileURL)
            thumbFile.write(fileObject.content)
