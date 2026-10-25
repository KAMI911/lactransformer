#!/usr/bin/python

try:
    import traceback
    from pyproj import Transformer
except ImportError as err:
    print(f'Error {__name__} import module: {err}')
    traceback.print_exc()
    exit(128)

WGS84_PROJ = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
WGS84GEO_PROJ = '+proj=geocent +ellps=WGS84 +datum=WGS84 +no_defs'
EOV_PROJ = ('+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778'
            ' +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs')

wgs84_to_wgs84geo = Transformer.from_crs(WGS84_PROJ, WGS84GEO_PROJ, always_xy=True)
wgs84_to_eov = Transformer.from_crs(WGS84_PROJ, EOV_PROJ, always_xy=True)


def frange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


def main():
    with open('plain-wgs84longlat-hun.txt', 'w') as wgs_ll_txtfile, \
         open('plain-wgs84geo-hun.txt', 'w') as wgs_gc_txtfile, \
         open('point-wgs84geo-hun.txt', 'w') as point_wgs_gc_txtfile, \
         open('ppac-wgs84geo-hun', 'w') as ppac_wgs_gc_txtfile, \
         open('plain-eov-hun.txt', 'w') as eov_txtfile, \
         open('point-eov-hun.txt', 'w') as point_eov_txtfile, \
         open('ppac-eov-hun', 'w') as ppac_eov_txtfile:

        index = 1
        ppac_wgs_gc_txtfile.write('Time[s],X[m],Y[m],Z[m],Roll[deg],Pitch[deg],Yaw[deg]\r\n')
        ppac_eov_txtfile.write('Time[s],X[m],Y[m],Z[m],Roll[deg],Pitch[deg],Yaw[deg]\r\n')
        # Budapest:
        # 47.3900, 47.5700, 0.001
        # 18.9300,  19.1900, 0.001
        # Hungary:
        # 45.7800, 48.6000, 0.01
        # 16.1200,  22.9100, 0.01
        for fi in frange(45.56000000, 48.91000000, 0.009):
            for la in frange(16.10000000, 23.07000000, 0.0013):
                for he in range(150, 151, 1):
                    ## WGS84 longlat
                    print(f'O: {la:.8f}, {fi:.8f}, {he:.8f}')
                    wgs_ll_txtfile.write(f'{la:.4f} {fi:.4f} {he:.1f}\n')
                    ## WGS84 geocent
                    XProjected, YProjected, ZProjected = wgs84_to_wgs84geo.transform(la, fi, he)
                    print(f'P: {XProjected:.8f}, {YProjected:.8f}, {ZProjected:.8f}')
                    wgs_gc_txtfile.write(f'{XProjected:.8f}  {YProjected:.8f}  {ZProjected:.8f}\n')
                    point_wgs_gc_txtfile.write(
                        f'PONT              {XProjected:.3f}      {YProjected:.3f}      {ZProjected:.3f}\n')
                    ppac_wgs_gc_txtfile.write(
                        f'{index},{XProjected:.14f},{YProjected:.14f},{ZProjected:.14f},1,1,1\n')
                    ## EOV
                    XEOVProjected, YEOVProjected, ZEOVProjected = wgs84_to_eov.transform(la, fi, he)
                    print(f'E: {XEOVProjected:.8f}, {YEOVProjected:.8f}, {ZEOVProjected:.8f}')
                    eov_txtfile.write(
                        f'{XEOVProjected:.8f}  {YEOVProjected:.8f}  {ZEOVProjected:.8f}\n')
                    point_eov_txtfile.write(
                        f'PONT              {XEOVProjected:.3f}      {YEOVProjected:.3f}      {ZEOVProjected:.3f}\n')
                    ppac_eov_txtfile.write(
                        f'{index},{XEOVProjected:.14f},{YEOVProjected:.14f},{ZEOVProjected:.14f},1,1,1\n')
                    index += 1


if __name__ == '__main__':
    main()
