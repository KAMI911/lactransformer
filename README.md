# lactransformer - LAS & Co Transformer

Travis status: [![Build Status](https://travis-ci.org/KAMI911/lactransformer.svg?branch=master)](https://travis-ci.org/KAMI911/lactransformer)

LAS & Co Transformer is an utility to convert

* WGS84 (World Geodetic System 1984) Geocentric coordinate system
* WGS84 (World Geodetic System 1984) Geodetic coordinate system
* WGS84 (World Geodetic System 1984) Pseudo-Mercator -- Spherical Mercator, Google Maps, OpenStreetMap, Bing, ArcGIS, ESRI coordinate system
* ETRS89 (European Terrestrial Reference System 1989) Geocentric coordinate system
* ETRS89 (European Terrestrial Reference System 1989) Geodetic coordinate system
* Hungarian EOV (Egységes Országos Vetület) Projected 2014 coordinate system
* Hungarian EOV (Egységes Országos Vetület) Projected 2009 coordinate system
* SVY21 (Singapore) Projected coordinate system

in following formats:

* LiDAR LAS files
* Trajectory CSV file
* TerraPhoto Image List file
* Riegl Camera CSV file
* PEF file
* RTK CSV format (strtxt)

## Fork me on Github

https://github.com/KAMI911/lactransformer

## Donation

If you find this useful, please consider a donation:

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=RLQZ58B26XSLA)

## Supported projections

**WGS84**     (EPSG:4326) projection : http://epsg.io/4326/

**WGS84geo**  (EPSG:4978) projection : http://epsg.io/4978/

**WGS84PM**  (EPSG:3857) projection : http://epsg.io/3857/

**EOV**       (EPSG:23700) projection: http://epsg.io/23700/

* EOV - without correction
* EOV2014 - EOV2014 (EPSG:23700) projection with grid correction 2014 (2x2 km grid points)
http://www.agt.bme.hu/~bence/proj_poszter_3d.pdf

* (experimental) EOV2014fine - EOV2014 (EPSG:23700) projection with grid correction 2014 (1x1 km geoid grid points)
* EOV2009 - EOV2009 (EPSG:23700) projection with grid correction 2014 (2x2 km grid points)
http://www.agt.bme.hu/gis/workshop3/eloadasok/transzformacio.pdf
http://www.agt.bme.hu/~bence/proj_poszter_3d.pdf

**ETRS89**    (EPSG:4258) projection: http://epsg.io/4258/

**ETRS89geo** (EPSG:4936) projection: http://epsg.io/4936/

**SVY21**     (EPSG:3414) projection: http://epsg.io/3414

## EOV correction grid

Original download: http://www.agt.bme.hu/on_line/etrs2eov/etrs2eov_doc.html

Created by: Zoltán Siki <siki@agt.bme.hu> and Bence Takács <bence@agt.bme.hu>

Github page: https://github.com/OSGeoLabBp/eov2etrs

## Modules

pyproj - https://pypi.python.org/pypi/pyproj/

laspy - https://pypi.python.org/pypi/laspy/

numpy - https://pypi.python.org/pypi/numpy/

pandas - https://pypi.python.org/pypi/pandas/

## Installation

### Linux (Debian/Ubuntu/Linux Mint)

**Install Python 2.7, Numpy, Pandas, pyproj, laspy**

```
sudo apt-get install python2.7 python-numpy python-pandas
```

**Install pyproj**

```
wget https://github.com/jswhit/pyproj/archive/v1.9.5rel.zip
unzip v1.9.5rel.zip
cd pyproj-v1.9.5rel
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

**Install Pandas**

Download:

http://www.lfd.uci.edu/~gohlke/pythonlibs/#pandas

One of these files:

pandas-0.17.1-cp27-none-win_amd64.whl for 64 bit version

http://www.lfd.uci.edu/~gohlke/pythonlibs/2y3mcodk/pandas-0.17.1-cp27-none-win_amd64.whl

pandas-0.17.1-cp27-none-win32.whl for 32 bit version

http://www.lfd.uci.edu/~gohlke/pythonlibs/2y3mcodk/pandas-0.17.1-cp27-none-win32.whl

And install it:

```
C:\Python27\Scripts\pip.exe install "pandas-0.17.1-cp27-none-win_amd64.whl"
```

**Install pyproj**

Download:

http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyproj

One of these files:

pyproj-1.9.5.1-cp27-cp27m-win_amd64.whl for 64 bit version

http://www.lfd.uci.edu/%7Egohlke/pythonlibs/6kbpejrn/pyproj-1.9.5.1-cp27-cp27m-win_amd64.whl

pyproj‑1.9.5.1‑cp27‑none‑win32.whl for 32 bit version

http://www.lfd.uci.edu/%7Egohlke/pythonlibs/6kbpejrn/pyproj-1.9.5.1-cp27-cp27m-win32.whl

And install it:

```
C:\Python27\Scripts\pip.exe install "pyproj-1.9.5-cp27-none-win_amd64.whl"
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
