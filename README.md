# wgslas2eovlas

Utility to convert geocentric WGS84 (World Geodetic System 1984) projected LiDAR LAS files to Hungarian EOV (Egységes Országos Vetület) projected LiDAR LAS files

## Fork me on Github

https://github.com/KAMI911/wgslas2eovlas

## EOV correction grid

Original download: http://www.agt.bme.hu/on_line/etrs2eov/etrs2eov_doc.html

Created by: Zoltán Siki <siki@agt.bme.hu> and Bence Takács <bence@agt.bme.hu>

## Supported projections

**WGS84**    (EPSG:2326) projection : http://spatialreference.org/ref/epsg/4326/

**WGS84geo** (EPSG:4978) projection : http://spatialreference.org/ref/epsg/4978/

**EOV**      (EPSG:23700) projection: http://spatialreference.org/ref/epsg/hd72-eov/


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

numpy-1.9.2+mkl-cp27-none-win32.whl for 32 bit version

numpy-1.9.2+mkl-cp27-none-win_amd64.whl for 64 bit version

And install it:

```
C:\Python27\Scripts\pip.exe install "numpy-1.9.2+mkl-cp27-none-win_amd64.whl"
```

**Install pyproj**

```
pip install pyproj
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
wgslas2eovlas.py -i wgs84.las -o eov.las
```

### A directory of LAS files

Convert all LAS files in a directory from WGS84 to EOV using 2 cores:

```
wgslas2eovlas.py -i wgs84dir/ -o eovdir/ -cores 2
```

Converting LAZ file is currently not supported.

### One Trajectory (CSV) text file

Convert Trajectory (CSV) text file from WGS84 to EOV:

```
wgslas2eovlas.py -i wgs84_trj.txt -o eov_trj.txt -input_format=txt
```

### A directory of Trajectory (CSV) text files

Convert all Trajectory (CSV) text files in a directory from WGS84 to EOV using 2 cores:

```
wgslas2eovlas.py -i wgs84dir_trj/ -o eovdir_trj/ -cores 2 -input_format=txt
```

