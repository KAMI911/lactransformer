import os
import logging
import glob

class FileListWithProjection:
    def __init__(self, input_file_or_dir, output_file_or_dir, input_projection_string, output_projection_string,
                 file_format='las'):
        self.__input_isdir = False
        self.__file_and_projection = []
        self.__input_file_or_dir = input_file_or_dir
        self.__output_file_or_dir = output_file_or_dir
        self.__input_projection_string = input_projection_string
        self.__output_projection_string = output_projection_string
        self.__file_format = file_format
        self.__output_path = os.path.normpath(self.__output_file_or_dir)

    # ---------PUBLIC METHODS--------------------

    def create_list(self):
        # If the specified folder is directory read all the matching file
        if os.path.isdir(self.__input_file_or_dir):
            self.__input_isdir = True
            inputfiles = glob.glob(os.path.join(self.__input_file_or_dir, '*' + self.__file_format))
            if not os.path.exists(self.__output_file_or_dir):
                os.makedirs(self.__output_file_or_dir)
            for in_file in inputfiles:
                logging.info('Adding %s to the queue.' % (in_file))
                out_file = os.path.join(self.__output_path, os.path.basename(in_file))
                self.__file_and_projection.append([in_file, out_file, self.__input_projection_string,
                                                   self.__output_projection_string, self.__file_format])
        elif os.path.isfile(self.__input_file_or_dir):
            self.__input_isdir = False
            in_file = self.__input_file_or_dir
            if os.path.basename(self.__output_file_or_dir) is not "":
                self.__file_and_projection.append([in_file, self.__output_file_or_dir, self.__input_projection_string,
                                                   self.__output_projection_string, self.__file_format])
            else:
                out_file = os.path.join(self.__output_path, os.path.basename(in_file))
                self.__file_and_projection.append([in_file, out_file, self.__input_projection_string,
                                                   self.__output_projection_string, self.__file_format])
            logging.info('Adding %s to the queue.' % (in_file))
        else:
            # Not a file, not a dir
            logging.error('Cannot found input LAS PointCloud file: %s' % (self.__input_file_or_dir))
            exit(1)

    def get_filelist(self):
        return self.__file_and_projection

    def get_isdir(self):
        return self.__input_isdir
