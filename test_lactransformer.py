#!/usr/bin/python

try:
    import traceback
    import logging
    import os
    import re
    import sys
    import tempfile
    import unittest
    from pathlib import Path
    from unittest import mock
    import laspy
    import lactransformer
    from lactransformer import gtx_ascii2bin, gtx_bin2ascii, lasdiff
    from lactransformer import lactransformer as lactransformer_main
    from lactransformer.libs import (FriendlyName, AssignProjection, TxtPanPyConverter, LasPyConverter, PefFile,
                                     FileListWithProjection, TransformerCommandLine, TransformerWorkflow,
                                     FileConverterCommandLine)
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)

_BASE = Path(__file__).parent


def grid_path(filename):
    return str(_BASE / 'lactransformer' / 'grid' / filename)


def input_file_path(filename):
    return str(_BASE / 'test' / 'input' / filename)


def compare_file_path(filename):
    return str(_BASE / 'test' / 'compare' / filename)


def temp_file_path(filename):
    tmp = _BASE / 'test' / 'tmp'
    tmp.mkdir(parents=True, exist_ok=True)
    return str(tmp / filename)


def text_files_close(path_a, path_b, tolerance=1e-7):
    """Compare text files line by line; numbers may differ by `tolerance` (PROJ versions differ in the last digits)."""
    lines_a = Path(path_a).read_text().splitlines()
    lines_b = Path(path_b).read_text().splitlines()
    if len(lines_a) != len(lines_b):
        return False
    for line_a, line_b in zip(lines_a, lines_b):
        tokens_a = [t for t in re.split(r'[,;=\s]+', line_a) if t]
        tokens_b = [t for t in re.split(r'[,;=\s]+', line_b) if t]
        if len(tokens_a) != len(tokens_b):
            return False
        for token_a, token_b in zip(tokens_a, tokens_b):
            if token_a == token_b:
                continue
            try:
                if abs(float(token_a) - float(token_b)) > tolerance:
                    return False
            except ValueError:
                return False
    return True


class TestFriendlyName(unittest.TestCase):
    def test_friendly_name_all(self):
        file_formats = {
            'las': 'LAS PointCloud',
            'laz': 'LAZ (compressed) PointCloud',
            'txt': 'Trajectory CSV file',
            'lastxt': 'PointText',
            'iml': 'TerraPhoto Image List',
            'csv': 'Riegl Camera CSV',
            'pef': 'PEF',
            'strtxt': 'String PointText',
        }
        for fmt, name in file_formats.items():
            self.assertEqual(FriendlyName.FriendlyName(fmt), name)


