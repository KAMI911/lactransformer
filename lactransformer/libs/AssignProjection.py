try:
    import traceback
    import os
    import logging

    from . import supported_projections
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    traceback.print_exc()
    exit(128)


def grid_path(filename):
    return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'grid', filename))


def AssignProjectionString(projection, proc_name = 'Unknown'):
    # Init does not work on Linux
    # WGS84 = Proj(init='EPSG:4326')
    # WGS84Geo = Proj(init='EPSG:4328')

    nadgrids_EOV2009 = grid_path('etrs2eov_notowgs.gsb')
    geoidgrids_EOV2009 = grid_path('geoid_eht.gtx')
    nadgrids_EOV2014 = grid_path('etrs2eov_notowgs.gsb')
    geoidgrids_EOV2014 = grid_path('geoid_eht2014.gtx')
    geoidgrids_EOV2014fine = grid_path('geoid_eht2014_fine.gtx')
    geoidgrids_SVY21c = grid_path('geoid_svy21_2009.gtx')

    if projection in ['EOVc', 'EOV2014']:
        if os.path.isfile(nadgrids_EOV2014) and os.path.isfile(geoidgrids_EOV2014):
            logging.info('[{0}] Found all required grids ...'.format(proc_name))
        else:
            logging.error('Cannot found %s and/or %s grids.' % (nadgrids_EOV2014, geoidgrids_EOV2014))
            exit(2)
    elif projection == 'EOV2014fine':
        if os.path.isfile(nadgrids_EOV2014) and os.path.isfile(geoidgrids_EOV2014fine):
            logging.info('[{0}] Found all required grids ...'.format(proc_name))
        else:
            logging.error('Cannot found %s and/or %s grids.' % (nadgrids_EOV2014, geoidgrids_EOV2014fine))
            exit(2)
    elif projection == 'EOV2009':
        if os.path.isfile(nadgrids_EOV2009) and os.path.isfile(geoidgrids_EOV2009):
            logging.info('[{0}] Found all required grids ...'.format(proc_name))
        else:
            logging.error('Cannot found %s and/or %s grids.' % (nadgrids_EOV2009, geoidgrids_EOV2009))
            exit(2)
    elif projection == 'EOVp':  # do not use
        if os.path.isfile(nadgrids_EOV2009):
            logging.info('[{0}] Found all required grids ...'.format(proc_name))
        else:
            logging.error('Cannot found %s grid.' % (nadgrids_EOV2009))
            exit(2)
    elif projection == 'SVY21c':
        if os.path.isfile(geoidgrids_SVY21c):
            logging.info('[{0}] Found all required grids ...'.format(proc_name))
        else:
            logging.error('Cannot found %s grid.' % (geoidgrids_SVY21c))
            exit(2)
    if projection in supported_projections.projections:
        return supported_projections.projections[projection]
    else:
        return False


def AssignFallbackProjectionString(projection):
    # Init does not work on Linux
    # WGS84 = Proj(init='EPSG:4326')
    # WGS84Geo = Proj(init='EPSG:4328')

    if projection in supported_projections.fallback_projections:
        return supported_projections.fallback_projections[projection]
    else:
        return False


def AssignProjectionName(projection):
    if projection in supported_projections.projectionnames:
        return supported_projections.projectionnames[projection]
    else:
        return False
