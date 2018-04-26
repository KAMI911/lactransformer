#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    import textwrap
    import logging
    import datetime
    import multiprocessing
    from libs import Logging, TransformerCommandLine, TransformerWorkflow, FileListWithProjection
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    exit(128)

script_path = __file__

script_header = textwrap.dedent('''LAS & Co Transformer''')


def main():
    logfilename = 'lactransformer_{0}.log'.format(datetime.datetime.today().strftime('%Y%m%d_%H%M%S'))
    Logging.SetLogging(logfilename)
    logging.info(script_header)

    lasconverterworkflow = TransformerCommandLine.TransformerCommandLine()
    lasconverterworkflow.parse()
    # File/Directory handler
    cores = lasconverterworkflow.cores

    results = []
    filelist = FileListWithProjection.FileListWithProjection()
    filelist.create_list(lasconverterworkflow.input,
                         lasconverterworkflow.output,
                         lasconverterworkflow.input_projection,
                         lasconverterworkflow.output_projection,
                         lasconverterworkflow.input_format,
                         lasconverterworkflow.full_header_update, lasconverterworkflow.separator)
    no_threads = lasconverterworkflow.no_threads
    del lasconverterworkflow
    file_queue = filelist.filelist

    # If we got one file, start only one process
    if filelist.isdir is False:
        cores = 1
    # Do not use threads when only use one core and disable threads
    # Probably this is related to https://github.com/grantbrown/laspy/issues/32
    if cores == 1 and no_threads is True:
        logging.info('Do not use threads.')
        for lst in file_queue:
            TransformerWorkflow.Transformer(lst)
    # Generally we use this to process transfromration
    else:
        logging.info('Using threads on {0} cores.'.format(cores))
        pool = multiprocessing.Pool(processes=cores)
        results.append(pool.map_async(TransformerWorkflow.Transformer, file_queue))
        pool.close()
        pool.join()
    del file_queue
    logging.info('Finished, exiting and go home ...')

if __name__ == '__main__':
    main()
