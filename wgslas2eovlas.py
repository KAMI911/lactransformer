import laspy
import laspy.file
import numpy as np
import math
from pyproj import Proj, transform
from lib import Timing

class LasPyConverter:
    def __init__(self, filename, backup=True):
        self.__FileName = filename
        self.__Backup = True

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

    def ScaleDimension(self):
        # Init does not work on Linux
        # WGS84 = Proj(init='EPSG:4326')
        # WGS84Geo = Proj(init='EPSG:4328')

        WGS84 = Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        WGS84Geo = Proj('+proj=geocent +ellps=WGS84 +datum=WGS84 +no_defs')
        EOV = Proj('+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs')
        #EOV = Proj(
        #    '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=etrs2eov_notowgs.gsb +units=m +no_defs')

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
        XTransformed, YTransformed, ZTransformed = transform(WGS84Geo, EOV, XOriginal, YOriginal, ZOriginal)
        print ('Offset:  %s %s %s' % (XOffset, YOffset, ZOffset))
        XTransformedOffset, YTransformedOffset, ZTransformedOffset = transform( WGS84Geo, EOV, XOffset, YOffset, ZOffset)

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


las = LasPyConverter('test.las')
las.Open()
# las.DumpHeaderFormat()
las.DumpPointFormat()
timer = Timing.Timing()
las.ScaleDimension()
print (timer.end())
las.Close()
print (timer.end())

