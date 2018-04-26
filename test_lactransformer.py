#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    import traceback
    import filecmp
    import os
    import unittest
    from lactransformer.libs import FriendlyName, AssignProjection, TxtPanPyConverter, LasPyConverter
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    traceback.print_exc()
    exit(128)


def grid_path(filename):
    return (os.path.abspath(os.path.join(os.path.dirname(__file__), 'lactransformer', 'grid', filename)))


def input_file_path(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'test', 'input', filename))


def compare_file_path(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'test', 'compare', filename))


def temp_file_path(filename):
    temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test', 'tmp'))
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return os.path.join(temp_dir, filename)


class TestFriendlyName(unittest.TestCase):
    def test_friendly_name_all(self):
        file_formats = {'las': 'LAS PointCloud', 'laz': 'LAZ (compressed) PointCloud', 'txt': 'Trajectory CSV file',
                        'lastxt': 'PointText',
                        'iml': 'TerraPhoto Image List', 'csv': 'Riegl Camera CSV', 'pef': 'PEF',
                        'strtxt': 'String PointText'}
        for type_ext, type_name in file_formats.items():
            self.assertEqual(FriendlyName.FriendlyName(type_ext), type_name)


class TestAssignProjection(unittest.TestCase):
    def setUp(self):
        nadgrids_EOV2009 = grid_path('etrs2eov_notowgs.gsb')
        geoidgrids_EOV2009 = grid_path('geoid_eht.gtx')
        nadgrids_EOV2014 = grid_path('etrs2eov_notowgs.gsb')
        geoidgrids_EOV2014 = grid_path('geoid_eht2014.gtx')
        geoidgrids_EOV2014fine = grid_path('geoid_eht2014_fine.gtx')
        geoidgrids_SVY21c = grid_path('geoid_svy21_2009.gtx')

        self.projections = {'WGS84': '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
                            'WGS84geo': '+proj=geocent +ellps=WGS84 +datum=WGS84 +units=m +no_defs',
                            'EOV': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                            'EOVc': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids_EOV2014 + ' +geoidgrids=' + geoidgrids_EOV2014 + ' +units=m +no_defs',
                            'EOV2014': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids_EOV2014 + ' +geoidgrids=' + geoidgrids_EOV2014 + ' +units=m +no_defs',
                            'EOV2014fine': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids_EOV2014 + ' +geoidgrids=' + geoidgrids_EOV2014fine + ' +units=m +no_defs',
                            'EOV2009': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids_EOV2009 + ' +geoidgrids=' + geoidgrids_EOV2009 + ' +units=m +no_defs',
                            'SVY21': '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs',
                            'SVY21c': '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +geoidgrids=' + geoidgrids_SVY21c + ' +units=m +no_defs',
                            'ETRS89': '+proj=longlat +ellps=GRS80 +no_defs',
                            'ETRS89geo': '+proj=geocent +ellps=GRS80 +units=m +no_defs'}

        self.fallback_projections = {'WGS84': '',
                                     'WGS84geo': '',
                                     'EOV': '',
                                     'EOVc': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                                     'EOV2014': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                                     'EOV2009': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                                     'SVY21': '',
                                     'SVY21c': '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs',
                                     'ETRS89': '',
                                     'ETRS89geo': ''}

        self.projectionnames = {'WGS84': 'WGS84', 'WGS84geo': 'WGS84geo', 'WGS84PM': 'WGS84PM', 'EOV': 'EOV',
                                'EOVc': 'EOV2014', 'EOV2014': 'EOV2014', 'EOV2014fine': 'EOV2014fine',
                                'EOV2009': 'EOV2009', 'EOVp': 'EOVp', 'SVY21': 'SVY21', 'SVY21c': 'SVY21',
                                'ETRS89': 'ETRS89', 'ETRS89geo': 'ETRS89geo'}

    def test_assign_projection_all(self):
        for projection, projection_string in self.projections.items():
            self.assertEqual(AssignProjection.AssignProjectionString(projection), projection_string)

    def test_assign_projection_missing(self):
        self.assertEqual(AssignProjection.AssignProjectionString('EOVcMISSING'), False)

    def test_assign_fallback_projection_all(self):
        for projection, fallback_projection_string in self.fallback_projections.items():
            self.assertEqual(AssignProjection.AssignFallbackProjectionString(projection),
                             fallback_projection_string)

    def test_assign_fallback_projection_missing(self):
        self.assertEqual(AssignProjection.AssignProjectionString('EOVcMISSING'), False)

    def test_assign_projection_name_all(self):
        for projection, projection_name in self.projectionnames.items():
            self.assertEqual(AssignProjection.AssignProjectionName(projection), projection_name)


