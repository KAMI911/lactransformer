try:
    import traceback
    import logging
    import multiprocessing
    from . import LasPyConverter, TxtPanPyConverter, FriendlyName, AssignProjection
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
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
    logging.info('[{0}] Starting ...'.format(proc_name))
    if input_format in ['las', 'laz']:
        logging.info(
            '[{0}] Opening {1} {2} file for converting to {3} {4} file ...'.format(
                proc_name, source_file, input_format_name, destination_file, input_format_name))
        logging.info(
            '[{0}] Source projections is: "{1}", destination projection is: "{2}".'.format(
                proc_name, AssignProjection.AssignProjectionName(source_projection),
                AssignProjection.AssignProjectionName(destination_projection)))
        # Opening source LAS files for read and write
        try:
            lasFiles = LasPyConverter.LasPyConverter(
                source_file, source_projection, destination_file, destination_projection)
            lasFiles.Open()
        except ValueError as err:
            logging.error(
                'Cannot open files: {0} and {1}, error: {0}. Probably this type of errors (ValueError) caused by corrupt LAS PointCloud file.'.format(
                    source_file, destination_file, str(err)))
            traceback.print_exc()
            exit(10)
        except Exception as err:
            logging.error('Cannot open files: {0} and {1}, error: {2}.'.format(source_file, destination_file, str(err)))
            traceback.print_exc()
            exit(10)
        try:
            logging.info('[{0}] Scaling {1}.'.format(proc_name, input_format_name))
            lasFiles.GetSourceScale()
            original, transformed = lasFiles.SetDestinationScale()
            logging.info(
                '[{0}] {1} file original/transformed offset: [{2[0]:.3f}, {2[1]:.3f}, {2[2]:.3f}]/[{3[0]:.3f}, {3[1]:.3f}, {3[2]:.3f}] coordinates.'.format(
                    proc_name, input_format_name, original, transformed))
            original_min = lasFiles.ReturnOriginalMin()
            original_max = lasFiles.ReturnOriginalMax()
            logging.info(
                '[{0}] Bounding box of original PointCloud min: [{1[0]:.3f}, {1[1]:.3f}, {1[2]:.3f}] max: [{2[0]:.3f}, {2[1]:.3f}, {2[2]:.3f}].'.format(
                    proc_name, original_min, original_max))
            logging.info('[{0}] Transforming {1}.'.format(proc_name, input_format_name))
            lasFiles.TransformPointCloud()
        except Exception as err:
            logging.error(
                'Cannot transform files form {0} to {1}, error: {2}.'.format(source_file, destination_file, str(err)))
            traceback.print_exc()
            exit(11)
        else:
            logging.info('[{0}] Successfully transformed {1} data for file: {2}.'.format(
                proc_name, input_format_name, destination_file))
            transformed_min = lasFiles.ReturnTransformedMin()
            transformed_max = lasFiles.ReturnTransformedMax()
            logging.info(
                '[{0}] Bounding box of transformed PointCloud min: [{1[0]:.3f}, {1[1]:.3f}, {1[2]:.3f}] max: [{2[0]:.3f}, {2[1]:.3f}, {2[2]:.3f}].'.format(
                    proc_name, transformed_min, transformed_max))
        try:
            logging.info('[{0}] Closing transformed {1} {2} file.'.format(proc_name, destination_file, input_format_name))
            lasFiles.Close(full_header_update)
        except Exception as err:
            logging.error('Cannot close files: {0} and {1}, error: {2}.'.format(source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[{0}] Transformed {1} {2} file has created.'.format(proc_name, destination_file, input_format_name))
            return 0
    elif input_format in ['txt', 'lastxt', 'iml', 'csv', 'pef', 'strtxt', 'listtxt']:
        logging.info(
            '[{0}] Opening {1} {2} file for converting to {3} {4} file ... Source projections is: "{5}", destination projection is: "{6}".'.format(
                proc_name, source_file, input_format_name, destination_file, input_format_name, source_projection,
                destination_projection))
        # Opening source Text pointcloud files for read and write
        try:
            txtFiles = TxtPanPyConverter.TxtPanPyConverter(source_file, source_projection, destination_file,
                                                           destination_projection, input_format, txt_separator)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: {0}.'.format(str(err)))
            exit(10)
        try:
            txtFiles.Transform()
        except Exception as err:
            logging.error(
                'Cannot transform files form {0} to {1}, error: {2}.'.format(source_file, destination_file, str(err)))
            exit(11)
        else:
            logging.info(
                '[{0}] Successfully transformed {1} for file: {2}.'.format(proc_name, input_format_name, destination_file))
        try:
            logging.info('[{0}] Closing transformed {1} {2} file.'.format(proc_name, destination_file, input_format_name))
            txtFiles.Close()
        except Exception as err:
            logging.error('Cannot close files: {0} and {1}, error: {2}.'.format(source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[{0}] Transformed {1} {2} file has created.'.format(proc_name, destination_file, input_format_name))
            return 0
    else:
        logging.critical('Unknown -input_format parameter is specified: "{0}".'.format(input_format))
