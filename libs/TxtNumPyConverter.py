try:
    import csv
    import numpy as np
    import re
    import sys
    from pyproj import Proj, transform
    from libs import PefFile, AssignProjection
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    exit(128)


class TxtNumPyConverter:
    def __init__(self, source_filename, source_projection, destination_filename, destination_projection, type='txt',
                 separator=','):
        self.__SourceFileName = source_filename
        self.__DestinationFileName = destination_filename
        self.__SourceProjection = source_projection
        self.__SourceProjectionString = AssignProjection.AssignProjectionString(source_projection)
        self.__SourceProj = Proj(self.__SourceProjectionString)
        self.__DestinationProjection = destination_projection
        self.__DestinationProjectionString = AssignProjection.AssignProjectionString(self.__DestinationProjection)
        self.__DestinationProj = Proj(self.__DestinationProjectionString)
        self.__Separator = separator
        self.__Type = type
        if self.__Type == 'txt':
            self.__SkipRows = 1
            self.__Fields = [1, 2, 3]
            self.__Format = ['%1.6f', '%1.12f', '%1.12f', '%1.12f', '%1.12f', '%1.12f', '%1.12f']
        elif self.__Type == 'lastxt':
            self.__SkipRows = 0
            self.__Fields = [0, 1, 2]
            self.__Format = ['%1.12f', '%1.12f', '%1.12f']
        elif self.__Type == 'iml':
            self.__SkipRows = 1
            self.__Fields = [1, 2, 3]
        elif self.__Type == 'csv':
            self.__SkipRows = 1
            self.__Fields = [2, 3, 4]
            self.__Format = ['%1.6f', '%1.12f', '%1.12f', '%1.12f', '%1.12f', '%1.12f', '%1.12f']
        if self.__DestinationProjection in ['WGS84'] and self.__Type != 'pef':
            for f in self.__Fields:
                self.__Format[f] = '%1.15f'

    def Open(self):
        try:
            if self.__Type != 'pef':
                if self.__SourceFileName != 'stdin':
                    self.__SourceData = np.loadtxt(self.__SourceFileName, delimiter=self.__Separator,
                                                   dtype=float, skiprows=self.__SkipRows)
                else:
                    self.__SourceData = np.loadtxt(sys.stdin, delimiter=self.__Separator,
                                                   dtype=float, skiprows=self.__SkipRows)
            elif self.__Type == 'pef':
                if self.__SourceFileName != 'stdin':
                    self.__SourceOpenedFile = PefFile.PefFile(self.__SourceFileName)
                else:
                    self.__SourceOpenedFile = PefFile.PefFile(sys.stdin)
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
            np.savetxt(self.__DestinationFileName, self.__SourceData,
                       fmt=self.__Format,
                       header="Time[s],X[m],Y[m],Z[m],Roll[deg],Pitch[deg],Yaw[deg]",
                       delimiter=self.__Separator, comments='')
        else:
            self.__SourceOpenedFile.Close()
            self.__DestinationOpenedFile.Close()
