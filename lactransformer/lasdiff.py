try:
    import traceback
    import argparse
    import textwrap
    import glob
    import os
    import logging
    import datetime
    import multiprocessing
    from libs import LasPyConverter
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    traceback.print_exc()
    exit(128)
script_path = __file__

header = textwrap.dedent('''LAS Diff''')


class LasPyParameters:
    def __init__(self):
        # predefinied paths
        self.parser = argparse.ArgumentParser(prog="lasdiff",
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
        self.parser.add_argument('-input_format', type=str, dest='input_format', required=False, choices=['las', 'laz'],
                                 help='optional:  input format (default=las, laz is not implemented (yet))')
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

    # ---------PUBLIC METHODS--------------------
    def get_output(self):
        return self.args.output

    def get_input(self):
        return self.args.input

    def get_input_format(self):
        return self.args.input_format

    def get_verbose(self):
        return self.args.verbose

    def get_cores(self):
        return self.args.cores


def DiffLas(parameters):
    # Parse incoming parameters
    source_file = parameters[0]
    destination_file = parameters[1]
    # Get name for this process
    current = multiprocessing.current_proces()
    proc_name = current.name

    logging.info('[%s] Starting ...' % (proc_name))
    logging.info(
        '[%s] Creating diff of %s LAS PointCloud file and %s LAS PointCloud file ...' % (
            proc_name, source_file, destination_file))
    # Opening source LAS files for read and write
    lasFiles = LasPyConverter.LasPyCompare(source_file, destination_file)
    # Opening destination LAS file
    logging.info('[%s] Opening %s LAS PointCloud file and %s LAS PointCloud file ...' % (
        proc_name, source_file, destination_file))
    lasFiles.OpenReanOnly()
    logging.info('[%s] Comparing %s LAS PointCloud file and %s LAS PointCloud file ...' % (
        proc_name, source_file, destination_file))
    lasFiles.ComparePointCloud()
    logging.info('[%s] Closing %s LAS PointCloud.' % (proc_name, destination_file))
    lasFiles.Close()
    logging.info('[%s] %s LAS PointCloud has closed.' % (proc_name, destination_file))
    return 0


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
    logfilename = 'lasdiff_' + datetime.datetime.today().strftime('%Y%m%d_%H%M%S') + '.log'
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

    doing = []

    if os.path.isdir(inputfiles):
        inputisdir = True
        inputfiles = glob.glob(os.path.join(inputfiles, '*' + inputformat))
        if not os.path.exists(outputfiles):
            os.makedirs(outputfiles)
        for workfile in inputfiles:
            if os.path.isfile(workfile) and os.path.isfile(os.path.join(outputpath, os.path.basename(workfile))):
                logging.info('Adding %s to the queue.' % (workfile))
                doing.append([workfile, os.path.join(outputpath, os.path.basename(workfile))])
            else:
                logging.info('The %s is not file, or pair of comparable files. Skipping.' % (workfile))
    elif os.path.isfile(inputfiles):
        inputisdir = False
        workfile = inputfiles
        if os.path.basename(outputfiles) is not "":
            doing.append([workfile, outputfiles])
        else:
            doing.append([workfile, os.path.join(outputpath, os.path.basename(workfile))])
        logging.info('Adding %s to the queue.' % (workfile))
    else:
        # Not a file, not a dir
        logging.error('Cannot found input LAS PointCloud file: %s' % (inputfiles))
        exit(1)

    # If we got one file, start only one process
    if inputisdir is False:
        cores = 1

    if cores != 1:
        pool = multiprocessing.Pool(processes=cores)
        results = pool.map_async(DiffLas, doing)
        pool.close()
        pool.join()
    else:
        for d in doing:
            DiffLas(d)

    logging.info('Finished, exiting and go home ...')


if __name__ == '__main__':
    main()
