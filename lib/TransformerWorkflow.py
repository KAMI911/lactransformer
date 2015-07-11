try:
    import logging
    import multiprocessing
    from lib import LasPyConverter, TxtPyConverter
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
    # Get name for this process
    current = multiprocessing.current_process()
    proc_name = current.name

    logging.info('[%s] Starting ...' % (proc_name))
    if input_format in ['las', 'laz']:
        logging.info(
            '[%s] Opening %s LAS PointCloud file for converting to %s LAS PointCloud file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, destination_file, source_projection, destination_projection))
        # Opening source LAS files for read and write
        try:
            lasFiles = LasPyConverter.LasPyConverter(source_file, source_projection, destination_file,
                                                     destination_projection)
            lasFiles.Open()
        except Exception as err:
            logging.error('Cannot open files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(10)
        try:
            logging.info('[%s] Scaling LAS PointCloud.' % (proc_name))
            lasFiles.GetSourceScale()
            trX, trY, trZ = lasFiles.SetDestinationScale()
            logging.info('[%s] LAS PointCloud file transformed offset: %s %s %s' % (proc_name, trX, trY, trZ))
            logging.info('[%s] Transforming LAS PointCloud.' % (proc_name))
            lasFiles.TransformPointCloud()
        except Exception as err:
            logging.error('Cannot transform files form %s to %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(11)
        else:
            logging.info('[%s] Successfully transformed LAS PointCloud data for file: %s.' % (proc_name, destination_file))
        try:
            logging.info('[%s] Closing transformed %s LAS PointCloud file.' % (proc_name, destination_file))
            lasFiles.Close()
        except Exception as err:
            logging.error('Cannot close files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[%s] Transformed %s LAS PointCloud file has created.' % (proc_name, destination_file))
            return 0

    elif input_format == 'txt':
        logging.info(
            '[%s] Opening %s PointText file for converting to %s PointText file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, destination_file, source_projection, destination_projection))
        # Opening source LAS files for read and write
        try:
            txtFiles = TxtPyConverter.TxtPyConverter(source_file, source_projection, destination_file,
                                                     destination_projection)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        try:
            txtFiles.TransformPointText()
        except Exception as err:
            logging.error('Cannot transform files form %s to %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(11)
        else:
            logging.info('[%s] Successfully transformed PointText data for file: %s.' % (proc_name, destination_file))
        try:
            logging.info('[%s] Closing transformed %s PointText file.' % (proc_name, destination_file))
            txtFiles.Close()
        except Exception as err:
            logging.error('Cannot close files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[%s] Transformed %s PointText file has created.' % (proc_name, destination_file))
            return 0

    elif input_format == 'iml':

        logging.info(
            '[%s] Opening %s TerraPhoto Image List file for converting to %s TerraPhoto Image List file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, destination_file, source_projection, destination_projection))
        # Opening source LAS files for read and write
        try:
            txtFiles = TxtPyConverter.TxtPyConverter(source_file, source_projection, destination_file,
                                                     destination_projection)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        try:
            txtFiles.TransformPointIML()
        except Exception as err:
            logging.error('Cannot transform files form %s to %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(11)
        else:
            logging.info('[%s] Successfully transformed PointText data for file: %s.' % (proc_name, destination_file))
        try:
            logging.info('[%s] Closing transformed %s TerraPhoto Image List file.' % (proc_name, destination_file))
            txtFiles.Close()
        except Exception as err:
            logging.error('Cannot close files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[%s] Transformed %s TerraPhoto Image List file has created.' % (proc_name, destination_file))
            return 0

    elif input_format == 'csv':

        logging.info(
            '[%s] Opening %s Riegl Camera CSV file for converting to %s Riegl Camera CSV file ... Source projections is: "%s", destination projection is: "%s".' % (
                proc_name, source_file, destination_file, source_projection, destination_projection))
        # Opening source LAS files for read and write
        try:
            txtFiles = TxtPyConverter.TxtPyConverter(source_file, source_projection, destination_file,
                                                     destination_projection)
            txtFiles.Open()
        except Exception as err:
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        try:
            txtFiles.TransformPointCSV()
        except Exception as err:
            logging.error('Cannot transform files form %s to %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(11)
        else:
            logging.info('[%s] Successfully transformed  Riegl Camera CSV data for file: %s.' % (proc_name, destination_file))
        try:
            logging.info('[%s] Closing transformed %s Riegl Camera CSV file.' % (proc_name, destination_file))
            txtFiles.Close()
        except Exception as err:
            logging.error('Cannot close files: %s and %s, error: %s.' % (source_file, destination_file, str(err)))
            exit(12)
        else:
            logging.info('[%s] Transformed %s Riegl Camera CSV file has created.' % (proc_name, destination_file))
            return 0