try:
    import csv
    import re
    from pyproj import Proj, transform
    from libs import PefFile
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)


class TxtPyConverter:
    def __init__(self, source_filename, source_projection, destination_filename, destination_projection, type='txt',
                 separator=','):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        self.__SourceProj = Proj(source_projection)
        self.__DestinationProjection = destination_projection
        self.__DestinationProj = Proj(destination_projection)
        self.__Separator = separator
        self.__Type = type

    def Open(self):
        try:
            if self.__Type != 'pef':
                self.__SourceOpenedFile = open(self.__SourceFileName, 'rb')
                self.__DestinationOpenedFile = open(self.__DestinationFileName, 'wb')
            elif self.__Type == 'pef':
                self.__SourceOpenedFile = PefFile.PefFile(self.__SourceFileName)
                self.__SourceOpenedFile.OpenRO()
                self.__DestinationOpenedFile = PefFile.PefFile(self.__DestinationFileName)
                self.__DestinationOpenedFile.OpenOW()
        except Exception as err:
            raise

    def OpenReanOnly(self):
        try:
            self.__SourceOpenedFile = open(self.__SourceFileName, 'rb')
            self.__DestinationOpenedFile = open(self.__DestinationFileName, 'wb')
        except Exception as err:
            raise

    def Transform(self):
        if self.__Type == 'txt':
            self.TransformPointText()
        elif self.__Type == 'lastxt':
            self.TransformLASText()
        elif self.__Type == 'iml':
            self.TransformPointIML()
        elif self.__Type == 'csv':
            self.TransformPointCSV()
        elif self.__Type == 'pef':
            self.TransformPEF()

    def DoTransform(self, x_in, y_in, z_in, x_out, y_out, z_out, skip_first_lines):
        self.r = csv.reader(self.__SourceOpenedFile, delimiter=self.__Separator)
        self.w = csv.writer(self.__DestinationOpenedFile, delimiter=self.__Separator)
        for i, row in enumerate(self.r):
            if i >= skip_first_lines:  # skip header transformation
                row[x_out], row[y_out], row[z_out] = transform(self.__SourceProj, self.__DestinationProj,
                                                               row[x_in], row[y_in], row[z_in])
            self.w.writerow(row)

    def TransformLASText(self):
        # Transforming LASText, type lastxt
        self.DoTransform(0, 1, 2, 0, 1, 2, 0)

    def TransformPointText(self):
        # Transforming PointText, type txt
        self.DoTransform(1, 2, 3, 1, 2, 3, 1)

    def TransformPointCSV(self):
        # Transforming CSV, type csv
        self.DoTransform(2, 3, 4, 2, 3, 4, 1)

    def TransformPointIML(self):
        # Transforming IML, type iml
        self.DoTransform(1, 2, 3, 1, 2, 3, 1)

    def TransformPEF(self):
        # Transforming PEF, type pef
        point_pattern = re.compile('P\d{1,3}')  # format is Pn or Pnn or Pnnn
        while True:
            Content = self.__SourceOpenedFile.ReadNextItem()
            if not Content:
                break
            # self.__DestinationOpenedFile.
            for i, row in enumerate(Content):
                point_number = point_pattern.search(row[0])
                if point_number is not None:
                    coordinates = row[1].split(' ')
                    coordinates[0], coordinates[1], coordinates[2] = transform(self.__SourceProj,
                                                                               self.__DestinationProj,
                                                                               coordinates[0], coordinates[1],
                                                                               coordinates[2])
                    Content[i][1] = '%s %s %s' % (coordinates[0], coordinates[1], coordinates[2])
            self.__DestinationOpenedFile.WriteNextItem(Content)

    def Close(self, type='txt'):
        if self.__Type != 'pef':
            self.__SourceOpenedFile.close()
            self.__DestinationOpenedFile.close()
        elif self.__Type == 'pef':
            self.__SourceOpenedFile.Close()
            self.__DestinationOpenedFile.Close()
