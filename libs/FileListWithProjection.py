try:
    import os
    import logging
    import glob
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)


class FileListWithProjection:
    def __init__(self):
        self.__input_isdir = False
        self.__file_and_projection = []

    # ---------PUBLIC METHODS--------------------

    def create_list(self, input_file_or_dir, output_file_or_dir, input_projection, output_projection,
                    file_format='las', full_header_update=False, txt_separator=','):
        self.__input_file_or_dir = input_file_or_dir
        self.__output_file_or_dir = output_file_or_dir
        self.__input_projection = input_projection
        self.__output_projection = output_projection
        self.__file_format = file_format
        self.__full_header_update = full_header_update
        self.__txt_separator = txt_separator
        self.__output_path = os.path.normpath(
            self.__output_file_or_dir)  # If the specified folder is directory read all the matching file
        if os.path.isdir(self.__input_file_or_dir):
            self.__input_isdir = True
            inputfiles = glob.glob(os.path.join(self.__input_file_or_dir, '*' + self.__file_format))
            if not os.path.exists(self.__output_file_or_dir):
                os.makedirs(self.__output_file_or_dir)
            for in_file in inputfiles:
                logging.info('Adding %s to the queue.' % (in_file))
                out_file = os.path.join(self.__output_path, os.path.basename(in_file))
                self.__file_and_projection.append(
                    [in_file, out_file, self.__input_projection, self.__output_projection, self.__file_format,
                     self.__full_header_update, self.__txt_separator])
        elif os.path.isfile(self.__input_file_or_dir):
            self.__input_isdir = False
            in_file = self.__input_file_or_dir
            if os.path.basename(self.__output_file_or_dir) is not "":
                self.__file_and_projection.append(
                    [in_file, self.__output_file_or_dir, self.__input_projection, self.__output_projection,
                     self.__file_format,
                     self.__full_header_update, self.__txt_separator])
            else:
                out_file = os.path.join(self.__output_path, os.path.basename(in_file))
                self.__file_and_projection.append(
                    [in_file, out_file, self.__input_projection, self.__output_projection, self.__file_format,
                     self.__full_header_update, self.__txt_separator])
            logging.info('Adding %s to the queue.' % (in_file))
        else:
            # Not a file, not a dir
            logging.error('Cannot found input LAS PointCloud file: %s' % (self.__input_file_or_dir))
            exit(1)

    def get_filelist(self):
        return self.__file_and_projection

    def get_isdir(self):
        return self.__input_isdir