try:
    import logging
except ImportError as err:
    print("Error import module: " + str(err))
    exit(128)


def FriendlyName(input_format):
    # This function returns with friendly name of selected input format
    if input_format == 'las':
        return 'LAS PointCloud'
    elif input_format == 'laz':
        return 'LAZ PointCloud'
    elif input_format == 'txt':
        return 'PointText'
    elif input_format == 'lastxt':
        return 'PointText'
    elif input_format == 'iml':
        return 'TerraPhoto Image List'
    elif input_format == 'csv':
        return 'Riegl Camera CSV'
    elif input_format == 'pef':
        return 'PEF'