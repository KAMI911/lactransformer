try:
    import traceback
    import argparse
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)


class FileConverterCommandLine:
    def __init__(self, prog='gtx_converter', description=''):
        self.parser = argparse.ArgumentParser(prog=prog, description=description)
        self.parser.add_argument('-i', type=str, dest='input', required=True, help='required:  input file')
        self.parser.add_argument('-o', type=str, dest='output', required=False, default=None,
                                 help='optional:  output file (default=input file name with new extension)')

    def parse(self, argv=None):
        self.args = self.parser.parse_args(argv)

    @property
    def input(self):
        return self.args.input

    @property
    def output(self):
        return self.args.output
