try:
    import traceback
    import logging
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    traceback.print_exc()
    exit(128)

projectionnames = {'WGS84': 'WGS84', 'WGS84geo': 'WGS84geo', 'WGS84PM': 'WGS84PM', 'EOV': 'EOV',
                   'EOVc': 'EOV2014', 'EOV2014': 'EOV2014', 'EOV2014fine': 'EOV2014fine',
                   'EOV2009': 'EOV2009', 'EOVp': 'EOVp', 'SVY21': 'SVY21', 'SVY21c': 'SVY21',
                   'ETRS89': 'ETRS89', 'ETRS89geo': 'ETRS89geo'}
