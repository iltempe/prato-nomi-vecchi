"""Converte le coordinate Gauss-Boaga (EPSG:3003) presenti nelle note delle schede in WGS84 -> data/geo_gb.json.
Le coordinate fuori dal territorio (formato non riconosciuto) vengono scartate e geocodificate con geo_all.py."""
import json, re
from pyproj import Transformer
T = Transformer.from_crs('EPSG:3003', 'EPSG:4326', always_xy=True)
gb, bad = {}, []
for o in json.load(open('data/schede_prato_all.json')):
    m = re.search(r'Coordinata Est:\s*([\d.,]+)\s*Coordinata Nord:\s*([\d.,]+)', o['full'])
    if not m: continue
    e, n = [float(x.replace(',', '.')) for x in m.groups()]
    lon, lat = T.transform(e, n)
    if 43.78 < lat < 43.96 and 10.98 < lon < 11.21: gb[str(o['n'])] = dict(lat=lat, lon=lon, how='gb')
    else: bad.append(o['n'])
json.dump(gb, open('data/geo_gb.json', 'w'))
print('convertite', len(gb), '- formato non riconosciuto', len(bad))
