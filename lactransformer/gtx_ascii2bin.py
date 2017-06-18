try:
    from __future__ import print_function

    import struct

    import os
    from libs import FileConverterCommandLine
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    exit(128)

# It is big endian
# Documentation: http://vdatum.noaa.gov/docs/gtx_info.html
HEADER_STRUCT = '>4d2i'
DATA_STRUCT = '>f'

fileconverterworkflow = FileConverterCommandLine.FileConverterCommandLine()
fileconverterworkflow.parse()

input_file = fileconverterworkflow.input
output_file = fileconverterworkflow.output

index = 0

if output_file is None:
    output_file = input_file + '.gtx'

if not os.path.isfile(input_file):
    raise Exception('Cannot found input file: {0}'.format(input_file))
else:
    try:
        with open(output_file, 'w') as fw:
            with open(input_file, 'r') as fr:
                row = fr.readline()
                row = row.strip().split(' ')
                header = struct.pack(HEADER_STRUCT, float(row[0]), float(row[1]), float(row[2]), float(row[3]),
                                     int(row[4]), int(row[5]))
                fw.write(header)
                # print(header, end='')
                while 1:
                    try:
                        height = fr.readline()
                        height = height.strip()
                        # Insert special null value, when the input uses the base level (no geoid offset for this point)
                        if height == '150':
                            height = '-88.8888'
                        data = struct.pack(DATA_STRUCT, float(height.strip()))
                        print(height)
                        fw.write(data)
                        index += 1
                    except ValueError as err:
                        print (err)
                        print('Number of lines: {0} position {2} value: W{1}W'.format(index, height, fr.tell()))
                        break

    except IOError as err:
        print('Error opening: {0}, error: {1}'.format(output_file, err))
        exit(1)
