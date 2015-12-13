try:
    import textwrap
    import glob
    import os
    import logging
    import datetime
    import multiprocessing
    from libs import Logging, TransformerCommandLine, TransformerWorkflow, FileListWithProjection
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)

script_path = __file__

header = textwrap.dedent('''LAS & Co Transformer''')


def main():
    logfilename = 'lactransformer_' + datetime.datetime.today().strftime('%Y%m%d_%H%M%S') + '.log'
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
    file_queue = filelist.get_filelist()

    # If we got one file, start only one process
    if filelist.get_isdir() is False:
        cores = 1
    if cores != 1:
        pool = multiprocessing.Pool(processes=cores)
        results.append(pool.map_async(TransformerWorkflow.Transformer, file_queue))
        pool.close()
        pool.join()
    else:
        for d in file_queue:
            TransformerWorkflow.Transformer(d)

    logging.info('Finished, exiting and go home ...')


if __name__ == '__main__':
    main()
