try:
    import textwrap
    import glob
    import os
    import logging
    import datetime
    import multiprocessing
    from lib import TransformerCommandLine, TransformerWorkflow, FileListWithProjection
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)

script_path = __file__

header = textwrap.dedent('''WGS84 LAS 2 EOV LAS Converter''')


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
    logfilename = 'transformer_' + datetime.datetime.today().strftime('%Y%m%d_%H%M%S') + '.log'
    SetLogging(logfilename)
    logging.info(header)

    lasconverterworkflow = TransformerCommandLine.TransformerCommandLine()
    lasconverterworkflow.parse()

    # File/Directory handler
    cores = lasconverterworkflow.get_cores()

    file_queue = []
    results = []
    filelist = FileListWithProjection.FileListWithProjection(lasconverterworkflow.get_input(),
                                                             lasconverterworkflow.get_output(),
                                                             AssignProjection(
                                                                 lasconverterworkflow.get_input_projection()),
                                                             AssignProjection(
                                                                 lasconverterworkflow.get_output_projection()),
                                                             lasconverterworkflow.get_input_format())
    filelist.create_list()
    file_queue = filelist.get_filelist()

    # If we got one file, start only one process
    if filelist.get_isdir() is False:
        cores = 1

    if cores != 1:
        pool = multiprocessing.Pool(processes=cores)
        results = pool.map_async(TransformerWorkflow.Transformer, file_queue)
        pool.close()
        pool.join()
    else:
        for d in file_queue:
            TransformerWorkflow.Transformer(d)

    logging.info('Finished, exiting and go home ...')


if __name__ == '__main__':
    main()
