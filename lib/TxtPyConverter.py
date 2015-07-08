import csv

from pyproj import Proj, transform


class TxtPyConverter:
    def __init__(self, source_filename, source_projection, destination_filename, destination_projection):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        self.__SourceProj = Proj(source_projection)
        self.__DestinationProjection = destination_projection
        self.__DestinationProj = Proj(destination_projection)

    def Open(self):
        try:
            self.__SourceOpenedFile = open(self.__SourceFileName, 'rb')
            self.__DestinationOpenedFile = open(self.__DestinationFileName, 'wb')
        except Exception as err:
            raise

    def OpenReanOnly(self):
        try:
            self.__SourceOpenedFile = open(self.__SourceFileName, 'rb')
            self.__DestinationOpenedFile = open(self.__DestinationFileName, 'wb')
        except Exception as err:
            raise

    def TransformPointText(self):
        # Transforming PointText
        r = csv.reader(self.__SourceOpenedFile, delimiter=',')
        w = csv.writer(self.__DestinationOpenedFile, delimiter=',')
        for i, row in enumerate(r):
            if i > 0:  # skip header transformation
                row[1], row[2], row[3] = transform(self.__SourceProj, self.__DestinationProj,
                                               row[1], row[2], row[3])
            w.writerow(row)

    def Close(self):
        self.__SourceOpenedFile.close()
        self.__DestinationOpenedFile.close()
