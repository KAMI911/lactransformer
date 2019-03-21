try:
    import traceback
    import logging
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    traceback.print_exc()
    exit(128)

    projections = {'WGS84': '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
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

    fallback_projections = {'WGS84': '',
                            'WGS84geo': '',
                            'EOV': '',
                            'EOVc': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                            'EOV2014': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                            'EOV2014fine': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                            'EOV2009': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                            'SVY21': '',
                            'SVY21c': '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs',
                            'ETRS89': '',
                            'ETRS89geo': ''}

    projectionnames = {'WGS84': 'WGS84', 'WGS84geo': 'WGS84geo', 'WGS84PM': 'WGS84PM', 'EOV': 'EOV',
                       'EOVc': 'EOV2014', 'EOV2014': 'EOV2014', 'EOV2014fine': 'EOV2014fine',
                       'EOV2009': 'EOV2009', 'EOVp': 'EOVp', 'SVY21': 'SVY21', 'SVY21c': 'SVY21',
                       'ETRS89': 'ETRS89', 'ETRS89geo': 'ETRS89geo'}
