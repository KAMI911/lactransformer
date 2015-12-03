try:
    import logging
    import os
    import numpy as np
    import math
    from pyproj import Proj, transform
    import laspy
    import laspy.file
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)


class LasPyConverter:
    def __init__(self, source_filename, source_projection, source_fallback_projection, destination_filename,
                 destination_projection, destination_fallback_projection):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        self.__SourceProj = Proj(source_projection)
        if source_fallback_projection:
            self.__SourceFallbackProjection = source_fallback_projection
            self.__SourceFallbackProj = Proj(source_fallback_projection)
        else:
            self.__SourceFallbackProjection = ''
            self.__SourceFallbackProj = ''
        self.__DestinationProjection = destination_projection
        self.__DestinationProj = Proj(destination_projection)
        if destination_fallback_projection:
            self.__DestinationFallbackProjection = destination_fallback_projection
            self.__DestinationFallbackProj = Proj(destination_fallback_projection)
        else:
            self.__DestinationFallbackProjection = ''
            self.__DestinationFallbackProj = ''

    def Open(self):
        try:
            self.__SourceOpenedFile = laspy.file.File(self.__SourceFileName, mode='r')
            self.__DestinationOpenedFile = laspy.file.File(self.__DestinationFileName, mode='w',
                                                           header=self.__SourceOpenedFile.header)
        except Exception as err:
            raise

    def OpenReanOnly(self):
        try:
            self.__SourceOpenedFile = laspy.file.File(self.__SourceFileName, mode='r')
            self.__DestinationOpenedFile = laspy.file.File(self.__DestinationFileName, mode='r')
        except Exception as err:
            raise

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
        try:
            self.__SourceScale = [self.__SourceOpenedFile.header.scale[0], self.__SourceOpenedFile.header.scale[1],
                                  self.__SourceOpenedFile.header.scale[2]]
            # Use offset as is as
            self.__SourceOffset = [self.__SourceOpenedFile.header.offset[0], self.__SourceOpenedFile.header.offset[1],
                                   self.__SourceOpenedFile.header.offset[2]]
        except Exception:
            raise

    def SetDestinationScale(self):
        # Use scale as is as
        try:
            self.__DestinationScale = [self.__SourceOpenedFile.header.scale[0],
                                       self.__SourceOpenedFile.header.scale[1],
                                       self.__SourceOpenedFile.header.scale[2]]
            # Use offset as is as
            self.__DestinationOffset = np.array([0, 0, 0])
            if self.__DestinationFallbackProjection:
                self.__DestinationOffset[0], self.__DestinationOffset[1], self.__DestinationOffset[2] = transform(
                    self.__SourceProj, self.__DestinationFallbackProj,
                    self.__SourceOffset[0], self.__SourceOffset[1],
                    self.__SourceOffset[2])
            else:
                self.__DestinationOffset[0], self.__DestinationOffset[1], self.__DestinationOffset[2] = transform(
                    self.__SourceProj, self.__DestinationProj,
                    self.__SourceOffset[0], self.__SourceOffset[1],
                    self.__SourceOffset[2])
            self.__DestinationOffset = [math.floor(self.__DestinationOffset[0]),
                                        math.floor(self.__DestinationOffset[1]),
                                        math.floor(self.__DestinationOffset[2])]
            self.__DestinationOpenedFile.header.set_scale((
                self.__DestinationScale[0], self.__DestinationScale[1], self.__DestinationScale[2]))
            self.__DestinationOpenedFile.header.set_offset((
                self.__DestinationOffset[0], self.__DestinationOffset[1], self.__DestinationOffset[2]))
        except Exception:
            raise
        else:
            return self.__SourceOffset, self.__DestinationOffset

    def TransformPointCloud(self):
        # Transforming PointCloud
        try:
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
        except Exception:
            raise

    def TransformPointCloudCoordsOnly(self):
        try:
            self.__DestinationOpenedFile.x, self.__DestinationOpenedFile.y, self.__DestinationOpenedFile.z = transform(
                self.__SourceProj,
                self.__DestinationProj,
                self.__SourceOpenedFile.x, self.__SourceOpenedFile.y,
                self.__SourceOpenedFile.z)
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
        except Exception:
            raise

    def CloseDestinationFile(self, full_header_update=False):
        try:
            self.__DestinationOpenedFile.close(ignore_header_changes=not (full_header_update))
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
            diff_x = self.__SourceOpenedFile.x - self.__DestinationOpenedFile.x
            diff_y = self.__SourceOpenedFile.y - self.__DestinationOpenedFile.y
            diff_z = self.__SourceOpenedFile.z - self.__DestinationOpenedFile.z

            logging.info('%s diff: Xmin: %s / Xmax: %s, Ymin: %s / Ymax: %s, Zmin: %s / Zmax: %s' % (
                os.path.basename(self.__SourceFileName), np.min(diff_x), np.max(diff_x), np.min(diff_y), np.max(diff_y),
                np.min(diff_z), np.max(diff_z)))
        except Exception:
            raise

    def Close(self):
        try:
            self.__SourceOpenedFile.close()
            self.__DestinationOpenedFile.close()
        except Exception:
            raise
