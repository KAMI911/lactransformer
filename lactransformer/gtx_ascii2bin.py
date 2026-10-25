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
DATA_STRUCT = '>f'
# Value used by GTX files for points without geoid offset
GTX_NULL_VALUE = '-88.8888'


def convert(input_file, output_file=None):
    """Convert an ASCII grid (header line + one height per line) to a GTX binary grid."""
    if output_file is None:
        output_file = input_file + '.gtx'
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f'Cannot find input file: {input_file}')

    count = 0
    with open(input_file) as fr, open(output_file, 'wb') as fw:
        row = fr.readline().strip().split()
        if len(row) != 6:
            raise ValueError(f'Invalid GTX header in {input_file}: expected 6 values, got {len(row)}')
        fw.write(struct.pack(HEADER_STRUCT, float(row[0]), float(row[1]), float(row[2]), float(row[3]),
                             int(row[4]), int(row[5])))
        for line_number, height in enumerate(fr, start=2):
            height = height.strip()
            if not height:
                continue
            # Insert special null value when input uses base level (no geoid offset for this point)
            if height == '150':
                height = GTX_NULL_VALUE
            try:
                fw.write(struct.pack(DATA_STRUCT, float(height)))
            except ValueError as err:
                raise ValueError(f'Invalid height "{height}" at line {line_number} of {input_file}') from err
            count += 1
    logging.info(f'Wrote {count} values to {output_file}')
    return output_file


def main(argv=None):
    command_line = FileConverterCommandLine.FileConverterCommandLine(prog='gtx_ascii2bin')
    command_line.parse(argv)
    try:
        convert(command_line.input, command_line.output)
    except (OSError, ValueError) as err:
        print(f'Error: {err}')
        return 1
    return 0


if __name__ == '__main__':
    exit(main())
