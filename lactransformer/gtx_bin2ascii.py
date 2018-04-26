#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from __future__ import print_function
    import traceback
    import os
    import struct
    from libs import FileConverterCommandLine
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    traceback.print_exc()
    exit(128)

# It is big endian
# Documentation: http://vdatum.noaa.gov/docs/gtx_info.html
HEADER_STRUCT = '>4d2i'
DATA_STRUCT = '>f'

fileconverterworkflow = FileConverterCommandLine.FileConverterCommandLine()
fileconverterworkflow.parse()

index = 0

input_file = fileconverterworkflow.input
output_file = fileconverterworkflow.output

if output_file is None:
    output_file = input_file + '.txt'

if not os.path.isfile(input_file):
    raise Exception('Cannot found input file: {0}'.format(input_file))
else:
    try:
        with open(output_file, 'w') as fw:
            with open (input_file, 'rb') as fr:
                row = fr.read(40)
                # I cannot really understand but it seems it is big endian
                # Documentation: http://vdatum.noaa.gov/docs/gtx_info.html
                header = struct.unpack(HEADER_STRUCT, row)
                line = ' '.join(map(str,header))+'\n'
                fw.write(line)
                print(line, end='')
                while 1:
                    try:
                        height = fr.read(4)
                        if len(height) == 4:
                            data = struct.unpack(DATA_STRUCT, height)
                            line = '{0:.4f}\n'.format(data[0])
                            # print(line, end='')
                            fw.write(line)
                            # print('Number of lines: {0} position {2} value: W{1}W'.format(index, height, fr.tell()))
                            index += 1
                        else:
                            break
                    except ValueError as err:
                        print('Number of lines: {0} position {2} value: W{1}W'.format(index, height, fr.tell()))
                        break
    except IOError as err:
        print ('Error opening: {0}, error: {1}'.format(output_file, err))
        exit(1)