class TestAssignProjection(unittest.TestCase):
    def setUp(self):
        nadgrids_EOV2009 = grid_path('etrs2eov_notowgs.gsb')
        geoidgrids_EOV2009 = grid_path('geoid_eht.gtx')
        nadgrids_EOV2014 = grid_path('etrs2eov_notowgs.gsb')
        geoidgrids_EOV2014 = grid_path('geoid_eht2014.gtx')
        geoidgrids_EOV2014fine = grid_path('geoid_eht2014_fine.gtx')
        geoidgrids_SVY21c = grid_path('geoid_svy21_2009.gtx')

        self.projections = {
            'WGS84':      '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
            'WGS84geo':   '+proj=geocent +ellps=WGS84 +datum=WGS84 +units=m +no_defs',
            'EOV':        '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                          ' +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
            'EOVc':       f'+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                          f' +x_0=650000 +y_0=200000 +ellps=GRS67'
                          f' +nadgrids={nadgrids_EOV2014} +geoidgrids={geoidgrids_EOV2014} +units=m +no_defs',
            'EOV2014':    f'+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                          f' +x_0=650000 +y_0=200000 +ellps=GRS67'
                          f' +nadgrids={nadgrids_EOV2014} +geoidgrids={geoidgrids_EOV2014} +units=m +no_defs',
            'EOV2014fine': f'+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                           f' +x_0=650000 +y_0=200000 +ellps=GRS67'
                           f' +nadgrids={nadgrids_EOV2014} +geoidgrids={geoidgrids_EOV2014fine} +units=m +no_defs',
            'EOV2009':    f'+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                          f' +x_0=650000 +y_0=200000 +ellps=GRS67'
                          f' +nadgrids={nadgrids_EOV2009} +geoidgrids={geoidgrids_EOV2009} +units=m +no_defs',
            'SVY21':      '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1'
                          ' +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs',
            'SVY21c':     f'+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1'
                          f' +x_0=28001.642 +y_0=38744.572 +ellps=WGS84'
                          f' +geoidgrids={geoidgrids_SVY21c} +units=m +no_defs',
            'ETRS89':     '+proj=longlat +ellps=GRS80 +no_defs',
            'ETRS89geo':  '+proj=geocent +ellps=GRS80 +units=m +no_defs',
        }

        self.fallback_projections = {
            'WGS84':      '',
            'WGS84geo':   '',
            'EOV':        '',
            'EOVc':       '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                          ' +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
            'EOV2014':    '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                          ' +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
            'EOV2009':    '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                          ' +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
            'SVY21':      '',
            'SVY21c':     '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1'
                          ' +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs',
            'ETRS89':     '',
            'ETRS89geo':  '',
        }

        self.projectionnames = {
            'WGS84': 'WGS84', 'WGS84geo': 'WGS84geo', 'WGS84PM': 'WGS84PM',
            'EOV': 'EOV', 'EOVc': 'EOV2014', 'EOV2014': 'EOV2014', 'EOV2014fine': 'EOV2014fine',
            'EOV2009': 'EOV2009', 'EOVp': 'EOVp', 'SVY21': 'SVY21', 'SVY21c': 'SVY21',
            'ETRS89': 'ETRS89', 'ETRS89geo': 'ETRS89geo',
        }

    def test_assign_projection_all(self):
        for projection, projection_string in self.projections.items():
            self.assertEqual(AssignProjection.AssignProjectionString(projection), projection_string)

    def test_assign_projection_missing(self):
        self.assertFalse(AssignProjection.AssignProjectionString('EOVcMISSING'))

    def test_assign_fallback_projection_all(self):
        for projection, fallback_string in self.fallback_projections.items():
            self.assertEqual(AssignProjection.AssignFallbackProjectionString(projection), fallback_string)

    def test_assign_fallback_projection_missing(self):
        self.assertFalse(AssignProjection.AssignProjectionString('EOVcMISSING'))

    def test_assign_projection_name_all(self):
        for projection, projection_name in self.projectionnames.items():
            self.assertEqual(AssignProjection.AssignProjectionName(projection), projection_name)


class _TxtBase(unittest.TestCase):
    """Shared setUp/tearDown for text converter tests."""
    input_filename = None

    def setUp(self):
        self.input_file = input_file_path(self.input_filename)
        self.temp_file = None

    def tearDown(self):
        if self.temp_file:
            Path(self.temp_file).unlink(missing_ok=True)

    def _run(self, output_filename, src_proj, dst_proj, fmt, sep=','):
        self.temp_file = temp_file_path(output_filename)
        Path(self.temp_file).unlink(missing_ok=True)
        converter = TxtPanPyConverter.TxtPanPyConverter(
            self.input_file, src_proj, self.temp_file, dst_proj, fmt, sep)
        converter.Open()
        converter.Transform()
        converter.Close()
        self.assertTrue(text_files_close(self.temp_file, compare_file_path(output_filename)))


class TestTxtTransformation_from_WGS84geo(_TxtBase):
    input_filename = 'txt_wgs84geo_bp.txt'

    def test_text_transformation_lastext_to_EOV2009(self):
        self._run('txt_eov2009_bp.txt', 'WGS84geo', 'EOV2009', 'txt')

    def test_text_transformation_lastext_to_EOV2014(self):
        self._run('txt_eov2014_bp.txt', 'WGS84geo', 'EOV2014', 'txt')

    def test_text_transformation_lastext_to_EOVc(self):
        self._run('txt_eov2014_bp.txt', 'WGS84geo', 'EOVc', 'txt')

    def test_text_transformation_lastext_to_WGS84(self):
        self._run('txt_wgs84_bp.txt', 'WGS84geo', 'WGS84', 'txt')


class TestPefTransformation_from_WGS84geo(_TxtBase):
    input_filename = 'pef_wgs84geo_bp.txt'

    def test_text_transformation_pef_to_EOV2009(self):
        self._run('pef_eov2009_bp.txt', 'WGS84geo', 'EOV2009', 'pef')

    def test_text_transformation_pef_to_EOV2014(self):
        self._run('pef_eov2014_bp.txt', 'WGS84geo', 'EOV2014', 'pef')

    def test_text_transformation_pef_to_EOVc(self):
        self._run('pef_eov2014_bp.txt', 'WGS84geo', 'EOVc', 'pef')

    def test_text_transformation_pef_to_WGS84(self):
        self._run('pef_wgs84_bp.txt', 'WGS84geo', 'WGS84', 'pef')


