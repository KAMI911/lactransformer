import argparse
import textwrap
import numpy as np
import glob
import shutil
import os
import logging
import datetime
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

        #optional parameters
        self.parser.add_argument('-input_format', type=str, dest='input_format', required=False, choices=['las', 'laz'],
                                 help='optional:  input format (default= laz)')
        self.parser.add_argument('-input_projection', type=str, dest='input_projection', required=False, choices=['WGS84', 'WGS84geo', 'EOV', 'EOVc', 'EOVp'],
                                 help='optional:  input format (default=wgs84geo, eovc and eovp arent inmpelemted)')
        self.parser.add_argument('-output_projection', type=str, dest='output_projection', required=False, choices=['WGS84', 'WGS84geo', 'EOV', 'EOVc', 'EOVp'],
                                 help='optional:  input format (default=eov, eovc and eovp arent inmpelemted)')
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
        if self.args.input_projection == None:
            self.args.input_projection = 'WGS84geo'
        if self.args.output_projection == None:
            self.args.output_projection = 'EOV'

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

def ConvertLas(workfile, sourceprojection, destinationprojection):
    logging.info('Opening %s file for converting...' % (workfile))
    las = LasPyConverter.LasPyConverter(workfile)
    las.Open()
    # las.DumpHeaderFormat()
    logging.info('Source projection is %s.' % (sourceprojection))
    las.SetSourceProjection(sourceprojection)
    logging.info('Destionation projection is %s.' % (destinationprojection))
    las.SetDestinationProjection(destinationprojection)
    logging.info('Dumping LAS pointcloud information.')
    las.DumpPointFormat()
    logging.info('Scaling LAS pointcloud.')
    las.ScaleDimension()
    logging.info('Closing transformed %s LAS pointcloud.' % (workfile))
    las.Close()
    logging.info('Transformed %s LAS pointcloud has created.' % (workfile))

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
    elif projection == 'EOVc': # do not use
        projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=grid\etrs2eov_notowgs.gsb +geoidgrids=grid\geoid_eht.gtx +units=m +no_defs'
    elif projection == 'EOVp': # do not use
        projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=grid\etrs2eov_notowgs.gsb +units=m +no_defs'
    return projectionstring

print(header)
timer = Timing.Timing()
lasconverterworkflow = LasPyParameters()
lasconverterworkflow.parse()

inputprojection = lasconverterworkflow.get_input_projection()
outputprojection = lasconverterworkflow.get_output_projection()
# File/Directory handler
inputfiles = lasconverterworkflow.get_input()
outputfiles = lasconverterworkflow.get_output()
inputisdir = False
outputisdir = False

logging.basicConfig(
    filename=outputfiles + '_' + datetime.datetime.today().strftime('%Y%m%d') + '_lastransform.log',
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

if os.path.isdir(inputfiles):
    inputisdir = True
    inputfiles = glob.glob(inputfiles)
elif os.path.isfile(inputfiles):
    inputisdir = False
    inputfiles = glob.glob(inputfiles)

inputprojectionstring = AssignProjection(inputprojection)
outputprojectionstring = AssignProjection(outputprojection)

for workfile in inputfiles:
    logging.info('Copy %s to %s' % (workfile, outputfiles))
    shutil.copyfile(workfile, outputfiles)
    logging.info('Converting: %s (%s) to: %s (%s)' % (workfile, inputprojection, outputfiles, outputprojection))
    print ('Converting: %s (%s) to: %s (%s)' % (workfile, inputprojection, outputfiles, outputprojection))
    ConvertLas(outputfiles, inputprojectionstring, outputprojectionstring)

