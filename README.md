# wgslas2eovlas

Utility to convert geocentric WGS84 (World Geodetic System 1984) projected LiDAR LAS files to Hungarian EOV (Egységes Országos Vetület) projected LiDAR LAS files

## Fork me on Github

https://github.com/KAMI911/wgslas2eovlas

## EOV correction grid

Original download: http://www.agt.bme.hu/on_line/etrs2eov/etrs2eov_doc.html

Created by: Zoltán Siki <siki@agt.bme.hu>
            Bence Takács <bence@agt.bme.hu>

## Supported projections

**WGS84**    (EPSG:2326) projection : http://spatialreference.org/ref/epsg/4326/

**WGS84geo** (EPSG:4978) projection : http://spatialreference.org/ref/epsg/4978/

**EOV**      (EPSG:23700) projection: http://spatialreference.org/ref/epsg/hd72-eov/


## Installation

### Linux (Debian/Ubuntu/Linux Mint)

**Install Python 2.7, Numpy, pyproj**

*sudo apt-get install python2.7 python-numpy python-pyproj*

**Install laspy**

wget https://github.com/grantbrown/laspy/archive/master.zip

unzip master.zip

cd laspy-master.zip