class TestLasTxtTransformation_from_WGS84geo(_TxtBase):
    input_filename = 'lastxt_wgs84geo_bp.txt'

    def test_lastxt_transformation_to_EOV2014(self):
        self._run('lastxt_eov2014_bp.txt', 'WGS84geo', 'EOV2014', 'lastxt', ' ')


class TestLasTxtTransformation_from_EOV2009(_TxtBase):
    input_filename = 'lastxt_eov2009_bp.txt'

    def test_lastxt_transformation_to_WGS84geo(self):
        self._run('lastxt_wgs84geo_bp.txt', 'EOV2009', 'WGS84geo', 'lastxt', ' ')

    def test_lastxt_transformation_to_EOV2014(self):
        self._run('lastxt_eov2014_bp_a.txt', 'EOV2009', 'EOV2014', 'lastxt', ' ')

    def test_lastxt_transformation_to_EOVc(self):
        self._run('lastxt_eov2014_bp_a.txt', 'EOV2009', 'EOVc', 'lastxt', ' ')


class TestLasTxtTransformation_from_Javad_EOV2009(_TxtBase):
    input_filename = 'javad_rtk_eov.csv'

    def test_lastxt_transformation_javad_to_WGS84geo(self):
        self._run('javad_rtk_wgs84geo.csv', 'EOV2009', 'WGS84geo', 'strtxt', ';')

    def test_lastxt_transformation_javad_to_WGS84(self):
        self._run('javad_rtk_wgs84.csv', 'EOV2009', 'WGS84', 'strtxt', ';')


class TestLasTransformation_from_WGS84geo(unittest.TestCase):
    def setUp(self):
        self.input_file = input_file_path('las_wgs84geo.las')
        self.temp_file = None

    def tearDown(self):
        if self.temp_file:
            Path(self.temp_file).unlink(missing_ok=True)

    def _run(self, output_filename, dst_proj):
        self.temp_file = temp_file_path(output_filename)
        Path(self.temp_file).unlink(missing_ok=True)
        las = LasPyConverter.LasPyConverter(self.input_file, 'WGS84geo', self.temp_file, dst_proj)
        las.Open()
        las.GetSourceScale()
        las.SetDestinationScale()
        las.TransformPointCloud()
        las.Close()
        cmp = LasPyConverter.LasPyCompare(self.temp_file, compare_file_path(output_filename))
        cmp.OpenReadOnly()
        if not cmp.is_equal():
            print(cmp.ComparePointCloud())
        self.assertTrue(cmp.is_equal())
        cmp.Close()

    def test_las_transformation_to_EOV2014(self):
        self._run('las_eov2014.las', 'EOVc')

    def test_las_transformation_to_EOV2009(self):
        self._run('las_eov2009.las', 'EOV2009')


