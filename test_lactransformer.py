import unittest
import os
import filecmp

from libs import FriendlyName, AssignProjection, TxtPanPyConverter


script_path = os.path.join(__file__)
script_path_local = os.path.dirname(script_path)


def input_file_path(filename):
    return os.path.join('.', 'test', 'input', filename)

def compare_file_path(filename):
    return os.path.join('.', 'test', 'compare', filename)


class TestFriendlyName(unittest.TestCase):
    def test_friendly_name_all(self):
        file_formats = {'las': 'LAS PointCloud', 'laz': 'LAZ (compressed) PointCloud', 'txt': 'Trajectory CSV file', 'lastxt': 'PointText',
                        'iml': 'TerraPhoto Image List', 'csv': 'Riegl Camera CSV', 'pef': 'PEF',
                        'strtxt': 'String PointText'}
        for type, type_name in file_formats.items():
            self.assertEqual(FriendlyName.FriendlyName(type), type_name)


class TestAssignProjection(unittest.TestCase):
    def setUp(self):
        nadgrids_EOV2009 = os.path.join(os.path.dirname(script_path), 'grid', 'etrs2eov_notowgs.gsb')
        geoidgrids_EOV2009 = os.path.join(os.path.dirname(script_path), 'grid', 'geoid_eht.gtx')
        nadgrids_EOV2014 = os.path.join(os.path.dirname(script_path), 'grid', 'etrs2eov_notowgs.gsb')
        geoidgrids_EOV2014 = os.path.join(os.path.dirname(script_path), 'grid', 'geoid_eht2014.gtx')
        geoidgrids_SVY21c = os.path.join(os.path.dirname(script_path), 'grid', 'geoid_svy21_2009.gtx')

        self.projections = {'WGS84': '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
                            'WGS84geo': '+proj=geocent +ellps=WGS84 +datum=WGS84 +units=m +no_defs',
                            'EOV': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                            'EOVc': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids_EOV2014 + ' +geoidgrids=' + geoidgrids_EOV2014 + ' +units=m +no_defs',
                            'EOV2014': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids_EOV2014 + ' +geoidgrids=' + geoidgrids_EOV2014 + ' +units=m +no_defs',
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

    def test_assign_projection_all(self):
        for projection, projection_string in self.projections.items():
            self.assertEqual(AssignProjection.AssignProjectionString(projection, script_path), projection_string)

    def test_assign_fallback_projection_all(self):
        for projection, projection_string in self.fallback_projections.items():
            self.assertEqual(AssignProjection.AssignFallbackProjectionString(projection, script_path),
                             projection_string)


class TestTxtTransformation_from_WGS84geo(unittest.TestCase):

    def setUp(self):
        self.input_file = input_file_path('txt_wgs84geo_bp.txt')

    def test_text_transformation_lastext_to_EOV2009(self):
        self.compare_file = compare_file_path('txt_eov2009_bp.txt')
        self.temp_file = 'test_txt_eov2009_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2009',
                                                             'txt')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)


    def test_text_transformation_lastext_to_EOV2014(self):
        self.compare_file = compare_file_path('txt_eov2014_bp.txt')
        self.temp_file = 'test_txt_eov2014_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2014',
                                                             'txt')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)


    def test_text_transformation_lastext_to_EOVc(self):
        self.compare_file = compare_file_path('txt_eov2014_bp.txt')
        self.temp_file = 'test_txt_eov2014_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOVc',
                                                             'txt')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_text_transformation_lastext_to_WGS84(self):
        self.compare_file = compare_file_path('txt_wgs84_bp.txt')
        self.temp_file = 'test_txt_wgs84_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'WGS84',
                                                             'txt')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

class TestPefTransformation_from_WGS84geo(unittest.TestCase):
    def setUp(self):
        self.input_file = os.path.join('.', 'test', 'input', 'pef_wgs84geo_bp.txt')

    def test_text_transformation_pef_to_EOV2009(self):
        self.compare_file = compare_file_path('pef_eov2009_bp.txt')
        self.temp_file = 'test_pef_eov2009_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2009',
                                                             'pef')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)


    def test_text_transformation_pef_to_EOV2014(self):
        self.compare_file = compare_file_path('pef_eov2014_bp.txt')
        self.temp_file = 'test_pef_eov2014_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2014',
                                                             'pef')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_text_transformation_pef_to_EOVc(self):
        self.compare_file = compare_file_path('pef_eov2014_bp.txt')
        self.temp_file = 'test_pef_eov2014_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOVc',
                                                             'pef')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_text_transformation_pef_to_WGS84(self):
        self.compare_file = compare_file_path('pef_wgs84_bp.txt')
        self.temp_file = 'test_pef_wgs84_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'WGS84',
                                                             'pef')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

class TestLasTxtTransformation_from_WGS84geo(unittest.TestCase):
    def setUp(self):
        self.input_file = os.path.join('.', 'test', 'input', 'lastxt_wgs84geo_bp.txt')

    def test_lastxt_transformation_pef_to_EOV2014(self):
        self.compare_file = compare_file_path('lastxt_eov2014_bp.txt')
        self.temp_file = 'test_lastxt_eov2014_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'WGS84geo', self.temp_file, 'EOV2014',
                                                             'lastxt', ' ')

class TestLasTxtTransformation_from_EOV2009(unittest.TestCase):
    def setUp(self):
        self.input_file = os.path.join('.', 'test', 'input', 'lastxt_eov2009_bp.txt')

    def test_lastxt_transformation_pef_to_WGS84geo(self):
        self.compare_file = compare_file_path('lastxt_wgs84geo_bp.txt')
        self.temp_file = 'test_lastxt_wgs84geo_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'EOV2009', self.temp_file, 'WGS84geo',
                                                             'lastxt', ' ')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_lastxt_transformation_pef_to_EOV2014(self):
        self.compare_file = compare_file_path('lastxt_eov2014_bp.txt')
        self.temp_file = 'test_lastxt_eov2014_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'EOV2009', self.temp_file, 'EOV2014',
                                                             'lastxt', ' ')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_lastxt_transformation_pef_to_EOVc(self):
        self.compare_file = compare_file_path('lastxt_eov2014_bp.txt')
        self.temp_file = 'test_lastxt_eovc_bp.txt'
        self.text_data = TxtPanPyConverter.TxtPanPyConverter(self.input_file, 'EOV2009', self.temp_file, 'EOVc',
                                                             'lastxt', ' ')
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        self.text_data.Open()
        self.text_data.Transform()
        self.text_data.Close()
        self.assertTrue(filecmp.cmp(self.temp_file, self.compare_file))
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)


def testing_lactransformer():
    friendly_name = unittest.TestLoader().loadTestsFromTestCase(TestFriendlyName)
    assign_projection = unittest.TestLoader().loadTestsFromTestCase(TestAssignProjection)
    txt_transformation_wgs84geo = unittest.TestLoader().loadTestsFromTestCase(TestTxtTransformation_from_WGS84geo)
    pef_transformation_wgs84geo = unittest.TestLoader().loadTestsFromTestCase(TestPefTransformation_from_WGS84geo)
    lastxt_transformation_eov2009 = unittest.TestLoader().loadTestsFromTestCase(TestLasTxtTransformation_from_EOV2009)
    lastxt_transformation_wgs84geo = unittest.TestLoader().loadTestsFromTestCase(TestLasTxtTransformation_from_WGS84geo)
    suite = unittest.TestSuite(
        [friendly_name, assign_projection, txt_transformation_wgs84geo, pef_transformation_wgs84geo, lastxt_transformation_eov2009, lastxt_transformation_wgs84geo])
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    testing_lactransformer()
