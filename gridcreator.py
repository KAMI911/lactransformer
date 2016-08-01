try:
    from pyproj import Proj, transform
except ImportError as err:
    print('Error {0} import module: {1}'.format(__name__, err))
    exit(128)

WGS84 = Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
WGS84Geo = Proj('+proj=geocent +ellps=WGS84 +datum=WGS84 +no_defs')
EOV = Proj(
    '+proj=somerc +lat_0=47.14439372222222 +lon_0=19.04857177777778 +k_0=0.99993 +x_0=650000 +y_0=200000 +ellps=GRS67 +units=m +no_defs')


def frange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


with open('plain-wgs84longlat-hun.txt', 'w') as wgs_ll_txtfile:
    with open('plain-wgs84geo-hun.txt', 'w') as wgs_gc_txtfile:
        with open('point-wgs84geo-hun.txt', 'w') as point_wgs_gc_txtfile:
            with open('ppac-wgs84geo-hun', 'w') as ppac_wgs_gc_txtfile:
                with open('plain-eov-hun.txt', 'w') as eov_txtfile:
                    with open('point-eov-hun.txt', 'w') as point_eov_txtfile:
                        with open('ppac-eov-hun', 'w') as ppac_eov_txtfile:
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
                                        print('O: %.8f, %.8f, %.8f' % (la, fi, he))
                                        wgs_ll_txtfile.write('%.4f %.4f %.1f\n' % (la, fi, he))
                                        ## WGS84 geocent
                                        XProjected, YProjected, ZProjected = transform(WGS84, WGS84Geo, la, fi, he)
                                        print('P: %.8f, %.8f, %.8f' % (XProjected, YProjected, ZProjected))
                                        wgs_gc_txtfile.write(
                                            '%.8f  %.8f  %.8f\n' % (XProjected, YProjected, ZProjected))
                                        point_wgs_gc_txtfile.write('PONT              %.3f      %.3f      %.3f\n' % (
                                            XProjected, YProjected, ZProjected))
                                        ppac_wgs_gc_txtfile.write('%s,%.14f,%.14f,%.14f,1,1,1\n' % (
                                            index, XProjected, YProjected, ZProjected))
                                        ## EOV
                                        XEOVProjected, YEOVProjected, ZEOVProjected = transform(WGS84, EOV, la, fi, he)
                                        print('E: %.8f, %.8f, %.8f' % (XEOVProjected, YEOVProjected, ZEOVProjected))
                                        eov_txtfile.write(
                                            '%.8f  %.8f  %.8f\n' % (XEOVProjected, YEOVProjected, ZEOVProjected))
                                        point_eov_txtfile.write('PONT              %.3f      %.3f      %.3f\n' % (
                                            XEOVProjected, YEOVProjected, ZEOVProjected))
                                        ppac_eov_txtfile.write('%s,%.14f,%.14f,%.14f,1,1,1\n' % (
                                            index, XEOVProjected, YEOVProjected, ZEOVProjected))
                                        index = index + 1
