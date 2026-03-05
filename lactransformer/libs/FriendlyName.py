try:
    import traceback
    from typing import Optional
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)

friendly_names = {
    'las':     'LAS PointCloud',
    'laz':     'LAZ (compressed) PointCloud',
    'txt':     'Trajectory CSV file',
    'lastxt':  'PointText',
    'iml':     'TerraPhoto Image List',
    'csv':     'Riegl Camera CSV',
    'pef':     'PEF',
    'strtxt':  'String PointText',
    'listtxt': 'List PointText',
}


def FriendlyName(input_format: str) -> Optional[str]:
    return friendly_names.get(input_format)
