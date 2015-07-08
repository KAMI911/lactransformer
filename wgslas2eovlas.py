try:
    import argparse
    import textwrap
    import glob
    import os
    import logging
    import datetime
    import multiprocessing
    from lib import LasPyConverter, TxtPyConverter
except Exception as err:
    print("Error import module: " + str(err))
    exit(128)

script_path = __file__

header = textwrap.dedent('''WGS84 LAS 2 EOV LAS Converter''')


class LasPyParameters:
    def __init__(self):
        # predefinied paths
        self.parser = argparse.ArgumentParser(prog="wgslas2eovlas",
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
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
                                 choices=['las', 'laz', 'txt', 'csv', 'iml'],
                                 help='optional:  input format (default=las, laz is not implemented (yet))'
                                      ' txt = Trajectory CSV file, iml = TerraPhoto Image List file, csv = Riegl Camera CSV file')
        self.parser.add_argument('-input_projection', type=str, dest='input_projection', required=False,
                                 choices=['WGS84', 'WGS84geo', 'EOV', 'EOVc', 'EOVp'],
                                 help='optional:  input format (default=WGS84geo, EOVp is not implemented (yet))')
        self.parser.add_argument('-output_projection', type=str, dest='output_projection', required=False,
                                 choices=['WGS84', 'WGS84geo', 'EOV', 'EOVc', 'EOVp'],
                                 help='optional:  input format (default=EOVc, EOVp is not implemented (yet))')
        self.parser.add_argument('-cores', type=int, dest='cores', required=False, default=1,
                                 help='optional:  cores (default=1)')
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


