try:
    import traceback
    import argparse
    import textwrap
    from .. import __version__
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)


class TransformerCommandLine:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='lactransformer',
                                              formatter_class=argparse.RawTextHelpFormatter,
                                              description='',
                                              epilog=textwrap.dedent('''
        example:
            '''))
        # required parameters
        self.parser.add_argument('-i', type=str, dest='input', required=True,
                                 help='required:  input file or folder')
        self.parser.add_argument('-o', type=str, dest='output', required=True,
                                 help='required:  output file or folder')

        # optional parameters
        self.parser.add_argument('-input_format', type=str, dest='input_format', required=False,
                                 default='las',
                                 choices=['las', 'laz', 'txt', 'lastxt', 'csv', 'iml', 'pef', 'strtxt', 'listtxt'],
                                 help='optional:  input format (default=las)\n'
                                      '  las     = LAS PointCloud\n'
                                      '  laz     = LAZ (compressed) PointCloud\n'
                                      '  txt     = Trajectory CSV file\n'
                                      '  lastxt  = PointText\n'
                                      '  csv     = Riegl Camera CSV file\n'
                                      '  iml     = TerraPhoto Image List file\n'
                                      '  pef     = PEF file\n'
                                      '  strtxt  = String PointText\n'
                                      '  listtxt = List PointText\n')
        self.parser.add_argument('-input_projection', type=str, dest='input_projection', required=False,
                                 default='WGS84geo',
                                 choices=['WGS84', 'WGS84geo', 'WGS84PM', 'EOV', 'EOVc', 'EOV2009', 'EOV2014',
                                          'EOV2014fine', 'EOVp', 'SVY21', 'SVY21c', 'ETRS89', 'ETRS89geo'],
                                 help='optional:  input projection (default=WGS84geo)\n'
                                      '  WGS84        (EPSG:4326)  geographic\n'
                                      '  WGS84geo     (EPSG:4978)  geocentric\n'
                                      '  WGS84PM      (EPSG:3857)  Pseudo-Mercator\n'
                                      '  EOV          (EPSG:23700) Hungarian national grid\n'
                                      '  EOVc         (EPSG:23700) EOV with 2014 grid correction\n'
                                      '  EOV2009      (EPSG:23700) EOV with 2009 grid correction\n'
                                      '  EOV2014      (EPSG:23700) EOV with 2014 grid correction (2x2 km)\n'
                                      '  EOV2014fine  (EPSG:23700) EOV with 2014 grid correction'
                                      ' (1x1 km, experimental)\n'
                                      '  SVY21        (EPSG:3414)  Singapore\n'
                                      '  SVY21c       (EPSG:3414)  SVY21 with correction\n'
                                      '  ETRS89       (EPSG:4258)  geographic\n'
                                      '  ETRS89geo    (EPSG:4936)  geocentric\n')
        self.parser.add_argument('-output_projection', type=str, dest='output_projection', required=False,
                                 default='EOVc',
                                 choices=['WGS84', 'WGS84geo', 'WGS84PM', 'EOV', 'EOVc', 'EOV2009', 'EOV2014',
                                          'EOV2014fine', 'EOVp', 'SVY21', 'SVY21c', 'ETRS89', 'ETRS89geo'],
                                 help='optional:  output projection (default=EOVc, same choices as input_projection)')
        self.parser.add_argument('-cores', type=int, dest='cores', required=False, default=1,
                                 help='optional:  number of CPU cores to use (default=1)')
        self.parser.add_argument('-no_threads', dest='no_threads', required=False, default=False,
                                 help='optional:  disable threading when cores=1 (default=False)',
                                 action='store_true')
        self.parser.add_argument('-full_header_update', dest='full_header_update', required=False,
                                 help='optional:  full LAS header update on close (slower)',
                                 action='store_true')
        self.parser.add_argument('-separator', type=str, dest='separator', required=False,
                                 default=',',
                                 choices=[',', ' ', ';', '\t'],
                                 help='optional:  column separator for text files (default=,)')
        self.parser.add_argument('-v', dest='verbose', required=False,
                                 help='optional:  verbose output',
                                 action='store_true')
        self.parser.add_argument('-version', action='version', version=f'%(prog)s {__version__}')

    def parse(self):
        self.args = self.parser.parse_args()
        self.args.verbose = ' -v' if self.args.verbose else ''

    @property
    def output(self):
        return self.args.output

    @property
    def input(self):
        return self.args.input

    @property
    def input_format(self):
        return self.args.input_format

    @property
    def input_projection(self):
        return self.args.input_projection

    @property
    def output_projection(self):
        return self.args.output_projection

    @property
    def verbose(self):
        return self.args.verbose

    @property
    def cores(self):
        return self.args.cores

    @property
    def no_threads(self):
        return self.args.no_threads

    @property
    def full_header_update(self):
        return self.args.full_header_update

    @property
    def separator(self):
        return self.args.separator
