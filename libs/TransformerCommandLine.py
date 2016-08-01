try:
    import argparse
    import textwrap
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    exit(128)


class TransformerCommandLine:
    def __init__(self):
        # predefinied paths
        self.parser = argparse.ArgumentParser(prog="lactransformer",
                                              formatter_class=argparse.RawTextHelpFormatter,
                                              description='',
                                              epilog=textwrap.dedent('''
        example:
            '''))
        # reguired parameters
        self.parser.add_argument('-i', type=str, dest='input', required=True,
                                 help='required:  input file or folder')
        self.parser.add_argument('-o', type=str, dest='output', required=True,
                                 help='required:  output file or folder (d:\lasfiles\\tests\\results)')

        # optional parameters
        self.parser.add_argument('-input_format', type=str, dest='input_format', required=False,
                                 choices=['las', 'laz', 'txt', 'lastxt', 'csv', 'iml', 'pef', 'strtxt', 'listtxt'],
                                 help='optional:  input format (default=las, laz is not implemented (yet))'
                                      '  las = LAS PointCloud\n'
                                      '  laz = LAZ (compressed) PointCloud\n'
                                      '  txt = Trajectory CSV file\n'
                                      '  lastxt = PointText\n'
                                      '  csv = Riegl Camera CSV file\n'
                                      '  iml = TerraPhoto Image List file\n'
                                      '  pef = PEF file\n'
                                      '  strtxt = String PointText\n'
                                      '  listtxt = List PointText\n')
        self.parser.add_argument('-input_projection', type=str, dest='input_projection', required=False,
                                 choices=['WGS84', 'WGS84geo', 'WGS84PM', 'EOV', 'EOVc', 'EOV2009', 'EOV2014', 'EOV2014fine', 'EOVp', 'SVY21', 'SVY21c', 'ETRS89',
                                          'ETRS89geo'],
                                 help='optional:  input format (default=WGS84geo, EOVp is not implemented (yet))\n'
                                      '  WGS84 (EPSG:4326) projection: http://epsg.io/4326/\n'
                                      '  WGS84geo (EPSG:4978) geocentric projection: http://epsg.io/4978/\n'
                                      '  WGS84PM (EPSG:3857) Pseudo-Mercator projection: http://epsg.io/3857/\n'
                                      '  EOV (EPSG:23700) projection: http://epsg.io/23700/\n'
                                      '  EOVc (EPSG:23700) projection with grid correction 2014: http://epsg.io/23700/\n'
                                      '  EOV2009 (EPSG:23700) projection with grid correction 2009: http://epsg.io/23700/\n'
                                      '  EOV2014 (EPSG:23700) projection with grid correction 2014 (2x2 km grid points): http://epsg.io/23700/\n'
                                      '  (experimental) EOV2014fine (EPSG:23700) projection with grid correction 2014 (1x1 km geoid grid points): http://epsg.io/23700/\n'
                                      '  SVY21 (EPSG:3414) projection: http://epsg.io/3414/\n'
                                      '  SVY21c (EPSG:3414) projection with correction: http://epsg.io/3414/\n'
                                      '  ETRS89 (EPSG:4258) projection: http://epsg.io/4258/\n'
                                      '  ETRS89geo (EPSG:4936) projection: http://epsg.io/4936/\n')
        self.parser.add_argument('-output_projection', type=str, dest='output_projection', required=False,
                                 choices=['WGS84', 'WGS84geo', 'WGS84PM', 'EOV', 'EOVc', 'EOV2009', 'EOV2014', 'EOV2014fine', 'EOVp', 'SVY21', 'SVY21c', 'ETRS89',
                                          'ETRS89geo'],
                                 help='optional:  output format (default=EOVc, EOVp is not implemented (yet))\n'
                                      '  same as input_projection')
        self.parser.add_argument('-cores', type=int, dest='cores', required=False, default=1,
                                 help='optional:  cores (default=1)')
        self.parser.add_argument('-no_threads', dest='no_threads', required=False, default=False,
                                 help='optional:  do not use threads when cores = 1 (default=False)', action='store_true')
        self.parser.add_argument('-full_header_update', dest='full_header_update', required=False,
                                 help='optional:  Full header update - makes closing file slow (-full_header_update=on, nothing=off)',
                                 action='store_true')
        self.parser.add_argument('-separator', type=str, dest='separator', required=False,
                                 choices=[',', ' ', ';', '\t'],
                                 help='optional:  text separator for text based coordiante files (default=,)')
        self.parser.add_argument('-v', dest='verbose', required=False,
                                 help='optional:  verbose toggle (-v=on, nothing=off)', action='store_true')
        self.parser.add_argument('-version', action='version', version=self.parser.prog)

    def parse(self):
        self.args = self.parser.parse_args()

        ##defaults
        if self.args.verbose:
            self.args.verbose = ' -v'
        else:
            self.args.verbose = ''
        if self.args.input_format == None:
            self.args.input_format = 'las'
        if self.args.cores == None:
            self.args.cores = 1
        if self.args.input_projection == None:
            self.args.input_projection = 'WGS84geo'
        if self.args.output_projection == None:
            self.args.output_projection = 'EOVc'
        if self.args.separator == None:
            self.args.separator = ','

    # ---------PUBLIC METHODS--------------------
    def get_output(self):
        return self.args.output

    def get_input(self):
        return self.args.input

    def get_input_format(self):
        return self.args.input_format

    def get_input_projection(self):
        return self.args.input_projection

    def get_output_projection(self):
        return self.args.output_projection

    def get_verbose(self):
        return self.args.verbose

    def get_cores(self):
        return self.args.cores

    def get_no_threads(self):
        return self.args.no_threads

    def get_full_header_update(self):
        return self.args.full_header_update

    def get_separator(self):
        return self.args.separator
