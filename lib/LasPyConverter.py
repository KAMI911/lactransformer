import logging
import laspy
import laspy.file
import numpy as np
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
        self.__OpenedFile = laspy.file.File(self.__FileName, mode = 'r')
        self.__OpenedFileHeader = self.__OpenedFile.header
        self.SetScale()

    def Open(self, header):
        self.__OpenedFile = laspy.file.File(self.__FileName, mode = 'w', header = header)
        self.__OpenedFileHeader = self.__OpenedFile.header
        self.SetScale()

    def ReturnHeader(self):
        return self.__OpenedFile.header

    def DumpHeaderFormat(self):
        for spec in self.__OpenedFile.header.header_format:
            in_spec = self.__OpenedFile.header.get_schema()
            print('Setting: %s: %s'  % (spec.name, in_spec))

    def DumpPointFormat(self):
        for spec in self.__OpenedFile.point_format:
            in_spec = self.__OpenedFile.reader.get_dimension(spec.name)
            print('Setting: %s: %s' % (spec.name, in_spec))

    def ReturnPointFormat(self):
        for spec in inFile.reader.point_format:
            in_spec = inFile.reader.get_dimension(spec.name)
        return (spec.name, in_spec)

    def SetSourceProjection(self, sourceprojection):
        self.__SourceProjection =  sourceprojection
        self.__SourceProj =  Proj(sourceprojection)

    def SetDestinationProjection(self, destinationprojection):
        self.__DestinationProjection = destinationprojection
        self.__DestinationProj = Proj(destinationprojection)

    def SetScale(self):
        # Use scale as is as
        self.__Scale = [ self.__OpenedFile.header.scale[0], self.__OpenedFile.header.scale[1], self.__OpenedFile.header.scale[2] ]
        # Transform offset
        self.__Offset = [ self.__OpenedFile.header.offset[0],self.__OpenedFile.header.offset[1], self.__OpenedFile.header.offset[2] ]
    def ScaleDimension(self):
        self.__TransformedOffset = np.array([0,0,0])
        self.__TransformedOffset[0], self.__TransformedOffset[1], self.__TransformedOffset[2] = transform(self.__SourceProj, self.__DestinationProj, self.__Offset[0], self.__Offset[1], self.__Offset[2])
        self.__TransformedOffset = [ math.floor(self.__TransformedOffset[0]), math.floor(self.__TransformedOffset[1]), math.floor(self.__TransformedOffset[2]) ]
        logging.info('LAS PointCloud file transformed offset: %s %s %s' % (self.__TransformedOffset[0], self.__TransformedOffset[1], self.__TransformedOffset[2]))
        logging.info('Updating LAS file header offsets.')
        self.__OpenedFile.header.set_offset((self.__TransformedOffset[0], self.__TransformedOffset[1], self.__TransformedOffset[2]))

    def ReturnPointCloudCoordsOnly(self):
        # Reading PointCloud
        return np.array ([ self.__OpenedFile.X* self.__Scale[0] + self.__Offset[0],
                                            self.__OpenedFile.Y* self.__Scale[1] + self.__Offset[1],
                                            self.__OpenedFile.Z* self.__Scale[2] + self.__Offset[2] ])


    def ReturnPointCloud(self):
        # Reading PointCloud
        return np.array ([ self.__OpenedFile.X* self.__Scale[0] + self.__Offset[0],
                                            self.__OpenedFile.Y* self.__Scale[1] + self.__Offset[1],
                                            self.__OpenedFile.Z* self.__Scale[2] + self.__Offset[2],
                                            self.__OpenedFile.intensity, self.__OpenedFile.flag_byte, self.__OpenedFile.raw_classification, self.__OpenedFile.scan_angle_rank, self.__OpenedFile.user_data, self.__OpenedFile.pt_src_id, self.__OpenedFile.gps_time ])

    def TransformPointCloud(self, pointcloud):
        Transformed = np.empty_like(pointcloud)
        # Transforming PointCloud
        Transformed[0], Transformed[1], Transformed[2] = transform(self.__SourceProj, self.__DestinationProj, pointcloud[0], pointcloud[1], pointcloud[2])
        self.__OpenedFile.X = (Transformed[0] - self.__TransformedOffset[0]) / self.__Scale[0]
        self.__OpenedFile.Y = (Transformed[1] - self.__TransformedOffset[1]) / self.__Scale[1]
        self.__OpenedFile.Z = (Transformed[2] - self.__TransformedOffset[2]) / self.__Scale[2]

        self.__OpenedFile.intensity = pointcloud[3]
        self.__OpenedFile.flag_byte = pointcloud[4]
        self.__OpenedFile.raw_classification = pointcloud[5]
        self.__OpenedFile.scan_angle_rank = pointcloud[6]
        self.__OpenedFile.user_data = pointcloud[7]
        self.__OpenedFile.pt_src_id = pointcloud[8]
        self.__OpenedFile.gps_time = pointcloud[9]
        self.UpdateMinMax()

    def TransformPointCloudCoordsOnly(self):
        Transformed = np.empty_like(self.__PointCloudData)
        # Transforming PointCloud
        Transformed[0], Transformed[1], Transformed[2] = transform(self.__SourceProj, self.__DestinationProj, self.__PointCloudData[0], self.__PointCloudData[1], self.__PointCloudData[2])
        self.__OpenedFile.X = (Transformed[0] - self.__TransformedOffset[0]) / self.__Scale[0]
        self.__OpenedFile.Y = (Transformed[1] - self.__TransformedOffset[1]) / self.__Scale[1]
        self.__OpenedFile.Z = (Transformed[2] - self.__TransformedOffset[2]) / self.__Scale[2]
        self.UpdateMinMax()

    def UpdateMinMax(self):
        logging.info('Updating LAS file min and max values.')
        self.__OpenedFile.header.update_min_max()

    def Close(self):
        self.__OpenedFile.close()