class _TmpDirBase(unittest.TestCase):
    """Gives every test its own throw-away directory."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)


class TestAssignProjectionSecurity(unittest.TestCase):
    def test_raw_proj_string_is_not_accepted_as_projection_name(self):
        for value in ['+proj=longlat +ellps=WGS84', '../../etc/passwd', 'EOV; rm -rf /', '', 'wgs84']:
            self.assertFalse(AssignProjection.AssignProjectionString(value), value)

    def test_missing_grid_raises(self):
        with mock.patch.object(Path, 'is_file', return_value=False):
            for projection in ['EOVc', 'EOV2014', 'EOV2014fine', 'EOV2009', 'SVY21c']:
                with self.assertRaises(FileNotFoundError, msg=projection):
                    AssignProjection.AssignProjectionString(projection)


class TestSvy21RoundTrip(_TmpDirBase):
    def _convert(self, src, dst, src_proj, dst_proj):
        converter = TxtPanPyConverter.TxtPanPyConverter(str(src), src_proj, str(dst), dst_proj, 'txt', ',')
        converter.Open()
        converter.Transform()
        converter.Close()

    def test_wgs84_to_svy21_and_back(self):
        source = self.tmp / 'wgs84.txt'
        source.write_text('T,X,Y,Z\n1.0,103.8,1.3,10.0\n2.0,103.85,1.35,20.0\n')
        svy21 = self.tmp / 'svy21.txt'
        back = self.tmp / 'back.txt'
        self._convert(source, svy21, 'WGS84', 'SVY21')
        self._convert(svy21, back, 'SVY21', 'WGS84')

        easting, northing = [float(v) for v in svy21.read_text().splitlines()[1].split(',')[1:3]]
        self.assertTrue(20000 < easting < 30000, easting)
        self.assertTrue(28000 < northing < 35000, northing)
        lon, lat, height = [float(v) for v in back.read_text().splitlines()[1].split(',')[1:4]]
        self.assertAlmostEqual(lon, 103.8, places=6)
        self.assertAlmostEqual(lat, 1.3, places=6)
        self.assertAlmostEqual(height, 10.0, places=3)


class TestTxtConverterErrors(_TmpDirBase):
    def test_missing_input_file_raises(self):
        converter = TxtPanPyConverter.TxtPanPyConverter(
            str(self.tmp / 'missing.txt'), 'WGS84geo', str(self.tmp / 'out.txt'), 'EOV2014', 'txt', ',')
        with self.assertRaises(FileNotFoundError):
            converter.Open()

    def test_empty_input_file_raises(self):
        source = self.tmp / 'empty.txt'
        source.write_text('')
        converter = TxtPanPyConverter.TxtPanPyConverter(
            str(source), 'WGS84geo', str(self.tmp / 'out.txt'), 'EOV2014', 'txt', ',')
        with self.assertRaises(ValueError):
            converter.Open()

    def test_missing_pef_input_file_raises(self):
        converter = TxtPanPyConverter.TxtPanPyConverter(
            str(self.tmp / 'missing.pef'), 'WGS84geo', str(self.tmp / 'out.pef'), 'EOV2014', 'pef', ',')
        with self.assertRaises(IOError):
            converter.Open()


class TestPefFile(_TmpDirBase):
    def test_write_then_read_round_trip(self):
        items = [[['TYPE', 'PlaneObj'], ['P1', '1 2 3']], [['TYPE', 'PlaneObj'], ['P2', '4 5 6']]]
        path = str(self.tmp / 'test.pef')
        with PefFile.PefFile(path) as writer:
            writer.OpenOW()
            for item in items:
                writer.WriteNextItem(item)
        with PefFile.PefFile(path) as reader:
            reader.OpenRO()
            self.assertEqual(reader.ReadNextItem(), items[0])
            self.assertEqual(reader.ReadNextItem(), items[1])
            self.assertEqual(reader.ReadNextItem(), [])

    def test_context_manager_closes_file_on_exception(self):
        path = str(self.tmp / 'test.pef')
        Path(path).write_text('TYPE=PlaneObj\n')
        pef = PefFile.PefFile(path)
        with self.assertRaises(RuntimeError):
            with pef:
                pef.OpenRO()
                raise RuntimeError('boom')
        pef.Close()  # closing twice must be harmless

    def test_open_missing_file_raises_ioerror(self):
        with self.assertRaises(IOError):
            PefFile.PefFile(str(self.tmp / 'missing.pef')).OpenRO()

    def test_item_validation(self):
        pef = PefFile.PefFile('unused')
        valid = [['TYPE', 'PlaneObj'], ['A', '1'], ['B', '2'], ['C', '8']]
        self.assertEqual(pef.TestItem(valid), 0)
        self.assertEqual(pef.TestItem([]), 1)
        self.assertEqual(pef.TestItem([['TYPE', 'Other']]), 1)
        self.assertEqual(pef.TestItem([['TYPE', 'PlaneObj'], ['A', '1'], ['B', '2'], ['C', '7']]), 1)


class TestFileListWithProjection(_TmpDirBase):
    def _create(self, source, destination, file_format='las'):
        file_list = FileListWithProjection.FileListWithProjection()
        file_list.create_list(str(source), str(destination), 'WGS84geo', 'EOVc', file_format)
        return file_list

    def test_single_file(self):
        source = self.tmp / 'a.las'
        source.touch()
        file_list = self._create(source, self.tmp / 'out.las')
        self.assertFalse(file_list.isdir)
        self.assertEqual(file_list.filelist[0][:5], [str(source), str(self.tmp / 'out.las'),
                                                     'WGS84geo', 'EOVc', 'las'])

    def test_directory_is_walked_recursively_and_filtered_by_extension(self):
        source = self.tmp / 'in'
        (source / 'sub' / 'deeper').mkdir(parents=True)
        for name in ['a.las', 'sub/b.las', 'sub/deeper/c.las', 'sub/ignored.txt']:
            (source / name).touch()
        file_list = self._create(source, self.tmp / 'out')
        self.assertTrue(file_list.isdir)
        outputs = sorted(item[1] for item in file_list.filelist)
        self.assertEqual(outputs, sorted(str(self.tmp / 'out' / name)
                                         for name in ['a.las', 'sub/b.las', 'sub/deeper/c.las']))
        self.assertTrue((self.tmp / 'out' / 'sub' / 'deeper').is_dir())

    def test_missing_input_raises(self):
        with self.assertRaises(FileNotFoundError):
            self._create(self.tmp / 'missing.las', self.tmp / 'out.las')

    def test_unicode_and_space_in_names(self):
        source = self.tmp / 'árvíztűrő tükörfúrógép.las'
        source.touch()
        file_list = self._create(source, str(self.tmp / 'ki') + os.sep)
        self.assertEqual(file_list.filelist[0][1], str(self.tmp / 'ki' / source.name))

    def test_single_file_into_existing_directory(self):
        source = self.tmp / 'a.las'
        source.touch()
        (self.tmp / 'existing').mkdir()
        file_list = self._create(source, self.tmp / 'existing')
        self.assertEqual(file_list.filelist[0][1], str(self.tmp / 'existing' / 'a.las'))


class TestCommandLine(unittest.TestCase):
    def _parse(self, *argv):
        with mock.patch.object(sys, 'argv', ['lactransformer', *argv]):
            command_line = TransformerCommandLine.TransformerCommandLine()
            command_line.parse()
        return command_line

    def test_defaults(self):
        command_line = self._parse('-i', 'in.las', '-o', 'out.las')
        self.assertEqual(command_line.input, 'in.las')
        self.assertEqual(command_line.output, 'out.las')
        self.assertEqual(command_line.input_format, 'las')
        self.assertEqual(command_line.input_projection, 'WGS84geo')
        self.assertEqual(command_line.output_projection, 'EOVc')
        self.assertEqual(command_line.cores, 1)
        self.assertEqual(command_line.separator, ',')
        self.assertFalse(command_line.no_threads)
        self.assertFalse(command_line.full_header_update)
        self.assertEqual(command_line.verbose, '')

    def test_all_options(self):
        command_line = self._parse('-i', 'in', '-o', 'out', '-input_format', 'lastxt', '-input_projection', 'EOV2009',
                                   '-output_projection', 'WGS84', '-cores', '4', '-no_threads',
                                   '-full_header_update', '-separator', ';', '-v')
        self.assertEqual(
            (command_line.input_format, command_line.input_projection, command_line.output_projection,
             command_line.cores, command_line.no_threads, command_line.full_header_update,
             command_line.separator, command_line.verbose),
            ('lastxt', 'EOV2009', 'WGS84', 4, True, True, ';', ' -v'))

    def test_invalid_arguments_exit_with_usage_error(self):
        invalid = [
            ['-o', 'out.las'],
            ['-i', 'in.las'],
            ['-i', 'in.las', '-o', 'out.las', '-input_projection', '+proj=longlat'],
            ['-i', 'in.las', '-o', 'out.las', '-input_format', 'exe'],
            ['-i', 'in.las', '-o', 'out.las', '-separator', '|'],
            ['-i', 'in.las', '-o', 'out.las', '-cores', 'many'],
        ]
        for argv in invalid:
            with self.subTest(argv=argv), mock.patch('sys.stderr'):
                with self.assertRaises(SystemExit) as raised:
                    self._parse(*argv)
                self.assertEqual(raised.exception.code, 2)


class TestLasErrors(_TmpDirBase):
    def test_corrupt_las_file_raises(self):
        source = self.tmp / 'corrupt.las'
        source.write_bytes(b'not a las file' * 20)
        converter = LasPyConverter.LasPyConverter(str(source), 'WGS84geo', str(self.tmp / 'out.las'), 'EOVc')
        with self.assertRaises(laspy.errors.LaspyException):
            converter.Open()

    def test_empty_las_file_raises(self):
        source = self.tmp / 'empty.las'
        source.touch()
        converter = LasPyConverter.LasPyConverter(str(source), 'WGS84geo', str(self.tmp / 'out.las'), 'EOVc')
        with self.assertRaises(laspy.errors.LaspyException):
            converter.Open()

    def test_missing_las_file_raises(self):
        converter = LasPyConverter.LasPyConverter(
            str(self.tmp / 'missing.las'), 'WGS84geo', str(self.tmp / 'out.las'), 'EOVc')
        with self.assertRaises(FileNotFoundError):
            converter.Open()

    def test_unknown_projection_is_rejected_before_any_file_access(self):
        with self.assertRaises(Exception):  # noqa: B017 - pyproj raises its own CRSError for an empty CRS string
            LasPyConverter.LasPyConverter(input_file_path('las_wgs84geo.las'), 'WGS84geo',
                                          str(self.tmp / 'out.las'), 'DOES_NOT_EXIST')


class TestLasPropertiesPreserved(_TmpDirBase):
    """The LAS transformation must change the coordinates only, not the other point attributes."""

    def test_point_count_attributes_and_format_are_preserved(self):
        output = str(self.tmp / 'out.las')
        las = LasPyConverter.LasPyConverter(input_file_path('las_wgs84geo.las'), 'WGS84geo', output, 'EOVc')
        las.Open()
        las.GetSourceScale()
        las.SetDestinationScale()
        las.TransformPointCloud()
        las.Close()
        source = laspy.read(input_file_path('las_wgs84geo.las'))
        result = laspy.read(output)
        self.assertEqual(len(result.points), len(source.points))
        self.assertEqual(result.header.point_format.id, source.header.point_format.id)
        self.assertEqual(str(result.header.version), str(source.header.version))
        for dimension in ['intensity', 'return_number', 'classification', 'gps_time']:
            if dimension in source.point_format.dimension_names:
                self.assertTrue((getattr(result, dimension) == getattr(source, dimension)).all(), dimension)
        # EOV northing/easting must be in the Hungarian national grid range, bounds are updated in the header
        self.assertTrue(400000 < result.header.mins[0] < result.header.maxs[0] < 950000)
        self.assertTrue(30000 < result.header.mins[1] < result.header.maxs[1] < 400000)


class TestTransformerWorkflow(_TmpDirBase):
    def _parameters(self, source, destination, src_proj, dst_proj, file_format, separator=','):
        return [str(source), str(destination), src_proj, dst_proj, file_format, False, separator]

    def test_las_workflow_matches_reference(self):
        output = self.tmp / 'las_eov2014.las'
        result = TransformerWorkflow.Transformer(
            self._parameters(input_file_path('las_wgs84geo.las'), output, 'WGS84geo', 'EOVc', 'las'))
        self.assertEqual(result, str(output))
        comparison = LasPyConverter.LasPyCompare(str(output), compare_file_path('las_eov2014.las'))
        comparison.OpenReadOnly()
        self.assertTrue(comparison.is_equal())
        comparison.Close()

    def test_laz_workflow_matches_las_reference(self):
        source = self.tmp / 'las_wgs84geo.laz'
        laspy.read(input_file_path('las_wgs84geo.las')).write(str(source))
        output = self.tmp / 'las_eov2014.laz'
        result = TransformerWorkflow.Transformer(self._parameters(source, output, 'WGS84geo', 'EOVc', 'laz'))
        self.assertEqual(result, str(output))
        with open(output, 'rb') as handle:
            self.assertEqual(handle.read(4), b'LASF')
        compressed = laspy.read(str(output))
        reference = laspy.read(compare_file_path('las_eov2014.las'))
        self.assertTrue((compressed.points.array == reference.points.array).all())

    def test_text_workflow_matches_reference(self):
        output = self.tmp / 'txt_eov2014_bp.txt'
        result = TransformerWorkflow.Transformer(
            self._parameters(input_file_path('txt_wgs84geo_bp.txt'), output, 'WGS84geo', 'EOV2014', 'txt'))
        self.assertEqual(result, str(output))
        self.assertTrue(text_files_close(output, compare_file_path('txt_eov2014_bp.txt')))

    def test_pef_workflow_matches_reference(self):
        output = self.tmp / 'pef_eov2014_bp.txt'
        TransformerWorkflow.Transformer(
            self._parameters(input_file_path('pef_wgs84geo_bp.txt'), output, 'WGS84geo', 'EOV2014', 'pef'))
        self.assertTrue(text_files_close(output, compare_file_path('pef_eov2014_bp.txt')))

    def test_unknown_format_returns_none_and_writes_nothing(self):
        output = self.tmp / 'out.xyz'
        with self.assertLogs(level=logging.CRITICAL):
            result = TransformerWorkflow.Transformer(
                self._parameters(input_file_path('txt_wgs84geo_bp.txt'), output, 'WGS84geo', 'EOV2014', 'xyz'))
        self.assertIsNone(result)
        self.assertFalse(output.exists())

    def test_corrupt_las_is_logged_and_reraised(self):
        source = self.tmp / 'corrupt.las'
        source.write_bytes(b'corrupt' * 30)
        output = self.tmp / 'out.las'
        with self.assertLogs(level=logging.ERROR), mock.patch('traceback.print_exc'):
            with self.assertRaises(laspy.errors.LaspyException):
                TransformerWorkflow.Transformer(self._parameters(source, output, 'WGS84geo', 'EOVc', 'las'))
        self.assertFalse(output.exists())

    def test_missing_text_file_is_logged_and_reraised(self):
        with self.assertLogs(level=logging.ERROR):
            with self.assertRaises(FileNotFoundError):
                TransformerWorkflow.Transformer(
                    self._parameters(self.tmp / 'missing.txt', self.tmp / 'out.txt', 'WGS84geo', 'EOV2014', 'txt'))


class TestMainEndToEnd(_TmpDirBase):
    def setUp(self):
        super().setUp()
        self._cwd = os.getcwd()
        os.chdir(self.tmp)  # main() writes its log file to the current directory
        self.addCleanup(os.chdir, self._cwd)
        root = logging.getLogger()
        handlers = list(root.handlers)
        self.addCleanup(lambda: [root.removeHandler(h) for h in list(root.handlers) if h not in handlers])

    def _main(self, *argv):
        with mock.patch.object(sys, 'argv', ['lactransformer', *argv]):
            lactransformer_main.main()

    def test_single_las_file(self):
        output = self.tmp / 'out.las'
        self._main('-i', input_file_path('las_wgs84geo.las'), '-o', str(output),
                   '-input_projection', 'WGS84geo', '-output_projection', 'EOVc', '-no_threads')
        comparison = LasPyConverter.LasPyCompare(str(output), compare_file_path('las_eov2014.las'))
        comparison.OpenReadOnly()
        self.assertTrue(comparison.is_equal())
        comparison.Close()

    def test_directory_with_multiple_processes(self):
        source = self.tmp / 'in'
        (source / 'sub').mkdir(parents=True)
        for name in ['a.txt', 'sub/b.txt']:
            (source / name).write_bytes(Path(input_file_path('txt_wgs84geo_bp.txt')).read_bytes())
        self._main('-i', str(source), '-o', str(self.tmp / 'out'), '-input_format', 'txt',
                   '-input_projection', 'WGS84geo', '-output_projection', 'EOV2014', '-cores', '2')
        for name in ['a.txt', 'sub/b.txt']:
            self.assertTrue(text_files_close(self.tmp / 'out' / name, compare_file_path('txt_eov2014_bp.txt')), name)

    def test_missing_input_raises(self):
        with self.assertRaises(FileNotFoundError):
            self._main('-i', str(self.tmp / 'missing.las'), '-o', str(self.tmp / 'out.las'))


class TestGtxConversion(_TmpDirBase):
    HEADER = '47.0 16.0 0.5 0.5 2 2'

    def _write_ascii(self, *heights, header=HEADER):
        path = self.tmp / 'grid.txt'
        path.write_text('\n'.join([header, *heights]) + '\n')
        return path

    def test_ascii_to_binary_and_back(self):
        source = self._write_ascii('1.5', '150', '2.25', '3.0')
        binary = self.tmp / 'grid.gtx'
        self.assertEqual(gtx_ascii2bin.main(['-i', str(source), '-o', str(binary)]), 0)
        self.assertEqual(binary.stat().st_size, 40 + 4 * 4)
        text = self.tmp / 'back.txt'
        self.assertEqual(gtx_bin2ascii.main(['-i', str(binary), '-o', str(text)]), 0)
        self.assertEqual(text.read_text().split('\n'),
                         ['47.0 16.0 0.5 0.5 2 2', '1.5000', '-88.8888', '2.2500', '3.0000', ''])

    def test_default_output_names(self):
        source = self._write_ascii('1.0')
        self.assertEqual(gtx_ascii2bin.convert(str(source)), str(source) + '.gtx')
        self.assertEqual(gtx_bin2ascii.convert(str(source) + '.gtx'), str(source) + '.gtx.txt')

    def test_invalid_input_is_reported(self):
        header_only_short = self._write_ascii('1.0', header='47.0 16.0')
        with self.assertRaises(ValueError):
            gtx_ascii2bin.convert(str(header_only_short), str(self.tmp / 'a.gtx'))
        bad_height = self._write_ascii('1.0', 'abc')
        with self.assertRaises(ValueError):
            gtx_ascii2bin.convert(str(bad_height), str(self.tmp / 'b.gtx'))
        with self.assertRaises(FileNotFoundError):
            gtx_ascii2bin.convert(str(self.tmp / 'missing.txt'))
        truncated = self.tmp / 'short.gtx'
        truncated.write_bytes(b'\x00' * 10)
        with self.assertRaises(ValueError):
            gtx_bin2ascii.convert(str(truncated), str(self.tmp / 'c.txt'))
        with self.assertRaises(FileNotFoundError):
            gtx_bin2ascii.convert(str(self.tmp / 'missing.gtx'))

    def test_main_returns_error_code(self):
        with mock.patch('builtins.print'):
            self.assertEqual(gtx_ascii2bin.main(['-i', str(self.tmp / 'missing.txt')]), 1)
            self.assertEqual(gtx_bin2ascii.main(['-i', str(self.tmp / 'missing.gtx')]), 1)

    def test_command_line_requires_input(self):
        command_line = FileConverterCommandLine.FileConverterCommandLine()
        with mock.patch('sys.stderr'), self.assertRaises(SystemExit):
            command_line.parse([])
        command_line.parse(['-i', 'in', '-o', 'out'])
        self.assertEqual((command_line.input, command_line.output), ('in', 'out'))


class TestLasDiff(_TmpDirBase):
    def setUp(self):
        super().setUp()
        self._cwd = os.getcwd()
        os.chdir(self.tmp)  # main() writes its log file to the current directory
        self.addCleanup(os.chdir, self._cwd)
        root = logging.getLogger()
        handlers = list(root.handlers)
        self.addCleanup(lambda: [root.removeHandler(h) for h in list(root.handlers) if h not in handlers])

    def test_diff_of_identical_files(self):
        reference = compare_file_path('las_eov2014.las')
        with mock.patch('builtins.print'):
            self.assertEqual(lasdiff.DiffLas([reference, reference]), 0)

    def test_diff_of_different_files_prints_statistics(self):
        with mock.patch('builtins.print') as printed:
            lasdiff.DiffLas([compare_file_path('las_eov2014.las'), compare_file_path('las_eov2009.las')])
        self.assertIn('Xmin/max/avg/std', ''.join(str(call) for call in printed.call_args_list))

    def test_main_compares_directories(self):
        directory = self.tmp / 'a'
        directory.mkdir()
        (directory / 'x.las').write_bytes(Path(compare_file_path('las_eov2014.las')).read_bytes())
        with mock.patch.object(sys, 'argv', ['lasdiff', '-i', str(directory), '-o', str(directory), '-cores', '2']), \
                mock.patch('builtins.print'):
            lasdiff.main()

    def test_main_missing_input_exits(self):
        with mock.patch.object(sys, 'argv', ['lasdiff', '-i', str(self.tmp / 'missing.las'), '-o', 'out.las']):
            with self.assertRaises(SystemExit):
                lasdiff.main()


class TestVersion(unittest.TestCase):
    def test_version_is_exposed_and_printed(self):
        self.assertRegex(lactransformer.__version__, r'^\d+\.\d+\.\d+')
        with mock.patch.object(sys, 'argv', ['lactransformer', '-version']), \
                mock.patch('sys.stdout') as stdout, self.assertRaises(SystemExit) as raised:
            TransformerCommandLine.TransformerCommandLine().parse()
        self.assertEqual(raised.exception.code, 0)
        self.assertIn(lactransformer.__version__, ''.join(str(call) for call in stdout.write.call_args_list))


def testing_lactransformer():
    suite = unittest.TestLoader().loadTestsFromNames([
        'test_lactransformer.TestFriendlyName',
        'test_lactransformer.TestAssignProjection',
        'test_lactransformer.TestTxtTransformation_from_WGS84geo',
        'test_lactransformer.TestPefTransformation_from_WGS84geo',
        'test_lactransformer.TestLasTxtTransformation_from_EOV2009',
        'test_lactransformer.TestLasTxtTransformation_from_Javad_EOV2009',
        'test_lactransformer.TestLasTxtTransformation_from_WGS84geo',
        'test_lactransformer.TestLasTransformation_from_WGS84geo',
        'test_lactransformer.TestAssignProjectionSecurity',
        'test_lactransformer.TestSvy21RoundTrip',
        'test_lactransformer.TestTxtConverterErrors',
        'test_lactransformer.TestPefFile',
        'test_lactransformer.TestFileListWithProjection',
        'test_lactransformer.TestCommandLine',
        'test_lactransformer.TestLasErrors',
        'test_lactransformer.TestLasPropertiesPreserved',
        'test_lactransformer.TestTransformerWorkflow',
        'test_lactransformer.TestMainEndToEnd',
        'test_lactransformer.TestGtxConversion',
        'test_lactransformer.TestLasDiff',
        'test_lactransformer.TestVersion',
    ])
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    unittest.main()
