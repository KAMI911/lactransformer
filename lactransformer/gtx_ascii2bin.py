#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import traceback
    import struct
    import os
    from libs import FileConverterCommandLine
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
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
    raise FileNotFoundError(f'Cannot find input file: {input_file}')

try:
    with open(output_file, 'wb') as fw, open(input_file, 'r') as fr:
        row = fr.readline().strip().split(' ')
        header = struct.pack(HEADER_STRUCT, float(row[0]), float(row[1]), float(row[2]), float(row[3]),
                             int(row[4]), int(row[5]))
        fw.write(header)
        while True:
            height = fr.readline()
            if not height:
                break
            height = height.strip()
            # Insert special null value when input uses base level (no geoid offset for this point)
            if height == '150':
                height = '-88.8888'
            try:
                data = struct.pack(DATA_STRUCT, float(height))
            except ValueError as err:
                print(err)
                print(f'Number of lines: {index} position {fr.tell()} value: W{height}W')
                break
            print(height)
            fw.write(data)
            index += 1
except IOError as err:
    print(f'Error opening: {output_file}, error: {err}')
    exit(1)
