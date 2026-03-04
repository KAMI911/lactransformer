# -*- coding: UTF-8 -*-


class PefFile:
    def __init__(self, filename):
        self.__FileName = filename
        self.__PefLines = 8
        self.__FileIndex = 0
        self.__PefFileHandler = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Close()
        return False

    def OpenRO(self):
        try:
            self.__PefFileHandler = open(self.__FileName, 'r')
        except IOError as err:
            raise IOError(f'Cannot open {self.__FileName} for reading: {err}') from err

    def Open(self):
        self.__PefFileHandler = open(self.__FileName, 'a')

    def OpenOW(self):
        self.__PefFileHandler = open(self.__FileName, 'w')

    def GotoStart(self):
        self.__FileIndex = 0

    def ReadNextItem(self, FileSeek=None):
        if FileSeek is None:
            FileSeek = self.__FileIndex
        PefContent = []
        for line in self.__PefFileHandler:
            stripped = line.rstrip('\n\r')
            if stripped == '':
                if PefContent:
                    break
            else:
                PefContent.append(stripped.split('='))
        self.__FileIndex = self.__PefFileHandler.tell()
        return PefContent

    def TestItem(self, PefContent):
        errors = 0
        if not (PefContent[0][0] == 'TYPE' and PefContent[0][1] == 'PlaneObj'):
            errors += 1
        if PefContent[3][1] != '8':
            errors += 1
        return errors

    def WriteNextItem(self, PefContent):
        for line in PefContent:
            self.__PefFileHandler.write(f'{line[0]}={line[1]}\r\n')
        self.__PefFileHandler.write('\r\n')

    def Close(self):
        if self.__PefFileHandler is not None:
            self.__PefFileHandler.close()
            self.__PefFileHandler = None
