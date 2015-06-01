import argparse
import textwrap
import glob
import shutil
import os
import logging
import datetime
from multiprocessing import Process, Manager, Queue

from lib import Timing, LasPyConverter

header = textwrap.dedent('''
WGS84 LAS 2 EOV LAS Converter''')


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
        self.parser.add_argument('-input_format', type=str, dest='input_format', required=False, choices=['las', 'laz'],
                                 help='optional:  input format (default= laz)')
        self.parser.add_argument('-input_projection', type=str, dest='input_projection', required=False,
                                 choices=['WGS84', 'WGS84geo', 'EOV', 'EOVc', 'EOVp'],
                                 help='optional:  input format (default=WGS84geo, EOVp is not inmpelemted (yet))')
        self.parser.add_argument('-output_projection', type=str, dest='output_projection', required=False,
                                 choices=['WGS84', 'WGS84geo', 'EOV', 'EOVc', 'EOVp'],
                                 help='optional:  input format (default=EOVc, EOVp is not inmpelemted (yet))')
        self.parser.add_argument('-cores', type=int, dest='cores', required=False, default=1,
                                 help='optional:  cores (default=1)')
        self.parser.add_argument('-v', dest='verbose', required=False,
                                 help='optional:  verbose toogle (-v=on, nothing=off)', action='store_true')
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


class ConvertEngine(Process):

    def __init__(self, filequeue, sourceprojection, destinationprojection):
        Process.__init__(self)
        self.filequeue = filequeue
        self.sourceprojection = sourceprojection
        self.destinationprojection = destinationprojection
        self.ConvertLas()

    def ConvertLas(self):
        proc_name = self.name
        print('Starting: %s process.' % (proc_name))
        while True:
            if self.filequeue.empty() is False:
                sourcefile, destinationfile = self.filequeue.get()
                print('%s Copy %s to %s' % (proc_name, sourcefile, destinationfile))
                logging.info('%s Copy %s to %s' % (proc_name, sourcefile, destinationfile))
                shutil.copyfile(sourcefile, destinationfile)
                logging.info('Opening %s LAS PointCloud file for converting...' % (destinationfile))
                las = LasPyConverter.LasPyConverter(destinationfile)
                las.Open()
                # las.DumpHeaderFormat()
                logging.info('Source projection is %s.' % (self.sourceprojection))
                las.SetSourceProjection(self.sourceprojection)
                logging.info('Destionation projection is %s.' % (self.destinationprojection))
                las.SetDestinationProjection(self.destinationprojection)
                logging.info('Dumping LAS PointCloud information.')
                las.DumpPointFormat()
                logging.info('Scaling LAS PointCloud.')
                las.ScaleDimension()
                logging.info('Reading LAS PointCloud.')
                las.ReadPointCloudCoordsOnly()
                logging.info('Transforming LAS PointCloud.')
                las.TransformPointCloud()
                print('%s Closing transformed %s LAS PointCloud.' % (proc_name, destinationfile))
                logging.info('%s Closing transformed %s LAS PointCloud.' % (proc_name, destinationfile))
                las.Close()
                logging.info('Transformed %s LAS PointCloud has created.' % (destinationfile))
            else:
                break
        print('Exiting: %s process.' % (proc_name))
        return


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
        projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=grid\etrs2eov_notowgs.gsb +geoidgrids=grid\geoid_eht.gtx +units=m +no_defs'
    elif projection == 'EOVp':  # do not use
        projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=grid\etrs2eov_notowgs.gsb +units=m +no_defs'
    return projectionstring


def main():
    print(header)
    timer = Timing.Timing()
    lasconverterworkflow = LasPyParameters()
    lasconverterworkflow.parse()

    inputprojection = lasconverterworkflow.get_input_projection()
    outputprojection = lasconverterworkflow.get_output_projection()
    # File/Directory handler
    inputfiles = lasconverterworkflow.get_input()
    inputformat = lasconverterworkflow.get_input_format()
    outputfiles = lasconverterworkflow.get_output()
    outputpath = os.path.normpath(outputfiles)
    cores = lasconverterworkflow.get_cores()
    inputisdir = False

    filequeue = Queue()

    if os.path.isdir(inputfiles):
        inputisdir = True
        inputfiles = glob.glob(inputfiles + '\*' + inputformat)
        if not os.path.exists(outputfiles):
            os.makedirs(outputfiles)
        for workfile in inputfiles:
            filequeue.put([workfile, outputpath + '\\' + os.path.basename(workfile)])
        filename = outputpath + '\\lastransform_' + datetime.datetime.today().strftime('%Y%m%d') + '_batch.log',
    elif os.path.isfile(inputfiles):
        inputisdir = False
        workfile = inputfiles
        if os.path.basename(outputfiles) is not "":
            filequeue.put([workfile, outputfiles])
        else:
            filequeue.put([workfile, outputpath + '\\' + os.path.basename(workfile)])
        filename = outputpath + '\\lastransform_' + datetime.datetime.today().strftime('%Y%m%d') + '.log',

    if inputisdir is False:
        cores = 1

    logging.basicConfig(
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

    inputprojectionstring = AssignProjection(inputprojection)
    outputprojectionstring = AssignProjection(outputprojection)

    for p in range(cores):
        proc = Process(target = ConvertEngine, args=(filequeue, inputprojectionstring, outputprojectionstring))
        proc.daemon = True
        proc.start()
    proc.join()

if __name__ == '__main__':
    main()