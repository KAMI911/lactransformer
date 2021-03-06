try:
    import traceback
    import logging
    import os
    import numpy as np
    import math
    from pyproj import Proj, transform
    import laspy
    import sys
    import laspy.file
    from . import AssignProjection
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    traceback.print_exc()
    exit(128)


class LasPyConverter:
    def __init__(self, source_filename, source_projection, destination_filename,
                 destination_projection, proc_name = 'Unknown'):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        self.__SourceProjectionString = AssignProjection.AssignProjectionString(self.__SourceProjection, proc_name )
        self.__SourceProj = Proj(self.__SourceProjectionString)
        self.__SourceFallbackProjectionString = AssignProjection.AssignFallbackProjectionString(self.__SourceProjection)
        if self.__SourceFallbackProjectionString:
            self.__SourceFallbackProjection = AssignProjection.AssignProjectionName(self.__SourceProjection)
            self.__SourceFallbackProj = Proj(self.__SourceFallbackProjectionString)
        else:
            self.__SourceFallbackProjection = AssignProjection.AssignProjectionName(self.__SourceProjection)
            self.__SourceFallbackProj = ''

        self.__DestinationProjection = destination_projection
        self.__DestinationProjectionString = AssignProjection.AssignProjectionString(self.__DestinationProjection, proc_name)
        self.__DestinationProj = Proj(self.__DestinationProjectionString)

        self.__DestinationFallbackProjectionString = AssignProjection.AssignFallbackProjectionString(
            self.__DestinationProjection)
        if self.__DestinationFallbackProjectionString:
            self.__DestinationFallbackProjection = AssignProjection.AssignProjectionName(self.__DestinationProjection)
            self.__DestinationFallbackProj = Proj(self.__DestinationFallbackProjectionString)
        else:
            self.__DestinationFallbackProjection = AssignProjection.AssignProjectionName(self.__DestinationProjection)
            self.__DestinationFallbackProj = ''

    def Open(self):
        try:
            if self.__SourceFileName != 'stdin':
                self.__SourceOpenedFile = laspy.file.File(self.__SourceFileName, mode='r')
            else:
                self.__SourceOpenedFile = laspy.file.File(sys.stdin, mode='r')
            self.__DestinationOpenedFile = laspy.file.File(self.__DestinationFileName, mode='w',
                                                           header=self.__SourceOpenedFile.header)
        except Exception as err:
            raise

    def OpenReanOnly(self):
        try:
            if self.__SourceFileName != 'stdin':
                self.__SourceOpenedFile = laspy.file.File(self.__SourceFileName, mode='r')
            else:
                self.__SourceOpenedFile = laspy.file.File(sys.stdin, mode='r')
            self.__DestinationOpenedFile = laspy.file.File(self.__DestinationFileName, mode='r')
        except Exception as err:
            raise

    def DumpHeaderFormat(self):
        for spec in self.__SourceOpenedFile.header.header_format:
            in_spec = self.__SourceOpenedFile.header.get_schema()
            logging.info('Source setting: {0}: {1}'.format(spec.name, in_spec))
        for spec in self.__DestinationOpenedFile.header.header_format:
            in_spec = self.__DestinationOpenedFile.header.get_schema()
            logging.info('Destination setting: {0}: {1}'.format(spec.name, in_spec))

    def DumpPointFormat(self):
        for spec in self.__SourceOpenedFile.point_format:
            in_spec = self.__SourceOpenedFile.reader.get_dimension(spec.name)
            logging.info('Source setting: {0}: {1}'.format(spec.name, in_spec))
        for spec in self.__DestinationOpenedFile.point_format:
            in_spec = self.__DestinationOpenedFile.reader.get_dimension(spec.name)
            logging.info('Destination setting: {0}: {1}'.format(spec.name, in_spec))

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
        try:
            self.__SourceScale = self.__SourceOpenedFile.header.scale
            # Use offset as is as
            self.__SourceOffset = self.__SourceOpenedFile.header.offset
        except Exception:
            raise

    def SetDestinationScale(self):
        # Use scale as is as
        try:
            self.__DestinationScale = self.__SourceScale
            # Use offset as is as
            self.__DestinationOffset = np.array([0, 0, 0])
            if self.__DestinationFallbackProjection:
                self.__DestinationOffset = transform(
                    self.__SourceProj, self.__DestinationFallbackProj,
                    self.__SourceOffset[0], self.__SourceOffset[1], self.__SourceOffset[2])
            else:
                self.__DestinationOffset = transform(
                    self.__SourceProj, self.__DestinationProj,
                    self.__SourceOffset[0], self.__SourceOffset[1], self.__SourceOffset[2])
            self.__DestinationOffset = [math.floor(self.__DestinationOffset[0]),
                                        math.floor(self.__DestinationOffset[1]),
                                        math.floor(self.__DestinationOffset[2])]
            self.__DestinationOpenedFile.header.set_scale(self.__DestinationScale)
            self.__DestinationOpenedFile.header.set_offset(self.__DestinationOffset)
        except Exception:
            raise
        else:
            return self.__SourceOffset, self.__DestinationOffset

    def TransformPointCloud(self):
        # Transforming PointCloud
        try:
            self.__DestinationOpenedFile.points = self.__SourceOpenedFile.points
            self.__DestinationOpenedFile.x, self.__DestinationOpenedFile.y, self.__DestinationOpenedFile.z = transform(self.__SourceProj, self.__DestinationProj, self.__SourceOpenedFile.x, self.__SourceOpenedFile.y, self.__SourceOpenedFile.z)
            self.UpdateDestinationMinMax()
        except Exception:
            raise

    def TransformPointCloudCoordsOnly(self):
        try:
            self.__DestinationOpenedFile.x, self.__DestinationOpenedFile.y, self.__DestinationOpenedFile.z = transform(self.__SourceProj, self.__DestinationProj, self.__SourceOpenedFile.x, self.__SourceOpenedFile.y, self.__SourceOpenedFile.z)
            self.UpdateDestinationMinMax()
        except Exception:
            raise

    def ReturnOriginalMin(self):
        return np.amin([self.__SourceOpenedFile.x, self.__SourceOpenedFile.y, self.__SourceOpenedFile.z], axis=1)

    def ReturnOriginalMax(self):
        return np.amax([self.__SourceOpenedFile.x, self.__SourceOpenedFile.y, self.__SourceOpenedFile.z], axis=1)

    def ReturnTransformedMin(self):
        return np.amin([self.__DestinationOpenedFile.x, self.__DestinationOpenedFile.y, self.__DestinationOpenedFile.z],
                       axis=1)

    def ReturnTransformedMax(self):
        return np.amax([self.__DestinationOpenedFile.x, self.__DestinationOpenedFile.y, self.__DestinationOpenedFile.z],
                       axis=1)

    def UpdateDestinationMinMax(self):
        try:
            self.__DestinationOpenedFile.header.update_min_max()
        except Exception:
            raise

    def CloseSourceFile(self):
        try:
            self.__SourceOpenedFile.close()
            del self.__SourceOpenedFile
        except Exception:
            raise

    def CloseDestinationFile(self, full_header_update=False):
        try:
            self.__DestinationOpenedFile.close(ignore_header_changes=not (full_header_update))
            del self.__DestinationOpenedFile
        except Exception:
            raise

    def Close(self, full_header_update=False):
        try:
            self.CloseSourceFile()
            self.CloseDestinationFile(full_header_update)
        except Exception:
            raise


