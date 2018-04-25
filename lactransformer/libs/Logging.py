try:
    import traceback
    import logging
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    traceback.print_exc()
    exit(128)


def SetLogging(logfilename):
    # set up logging to file - see previous section for more details
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
