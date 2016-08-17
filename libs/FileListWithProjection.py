try:
    import os
    import fnmatch
    import logging
    import glob
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
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
            self.__output_file_or_dir)
        # If the specified folder is directory read all the matching file
        if os.path.isdir(self.__input_file_or_dir):
            self.__input_isdir = True
            # Recursive scan of files
            if not os.path.exists(self.__output_file_or_dir):
                os.makedirs(self.__output_file_or_dir)
            self.__input_isdir = True
            matches = []
            for root, dirnames, filenames in os.walk(input_file_or_dir):
                for filename in fnmatch.filter(filenames, '*' + self.__file_format):
                    matches.append([root, filename])
                if not os.path.exists(root):
                    os.makedirs(root)
                '''
                inputfiles = glob.glob(os.path.join(self.__input_file_or_dir, '*' + self.__file_format))
                '''
            for i in matches:
                in_folder = i[0]
                in_filename = i[1]
                in_file = os.path.join(in_folder, in_filename)
                if os.path.join(in_folder) == os.path.join(self.__input_file_or_dir):
                    in_folder_diff = ""
                else:
                    in_folder_diff = os.path.relpath(in_folder, self.__input_file_or_dir)
                out_file = os.path.join(self.__output_path, in_folder_diff, in_filename)
                logging.info('Adding {0} to the queue to create {1} file. '.format(in_file, out_file))
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
