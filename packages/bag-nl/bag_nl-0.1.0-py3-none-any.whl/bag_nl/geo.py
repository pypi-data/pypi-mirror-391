__all__ = ['geo', 'geo2tile']

import json
import re

from .tile import tile

re_geo2 = re.compile(r'([0-9.]+) ([0-9.]+)'), r'\1,\2'
re_geo3 = re.compile(r'([0-9.]+) ([0-9.]+) ([0-9.]+)'), r'\1,\2'
re_rd = re.compile(r'([0-9.]+)[, ]([0-9.]+)')

def geo(data):
    match data:
        case {'punt':value}:
            return geo(value)
        case {'vlak':value}:
            return geo(value)
        case {'multivlak':value}:
            return geo(value)
        case {'Point':{'pos':value}}:
            return ','.join(value.split(' ')[0:2])
        case {'LineString':{'posList':value}}:
            return re.sub(*re_geo2, value)
        case {'Polygon':{'srsDimension':'3','exterior':{'LinearRing':{'posList':{'_':value}}}}}:
            return re.sub(*re_geo3, value)
        case {'Polygon':{'exterior':{'LinearRing':{'posList':{'_':value}}}}}:
            return re.sub(*re_geo2, value)
        case {'Polygon':{'exterior':{'LinearRing':{'posList':value}}}}:
            return re.sub(*re_geo2, value)
        case {'MultiSurface':{'surfaceMember':{'Polygon':{'exterior':{'LinearRing':{'posList':value}}}}}}:
            return re.sub(*re_geo2, value)
        case {'MultiSurface':{'surfaceMember':values}}:
            return ';'.join(geo(value) for value in values)
        case _:
            # MISSING
            return json.dumps(data, separators=(',', ':'))

def geo2tile(a, granularity=4):
    if match := re.search(re_rd, a):
        return tile(
            float(match[1]),
            float(match[2]),
            granularity=granularity
        )
