offsetX = 84.7
offsetY = 29.8
offsetZ = -43.5

mindiffX = 0
maxdiffX = 0
mindiffY = 0
maxdiffY = 0
mindiffZ = 0
maxdiffZ = 0

with open('point-wgs84geo-hun.txt', 'r') as point_wgs_gc_txtfile:
    with open('point-eov-hun.txt', 'r') as point_eov_txtfile:
        with open('point-eov-eht2-3.0-hun.txt', 'r') as point_eov_eht2_3_0_txtfile:
            with open('grid-wgs-gc-eov-eht2-3.0-hun.txt', 'w') as grid_wgs_gc_eov_eht2_3_0_txtfile:
                index = 1
                for wgsline in point_wgs_gc_txtfile:
                    eovline = point_eov_txtfile.readline()
                    eoveht2_3_0_line = point_eov_eht2_3_0_txtfile.readline()
                    point, wgsX, wgsY, wgsZ = wgsline.split()
                    point, eovX, eovY, eovZ = eovline.split()
                    point, eoveht2X, eoveht2Y, eoveht2Z = eoveht2_3_0_line.split()
                    diffX = float(eovX) + offsetX - float(eoveht2X)
                    diffY = float(eovY) + offsetY - float(eoveht2Y)
                    diffZ = float(eovZ) + offsetZ - float(eoveht2Z)
                    if index == 1:
                        mindiffX = diffX
                        maxdiffX = diffX
                        mindiffY = diffY
                        maxdiffY = diffY
                        mindiffZ = diffZ
                        maxdiffZ = diffZ

                    print('%s %s %s %s %s %s' % (wgsX, wgsY, wgsZ, diffX, diffY, diffZ))
                    grid_wgs_gc_eov_eht2_3_0_txtfile.write(
                        '%s %s %s %s %s %s\r\n' % (wgsX, wgsY, wgsZ, diffX, diffY, diffZ))
                    if mindiffX < diffX:
                        mindiffX = diffX
                    if maxdiffX > diffX:
                        maxdiffX = diffX

                    if mindiffY < diffY:
                        mindiffY = diffY
                    if maxdiffY > diffY:
                        maxdiffY = diffY

                    if mindiffZ < diffZ:
                        mindiffZ = diffZ
                    if maxdiffZ > diffZ:
                        maxdiffZ = diffZ

                    index = index + 1

print('Diffs minX/maxX: %s/%s minY/maxY: %s/%s minZ/maxZ: %s/%s' % (
    mindiffX, maxdiffX, mindiffY, maxdiffY, mindiffZ, maxdiffZ))