class LasPyCompare:
    def __init__(self, source_filename, destination_filename):
        try:
            self.__SourceFileName = source_filename
            self.__DestinationFileName = destination_filename
        except Exception:
            raise

    def OpenReanOnly(self):
        try:
            self.__SourceOpenedFile = laspy.file.File(self.__SourceFileName, mode='r')
            self.__DestinationOpenedFile = laspy.file.File(self.__DestinationFileName, mode='r')
        except Exception:
            raise

    def ComparePointCloud(self):
        try:
            diff = [self.__SourceOpenedFile.x - self.__DestinationOpenedFile.x,
                    self.__SourceOpenedFile.y - self.__DestinationOpenedFile.y,
                    self.__SourceOpenedFile.z - self.__DestinationOpenedFile.z]
            diff_min, diff_max, diff_avg, diff_std = [], [], [], []
            for i in range(0, 3):
                diff_min.append(np.min(diff[i]))
                diff_max.append(np.max(diff[i]))
                diff_avg.append(np.mean(diff[i]))
                diff_std.append(np.std(diff[i]))
            logging.info('{0} file differences:'.format(
                os.path.basename(self.__SourceFileName)))
            print('Xmin/max/avg/std: {0[0]:.4f}/{1[0]:.4f}/{2[0]:.4f}/{3[0]:.4f}, Ymin/max/avg/std: {0[1]:.4f}/{1[1]:.4f}/{2[1]:.4f}/{3[1]:.4f}, Zmin/max/avg/std: {0[2]:.4f}/{1[2]:.4f}/{2[2]:.4f}/{3[2]:.4f}'.format(
                diff_min, diff_max, diff_avg, diff_std))
            logging.info(
                'Xmin/max/avg/std: {0[0]:.4f}/{1[0]:.4f}/{2[0]:.4f}/{3[0]:.4f}, Ymin/max/avg/std: {0[1]:.4f}/{1[1]:.4f}/{2[1]:.4f}/{3[1]:.4f}, Zmin/max/avg/std: {0[2]:.4f}/{1[2]:.4f}/{2[2]:.4f}/{3[2]:.4f}'.format(
                    diff_min, diff_max, diff_avg, diff_std))
            return diff_min, diff_max, diff_avg, diff_std

        except Exception as err:
            raise

    def is_equal(self):
        return np.array_equal(self.__SourceOpenedFile.points, self.__DestinationOpenedFile.points)

    def Close(self):
        try:
            self.__SourceOpenedFile.close()
            del self.__SourceOpenedFile
            self.__DestinationOpenedFile.close()
            del self.__DestinationOpenedFile
        except Exception:
            raise
