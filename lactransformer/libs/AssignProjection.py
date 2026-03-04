try:
    import traceback
    import logging
    from pathlib import Path

    from . import supported_projections
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)


def grid_path(filename: str) -> Path:
    return Path(__file__).parent.parent / 'grid' / filename


def AssignProjectionString(projection: str, proc_name: str = 'Unknown') -> str:
    nadgrids_EOV2009 = grid_path('etrs2eov_notowgs.gsb')
    geoidgrids_EOV2009 = grid_path('geoid_eht.gtx')
    nadgrids_EOV2014 = grid_path('etrs2eov_notowgs.gsb')
    geoidgrids_EOV2014 = grid_path('geoid_eht2014.gtx')
    geoidgrids_EOV2014fine = grid_path('geoid_eht2014_fine.gtx')
    geoidgrids_SVY21c = grid_path('geoid_svy21_2009.gtx')

    projections = {
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

    if projection in ['EOVc', 'EOV2014']:
        if nadgrids_EOV2014.is_file() and geoidgrids_EOV2014.is_file():
            logging.info(f'[{proc_name}] Found all required grids ...')
        else:
            raise FileNotFoundError(
                f'Cannot find required grid files: {nadgrids_EOV2014} and/or {geoidgrids_EOV2014}')
    elif projection == 'EOV2014fine':
        if nadgrids_EOV2014.is_file() and geoidgrids_EOV2014fine.is_file():
            logging.info(f'[{proc_name}] Found all required grids ...')
        else:
            raise FileNotFoundError(
                f'Cannot find required grid files: {nadgrids_EOV2014} and/or {geoidgrids_EOV2014fine}')
    elif projection == 'EOV2009':
        if nadgrids_EOV2009.is_file() and geoidgrids_EOV2009.is_file():
            logging.info(f'[{proc_name}] Found all required grids ...')
        else:
            raise FileNotFoundError(
                f'Cannot find required grid files: {nadgrids_EOV2009} and/or {geoidgrids_EOV2009}')
    elif projection == 'EOVp':  # do not use
        if nadgrids_EOV2009.is_file():
            logging.info(f'[{proc_name}] Found all required grids ...')
        else:
            raise FileNotFoundError(f'Cannot find required grid file: {nadgrids_EOV2009}')
    elif projection == 'SVY21c':
        if geoidgrids_SVY21c.is_file():
            logging.info(f'[{proc_name}] Found all required grids ...')
        else:
            raise FileNotFoundError(f'Cannot find required grid file: {geoidgrids_SVY21c}')

    return projections.get(projection, False)


def AssignFallbackProjectionString(projection: str) -> str:
    fallback_projections = {
        'WGS84':      '',
        'WGS84geo':   '',
        'EOV':        '',
        'EOVc':       '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                      ' +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
        'EOV2014':    '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                      ' +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
        'EOV2014fine': '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                       ' +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
        'EOV2009':    '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993'
                      ' +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs',
        'SVY21':      '',
        'SVY21c':     '+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1'
                      ' +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs',
        'ETRS89':     '',
        'ETRS89geo':  '',
    }
    return fallback_projections.get(projection, False)


def AssignProjectionName(projection: str) -> str:
    if projection in supported_projections.projectionnames:
        return supported_projections.projectionnames[projection]
    return False
