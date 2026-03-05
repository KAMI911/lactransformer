try:
    import traceback
    import logging
    import multiprocessing
    from . import LasPyConverter, TxtPanPyConverter, FriendlyName, AssignProjection
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
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
    logging.info(f'[{proc_name}] Starting ...')
    if input_format in ['las', 'laz']:
        logging.info(
            f'[{proc_name}] Opening {source_file} {input_format_name}'
            f' ({AssignProjection.AssignProjectionName(source_projection)}) file'
            f' for converting to {destination_file} {input_format_name}'
            f' ({AssignProjection.AssignProjectionName(destination_projection)}) file ...')
        # Opening source LAS files for read and write
        try:
            lasFiles = LasPyConverter.LasPyConverter(
                source_file, source_projection, destination_file, destination_projection, proc_name)
            lasFiles.Open()
        except ValueError as err:
            logging.error(
                f'Cannot open files: {source_file} and {destination_file}, error: {err}.'
                ' Probably this type of errors (ValueError) caused by corrupt LAS PointCloud file.')
            traceback.print_exc()
            raise
        except Exception as err:
            logging.error(f'Cannot open files: {source_file} and {destination_file}, error: {err}.')
            traceback.print_exc()
            raise
        try:
            logging.info(f'[{proc_name}] Scaling {input_format_name}.')
            lasFiles.GetSourceScale()
            original, transformed = lasFiles.SetDestinationScale()
            logging.info(
                f'[{proc_name}] {input_format_name} file original/transformed offset:'
                f' [{original[0]:.3f}, {original[1]:.3f}, {original[2]:.3f}]/'
                f'[{transformed[0]:.3f}, {transformed[1]:.3f}, {transformed[2]:.3f}] coordinates.')
            original_min = lasFiles.ReturnOriginalMin()
            original_max = lasFiles.ReturnOriginalMax()
            logging.info(
                f'[{proc_name}] Bounding box of original PointCloud'
                f' min: [{original_min[0]:.3f}, {original_min[1]:.3f}, {original_min[2]:.3f}]'
                f' max: [{original_max[0]:.3f}, {original_max[1]:.3f}, {original_max[2]:.3f}].')
            logging.info(f'[{proc_name}] Transforming {input_format_name}.')
            lasFiles.TransformPointCloud()
        except Exception as err:
            logging.error(
                f'Cannot transform files from {source_file} to {destination_file}, error: {err}.')
            traceback.print_exc()
            raise
        else:
            logging.info(
                f'[{proc_name}] Successfully transformed {input_format_name} data for file: {destination_file}.')
            transformed_min = lasFiles.ReturnTransformedMin()
            transformed_max = lasFiles.ReturnTransformedMax()
            logging.info(
                f'[{proc_name}] Bounding box of transformed PointCloud'
                f' min: [{transformed_min[0]:.3f}, {transformed_min[1]:.3f}, {transformed_min[2]:.3f}]'
                f' max: [{transformed_max[0]:.3f}, {transformed_max[1]:.3f}, {transformed_max[2]:.3f}].')
        try:
            logging.info(
                f'[{proc_name}] Closing transformed {destination_file} {input_format_name} file.')
            lasFiles.Close(full_header_update)
        except Exception as err:
            logging.error(
                f'Cannot close files: {source_file} and {destination_file}, error: {err}.')
            raise
        else:
            logging.info(
                f'[{proc_name}] Transformed {destination_file} {input_format_name} file has been created.')
            return destination_file
    elif input_format in ['txt', 'lastxt', 'iml', 'csv', 'pef', 'strtxt', 'listtxt']:
        logging.info(
            f'[{proc_name}] Opening {source_file} {input_format_name} ({source_projection})'
            f' file for converting to {destination_file} {input_format_name}'
            f' ({destination_projection}) file ...')
        # Opening source Text pointcloud files for read and write
        try:
            txtFiles = TxtPanPyConverter.TxtPanPyConverter(source_file, source_projection, destination_file,
                                                           destination_projection, input_format, txt_separator, proc_name)
            txtFiles.Open()
        except Exception as err:
            logging.error(f'Cannot open file: {err}.')
            raise
        try:
            txtFiles.Transform()
        except Exception as err:
            logging.error(
                f'Cannot transform files from {source_file} to {destination_file}, error: {err}.')
            raise
        else:
            logging.info(
                f'[{proc_name}] Successfully transformed {input_format_name} for file: {destination_file}.')
        try:
            logging.info(
                f'[{proc_name}] Closing transformed {destination_file} {input_format_name} file.')
            txtFiles.Close()
        except Exception as err:
            logging.error(
                f'Cannot close files: {source_file} and {destination_file}, error: {err}.')
            raise
        else:
            logging.info(
                f'[{proc_name}] Transformed {destination_file} {input_format_name} file has been created.')
            return destination_file
    else:
        logging.critical(f'Unknown -input_format parameter is specified: "{input_format}".')