class TestTxtTransformation_from_WGS84geo(unittest.TestCase):
    def setUp(self):
        input_filename = 'txt_wgs84geo_bp.txt'
        self.input_file = input_file_path(input_filename)

    def test_text_transformation_lastext_to_EOV2009(self):
        output_filename = 'txt_eov2009_bp.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2009',
                                                             'txt')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_text_transformation_lastext_to_EOV2014(self):
        output_filename = 'txt_eov2014_bp.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2014',
                                                             'txt')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_text_transformation_lastext_to_EOVc(self):
        output_filename = 'txt_eov2014_bp.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOVc',
                                                             'txt')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_text_transformation_lastext_to_WGS84(self):
        output_filename = 'txt_wgs84_bp.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'WGS84',
                                                             'txt')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)


class TestPefTransformation_from_WGS84geo(unittest.TestCase):
    def setUp(self):
        input_filename = 'pef_wgs84geo_bp.txt'
        self.input_file = input_file_path(input_filename)

    def test_text_transformation_pef_to_EOV2009(self):
        output_filename = 'pef_eov2009_bp.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2009',
                                                             'pef')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_text_transformation_pef_to_EOV2014(self):
        output_filename = 'pef_eov2014_bp.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2014',
                                                             'pef')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_text_transformation_pef_to_EOVc(self):
        output_filename = 'pef_eov2014_bp.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOVc',
                                                             'pef')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_text_transformation_pef_to_WGS84(self):
        output_filename = 'pef_wgs84_bp.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'WGS84',
                                                             'pef')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)


class TestLasTxtTransformation_from_WGS84geo(unittest.TestCase):
    def setUp(self):
        input_filename = 'lastxt_wgs84geo_bp.txt'
        self.input_file = input_file_path(input_filename)

    def test_lastxt_transformation_pef_to_EOV2014(self):
        output_filename = 'lastxt_eov2014_bp.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2014',
                                                             'lastxt', ' ')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)


class TestLasTxtTransformation_from_EOV2009(unittest.TestCase):
    def setUp(self):
        input_filename = 'lastxt_eov2009_bp.txt'
        self.input_file = input_file_path(input_filename)

    def test_lastxt_transformation_pef_to_WGS84geo(self):
        output_filename = 'lastxt_wgs84geo_bp.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'EOV2009', self.temp_file, 'WGS84geo',
                                                             'lastxt', ' ')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_lastxt_transformation_pef_to_EOV2014(self):
        output_filename = 'lastxt_eov2014_bp_a.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'EOV2009', self.temp_file, 'EOV2014',
                                                             'lastxt', ' ')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_lastxt_transformation_pef_to_EOVc(self):
        output_filename = 'lastxt_eov2014_bp_a.txt'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'EOV2009', self.temp_file, 'EOVc',
                                                             'lastxt', ' ')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)


