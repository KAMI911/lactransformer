try:
    import traceback
    import argparse
    import textwrap
    import glob
    import os
    import logging
    import datetime
    import multiprocessing
    from .libs import LasPyConverter
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)

script_path = __file__

header = textwrap.dedent('''LAS Diff''')


class LasPyParameters:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='lasdiff',
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              description='',
                                              epilog=textwrap.dedent('''
        example:
            '''))
        self.parser.add_argument('-i', type=str, dest='input', required=True,
                                 help='required:  input file or folder')
        self.parser.add_argument('-o', type=str, dest='output', required=True,
                                 help='required:  output file or folder')
        self.parser.add_argument('-input_format', type=str, dest='input_format', required=False,
                                 choices=['las', 'laz'],
                                 help='optional:  input format (default=las)')
        self.parser.add_argument('-cores', type=int, dest='cores', required=False, default=1,
                                 help='optional:  cores (default=1)')
        self.parser.add_argument('-v', dest='verbose', required=False,
                                 help='optional:  verbose toggle (-v=on, nothing=off)',
                                 action='store_true')
        self.parser.add_argument('-version', action='version', version=self.parser.prog)

    def parse(self):
        self.args = self.parser.parse_args()
        self.args.verbose = ' -v' if self.args.verbose else ''
        if self.args.input_format is None:
            self.args.input_format = 'las'
        if self.args.cores is None:
            self.args.cores = 1

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
    source_file = parameters[0]
    destination_file = parameters[1]
    current = multiprocessing.current_process()
    proc_name = current.name

    logging.info(f'[{proc_name}] Starting ...')
    logging.info(f'[{proc_name}] Creating diff of {source_file} LAS PointCloud file'
                 f' and {destination_file} LAS PointCloud file ...')
    lasFiles = LasPyConverter.LasPyCompare(source_file, destination_file)
    logging.info(f'[{proc_name}] Opening {source_file} LAS PointCloud file'
                 f' and {destination_file} LAS PointCloud file ...')
    lasFiles.OpenReadOnly()
    logging.info(f'[{proc_name}] Comparing {source_file} LAS PointCloud file'
                 f' and {destination_file} LAS PointCloud file ...')
    lasFiles.ComparePointCloud()
    logging.info(f'[{proc_name}] Closing {destination_file} LAS PointCloud.')
    lasFiles.Close()
    logging.info(f'[{proc_name}] {destination_file} LAS PointCloud has closed.')
    return 0


def SetLogging(logfilename):
    logging.basicConfig(
        filename=logfilename,
        filemode='w',
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S',
        level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def main():
    logfilename = 'lasdiff_' + datetime.datetime.today().strftime('%Y%m%d_%H%M%S') + '.log'
    SetLogging(logfilename)
    logging.info(header)

    lasconverterworkflow = LasPyParameters()
    lasconverterworkflow.parse()

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
                logging.info(f'Adding {workfile} to the queue.')
                doing.append([workfile, os.path.join(outputpath, os.path.basename(workfile))])
            else:
                logging.info(f'The {workfile} is not a file, or pair of comparable files. Skipping.')
    elif os.path.isfile(inputfiles):
        inputisdir = False
        workfile = inputfiles
        if os.path.basename(outputfiles) != '':
            doing.append([workfile, outputfiles])
        else:
            doing.append([workfile, os.path.join(outputpath, os.path.basename(workfile))])
        logging.info(f'Adding {workfile} to the queue.')
    else:
        logging.error(f'Cannot find input LAS PointCloud file: {inputfiles}')
        exit(1)

    if inputisdir is False:
        cores = 1

    if cores != 1:
        pool = multiprocessing.Pool(processes=cores)
        results = pool.map_async(DiffLas, doing)
        pool.close()
        pool.join()
        results.get()
    else:
        for d in doing:
            DiffLas(d)

    logging.info('Finished, exiting and go home ...')


if __name__ == '__main__':
    main()
