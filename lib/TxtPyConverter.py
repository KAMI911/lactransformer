try:
    import csv
    from pyproj import Proj, transform
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)


class TxtPyConverter:
    def __init__(self, source_filename, source_projection, destination_filename, destination_projection, separator = ','):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        self.__SourceProj = Proj(source_projection)
        self.__DestinationProjection = destination_projection
        self.__DestinationProj = Proj(destination_projection)
        self.__Separator = separator


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

    def TransformLASText(self):
        # Transforming PointText
        r = csv.reader(self.__SourceOpenedFile, delimiter=self.__Separator)
        w = csv.writer(self.__DestinationOpenedFile, delimiter=self.__Separator)
        for i, row in enumerate(r):
            row[0], row[1], row[2] = transform(self.__SourceProj, self.__DestinationProj,
                                                       row[0], row[1], row[2])
            w.writerow(row)

    def TransformPointText(self):
        # Transforming PointText
        r = csv.reader(self.__SourceOpenedFile, delimiter=self.__Separator)
        w = csv.writer(self.__DestinationOpenedFile, delimiter=self.__Separator)
        for i, row in enumerate(r):
            if i > 0:  # skip header transformation
                row[1], row[2], row[3] = transform(self.__SourceProj, self.__DestinationProj,
                                                       row[1], row[2], row[3])
            w.writerow(row)

    def TransformPointCSV(self):
        # Transforming PointText
        r = csv.reader(self.__SourceOpenedFile, self.__Separator)
        w = csv.writer(self.__DestinationOpenedFile, self.__Separator)
        for i, row in enumerate(r):
            if i > 0:  # skip header transformation
                row[2], row[3], row[4] = transform(self.__SourceProj, self.__DestinationProj,
                                                   row[2], row[3], row[4])
            w.writerow(row)

    def TransformPointIML(self):
        # Transforming PointText
        r = csv.reader(self.__SourceOpenedFile, delimiter=' ')
        w = csv.writer(self.__DestinationOpenedFile, delimiter=' ')
        for i, row in enumerate(r):
            if i > 0:  # skip header transformation
                row[1], row[2], row[3] = transform(self.__SourceProj, self.__DestinationProj,
                                                   row[1], row[2], row[3])
            w.writerow(row)

    def Close(self):
        self.__SourceOpenedFile.close()
        self.__DestinationOpenedFile.close()
