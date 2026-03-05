offsetX = 84.7
offsetY = 29.8
offsetZ = -43.5

mindiffX = mindiffY = mindiffZ = 0
maxdiffX = maxdiffY = maxdiffZ = 0

with open('point-wgs84geo-hun.txt', 'r') as point_wgs_gc_txtfile, \
     open('point-eov-hun.txt', 'r') as point_eov_txtfile, \
     open('point-eov-eht2-3.0-hun.txt', 'r') as point_eov_eht2_3_0_txtfile, \
     open('grid-wgs-gc-eov-eht2-3.0-hun.txt', 'w') as grid_wgs_gc_eov_eht2_3_0_txtfile:

    for index, wgsline in enumerate(point_wgs_gc_txtfile, start=1):
        eovline = point_eov_txtfile.readline()
        eoveht2_3_0_line = point_eov_eht2_3_0_txtfile.readline()
        _, wgsX, wgsY, wgsZ = wgsline.split()
        _, eovX, eovY, eovZ = eovline.split()
        _, eoveht2X, eoveht2Y, eoveht2Z = eoveht2_3_0_line.split()
        diffX = float(eovX) + offsetX - float(eoveht2X)
        diffY = float(eovY) + offsetY - float(eoveht2Y)
        diffZ = float(eovZ) + offsetZ - float(eoveht2Z)

        if index == 1:
            mindiffX = maxdiffX = diffX
            mindiffY = maxdiffY = diffY
            mindiffZ = maxdiffZ = diffZ

        mindiffX, maxdiffX = min(mindiffX, diffX), max(maxdiffX, diffX)
        mindiffY, maxdiffY = min(mindiffY, diffY), max(maxdiffY, diffY)
        mindiffZ, maxdiffZ = min(mindiffZ, diffZ), max(maxdiffZ, diffZ)

        line = f'{wgsX} {wgsY} {wgsZ} {diffX} {diffY} {diffZ}'
        print(line)
        grid_wgs_gc_eov_eht2_3_0_txtfile.write(line + '\r\n')

print(f'Diffs minX/maxX: {mindiffX}/{maxdiffX}'
      f' minY/maxY: {mindiffY}/{maxdiffY}'
      f' minZ/maxZ: {mindiffZ}/{maxdiffZ}')
