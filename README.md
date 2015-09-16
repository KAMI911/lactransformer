# lactransformer - LAS & Co Transformer

LAS & Co Transformer is an utility to convert

* WGS84 (World Geodetic System 1984) Geocentric coordinate system
* WGS84 (World Geodetic System 1984) Geodetic coordinate system
* ETRS89 (European Terrestrial Reference System 1989) Geocentric coordinate system
* ETRS89 (European Terrestrial Reference System 1989) Geodetic coordinate system
* Hungarian EOV (Egységes Országos Vetület) Projected coordinate system

in following formats:

* LiDAR LAS files
* Trajectory CSV file
* TerraPhoto Image List file
* Riegl Camera CSV file
* PEF file

## Fork me on Github

https://github.com/KAMI911/lactransformer

## Supported projections

**WGS84**     (EPSG:4326) projection : http://epsg.io/4326/

**WGS84geo**  (EPSG:4978) projection : http://epsg.io/4978/

**EOV**       (EPSG:23700) projection: http://epsg.io/23700/

**ETRS89**    (EPSG:4258) projection: http://epsg.io/4258/

**ETRS89geo** (EPSG:4936) projection: http://epsg.io/4936/

## EOV correction grid

Original download: http://www.agt.bme.hu/on_line/etrs2eov/etrs2eov_doc.html

Created by: Zoltán Siki <siki@agt.bme.hu> and Bence Takács <bence@agt.bme.hu>

Github page: https://github.com/OSGeoLabBp/eov2etrs

## Modules

pyproj - https://pypi.python.org/pypi/pyproj/

laspy - https://pypi.python.org/pypi/laspy/

numpy - https://pypi.python.org/pypi/numpy/

## Installation

### Linux (Debian/Ubuntu/Linux Mint)

**Install Python 2.7, Numpy, pyproj**

```
sudo apt-get install python2.7 python-numpy
```

**Install pyproj**

```
wget https://github.com/jswhit/pyproj/archive/v1.9.4rel.zip
unzip v1.9.4rel.zip
cd pyproj-v1.9.4rel
python setup.py build
sudo python setup.py install
```

**Install laspy**

```
wget https://github.com/grantbrown/laspy/archive/master.zip
unzip master.zip
cd laspy-master
python setup.py build
sudo python setup.py install
```

### Windows

**Install Python 2.7**

We prefer 64 bit AMD64 version.

https://www.python.org/downloads/

**Install pip**

Installation manual: https://pip.pypa.io/en/latest/installing.html

Download: https://bootstrap.pypa.io/get-pip.py

```
python get-pip.py
```

**Install Numpy**

Download:

http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy

One of these files:

numpy-1.9.2+mkl-cp27-none-win_amd64.whl for 64 bit version

http://www.lfd.uci.edu/~gohlke/pythonlibs/3i673h27/numpy-1.9.2+mkl-cp27-none-win_amd64.whl

numpy-1.9.2+mkl-cp27-none-win32.whl for 32 bit version

http://www.lfd.uci.edu/~gohlke/pythonlibs/3i673h27/numpy-1.9.2+mkl-cp27-none-win32.whl

And install it:

```
C:\Python27\Scripts\pip.exe install "numpy-1.9.2+mkl-cp27-none-win_amd64.whl"
```

**Install pyproj**

Download:

http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyproj

One of these files:

pyproj-1.9.4-cp27-none-win_amd64.whl for 64 bit version

http://www.lfd.uci.edu/%7Egohlke/pythonlibs/3i673h27/pyproj-1.9.4-cp27-none-win_amd64.whl

pyproj‑1.9.4‑cp27‑none‑win32.whl for 32 bit version

http://www.lfd.uci.edu/~gohlke/pythonlibs/3i673h27/pyproj-1.9.4-cp27-none-win32.whl

And install it:

```
C:\Python27\Scripts\pip.exe install "pyproj-1.9.4-cp27-none-win_amd64.whl"
```

**Install laspy**

Download: https://github.com/grantbrown/laspy/archive/master.zip

Unzip master.zip file

Enter to the folder of laspy-master

And build it:

```
python setup.py build
```

Then install it:

```
python setup.py install
```

## Usage

### One LAS file

Convert LAS file from WGS84 to EOV:

```
lactransformer.py -i wgs84.las -o eov.las
```

### A directory of LAS files

Convert all LAS files in a directory from WGS84 to EOV using 2 cores:

```
lactransformer.py -i wgs84dir/ -o eovdir/ -cores 2
```

Converting LAZ file is currently not supported.

### One Trajectory (CSV) text file

Convert Trajectory (CSV) text file from WGS84 to EOV:

```
lactransformer.py -i wgs84_trj.txt -o eov_trj.txt -input_format=txt
```

### A directory of Trajectory (CSV) text files

Convert all Trajectory (CSV) text files in a directory from WGS84 to EOV using 2 cores:

```
lactransformer.py -i wgs84dir_trj/ -o eovdir_trj/ -cores 2 -input_format=txt
```
