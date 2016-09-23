try:
    import textwrap
    import glob
    import os
    import logging
    import datetime
    import multiprocessing
    from libs import Logging, TransformerCommandLine, TransformerWorkflow, FileListWithProjection
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    exit(128)

script_path = __file__

header = textwrap.dedent('''LAS & Co Transformer''')


def main():
    logfilename = 'lactransformer_{0}.log'.format(datetime.datetime.today().strftime('%Y%m%d_%H%M%S'))
    Logging.SetLogging(logfilename)
    logging.info(header)

    lasconverterworkflow = TransformerCommandLine.TransformerCommandLine()
    lasconverterworkflow.parse()
    # File/Directory handler
    cores = lasconverterworkflow.get_cores()

    file_queue = []
    results = []
    filelist = FileListWithProjection.FileListWithProjection()
    filelist.create_list(lasconverterworkflow.get_input(),
                         lasconverterworkflow.get_output(),
                         lasconverterworkflow.get_input_projection(),
                         lasconverterworkflow.get_output_projection(),
                         lasconverterworkflow.get_input_format(),
                         lasconverterworkflow.get_full_header_update(), lasconverterworkflow.get_separator())
    no_threads = lasconverterworkflow.get_no_threads()
    del lasconverterworkflow
    file_queue = filelist.get_filelist()

    # If we got one file, start only one process
    if filelist.get_isdir() is False:
        cores = 1
    # Do not use threads when only use one core and disable threads
    # Probably this is related to https://github.com/grantbrown/laspy/issues/32
    if cores == 1 and no_threads == True:
        logging.info('Do not use threads.')
        for d in file_queue:
            TransformerWorkflow.Transformer(d)
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