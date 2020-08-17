import re
import pprint
from pathlib import Path


def CreatePrettyPrinter(stream=None):
    return pprint.PrettyPrinter(indent=0, width=60, stream=stream)


class FileNameParser:
    def __init__(self, fileExts, minFileSizeMB, ignoreWords):
        self.fileExts = fileExts
        self.minFileSizeMB = minFileSizeMB
        self.ignoreWords = ignoreWords

    def GetFiles(self, fileDir):
        videoFileList = []
        path = Path(fileDir)
        for fileExt in self.fileExts:
            videoFileList.extend(path.rglob(fileExt))

        fileNames = dict()
        for fileName in videoFileList:
            stat = fileName.stat()
            fileSizeMB = stat.st_size >> 20
            if self.minFileSizeMB > fileSizeMB:
                #print(f"ignore {str(fileName)} because file too small")
                continue

            bangou = self.ParseBangou(fileName.name)
            if not bangou:
                print(f"bangou not found in file {fileName.name}")
                continue

            bangou = bangou.upper()
            if bangou in fileNames:
                fileNames[bangou].append(fileName)
                fileNames[bangou].sort()
            else:
                fileNames[bangou] = [fileName]

        f = open("filebangous.txt", "w", encoding="utf-8")
        pp = CreatePrettyPrinter(f)
        print("find legal video files")
        pp.pprint(fileNames)

        return fileNames

    def ParseBangou(self, fileName):
        try:
            fileName = fileName.lower()
            for ignoreWord in self.ignoreWords:
                fileName = fileName.replace(ignoreWord, "")

            # TODO: fit different bangou format
            result = re.search("([a-zA-Z]{1,5})\-+(\d{3,5})", fileName)

            bangou = ""
            if result:
                bangou = result.group(1) + "-" + result.group(2)
            else:
                # non-strict version
                result = re.search(
                    "([a-zA-Z]{1,5})\s*\-*\s*(\d{3,5})", fileName)
                if result:
                    bangou = result.group(1) + "-" + result.group(2)

            if bangou == "MP-4":  # special case
                bangou = ""

            return bangou
        except:
            return ""
