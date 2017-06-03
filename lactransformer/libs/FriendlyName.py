try:
    import logging
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    exit(128)

friendly_names = {'las': 'LAS PointCloud', 'laz': 'LAZ (compressed) PointCloud', 'txt': 'Trajectory CSV file',
                  'lastxt': 'PointText', 'iml': 'TerraPhoto Image List', 'csv': 'Riegl Camera CSV', 'pef': 'PEF',
                  'strtxt': 'String PointText', 'listtxt': 'List PointText'}


def FriendlyName(input_format):
    # This function returns with friendly name of selected input format
    return friendly_names[input_format] if input_format in friendly_names else None
