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

    if projection == 'WGS84':
        projectionstring = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    elif projection == 'WGS84geo':
        projectionstring = '+proj=geocent +ellps=WGS84 +datum=WGS84 +units=m +no_defs'
    elif projection == 'WGS84PM':
        projectionstring = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs'
    elif projection == 'EOV':
        projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs'
    elif projection in ['EOVc', 'EOV2014']:
        nadgrids = grid_path('etrs2eov_notowgs.gsb')
        geoidgrids = grid_path('geoid_eht2014.gtx')
        if os.path.isfile(nadgrids) and os.path.isfile(geoidgrids):
            logging.info('Found all required grids ...')
            projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids + ' +geoidgrids=' + geoidgrids + ' +units=m +no_defs'
        else:
            logging.error('Cannot found %s and/or %s grids.' % (nadgrids, geoidgrids))
            exit(2)
    elif projection in ['EOV2014fine']:
        nadgrids = grid_path('etrs2eov_notowgs.gsb')
        geoidgrids = grid_path('geoid_eht2014_fine.gtx')
        if os.path.isfile(nadgrids) and os.path.isfile(geoidgrids):
            logging.info('Found all required grids ...')
            projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids + ' +geoidgrids=' + geoidgrids + ' +units=m +no_defs'
        else:
            logging.error('Cannot found %s and/or %s grids.' % (nadgrids, geoidgrids))
            exit(2)
    elif projection == 'EOV2009':
        nadgrids = grid_path('etrs2eov_notowgs.gsb')
        geoidgrids = grid_path('geoid_eht.gtx')
        if os.path.isfile(nadgrids) and os.path.isfile(geoidgrids):
            logging.info('Found all required grids ...')
            projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids + ' +geoidgrids=' + geoidgrids + ' +units=m +no_defs'
        else:
            logging.error('Cannot found %s and/or %s grids.' % (nadgrids, geoidgrids))
            exit(2)
    elif projection == 'EOVp':  # do not use
        nadgrids = grid_path('etrs2eov_notowgs.gsb')
        if os.path.isfile(nadgrids):
            logging.info('Found all required grids ...')
            projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +nadgrids=' + nadgrids + ' +units=m +no_defs'
        else:
            logging.error('Cannot found %s grid.' % (nadgrids))
            exit(2)
    elif projection == 'SVY21':
        projectionstring = '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs'
    elif projection == 'SVY21c':
        geoidgrids = grid_path('geoid_svy21_2009.gtx')
        if os.path.isfile(geoidgrids):
            logging.info('Found all required grids ...')
            projectionstring = '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +geoidgrids=' + geoidgrids + ' +units=m +no_defs'
        else:
            logging.error('Cannot found %s grid.' % (geoidgrids))
            exit(2)
    elif projection == 'ETRS89':
        projectionstring = '+proj=longlat +ellps=GRS80 +no_defs'
    elif projection == 'ETRS89geo':
        projectionstring = '+proj=geocent +ellps=GRS80 +units=m +no_defs'
    return projectionstring


def AssignFallbackProjectionString(projection):
    # Init does not work on Linux
    # WGS84 = Proj(init='EPSG:4326')
    # WGS84Geo = Proj(init='EPSG:4328')

    if projection == 'WGS84':
        fallback_projectionstring = ''
    elif projection == 'WGS84geo':
        fallback_projectionstring = ''
    elif projection == 'WGS84PM':
        fallback_projectionstring = ''
    elif projection == 'EOV':
        fallback_projectionstring = ''
    elif projection in ['EOVc', 'EOV2014']:
        fallback_projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs'
    elif projection in ['EOV2014fine']:
        fallback_projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs'
    elif projection == 'EOV2009':
        fallback_projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs'
    elif projection == 'EOVp':  # do not use
        fallback_projectionstring = '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs'
    elif projection == 'SVY21':
        fallback_projectionstring = ''
    elif projection == 'SVY21c':
        fallback_projectionstring = '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs'
    elif projection == 'ETRS89':
        fallback_projectionstring = ''
    elif projection == 'ETRS89geo':
        fallback_projectionstring = ''
    return fallback_projectionstring


def AssignProjectionName(projection):
    if projection == 'WGS84':
        fallback_projectionstring = 'WGS84'
    elif projection == 'WGS84geo':
        fallback_projectionstring = 'WGS84geo'
    elif projection == 'WGS84PM':
        fallback_projectionstring = 'WGS84PM'
    elif projection == 'EOV':
        fallback_projectionstring = 'EOV'
    elif projection in ['EOVc', 'EOV2014']:
        fallback_projectionstring = 'EOV2014'
    elif projection in ['EOV2014fine']:
        fallback_projectionstring = 'EOV2014fine'
    elif projection == 'EOV2009':
        fallback_projectionstring = 'EOV2009'
    elif projection == 'EOVp':  # do not use
        fallback_projectionstring = 'EOVp'
    elif projection == 'SVY21':
        fallback_projectionstring = 'SVY21'
    elif projection == 'SVY21c':
        fallback_projectionstring = 'SVY21'
    elif projection == 'ETRS89':
        fallback_projectionstring = 'ETRS89'
    elif projection == 'ETRS89geo':
        fallback_projectionstring = 'ETRS89geo'
    return fallback_projectionstring
