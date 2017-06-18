try:
    import os
    import logging
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    exit(128)


def grid_path(filename):
    return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'grid', filename))


def AssignProjectionString(projection):
    # Init does not work on Linux
    # WGS84 = Proj(init='EPSG:4326')
    # WGS84Geo = Proj(init='EPSG:4328')

    nadgrids_EOV2009 = grid_path('etrs2eov_notowgs.gsb')
    geoidgrids_EOV2009 = grid_path('geoid_eht.gtx')
    nadgrids_EOV2014 = grid_path('etrs2eov_notowgs.gsb')
    geoidgrids_EOV2014 = grid_path('geoid_eht2014.gtx')
    geoidgrids_EOV2014fine = grid_path('geoid_eht2014_fine.gtx')
    geoidgrids_SVY21c = grid_path('geoid_svy21_2009.gtx')

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

    if projection in ['EOVc', 'EOV2014']:
        if os.path.isfile(nadgrids_EOV2009) and os.path.isfile(geoidgrids_EOV2009):
            logging.info('Found all required grids ...')
        else:
            logging.error('Cannot found %s and/or %s grids.' % (nadgrids_EOV2009, geoidgrids_EOV2009))
            exit(2)
    elif projection in ['EOV2014fine']:
        if os.path.isfile(nadgrids_EOV2009) and os.path.isfile(geoidgrids_EOV2014fine):
            logging.info('Found all required grids ...')
        else:
            logging.error('Cannot found %s and/or %s grids.' % (nadgrids_EOV2009, geoidgrids_EOV2014fine))
            exit(2)
    elif projection == 'EOV2009':
        if os.path.isfile(nadgrids_EOV2009) and os.path.isfile(geoidgrids_EOV2009):
            logging.info('Found all required grids ...')
        else:
            logging.error('Cannot found %s and/or %s grids.' % (nadgrids, geoidgrids))
            exit(2)
    elif projection == 'EOVp':  # do not use
        if os.path.isfile(nadgrids_EOV2009):
            logging.info('Found all required grids ...')
        else:
            logging.error('Cannot found %s grid.' % (nadgrids))
            exit(2)
    elif projection == 'SVY21c':
        if os.path.isfile(geoidgrids_SVY21c):
            logging.info('Found all required grids ...')
        else:
            logging.error('Cannot found %s grid.' % (geoidgrids))
            exit(2)
    if projection in projections:
        return projections[projection]
    else:
        return False


def AssignFallbackProjectionString(projection):
    # Init does not work on Linux
    # WGS84 = Proj(init='EPSG:4326')
    # WGS84Geo = Proj(init='EPSG:4328')

    fallback_projections = {'WGS84': '',
                            'WGS84geo': '',
                            'EOV': '',
                            'EOVc': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                            'EOV2014': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                            'EOV2009': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
                            'SVY21': '',
                            'SVY21c': '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs',
                            'ETRS89': '',
                            'ETRS89geo': ''}
    if projection in fallback_projections:
        return fallback_projections[projection]
    else:
        return False


def AssignProjectionName(projection):
    fallback_projectionstring = {'WGS84': 'WGS84', 'WGS84geo': 'WGS84geo', 'WGS84PM': 'WGS84PM', 'EOV': 'EOV',
                                 'EOVc': 'EOV2014', 'EOV2014': 'EOV2014', 'EOV2014fine': 'EOV2014fine',
                                 'EOV2009': 'EOV2009', 'EOVp': 'EOVp', 'SVY21': 'SVY21', 'SVY21c': 'SVY21',
                                 'ETRS89': 'ETRS89', 'ETRS89geo': 'ETRS89geo'}
    if projection in fallback_projectionstring:
        return fallback_projectionstring[projection]
    else:
        return False