class TestLasTxtTransformation_from_Javad_EOV2009(unittest.TestCase):
    def setUp(self):
        input_filename = 'javad_rtk_eov.csv'
        self.input_file = input_file_path(input_filename)

    def test_lastxt_transformation_javad_to_WGS84geo(self):
        output_filename = 'javad_rtk_wgs84geo.csv'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'EOV2009', self.temp_file, 'WGS84geo',
                                                             'strtxt', ';')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_lastxt_transformation_javad_to_WGS84(self):
        output_filename = 'javad_rtk_wgs84.csv'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'EOV2009', self.temp_file, 'WGS84',
                                                             'strtxt', ';')
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        # with open(self.compare_file, 'r') as cmpf:
        #     with open(self.temp_file, 'r') as tmpf:
        #        diff = difflib.unified_diff(
        #            cmpf.readlines(),
        #            tmpf.readlines(),
        #            fromfile=self.compare_file,
        #            tofile=self.temp_file,
        #        )
        #        for line in diff:
        #            sys.stdout.write(line)
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)


class TestLasTransformation_from_WGS84geo(unittest.TestCase):
    def setUp(self):
        input_filename = 'las_wgs84geo.las'
        self.input_file = input_file_path(input_filename)

    def test_las_transformation_las_to_EOV2014(self):
        output_filename = 'las_eov2014.las'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.las_data = LasPyConverter.LasPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOVc')
        self.las_data.Open()
        self.las_data.GetSourceScale()
        self.las_data.SetDestinationScale()
        self.las_data.TransformPointCloud()
        self.las_data.Close()
        self.las_compare = LasPyConverter.LasPyCompare(self.temp_file, self.compare_file)
        self.las_compare.OpenReanOnly()
        if not self.las_compare.is_equal():
            print(self.las_compare.ComparePointCloud())
        self.assertTrue(self.las_compare.is_equal())
        self.las_compare.Close()
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_las_transformation_las_to_EOV2009(self):
        output_filename = 'las_eov2009.las'
        self.compare_file = compare_file_path(output_filename)
        self.temp_file = temp_file_path(output_filename)
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.las_data = LasPyConverter.LasPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2009')
        self.las_data.Open()
        self.las_data.GetSourceScale()
        self.las_data.SetDestinationScale()
        self.las_data.TransformPointCloud()
        self.las_data.Close()
        self.las_compare = LasPyConverter.LasPyCompare(self.temp_file, self.compare_file)
        self.las_compare.OpenReanOnly()
        if not self.las_compare.is_equal():
            print(self.las_compare.ComparePointCloud())
        self.assertTrue(self.las_compare.is_equal())
        self.las_compare.Close()
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)


def testing_lactransformer():
    friendly_name = unittest.TestLoader().loadTestsFromTestCase(TestFriendlyName)
    assign_projection = unittest.TestLoader().loadTestsFromTestCase(TestAssignProjection)
    txt_transformation_wgs84geo = unittest.TestLoader().loadTestsFromTestCase(TestTxtTransformation_from_WGS84geo)
    pef_transformation_wgs84geo = unittest.TestLoader().loadTestsFromTestCase(TestPefTransformation_from_WGS84geo)
    lastxt_transformation_eov2009 = unittest.TestLoader().loadTestsFromTestCase(TestLasTxtTransformation_from_EOV2009)
    lastxt_transformation_javad_eov2009 = unittest.TestLoader().loadTestsFromTestCase(
        TestLasTxtTransformation_from_Javad_EOV2009)
    lastxt_transformation_wgs84geo = unittest.TestLoader().loadTestsFromTestCase(TestLasTxtTransformation_from_WGS84geo)
    las_transformation_wgs84geo = unittest.TestLoader().loadTestsFromTestCase(TestLasTransformation_from_WGS84geo)
    suite = unittest.TestSuite(
        [friendly_name, assign_projection, txt_transformation_wgs84geo, pef_transformation_wgs84geo,
         lastxt_transformation_eov2009, lastxt_transformation_javad_eov2009, lastxt_transformation_wgs84geo,
         las_transformation_wgs84geo])
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    testing_lactransformer()
