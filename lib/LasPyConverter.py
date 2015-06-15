import logging
import numpy as np
from pyproj import Proj, transform
import math

import laspy
import laspy.file


class LasPyConverter:
    def __init__(self, source_filename, source_projection, destination_filename, destination_projection):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        self.__SourceProj = Proj(source_projection)
        self.__DestinationProjection = destination_projection
        self.__DestinationProj = Proj(destination_projection)

    def Open(self):
        self.__SourceOpenedFile = laspy.file.File(self.__SourceFileName, mode='r')
        self.__DestinationOpenedFile = laspy.file.File(self.__DestinationFileName, mode='w',
                                                       header=self.__SourceOpenedFile.header)

    def DumpHeaderFormat(self):
        for spec in self.__SourceOpenedFile.header.header_format:
            in_spec = self.__SourceOpenedFile.header.get_schema()
            logging.info('Source setting: %s: %s' % (spec.name, in_spec))
        for spec in self.__DestinationOpenedFile.header.header_format:
            in_spec = self.__DestinationOpenedFile.header.get_schema()
            logging.info('Destination setting: %s: %s' % (spec.name, in_spec))

    def DumpPointFormat(self):
        for spec in self.__SourceOpenedFile.point_format:
            in_spec = self.__SourceOpenedFile.reader.get_dimension(spec.name)
            logging.info('Source setting: %s: %s' % (spec.name, in_spec))
        for spec in self.__DestinationOpenedFile.point_format:
            in_spec = self.__DestinationOpenedFile.reader.get_dimension(spec.name)
            logging.info('Destination setting: %s: %s' % (spec.name, in_spec))

    def GetSourcePointFormat(self):
        for spec in self.__SourceOpenedFile.reader.point_format:
            in_spec = self.__SourceOpenedFile.reader.get_dimension(spec.name)
        return (spec.name, in_spec)

    def GetDestinationPointFormat(self):
        for spec in self.__DestinationOpenedFile.reader.point_format:
            in_spec = self.__DestinationOpenedFile.reader.get_dimension(spec.name)
        return (spec.name, in_spec)

    def GetSourceScale(self):
        # Use scale as is as
        self.__SourceScale = [self.__SourceOpenedFile.header.scale[0], self.__SourceOpenedFile.header.scale[1],
                              self.__SourceOpenedFile.header.scale[2]]
        # Use offset as is as
        self.__SourceOffset = [self.__SourceOpenedFile.header.offset[0], self.__SourceOpenedFile.header.offset[1],
                               self.__SourceOpenedFile.header.offset[2]]

    def SetDestinationScale(self):
        # Use scale as is as
        self.__DestinationScale = [self.__SourceOpenedFile.header.scale[0],
                                   self.__SourceOpenedFile.header.scale[1],
                                   self.__SourceOpenedFile.header.scale[2]]
        # Use offset as is as
        self.__DestinationOffset = np.array([0, 0, 0])
        self.__DestinationOffset[0], self.__DestinationOffset[1], self.__DestinationOffset[2] = transform(
            self.__SourceProj, self.__DestinationProj, self.__SourceOffset[0], self.__SourceOffset[1],
            self.__SourceOffset[2])
        self.__DestinationOffset = [math.floor(self.__DestinationOffset[0]), math.floor(self.__DestinationOffset[1]),
                                    math.floor(self.__DestinationOffset[2])]
        logging.info('LAS PointCloud file transformed offset: %s %s %s' % (
            self.__DestinationOffset[0], self.__DestinationOffset[1], self.__DestinationOffset[2]))
        logging.info('Updating LAS file header offset and scale.')
        self.__DestinationOpenedFile.header.set_scale((
            self.__DestinationScale[0], self.__DestinationScale[1], self.__DestinationScale[2]))
        self.__DestinationOpenedFile.header.set_offset((
            self.__DestinationOffset[0], self.__DestinationOffset[1], self.__DestinationOffset[2]))

    def TransformPointCloud(self):
        # Transforming PointCloud
        self.__DestinationOpenedFile.x, self.__DestinationOpenedFile.y, self.__DestinationOpenedFile.z = transform(
            self.__SourceProj, self.__DestinationProj,
            self.__SourceOpenedFile.x, self.__SourceOpenedFile.y,
            self.__SourceOpenedFile.z)

        self.__DestinationOpenedFile.intensity = self.__SourceOpenedFile.intensity
        self.__DestinationOpenedFile.flag_byte = self.__SourceOpenedFile.flag_byte
        self.__DestinationOpenedFile.raw_classification = self.__SourceOpenedFile.raw_classification
        self.__DestinationOpenedFile.scan_angle_rank = self.__SourceOpenedFile.scan_angle_rank
        self.__DestinationOpenedFile.user_data = self.__SourceOpenedFile.user_data
        self.__DestinationOpenedFile.pt_src_id = self.__SourceOpenedFile.pt_src_id
        self.__DestinationOpenedFile.gps_time = self.__SourceOpenedFile.gps_time

        self.UpdateDestinationMinMax()

    def TransformPointCloudCoordsOnly(self):
        self.__DestinationOpenedFile.x, self.__DestinationOpenedFile.y, self.__DestinationOpenedFile.z = transform(
            self.__SourceProj,
            self.__DestinationProj,
            self.__SourceOpenedFile.x, self.__SourceOpenedFile.y,
            self.__SourceOpenedFile.z)

        self.UpdateDestinationMinMax()

    def UpdateDestinationMinMax(self):
        logging.info('Updating LAS file min and max values.')
        self.__DestinationOpenedFile.header.update_min_max()

    def Close(self):
        self.__SourceOpenedFile.close()
        self.__DestinationOpenedFile.close()
