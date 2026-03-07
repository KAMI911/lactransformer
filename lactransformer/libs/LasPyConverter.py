try:
    import traceback
    import logging
    import os
    import numpy as np
    import math
    from pyproj import Transformer
    import laspy
    import sys
    from . import AssignProjection
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)


class LasPyConverter:
    def __init__(self, source_filename, source_projection, destination_filename,
                 destination_projection, proc_name='Unknown'):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        src_proj_str = AssignProjection.AssignProjectionString(source_projection, proc_name)
        self.__DestinationProjection = destination_projection
        dst_proj_str = AssignProjection.AssignProjectionString(destination_projection, proc_name)
        dst_fallback_str = AssignProjection.AssignFallbackProjectionString(destination_projection)

        self.__DestinationFallbackProjection = AssignProjection.AssignProjectionName(destination_projection)

        self.__Transformer = Transformer.from_crs(src_proj_str, dst_proj_str, always_xy=True)
        if dst_fallback_str:
            self.__OffsetTransformer = Transformer.from_crs(src_proj_str, dst_fallback_str, always_xy=True)
        else:
            self.__OffsetTransformer = self.__Transformer

    def Open(self):
        if self.__SourceFileName != 'stdin':
            self.__SourceOpenedFile = laspy.read(self.__SourceFileName)
        else:
            self.__SourceOpenedFile = laspy.read(sys.stdin.buffer)
        new_header = laspy.LasHeader(
            point_format=self.__SourceOpenedFile.header.point_format,
            version=self.__SourceOpenedFile.header.version
        )
        self.__DestinationOpenedFile = laspy.LasData(header=new_header)

    def OpenReadOnly(self):
        if self.__SourceFileName != 'stdin':
            self.__SourceOpenedFile = laspy.read(self.__SourceFileName)
        else:
            self.__SourceOpenedFile = laspy.read(sys.stdin.buffer)
        self.__DestinationOpenedFile = laspy.read(self.__DestinationFileName)

    def DumpHeaderFormat(self):
        logging.info(f'Source header: {self.__SourceOpenedFile.header}')
        logging.info(f'Destination header: {self.__DestinationOpenedFile.header}')

    def DumpPointFormat(self):
        for spec in self.__SourceOpenedFile.point_format:
            logging.info(f'Source point format: {spec.name}')
        for spec in self.__DestinationOpenedFile.point_format:
            logging.info(f'Destination point format: {spec.name}')

    def GetSourcePointFormat(self):
        specs = list(self.__SourceOpenedFile.point_format)
        return (specs[-1].name, None) if specs else (None, None)

    def GetDestinationPointFormat(self):
        specs = list(self.__DestinationOpenedFile.point_format)
        return (specs[-1].name, None) if specs else (None, None)

    def GetSourceScale(self):
        self.__SourceScale = self.__SourceOpenedFile.header.scales
        self.__SourceOffset = self.__SourceOpenedFile.header.offsets

    def SetDestinationScale(self):
        self.__DestinationScale = self.__SourceScale
        x, y, z = self.__OffsetTransformer.transform(
            self.__SourceOffset[0], self.__SourceOffset[1], self.__SourceOffset[2])
        self.__DestinationOffset = [math.floor(x), math.floor(y), math.floor(z)]
        self.__DestinationOpenedFile.header.scales = self.__DestinationScale
        self.__DestinationOpenedFile.header.offsets = np.array(self.__DestinationOffset)
        return self.__SourceOffset, self.__DestinationOffset

    def TransformPointCloud(self):
        src_points = self.__SourceOpenedFile.points
        dst_header = self.__DestinationOpenedFile.header
        new_points = laspy.ScaleAwarePointRecord(
            src_points.array.copy(),
            dst_header.point_format,
            scales=dst_header.scales,
            offsets=dst_header.offsets,
        )
        self.__DestinationOpenedFile.points = new_points
        x, y, z = self.__Transformer.transform(
            self.__SourceOpenedFile.x, self.__SourceOpenedFile.y, self.__SourceOpenedFile.z)
        self.__DestinationOpenedFile.x = x
        self.__DestinationOpenedFile.y = y
        self.__DestinationOpenedFile.z = z
        self.UpdateDestinationMinMax()

    def TransformPointCloudCoordsOnly(self):
        x, y, z = self.__Transformer.transform(
            self.__SourceOpenedFile.x, self.__SourceOpenedFile.y, self.__SourceOpenedFile.z)
        self.__DestinationOpenedFile.x = x
        self.__DestinationOpenedFile.y = y
        self.__DestinationOpenedFile.z = z
        self.UpdateDestinationMinMax()

    def ReturnOriginalMin(self):
        return np.amin([self.__SourceOpenedFile.x, self.__SourceOpenedFile.y, self.__SourceOpenedFile.z], axis=1)

    def ReturnOriginalMax(self):
        return np.amax([self.__SourceOpenedFile.x, self.__SourceOpenedFile.y, self.__SourceOpenedFile.z], axis=1)

    def ReturnTransformedMin(self):
        return np.amin([self.__DestinationOpenedFile.x, self.__DestinationOpenedFile.y,
                        self.__DestinationOpenedFile.z], axis=1)

    def ReturnTransformedMax(self):
        return np.amax([self.__DestinationOpenedFile.x, self.__DestinationOpenedFile.y,
                        self.__DestinationOpenedFile.z], axis=1)

    def UpdateDestinationMinMax(self):
        self.__DestinationOpenedFile.update_header()

    def CloseSourceFile(self):
        del self.__SourceOpenedFile

    def CloseDestinationFile(self, full_header_update=False):
        self.__DestinationOpenedFile.write(self.__DestinationFileName)
        del self.__DestinationOpenedFile

    def Close(self, full_header_update=False):
        self.CloseSourceFile()
        self.CloseDestinationFile(full_header_update)


