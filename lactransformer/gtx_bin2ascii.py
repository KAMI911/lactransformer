#!/usr/bin/env python3

try:
    import logging
    import os
    import struct
    import traceback
    from .libs import FileConverterCommandLine
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)

# It is big endian
# Documentation: http://vdatum.noaa.gov/docs/gtx_info.html
HEADER_STRUCT = '>4d2i'
HEADER_SIZE = struct.calcsize(HEADER_STRUCT)
DATA_STRUCT = '>f'
DATA_SIZE = struct.calcsize(DATA_STRUCT)


def convert(input_file, output_file=None):
    """Convert a GTX binary grid to ASCII (header line + one height per line)."""
    if output_file is None:
        output_file = input_file + '.txt'
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f'Cannot find input file: {input_file}')

    count = 0
    with open(input_file, 'rb') as fr, open(output_file, 'w') as fw:
        row = fr.read(HEADER_SIZE)
        if len(row) != HEADER_SIZE:
            raise ValueError(f'Invalid GTX header in {input_file}: file is too short')
        header = struct.unpack(HEADER_STRUCT, row)
        fw.write(' '.join(map(str, header)) + '\n')
        while True:
            height = fr.read(DATA_SIZE)
            if len(height) < DATA_SIZE:
                break
            fw.write(f'{struct.unpack(DATA_STRUCT, height)[0]:.4f}\n')
            count += 1
    logging.info(f'Wrote {count} values to {output_file}')
    return output_file


def main(argv=None):
    command_line = FileConverterCommandLine.FileConverterCommandLine(prog='gtx_bin2ascii')
    command_line.parse(argv)
    try:
        convert(command_line.input, command_line.output)
    except (OSError, ValueError) as err:
        print(f'Error: {err}')
        return 1
    return 0


if __name__ == '__main__':
    exit(main())
