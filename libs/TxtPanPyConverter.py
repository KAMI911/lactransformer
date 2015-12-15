try:
    import csv
    import numpy as np
    import pandas
    import re
    from pyproj import Proj, transform
    from libs import PefFile, AssignProjection
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)


class TxtPanPyConverter:
    def __init__(self, source_filename, source_projection, destination_filename, destination_projection, type='txt',
                 separator=','):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        self.__SourceProjectionString = AssignProjection.AssignProjection(source_projection, '..')
        self.__SourceProj = Proj(self.__SourceProjectionString)
        self.__DestinationProjection = destination_projection
        self.__DestinationProjectionString = AssignProjection.AssignProjection(self.__DestinationProjection, '..')
        self.__DestinationProj = Proj(self.__DestinationProjectionString)
        self.__Separator = separator
        self.__Type = type
        if self.__Type == 'txt':
            self.__HeaderRow = 0
            self.__Fields = [1, 2, 3]
        elif self.__Type == 'lastxt':
            self.__HeaderRow = None
            self.__Fields = [0, 1, 2]
        elif self.__Type == 'iml':
            self.__HeaderRow = 0
            self.__Fields = [1, 2, 3]
        elif self.__Type == 'csv':
            self.__HeaderRow = 0
            self.__Fields = [2, 3, 4]

    def Open(self):
        try:
            if self.__Type != 'pef':
                self.__DestinationOpenedFile = open(self.__DestinationFileName, 'wb')
                df = pandas.read_csv(self.__SourceFileName, sep=self.__Separator, header=self.__HeaderRow)
                self.__SourceData = df.values
                self.__Columns = df.columns
                self.__Header = ''
                if self.__HeaderRow != None:
                    self.__HeaderList = list(df.columns.values)
                    self.__Header = ','.join(self.__HeaderList)
                self.__Format = []
                for h in range(0, len(self.__Columns)):
                    self.__Format.append('%1.12f')
                if self.__Type == 'txt':
                    self.__Format[0] = '%1.6f'
                elif self.__Type == 'csv':
                    self.__Format[0] = '%1.6f'
                if self.__DestinationProjection in ['WGS84'] and self.__Type != 'pef':
                    for f in self.__Fields:
                        self.__Format[f] = '%1.15f'

            elif self.__Type == 'pef':
                self.__SourceOpenedFile = PefFile.PefFile(self.__SourceFileName)
                self.__SourceOpenedFile.OpenRO()
                self.__DestinationOpenedFile = PefFile.PefFile(self.__DestinationFileName)
                self.__DestinationOpenedFile.OpenOW()
        except Exception as err:
            raise

    def Transform(self):
        if self.__Type != 'pef':
            self.TransformTxt()
        else:
            self.TransformPEF()

    def TransformTxt(self):
        self.__SourceData[:, self.__Fields[0]], self.__SourceData[:, self.__Fields[1]], self.__SourceData[:,
                                                                                        self.__Fields[2]] = transform(
            self.__SourceProj,
            self.__DestinationProj,
            self.__SourceData[:, self.__Fields[0]],
            self.__SourceData[:, self.__Fields[1]],
            self.__SourceData[:, self.__Fields[2]])

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
            np.savetxt(self.__DestinationFileName, self.__SourceData, fmt=self.__Format, header=self.__Header,
                       delimiter=self.__Separator, comments='')

        else:
            self.__SourceOpenedFile.Close()
            self.__DestinationOpenedFile.Close()
