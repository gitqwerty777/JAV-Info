import mimetypes
import re
import pprint
from pathlib import Path


def CreatePrettyPrinter(stream=None):
    return pprint.PrettyPrinter(indent=0, width=60, stream=stream)


class BangouHandler:  # abstract
    def __init__(self, next):
        self.next = next

    def DoNext(self, fileName):
        if self.next:
            return self.next.Handle(fileName)
        else:
            return ""


class FC2BangouHandler(BangouHandler):
    def __init__(self, next):
        BangouHandler.__init__(self, next)
        self.fc2BangouRE = re.compile(r"(fc2)-*(ppv)*-*(\d{7})")

    def Handle(self, fileName):
        result = self.fc2BangouRE.search(fileName)

        if result:
            return result.group(1) + "-" + result.group(3)
        else:
            return self.DoNext(fileName)


class GeneralBangouHandler(BangouHandler):
    def __init__(self, next):
        BangouHandler.__init__(self, next)
        self.generalBangouRE = re.compile(r"([a-zA-Z]{1,5})\-+(\d{2,5})")

    def Handle(self, fileName):
        result = self.generalBangouRE.search(fileName)

        if result:
            return result.group(1) + "-" + result.group(2)
        else:
            return self.DoNext(fileName)


class GeneralLooseBangouHandler(BangouHandler):
    def __init__(self, next):
        BangouHandler.__init__(self, next)
        self.generalLooseBangouRE = re.compile(
            r"([a-zA-Z]{1,5})\s*\-*\s*(\d{2,5})")

    def Handle(self, fileName):
        result = self.generalLooseBangouRE.search(fileName)

        if result:
            bangou = result.group(1) + "-" + result.group(2)
            if bangou == "MP-4":  # special case
                bangou = ""
            if bangou:
                return bangou
        return self.DoNext(fileName)


class FileNameParser:
    def __init__(self, minFileSizeMB, ignoreWords):
        self.minFileSizeMB = minFileSizeMB
        self.ignoreWords = ignoreWords
        # TODO: fit different bangou format
        self.bangouHandler = FC2BangouHandler(
            GeneralBangouHandler(
                GeneralLooseBangouHandler(None)))

    def GetFiles(self, fileDir):
        videoFileList = []
        path = Path(fileDir)

        mimetypes.init()
        # Add new unknown video file extension if needed
        mimetypes.add_type('video/vnd.rn-realmedia-vbr', '.rmvb')
        mimetypes.add_type('video/rm', '.rm')
        mimetypes.add_type('video/x-flv', '.flv')
        mimetypes.add_type('video/dcv', '.dcv')

        for file in path.glob("**/*"):
            if file.is_dir():
                continue
            if file.suffix in mimetypes.types_map:
                mimetype = mimetypes.types_map[file.suffix]
                if "video" in mimetype:
                    videoFileList.append(file)
            # else:
                # print("unknown file extension: " + file.suffix)

        fileNames = dict()
        for fileName in videoFileList:
            stat = fileName.stat()
            fileSizeMB = stat.st_size >> 20
            if self.minFileSizeMB > fileSizeMB:
                # print(f"ignore {str(fileName)} because file too small")
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

        f = open("FilenameToBangou.txt", "w", encoding="utf-8")
        print("Legal video files with bangou")
        pp = CreatePrettyPrinter(f)
        pp.pprint(fileNames)
        pp = CreatePrettyPrinter()
        pp.pprint(fileNames)

        return fileNames

    def ParseBangou(self, fileName):
        fileName = fileName.lower()
        for ignoreWord in self.ignoreWords:
            fileName = fileName.replace(ignoreWord, "")

        return self.bangouHandler.Handle(fileName)
