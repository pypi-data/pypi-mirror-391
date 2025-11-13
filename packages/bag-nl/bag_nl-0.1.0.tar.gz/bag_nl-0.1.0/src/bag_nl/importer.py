__all__ = ['importer']

import json
from glob import glob
import importlib
from itertools import islice
from pathlib import Path
import sys
from zipfile import ZipFile
from dpath import get
from tqdm import tqdm

from inceptum import config, require

from .geo import geo, geo2tile

# FIXME
connect = require('database.connect')
julian_day = require('time.julian_day')
array = require('array')
xml = require('xml')

def importer(db, collections=None, test=False):
    Path(db).touch()
    if not collections: collections = ['text', 'wpl', 'wpl_gem', 'opr', 'num', 'vbo', 'vbo_purpose', 'pnd', 'vbo_pnd', 'sta', 'lig']
    if isinstance(collections, str): collections = collections.split(',')
    for collection in collections:
        print(f"-- {collection}", file=sys.stderr)
        rows = globals()[collection](read(collection))
        if test:
            rows = islice(rows, 10 if isinstance(test, bool) else test)
        with connect(db) as db:
            with open(importlib.resources.files("bag_nl") / 'sqlite' / f"{collection}.sql") as file:
                db.script(file.read())
            fields = next(rows)
            db.bulk(
                f"""
                    insert into
                        bag_{collection}
                        ({','.join(fields)})
                    values
                        ({','.join('?' for _ in fields)})
                """,
                tqdm(rows, miniters=1_000)
            )

def num(stream):
    yield ('id', 'postcode', 'number', 'extra', 'letter', 'type', 'opr', 'date')
    for data in stream:
        yield (
            int(data['identificatie']['_']),
            data.get('postcode'), # sometimes missing
            int(data['huisnummer']),
            data.get('huisnummertoevoeging'),
            data.get('huisletter'),
            data['typeAdresseerbaarObject'][0:1],
            int(get(data, ('ligtAan', 'OpenbareRuimteRef', '_'))),
            jd(data),
        )

def vbo(stream):
    yield ('id', 'num', 'geo', 'area', 'tile', 'date')
    for data in stream:
        yield (
            int(data['identificatie']['_']),
            int(get(data, ('heeftAlsHoofdadres', 'NummeraanduidingRef', '_'))),
            (g := geo(data['geometrie'])),
            int(data['oppervlakte']),
            geo2tile(g),
            jd(data),
        )

def vbo_purpose(stream):
    yield ('vbo', 'purpose')
    for data in stream:
        for purpose in array(data['gebruiksdoel']):
            yield (
                int(data['identificatie']['_']),
                TEXT[purpose]
            )

def pnd(stream):
    yield ('id', 'geo', 'year', 'status', 'date')
    for data in stream:
        yield (
            int(data['identificatie']['_']),
            geo(data['geometrie']),
            int(data['oorspronkelijkBouwjaar']),
            TEXT[data['status']],
            jd(data),
        )

def vbo_pnd(stream):
    yield ('vbo', 'pnd')
    for data in stream:
        for pand in array(get(data, ('maaktDeelUitVan', 'PandRef'))):
            yield (
                int(data['identificatie']['_']),
                int(pand['_']),
            )

def sta(stream):
    yield ('id', 'num', 'status', 'geo', 'tile', 'date')
    for data in stream:
        yield (
            int(data['identificatie']['_']),
            int(get(data, ('heeftAlsHoofdadres', 'NummeraanduidingRef', '_'))),
            TEXT[data['status']],
            (g := geo(data['geometrie'])),
            geo2tile(g),
            jd(data),
        )

lig = sta

def opr(stream):
    yield ('id', 'name', 'type', 'status', 'wpl', 'date')
    for data in stream:
        yield (
            int(data['identificatie']['_']),
            data['naam'],
            TEXT[data['type']],
            TEXT[data['status']],
            int(get(data, ('ligtIn', 'WoonplaatsRef', '_'))),
            jd(data),
        )

def wpl(stream):
    yield ('id', 'name', 'geo', 'tile', 'date')
    for data in stream:
        if data['status'] != 'Woonplaats aangewezen': continue
        yield (
            int(data['identificatie']['_']),
            data['naam'],
            (g := geo(data['geometrie'])),
            geo2tile(g, granularity=1),
            jd(data),
        )

def wpl_gem(stream):
    yield ('wpl', 'gem')
    for data in stream:
        yield (
            int(get(data, ('gerelateerdeWoonplaats', 'identificatie'))),
            int(get(data, ('gerelateerdeGemeente', 'identificatie'))),
        )

def text(_stream):
    yield ('text', 'id')
    yield from TEXT.items()

def read(collection):
    match collection:
        case 'text':
            return
        case 'wpl_gem':
            filename = glob('GEM-WPL*')[0]
        case _:
            filename = glob(f"9999*{collection.split('_')[0].upper()}*")[0]
    with ZipFile(filename, 'r') as zipfile:
        for name in zipfile.namelist():
            with zipfile.open(name) as file:
                if collection == 'wpl_gem':
                    for data in xml.parse(file, level=4):
                        if not data: continue
                        if get(data, ('tijdvakgeldigheid', 'einddatumTijdvakGeldigheid'), default=None): continue
                        yield data
                else:
                    for data in xml.parse(file, level=3):
                        if not data: continue
                        if not (data := data.get('bagObject')): continue
                        data = data[next(iter(data))]
                        if get(data, ('voorkomen', 'Voorkomen', 'eindGeldigheid'), default=None): continue
                        yield data

def jd(data):
    return julian_day(get(data, ('voorkomen', 'Voorkomen', 'beginGeldigheid')))

TEXT = {
    'Bouw gestart': 1,
    'Bouwvergunning verleend': 2,
    'Niet gerealiseerd pand': 3,
    'Pand buiten gebruik': 4,
    'Pand gesloopt': 5,
    'Pand in gebruik': 6,
    'Pand in gebruik (niet ingemeten)': 7,
    'Pand ten onrechte opgevoerd': 8,
    'Sloopvergunning verleend': 9,
    'Verbouwing pand': 10,
    'Administratief gebied': 21,
    'Kunstwerk': 22,
    'Landschappelijk gebied': 23,
    'Spoorbaan': 24,
    'Terrein': 25,
    'Water': 26,
    'Weg': 27,
    'Naamgeving ingetrokken': 41,
    'Naamgeving uitgegeven': 42,
    'Plaats aangewezen': 61,
    'Plaats ingetrokken': 62,
    'bijeenkomstfunctie': 81,
    'celfunctie': 82,
    'gezondheidszorgfunctie': 83,
    'industriefunctie': 84,
    'kantoorfunctie': 85,
    'logiesfunctie': 86,
    'onderwijsfunctie': 87,
    'overige gebruiksfunctie': 88,
    'sportfunctie': 89,
    'winkelfunctie': 90,
    'woonfunctie': 91,
}
