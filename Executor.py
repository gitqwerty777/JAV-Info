import requests
import colorama
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
        # TODO: save thumbs

    def HandleFile(self, info, path, index=-1):
        print(
            f"============== handle file {colorama.Back.YELLOW}{str(path)}{colorama.Back.RESET} ==================")
        self.Rename(info, path, index)
        # TODO: fill video meta description in video file
        # TODO: option: new folder for all video file, for the same actor, for the same tag # create link

    def Rename(self, info, path, index):  # TODO: refact
        newFileName = self.setting.fileNameFormat
        for key in info:
            infokey = "{" + key + "}"
            infovalue = info[key]
            if type(infovalue) is list:
                infovalue = ""
                for element in info[key]:
                    infovalue = infovalue + "[" + element + "]"
            newFileName = newFileName.replace(infokey, infovalue)

        # handle file name too long error
        if index == -1:
            if lenInBytes(newFileName) + lenInBytes(path.suffix) > self.setting.maxFileLength:
                print(f"File name too long: {newFileName}")
                maxFileLength = self.setting.maxFileLength - \
                    lenInBytes(path.suffix)
                while lenInBytes(newFileName) > maxFileLength:
                    newFileName = newFileName[0:-1]
                print(f"After truncate file name: {newFileName}")
            newName = newFileName + path.suffix
        else:  # handle multiple files with the same bangou
            numberStr = "_" + str(index+1)
            if lenInBytes(newFileName) + lenInBytes(path.suffix) + lenInBytes(numberStr) > self.setting.maxFileLength:
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

        # TODO: option to ask before rename

        if self.setting.dryRun:
            return

        try:
            path.rename(newPath)
        except Exception as e:
            print(
                f"{colorama.Back.RED}Rename [{str(path)}] to [{str(newPath)}] failed{colorama.Back.RESET}")
            print(e)

    def SaveAlbum(self, info, path):
        albumFileName = info["bangou"] + ".jpg"
        albumPath = Path(path.parents[0] / albumFileName)

        if albumPath.exists():
            print(
                f"Album {colorama.Back.BLUE}{str(albumPath)}{colorama.Back.RESET} already exists")
            return
        self.DoSaveAlbum(info, albumPath)

    def DoSaveAlbum(self, info, albumPath):
        print(
            f"Save album image {colorama.Back.GREEN}{str(albumPath)}{colorama.Back.RESET}")

        if self.setting.dryRun:
            return

        with open(albumPath, 'wb') as albumFile:
            fileURL = "http:" + info["album"]
            fileObject = requests.get(fileURL)
            albumFile.write(fileObject.content)