class LasPyCompare:
    def __init__(self, source_filename, destination_filename):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename

    def OpenReadOnly(self):
        self.__SourceOpenedFile = laspy.read(self.__SourceFileName)
        self.__DestinationOpenedFile = laspy.read(self.__DestinationFileName)

    def ComparePointCloud(self):
        diff = [self.__SourceOpenedFile.x - self.__DestinationOpenedFile.x,
                self.__SourceOpenedFile.y - self.__DestinationOpenedFile.y,
                self.__SourceOpenedFile.z - self.__DestinationOpenedFile.z]
        diff_min, diff_max, diff_avg, diff_std = [], [], [], []
        for i in range(3):
            diff_min.append(np.min(diff[i]))
            diff_max.append(np.max(diff[i]))
            diff_avg.append(np.mean(diff[i]))
            diff_std.append(np.std(diff[i]))
        logging.info(f'{os.path.basename(self.__SourceFileName)} file differences:')
        diff_msg = (
            f'Xmin/max/avg/std: {diff_min[0]:.4f}/{diff_max[0]:.4f}/{diff_avg[0]:.4f}/{diff_std[0]:.4f},'
            f' Ymin/max/avg/std: {diff_min[1]:.4f}/{diff_max[1]:.4f}/{diff_avg[1]:.4f}/{diff_std[1]:.4f},'
            f' Zmin/max/avg/std: {diff_min[2]:.4f}/{diff_max[2]:.4f}/{diff_avg[2]:.4f}/{diff_std[2]:.4f}')
        print(diff_msg)
        logging.info(diff_msg)
        return diff_min, diff_max, diff_avg, diff_std

    def is_equal(self):
        return np.array_equal(self.__SourceOpenedFile.points.array, self.__DestinationOpenedFile.points.array)

    def Close(self):
        del self.__SourceOpenedFile
        del self.__DestinationOpenedFile
