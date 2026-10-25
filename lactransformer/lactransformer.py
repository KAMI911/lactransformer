#!/usr/bin/python

try:
    import traceback
    import textwrap
    import logging
    import datetime
    import multiprocessing
    from . import __version__
    from .libs import Logging, TransformerCommandLine, TransformerWorkflow, FileListWithProjection
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)

script_path = __file__

script_header = textwrap.dedent(f'''LAS & Co Transformer {__version__}''')


def main():
    logfilename = f'lactransformer_{datetime.datetime.today().strftime("%Y%m%d_%H%M%S")}.log'
    Logging.SetLogging(logfilename)
    logging.info(script_header)

    lasconverterworkflow = TransformerCommandLine.TransformerCommandLine()
    lasconverterworkflow.parse()
    # File/Directory handler
    cores = lasconverterworkflow.cores

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
    # Generally we use this to process transformation
    else:
        logging.info(f'Using threads on {cores} cores.')
        pool = multiprocessing.Pool(processes=cores)
        result = pool.map_async(TransformerWorkflow.Transformer, file_queue)
        pool.close()
        pool.join()
        result.get()
    del file_queue
    logging.info('Finished, exiting and go home ...')


if __name__ == '__main__':
    main()
