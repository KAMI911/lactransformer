try:
    import traceback
    import fnmatch
    import logging
    from pathlib import Path
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)


class FileListWithProjection:
    def __init__(self):
        self.__input_isdir = False
        self.__file_and_projection = []

    def create_list(self, input_file_or_dir, output_file_or_dir, input_projection, output_projection,
                    file_format='las', full_header_update=False, txt_separator=','):
        input_path = Path(input_file_or_dir)
        output_path = Path(output_file_or_dir)

        if input_path.is_dir():
            self.__input_isdir = True
            output_path.mkdir(parents=True, exist_ok=True)
            for root, _, filenames in input_path.walk() if hasattr(input_path, 'walk') else self._walk(input_path):
                root_path = Path(root)
                for filename in fnmatch.filter(filenames, '*' + file_format):
                    in_file = root_path / filename
                    rel = root_path.relative_to(input_path)
                    out_file = output_path / rel / filename
                    out_file.parent.mkdir(parents=True, exist_ok=True)
                    logging.info(f'Adding {in_file} to the queue to create {out_file} file.')
                    self.__file_and_projection.append(
                        [str(in_file), str(out_file), input_projection, output_projection,
                         file_format, full_header_update, txt_separator])
        elif input_path.is_file():
            self.__input_isdir = False
            out_file = str(output_path) if output_path.name else str(output_path / input_path.name)
            logging.info(f'Adding {input_path} to the queue.')
            self.__file_and_projection.append(
                [str(input_path), out_file, input_projection, output_projection,
                 file_format, full_header_update, txt_separator])
        else:
            raise FileNotFoundError(f'Cannot find input file or directory: {input_file_or_dir}')

    @staticmethod
    def _walk(path):
        """Fallback os.walk wrapper for Python < 3.12."""
        import os
        yield from os.walk(path)

    @property
    def filelist(self):
        return self.__file_and_projection

    @property
    def isdir(self):
        return self.__input_isdir
