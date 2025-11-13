__all__ = ['tile', 'tile2bbox']

import math
from inceptum import require

intoRD = require('geo.intoRD')

def tile(*xy, granularity=1):
    if len(xy) == 1: xy = intoRD(xy[0])
    return ''.join(chr(70 + math.floor(a / 100_000)) for a in xy) + ''.join(
        str(int(a / d) % 10)
        for (_, d) in
        zip(range(granularity), (10_000, 1_000, 100, 10, 1))
        for a in xy
    )

def tile2bbox(t, details=False):
    xy = [0, 0]
    size = 1_000_000
    for i in range(0, len(t), 2):
        size //= 10
        for j in range(2):
            xy[j] += size * (ord(t[i + j]) - (0x30 if i else 70))
    bbox = [xy, [xy[0] + size, xy[1] + size]]
    if details:
        return {
            'tile': t,
            'bbox': bbox,
            'granularity': len(t) // 2 - 1,
        }
    return bbox
