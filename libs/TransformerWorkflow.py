try:
    import logging
    import multiprocessing
    from libs import LasPyConverter, TxtPanPyConverter, FriendlyName
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
            '[%s] Opening %s %s file for converting to %s %s file ...' % (
                proc_name, source_file, input_format_name, destination_file, input_format_name))
        logging.info(
            '[%s] Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_projection, destination_projection))
        # Opening source LAS files for read and write
        try:
            lasFiles = LasPyConverter.LasPyConverter(
                source_file, source_projection, destination_file, destination_projection)
            lasFiles.Open()
        except Exception as err:
            logging.error('Cannot open files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(10)
        try:
            logging.info('[%s] Scaling %s.' % (proc_name, input_format_name))
            lasFiles.GetSourceScale()
            original, transformed = lasFiles.SetDestinationScale()
            logging.info('[%s] %s file original / transformed offset: %s %s %s / %s %s %s coordinates.' % (
                proc_name, input_format_name, original[0], original[1], original[2], transformed[0], transformed[1],
                transformed[2]))
            logging.info('[%s] Bounding box of original PointCloud min: %s max: %s.' % (
                proc_name, lasFiles.ReturnOriginalMin(), lasFiles.ReturnOriginalMax()))
            logging.info('[%s] Transforming %s.' % (proc_name, input_format_name))
            lasFiles.TransformPointCloud()
        except Exception as err:
            logging.error(
                'Cannot transform files form %s to %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(11)
        else:
            logging.info('[%s] Successfully transformed %s data for file: %s.' % (
                proc_name, input_format_name, destination_file))
            logging.info('[%s] Bounding box of transformed PointCloud min: %s max %s.' % (
                proc_name, lasFiles.ReturnTransformedMin(), lasFiles.ReturnTransformedMax()))
        try:
            logging.info('[%s] Closing transformed %s %s file.' % (proc_name, destination_file, input_format_name))
            lasFiles.Close(full_header_update)
        except Exception as err:
            logging.error('Cannot close files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[%s] Transformed %s %s file has created.' % (proc_name, destination_file, input_format_name))
            return 0
    elif input_format in ['txt', 'lastxt', 'iml', 'csv', 'pef']:
        logging.info(
            '[%s] Opening %s %s file for converting to %s %s file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, input_format_name, destination_file, input_format_name, source_projection,
                destination_projection))
        # Opening source Text pointcloud files for read and write
        try:
            txtFiles = TxtPanPyConverter.TxtPanPyConverter(source_file, source_projection, destination_file,
                                                           destination_projection, input_format, txt_separator)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        try:
            txtFiles.Transform()
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
