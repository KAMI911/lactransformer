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
        self.parser.add_argument('-input_format', type=str, dest='input_format', required=False, choices=['las', 'laz', 'txt'],
                                 help='optional:  input format (default=las, laz is not implemented (yet))')
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
    input_format= parameters[4]
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
            lasFiles = LasPyConverter.LasPyConverter(source_file, source_projection, destination_file, destination_projection)
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
        logging.info('[%s] Closing transformed %s LAS PointCloud.' % (proc_name, destination_file))
        lasFiles.Close()
        logging.info('[%s] Transformed %s LAS PointCloud has created.' % (proc_name, destination_file))
        return 0
    elif input_format == 'txt':

        logging.info(
            '[%s] Opening %s PointText file for converting to %s PointText file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, destination_file, source_projection, destination_projection))
        # Opening source LAS files for read and write
        try:
            txtFiles = TxtPyConverter.TxtPyConverter(source_file, source_projection, destination_file, destination_projection)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        # Opening destination LAS file for write and adding header of source LAS file
        # logging.info('[%s] Dumping LAS PointCloud information.' % (proc_name))
        # las.DumpHeaderFormat()
        # lasOut.DumpPointFormat()
        txtFiles.TransformPointText()
        logging.info('[%s] Closing transformed %s PointText.' % (proc_name, destination_file))
        txtFiles.Close()
        logging.info('[%s] Transformed %s PointText has created.' % (proc_name, destination_file))
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
    inputfiles = lasconverterworkflow.get_input()
    inputformat = lasconverterworkflow.get_input_format()
    outputfiles = lasconverterworkflow.get_output()
    outputpath = os.path.normpath(outputfiles)
    cores = lasconverterworkflow.get_cores()
    inputisdir = False

    inputprojection = lasconverterworkflow.get_input_projection()
    outputprojection = lasconverterworkflow.get_output_projection()

    inputprojectionstring = AssignProjection(inputprojection)
    outputprojectionstring = AssignProjection(outputprojection)

    doing = []
    results = []

    if os.path.isdir(inputfiles):
        inputisdir = True
        inputfiles = glob.glob(os.path.join(inputfiles, '*' + inputformat))
        if not os.path.exists(outputfiles):
            os.makedirs(outputfiles)
        for workfile in inputfiles:
            if os.path.isfile(workfile):
                logging.info('Adding %s to the queue.' % (workfile))
                doing.append([workfile, os.path.join(outputpath, os.path.basename(workfile)), inputprojectionstring,
                          outputprojectionstring, inputformat])
            else:
                logging.info('The %s is not file, skipping.' % (workfile))
    elif os.path.isfile(inputfiles):
        inputisdir = False
        workfile = inputfiles
        if os.path.basename(outputfiles) is not "":
            doing.append([workfile, outputfiles, inputprojectionstring, outputprojectionstring, inputformat])
        else:
            doing.append([workfile, os.path.join(outputpath, os.path.basename(workfile)), inputprojectionstring,
                          outputprojectionstring, inputformat])
        logging.info('Adding %s to the queue.' % (workfile))
    else:
        # Not a file, not a dir
        logging.error('Cannot found input LAS PointCloud file: %s' % (inputfiles))
        exit(10)

    # If we got one file, start only one process
    if inputisdir is False:
        cores = 1

    if cores != 1:
        pool = multiprocessing.Pool(processes=cores)
        results = pool.map_async(ConvertLas, doing)
        pool.close()
        pool.join()
    else:
        for d in doing:
            ConvertLas(d)

    logging.info('Finished, exiting and go home ...')


if __name__ == '__main__':
    main()
