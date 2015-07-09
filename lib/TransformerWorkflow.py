try:
    import logging
    import multiprocessing
    from lib import LasPyConverter, TxtPyConverter
except Exception as err:
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
            logging.error('Cannot open file: %s.' % (str(err)))
            exit(10)
        # Opening destination LAS file for write and adding header of source LAS file
        # logging.info('[%s] Dumping LAS PointCloud information.' % (proc_name))
        # las.DumpHeaderFormat()
        # lasOut.DumpPointFormat()
        logging.info('[%s] Scaling LAS PointCloud.' % (proc_name))
        lasFiles.GetSourceScale()
        lasFiles.SetDestinationScale()
        logging.info('[%s] Transforming LAS PointCloud.' % (proc_name))
        lasFiles.TransformPointCloud()
        logging.info('[%s] Closing transformed %s LAS PointCloud file.' % (proc_name, destination_file))
        lasFiles.Close()
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
        txtFiles.TransformPointText()
        logging.info('[%s] Closing transformed %s PointText file.' % (proc_name, destination_file))
        txtFiles.Close()
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
        txtFiles.TransformPointIML()
        logging.info('[%s] Closing transformed %s TerraPhoto Image List file.' % (proc_name, destination_file))
        txtFiles.Close()
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
        txtFiles.TransformPointCSV()
        logging.info('[%s] Closing transformed %s Riegl Camera CSV file.' % (proc_name, destination_file))
        txtFiles.Close()
        logging.info('[%s] Transformed %s Riegl Camera CSV file has created.' % (proc_name, destination_file))
        return 0