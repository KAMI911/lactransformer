#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    import traceback
    import filecmp
    import unittest
    from pathlib import Path
    from lactransformer.libs import FriendlyName, AssignProjection, TxtPanPyConverter, LasPyConverter
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
        self.assertTrue(filecmp.cmp(self.temp_file, compare_file_path(output_filename)))


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
    ])
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    unittest.main()
