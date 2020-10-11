from setuptools import setup

version = '0.1.0'

# dependencies
with open('requirements.txt') as f:
    deps = f.read().splitlines()

setup(
    name='lactransformer',
    version='1.0.0',
    description='LAS & Co Transformer is an utility to convert WGS84 (geocentric & geodetic), ETRS89 (geocentric & geodetic), Hungarian EOV, SVY21 (Singapore) projections from/to LiDAR LAS, trajectory CSV, TerraPhoto Image List, Riegl Camera CSV, PEF file formats.',
    license='MPL',
    keywords='gis lidar las eov vitel vitel2009 vitel2014',
    author='Kalman Szalai - KAMI',
    author_email='kami911@gmail.com',
    url='https://github.com/KAMI911/lactransformer',
    py_modules=['lactransformer.lactransformer', 'lactransformer.libs.AssignProjection', 'lactransformer.libs.FileListWithProjection', 'lactransformer.libs.FriendlyName', 'lactransformer.libs.LasPyConverter', 'lactransformer.libs.Logging', 'lactransformer.libs.PefFile', 'lactransformer.libs.TransformerCommandLine', 'lactransformer.libs.TransformerWorkflow', 'lactransformer.libs.TxtNumPyConverter', 'lactransformer.libs.TxtPanPyConverter', 'lactransformer.libs.TxtPyConverter', 'test_lactransformer'],
    test_suite='test_lactransformer.testing_lactransformer',
    install_requires=deps,
    entry_points={'console_scripts':['lactransformer = lactransformer:main',]},
    data_files = [("grid", ["lactransformer/grid/etrs2eov_notowgs.gsb", "lactransformer/grid/geoid_eht2014_fine.gtx", "lactransformer/grid/geoid_eht2014.gtx", "lactransformer/grid/geoid_eht.gtx", "lactransformer/grid/geoid_svy21_2009.gtx"])],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MPL License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: GIS'
    ],
)