def ConvertLas(parameters):
    # Parse incoming parameters
    source_file = parameters[0]
    destination_file = parameters[1]
    source_projection = parameters[2]
    destination_projection = parameters[3]
    input_format = parameters[4]
    # Get name for this process
    current = multiprocessing.current_process()
    proc_name = current.name

    logging.info('[%s] Starting ...' % (proc_name))
    if input_format in ['las', 'laz']:
        logging.info(
            '[%s] Opening %s LAS PointCloud file for converting to %s LAS PointCloud file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, destination_file, source_projection, destination_projection))
        # Opening source LAS files for read and write
        try:
            lasFiles = LasPyConverter.LasPyConverter(source_file, source_projection, destination_file,
                                                     destination_projection)
            lasFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        # Opening destination LAS file for write and adding header of source LAS file
        # logging.info('[%s] Dumping LAS PointCloud information.' % (proc_name))
        # las.DumpHeaderFormat()
        # lasOut.DumpPointFormat()
        logging.info('[%s] Scaling LAS PointCloud.' % (proc_name))
        lasFiles.GetSourceScale()
        lasFiles.SetDestinationScale()
        logging.info('[%s] Transforming LAS PointCloud.' % (proc_name))
        lasFiles.TransformPointCloud()
        logging.info('[%s] Closing transformed %s LAS PointCloud file.' % (proc_name, destination_file))
        lasFiles.Close()
        logging.info('[%s] Transformed %s LAS PointCloud file has created.' % (proc_name, destination_file))
        return 0
    elif input_format == 'txt':

        logging.info(
            '[%s] Opening %s PointText file for converting to %s PointText file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, destination_file, source_projection, destination_projection))
        # Opening source LAS files for read and write
        try:
            txtFiles = TxtPyConverter.TxtPyConverter(source_file, source_projection, destination_file,
                                                     destination_projection)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        txtFiles.TransformPointText()
        logging.info('[%s] Closing transformed %s PointText file.' % (proc_name, destination_file))
        txtFiles.Close()
        logging.info('[%s] Transformed %s PointText file has created.' % (proc_name, destination_file))
        return 0
    elif input_format == 'iml':

        logging.info(
            '[%s] Opening %s TerraPhoto Image List file for converting to %s TerraPhoto Image List file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, destination_file, source_projection, destination_projection))
        # Opening source LAS files for read and write
        try:
            txtFiles = TxtPyConverter.TxtPyConverter(source_file, source_projection, destination_file,
                                                     destination_projection)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        txtFiles.TransformPointIML()
        logging.info('[%s] Closing transformed %s TerraPhoto Image List file.' % (proc_name, destination_file))
        txtFiles.Close()
        logging.info('[%s] Transformed %s TerraPhoto Image List file has created.' % (proc_name, destination_file))
        return 0
    elif input_format == 'csv':

        logging.info(
            '[%s] Opening %s Riegl Camera CSV file for converting to %s Riegl Camera CSV file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, destination_file, source_projection, destination_projection))
        # Opening source LAS files for read and write
        try:
            txtFiles = TxtPyConverter.TxtPyConverter(source_file, source_projection, destination_file,
                                                     destination_projection)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        txtFiles.TransformPointCSV()
        logging.info('[%s] Closing transformed %s Riegl Camera CSV file.' % (proc_name, destination_file))
        txtFiles.Close()
        logging.info('[%s] Transformed %s Riegl Camera CSV file has created.' % (proc_name, destination_file))
        return 0


def AssignProjection(projection):
    # Init does not work on Linux
    # WGS84 = Proj(init='EPSG:4326')
    # WGS84Geo = Proj(init='EPSG:4328')

    if projection == 'WGS84':
        projectionstring = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    elif projection == 'WGS84geo':
        projectionstring = '+proj=geocent +ellps=WGS84 +datum=WGS84 +no_defs'
    elif projection == 'EOV':
        projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs'
    elif projection == 'EOVc':
        nadgrids = os.path.join(os.path.dirname(script_path), 'grid', 'etrs2eov_notowgs.gsb')
        geoidgrids = os.path.join(os.path.dirname(script_path), 'grid', 'geoid_eht.gtx')
        if os.path.isfile(nadgrids) and os.path.isfile(geoidgrids):
            logging.info('Found all required grids ...')
            projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids + ' +geoidgrids=' + geoidgrids + ' +units=m +no_defs'
        else:
            logging.error('Cannot found %s and/or %s grids.' % (nadgrids, geoidgrids))
            exit(2)
    elif projection == 'EOVp':  # do not use
        nadgrids = os.path.join(os.path.dirname(script_path), 'grid', 'etrs2eov_notowgs.gsb')
        if os.path.isfile(nadgrids):
            logging.info('Found all required grids ...')
            projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids + ' +units=m +no_defs'
        else:
            logging.error('Cannot found %s grid.' % (nadgrids))
            exit(2)
    return projectionstring


class FileListWithProjection:
    def __init__(self, input_file_or_dir, output_file_or_dir, input_projection_string, output_projection_string,
                 file_format='las'):
        self.__input_isdir = False
        self.__file_and_projection = []
        self.__input_file_or_dir = input_file_or_dir
        self.__output_file_or_dir = output_file_or_dir
        self.__input_projection_string = input_projection_string
        self.__output_projection_string = output_projection_string
        self.__file_format = file_format
        self.__output_path = os.path.normpath(self.__output_file_or_dir)

    # ---------PUBLIC METHODS--------------------

    def create_list(self):
        # If the specified folder is directory read all the matching file
        if os.path.isdir(self.__input_file_or_dir):
            self.__input_isdir = True
            inputfiles = glob.glob(os.path.join(self.__input_file_or_dir, '*' + self.__file_format))
            if not os.path.exists(self.__output_file_or_dir):
                os.makedirs(self.__output_file_or_dir)
            for in_file in inputfiles:
                logging.info('Adding %s to the queue.' % (in_file))
                out_file = os.path.join(self.__output_path, os.path.basename(in_file))
                self.__file_and_projection.append([in_file, out_file, self.__input_projection_string,
                                                   self.__output_projection_string, self.__file_format])
        elif os.path.isfile(self.__input_file_or_dir):
            self.__input_isdir = False
            in_file = self.__input_file_or_dir
            if os.path.basename(self.__output_file_or_dir) is not "":
                self.__file_and_projection.append([in_file, self.__output_file_or_dir, self.__input_projection_string,
                                                   self.__output_projection_string, self.__file_format])
            else:
                out_file = os.path.join(self.__output_path, os.path.basename(in_file))
                self.__file_and_projection.append([in_file, out_file, self.__input_projection_string,
                                                   self.__output_projection_string, self.__file_format])
            logging.info('Adding %s to the queue.' % (in_file))
        else:
            # Not a file, not a dir
            logging.error('Cannot found input LAS PointCloud file: %s' % (self.__input_file_or_dir))
            exit(1)

    def get_filelist(self):
        return self.__file_and_projection

    def get_isdir(self):
        return self.__input_isdir


def SetLogging(logfilename):
    logging.basicConfig(
        filename=logfilename,
        filemode='w',
        format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S',
        level=logging.DEBUG)
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def main():
    logfilename = 'lastransform_' + datetime.datetime.today().strftime('%Y%m%d_%H%M%S') + '.log'
    SetLogging(logfilename)
    logging.info(header)

    lasconverterworkflow = LasPyParameters()
    lasconverterworkflow.parse()

    # File/Directory handler
    cores = lasconverterworkflow.get_cores()

    file_queue = []
    results = []
    filelist = FileListWithProjection(lasconverterworkflow.get_input(), lasconverterworkflow.get_output(),
                                      AssignProjection(lasconverterworkflow.get_input_projection()),
                                      AssignProjection(lasconverterworkflow.get_output_projection()),
                                      lasconverterworkflow.get_input_format())
    filelist.create_list()
    file_queue = filelist.get_filelist()

    # If we got one file, start only one process
    if filelist.get_isdir() is False:
        cores = 1

    if cores != 1:
        pool = multiprocessing.Pool(processes=cores)
        results = pool.map_async(ConvertLas, file_queue)
        pool.close()
        pool.join()
    else:
        for d in file_queue:
            ConvertLas(d)

    logging.info('Finished, exiting and go home ...')


if __name__ == '__main__':
    main()
