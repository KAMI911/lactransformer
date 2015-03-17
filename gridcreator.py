from pyproj import Proj, transform

WGS84 = Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
WGS84Geo = Proj('+proj=geocent +ellps=WGS84 +datum=WGS84 +no_defs')
EOV = Proj('+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs')

def frange(start, stop, step):
  r = start
  while r < stop:
    yield r
    r += step

with open('wgs84longlat-hun.txt', 'w') as wgslltxtfile:
  with open('wgs84geo-hun.txt', 'w') as wgsgctxtfile:
    with open('eovhun.txt', 'w') as eovtxtfile:
      for fi in frange (45.7800, 48.6000, 0.1):
        for la in frange (16.1200,  22.9100, 0.1):
          for he in range (100, 200, 10):
            print ('O: %s %s %s' % (fi, la, he))
            wgslltxtfile.write('%s %s %s\r\n' % (fi, la, he))
            XProjected, YProjected,ZProjected = transform(WGS84, WGS84Geo, la, fi, he)
            print ('P: %s, %s, %s' % (XProjected, YProjected, ZProjected))
            wgsgctxtfile.write('PONT  %s  %s  %s\r\n' % (XProjected, YProjected, ZProjected))
            XEOVProjected, YEOVProjected, ZEOVProjected = transform(WGS84Geo, EOV, XProjected, YProjected, ZProjected)
            print ('E: %s, %s, %s' % (XEOVProjected, YEOVProjected, ZEOVProjected))
            eovtxtfile.write('%s  %s  %s\r\n' % (XEOVProjected, YEOVProjected, ZEOVProjected))

