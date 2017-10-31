try:
    import csv
    import numpy as np
    import pandas
    import re
    import sys
    import os
    from pyproj import Proj, transform
    from . import PefFile, AssignProjection
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    exit(128)


class TxtPanPyConverter:
    def __init__(self, source_filename, source_projection, destination_filename, destination_projection, type='txt',
                 separator=',', proc_name = 'Unknown'):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        self.__SourceProjectionString = AssignProjection.AssignProjectionString(source_projection, proc_name)
        self.__SourceProj = Proj(self.__SourceProjectionString)
        self.__DestinationProjection = destination_projection
        self.__DestinationProjectionString = AssignProjection.AssignProjectionString(self.__DestinationProjection, proc_name)
        self.__DestinationProj = Proj(self.__DestinationProjectionString)
        self.__Separator = separator
        self.__Type = type
        if self.__Type == 'txt':
            self.__HeaderRow = 0
            self.__Fields = [1, 2, 3]
        elif self.__Type == 'lastxt':
            self.__HeaderRow = None
            self.__Fields = [0, 1, 2]
        elif self.__Type in ['strtxt', 'listtxt']:
            self.__HeaderRow = None
            self.__Fields = [1, 2, 3]
        elif self.__Type == 'iml':
            self.__HeaderRow = 0
            self.__Fields = [1, 2, 3]
        elif self.__Type == 'csv':
            self.__HeaderRow = 0
            self.__Fields = [2, 3, 4]

    # Replaces the header of text files to the correct one based on Destination Projection
    def __projection_replace_header(self):
        new_header_part = []
        if self.__DestinationProjection in ['WGS84geo']:
            new_header_part = ['X[m]', 'Y[m]', 'Z[m]']
        elif self.__DestinationProjection in ['EOV', 'EOVc', 'EOV2009', 'EOV2014', 'SVY21', 'SVY21c']:
            new_header_part = ['Easting[m]', 'Northing[m]', 'Elevation[m]']
        if new_header_part != []:
            for i in range(0, 3):
                self.__HeaderList[self.__Fields[i]] = new_header_part[i]

    def Open(self):
        try:
            if self.__Type != 'pef':
                self.__DestinationOpenedFile = open(self.__DestinationFileName, 'wb')
                if self.__SourceFileName != 'stdin':
                    df = pandas.read_csv(self.__SourceFileName, sep=self.__Separator, header=self.__HeaderRow)
                else:
                    df = pandas.read_csv(sys.stdin, sep=self.__Separator, header=self.__HeaderRow)
                self.__SourceData = df.values
                self.__Columns = df.columns
                self.__Header = ''
                if self.__HeaderRow != None:
                    self.__HeaderList = list(df.columns.values)
                    self.__projection_replace_header()
                    self.__Header = ','.join(self.__HeaderList)
                if self.__Type not in [ 'strtxt', 'listtxt']:
                    self.__Format = [ '%1.12f'.format(h) for h in range(0, len(self.__Columns)) ]
                else:
                    self.__Format = [ '%s'.format(h) for h in range(0, len(self.__Columns)) ]
                if self.__Type in  [ 'txt', 'csv' ]: self.__Format[0] = '%1.6f'
                if self.__Type == 'listtxt': self.__Format[0] = '%06d'
                if self.__DestinationProjection in ['WGS84'] and self.__Type != 'pef':
                    for f in self.__Fields:
                        self.__Format[f] = '%1.15f'
                elif self.__DestinationProjection not in ['WGS84'] and self.__Type != 'pef':
                    for f in self.__Fields:
                        self.__Format[f] = '%1.4f'
            elif self.__Type == 'pef':
                self.__SourceOpenedFile = PefFile.PefFile(self.__SourceFileName) if self.__SourceFileName != 'stdin' else PefFile.PefFile(sys.stdin)
                self.__SourceOpenedFile.OpenRO()
                self.__DestinationOpenedFile = PefFile.PefFile(self.__DestinationFileName)
                self.__DestinationOpenedFile.OpenOW()
        except Exception as err:
            raise

    def Transform(self):
        self.TransformTxt() if self.__Type != 'pef' else  self.TransformPEF()

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
                    Content[i][1] = '%.10f %.10f %.10f' % (coordinates[0], coordinates[1], coordinates[2])
            self.__DestinationOpenedFile.WriteNextItem(Content)

    def Close(self, type='txt'):
        if self.__Type != 'pef':
            with open(self.__DestinationFileName, 'wb') as f:
                np.savetxt(f, self.__SourceData, fmt=self.__Format, header=self.__Header, delimiter=self.__Separator,
                           comments='', newline='\r\n')
        else:
            self.__SourceOpenedFile.Close()
            self.__DestinationOpenedFile.Close()
