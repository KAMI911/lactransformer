import laspy
import laspy.file
from pyproj import Proj, transform
import math

class LasPyConverter:
    def __init__(self, filename, backup=True):
        self.__FileName = filename
        self.__Backup = True
        self.__SourceProjection = ""
        self.__DestinationProjection = ""
        self.__SourceProj = ""
        self.__DestinationProj = ""

    def OpenRO(self):
        self.__OpenedFile = laspy.file.File(self.__FileName, mode='r')

    def Open(self):
        self.__OpenedFile = laspy.file.File(self.__FileName, mode='rw')

    def DumpHeaderFormat(self):
        for spec in self.__OpenedFile.header.header_format:
            in_spec = self.__OpenedFile.header.get_schema()
            print('Setting: %s: %s'  % (spec.name, in_spec))

    def DumpPointFormat(self):
        for spec in self.__OpenedFile.point_format:
            in_spec = self.__OpenedFile.reader.get_dimension(spec.name)
            print('Setting: %s: %s' % (spec.name, in_spec))

    def GetPointFormat(self):
        for spec in inFile.reader.point_format:
            in_spec = inFile.reader.get_dimension(spec.name)
        return (spec.name, in_spec)

    def SetSourceProjection(self, sourceprojection):
        self.__SourceProjection =  sourceprojection
        self.__SourceProj =  Proj(sourceprojection)

    def SetDestinationProjection(self, destinationprojection):
        self.__DestinationProjection = destinationprojection
        self.__DestinationProj = Proj(destinationprojection)

    def ScaleDimension(self):
        XScale = self.__OpenedFile.header.scale[0]
        XOffset = self.__OpenedFile.header.offset[0]
        YScale = self.__OpenedFile.header.scale[1]
        YOffset = self.__OpenedFile.header.offset[1]
        ZScale = self.__OpenedFile.header.scale[2]
        ZOffset = self.__OpenedFile.header.offset[2]

        XDimension = self.__OpenedFile.X
        YDimension = self.__OpenedFile.Y
        ZDimension = self.__OpenedFile.Z

        XOriginal = XDimension * XScale + XOffset
        YOriginal = YDimension * YScale + YOffset
        ZOriginal = ZDimension * ZScale + ZOffset

        print ('Central: %s %s %s' % (XOriginal, YOriginal, ZOriginal))
        XTransformed, YTransformed, ZTransformed = transform(self.__SourceProj, self.__DestinationProj, XOriginal, YOriginal, ZOriginal)
        print ('Offset:  %s %s %s' % (XOffset, YOffset, ZOffset))
        XTransformedOffset, YTransformedOffset, ZTransformedOffset = transform(self.__SourceProj, self.__DestinationProj, XOffset, YOffset, ZOffset)

        XTransformedOffset = math.floor(XTransformedOffset)
        YTransformedOffset = math.floor(YTransformedOffset)
        ZTransformedOffset = math.floor(ZTransformedOffset)

        XProjected = (XTransformed - XTransformedOffset) / XScale
        YProjected = (YTransformed - YTransformedOffset) / YScale
        ZProjected = (ZTransformed - ZTransformedOffset) / YScale

        print('%s -- %s -- %s' % (XTransformedOffset, YTransformedOffset, ZTransformedOffset))
        print ('%s, %s, %s\n%s, %s, %s' % (XOriginal, YOriginal, ZOriginal, XProjected, YProjected, ZProjected))

        self.__OpenedFile.X = XProjected
        self.__OpenedFile.Y = YProjected
        self.__OpenedFile.Z = ZProjected
        self.__OpenedFile.header.set_offset((XTransformedOffset, YTransformedOffset, ZTransformedOffset))
        self.__OpenedFile.header.update_min_max()

    def Close(self):
        self.__OpenedFile.close()