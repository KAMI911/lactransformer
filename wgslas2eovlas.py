try:
    import textwrap
    import glob
    import os
    import logging
    import datetime
    import multiprocessing
    from lib import TransformerCommandLine, TransformerWorkflow, FileListWithProjection, Assignprojection
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)

script_path = __file__

header = textwrap.dedent('''WGS84 LAS 2 EOV LAS Converter''')

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
    filelist = FileListWithProjection.FileListWithProjection()
    filelist.create_list(lasconverterworkflow.get_input(),
                                                             lasconverterworkflow.get_output(),
                                                             Assignprojection.AssignProjection(
                                                                 lasconverterworkflow.get_input_projection(), script_path),
                                                             Assignprojection.AssignProjection(
                                                                 lasconverterworkflow.get_output_projection(), script_path),
                                                             lasconverterworkflow.get_input_format(),
                                                             lasconverterworkflow.get_full_header_update())
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
