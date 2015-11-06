# -*- coding: UTF-8 -*-


class PefFile:
    def __init__(self, filename):
        self.__FileName = filename
        self.__PefLines = 8
        self.__FileIndex = 0

    def OpenRO(self):
        try:
            self.__PefFileHandler = open(self.__FileName, 'r')
        except IOError as ErrorText:
            print ('Error: %s' % str(ErrorText))

    def Open(self):
        self.__PefFileHandler = open(self.__FileName, 'a')

    def OpenOW(self):
        self.__PefFileHandler = open(self.__FileName, 'w')
        self.__PefFileHandler.truncate()

    def GotoStart(self):
        self.__FileIndex = 0

    def ReadNextItem(self, FileSeek=None):
        if not FileSeek:
            FileSeek = self.__FileIndex
        PefContent = []
        HasData = False
        while True:
            OneLine = (self.__PefFileHandler.readline().rstrip('\n\r'))
            if OneLine != '':
                HasData = True
                TwoPairs = OneLine.split('=')
                PefContent.append(TwoPairs)
            elif OneLine == '' and HasData == True:
                break
            elif OneLine == '' and HasData == False:
                break
        self.__FileIndex = self.__PefFileHandler.tell()
        return PefContent

    def TestItem(self, PefContent):
        errors = 0
        if PefContent[0][0] == 'TYPE' and PefContent[0][1] == 'PlaneObj':
            ('PEF Type is okay...')
        else:
            errors += 1
        if PefContent[3][1] == '8':
            print ('Count is 8')
        else:
            errors += 1
        print (errors)
        return errors

    def WriteNextItem(self, PefContent):
        for line in PefContent:
            OneLine = '%s=%s\n' % (line[0], line[1])
            self.__PefFileHandler.writelines(OneLine)
        self.__PefFileHandler.writelines('\n')

    def PrintNextItem(self):
        print (self.__FileIndex)
        Lines = self.ReadNextItem()
        print (self.__FileIndex)
        for l in Lines:
            print (l)

    def Close(self):
        self.__PefFileHandler.close()
