try:
    import logging
    import multiprocessing
    from lib import LasPyConverter, TxtPyConverter, FriendlyName
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)


def Transformer(parameters):
    # Parse incoming parameters
    source_file = parameters[0]
    destination_file = parameters[1]
    source_projection = parameters[2]
    destination_projection = parameters[3]
    input_format = parameters[4]
    full_header_update = parameters[5]
    txt_separator = parameters[6]
    # Get name for this process
    current = multiprocessing.current_process()
    proc_name = current.name
    # Define friendly name of input formats
    input_format_name = FriendlyName.FriendlyName(input_format)
    logging.info('[%s] Starting ...' % (proc_name))
    if input_format in ['las', 'laz']:
        logging.info(
            '[%s] Opening %s %s file for converting to %s %s file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, input_format_name, destination_file, input_format_name, source_projection,
                destination_projection))
        # Opening source LAS files for read and write
        try:
            lasFiles = LasPyConverter.LasPyConverter(source_file, source_projection, destination_file,
                                                     destination_projection)
            lasFiles.Open()
        except Exception as err:
            logging.error('Cannot open files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(10)
        try:
            logging.info('[%s] Scaling %s.' % (proc_name, input_format_name))
            lasFiles.GetSourceScale()
            trX, trY, trZ = lasFiles.SetDestinationScale()
            logging.info('[%s] %s file transformed offset: %s %s %s' % (proc_name, input_format_name, trX, trY, trZ))
            logging.info('[%s] Transforming %s.' % (proc_name, input_format_name))
            lasFiles.TransformPointCloud()
        except Exception as err:
            logging.error(
                'Cannot transform files form %s to %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(11)
        else:
            logging.info(
                '[%s] Successfully transformed %s data for file: %s.' % (
                    proc_name, input_format_name, destination_file))
        try:
            logging.info('[%s] Closing transformed %s %s file.' % (proc_name, destination_file, input_format_name))
            lasFiles.Close(full_header_update)
        except Exception as err:
            logging.error('Cannot close files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[%s] Transformed %s %s file has created.' % (proc_name, destination_file, input_format_name))
            return 0

    elif input_format in ['txt', 'lastxt', 'iml', 'csv']:
        logging.info(
            '[%s] Opening %s %s file for converting to %s %s file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, input_format_name, destination_file, input_format_name, source_projection,
                destination_projection))
        # Opening source LAS files for read and write
        try:
            if input_format in ['txt', 'lastxt']:
                txtFiles = TxtPyConverter.TxtPyConverter(source_file, source_projection, destination_file,
                                                         destination_projection, txt_separator)
            if input_format in ['iml', 'csv']:
                txtFiles = TxtPyConverter.TxtPyConverter(source_file, source_projection, destination_file,
                                                         destination_projection)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        try:
            if input_format == 'txt':
                txtFiles.TransformPointText()
            elif input_format == 'lastxt':
                txtFiles.TransformLASText()
            elif input_format == 'iml':
                txtFiles.TransformPointIML()
            elif input_format == 'csv':
                txtFiles.TransformPointCSV()
        except Exception as err:
            logging.error(
                'Cannot transform files form %s to %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(11)
        else:
            logging.info(
                '[%s] Successfully transformed %s for file: %s.' % (proc_name, input_format_name, destination_file))
        try:
            logging.info('[%s] Closing transformed %s %s file.' % (proc_name, destination_file, input_format_name))
            txtFiles.Close()
        except Exception as err:
            logging.error('Cannot close files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[%s] Transformed %s %s file has created.' % (proc_name, destination_file, input_format_name))
            return 0
