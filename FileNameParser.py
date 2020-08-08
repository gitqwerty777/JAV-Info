import re
import pprint
from pathlib import Path

def CreatePrettyPrinter():
    return pprint.PrettyPrinter(indent=0, width=60)

class FileNameParser:
    def __init__(self, fileExts):
        self.fileExts = fileExts

    def GetFiles(self, fileDir):
        videoFileList = []
        path = Path(fileDir)
        for fileExt in self.fileExts:
            videoFileList.extend(path.rglob(fileExt))

        fileNames = dict()
        for fileName in videoFileList:
            bangou = self.ParseBangou(fileName.name)
            if not bangou:
                continue

            bangou = bangou.upper()
            if bangou in fileNames:
                fileNames[bangou].append(fileName)
                fileNames[bangou].sort()
            else:
                fileNames[bangou] = [fileName]

        pp = CreatePrettyPrinter()
        print("find video files")
        pp.pprint(fileNames)

        return fileNames

    def ParseBangou(self, fileName):
        try:
            bangou = re.search("\w+\-*\d+", fileName).group(0) # TODO: fit different bangou format
            return bangou
        except:
            return ""
