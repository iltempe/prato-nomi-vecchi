"""Costruisce base.json (base cartografica OSM semplificata) e luoghi.geojson (toponimi)."""
import json, re, math, sys
D = '/home/claude/data/'
OUT = '/home/claude/site/'

# ---------------- base cartografica ----------------
def dp(pts, eps):
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0]-a[0], b[1]-a[1]
    L = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(pts)-1):
        p = pts[i]
        d = abs(dy*(p[0]-a[0]) - dx*(p[1]-a[1])) / L
        if d > dmax: dmax, idx = d, i
    if dmax > eps:
        return dp(pts[:idx+1], eps)[:-1] + dp(pts[idx:], eps)
    return [a, b]

def line(g, eps=0.00003):
    pts = [(p['lat'], p['lon']) for p in g if p]
    pts = dp(pts, eps)
    return [[round(p[0], 5), round(p[1], 5)] for p in pts]

roads = json.load(open('/tmp/roads_snap.json'))
cls = {'motorway':'A','trunk':'A','motorway_link':'A','trunk_link':'A','primary':'B','primary_link':'B',
       'secondary':'C','secondary_link':'C','tertiary':'C','tertiary_link':'C'}
base = {'A':[], 'B':[], 'C':[], 'D':[], 'river':[], 'gora':[], 'rail':[], 'park':[], 'water':[], 'confine':[], 'labels':[]}
named = {}
for e in roads:
    if 'geometry' not in e: continue
    hw = e['tags'].get('highway')
    c = cls.get(hw, 'D')
    l = line(e['geometry'], 0.00003 if c != 'D' else 0.00004)
    if len(l) < 2: continue
    nm = e['tags'].get('name')
    base[c].append(l)
    if nm and c in 'ABC':
        named.setdefault(nm, []).append(l)
# etichette: punto medio del tratto più lungo per ciascun nome principale
for nm, ls in named.items():
    best = max(ls, key=len)
    m = best[len(best)//2]
    base['labels'].append([m[0], m[1], nm])

other = json.load(open(D+'osm/other.json'))['elements']
for e in other:
    t = e.get('tags', {})
    if e['type'] == 'relation':
        if t.get('boundary') == 'administrative':
            for m in e.get('members', []):
                if m.get('role') == 'outer' and 'geometry' in m:
                    base['confine'].append(line(m['geometry'], 0.00008))
        elif t.get('leisure') == 'park':
            for m in e.get('members', []):
                if m.get('role') == 'outer' and 'geometry' in m:
                    base['park'].append(line(m['geometry'], 0.00005))
        continue
    if 'geometry' not in e: continue
    w = t.get('waterway')
    if w == 'river':
        base['river'].append([line(e['geometry']), t.get('name', '')])
    elif w in ('canal', 'ditch', 'drain', 'stream'):
        base['gora'].append([line(e['geometry'], 0.00004), t.get('name', '')])
    elif t.get('railway') == 'rail':
        base['rail'].append(line(e['geometry']))
    elif t.get('leisure') == 'park':
        base['park'].append(line(e['geometry'], 0.00005))
    elif t.get('natural') == 'water':
        base['water'].append(line(e['geometry'], 0.00005))

# ---------------- toponimi ----------------
schede = {s['n']: s for s in json.load(open(D+'schede_prato_all.json'))}
geo = json.load(open(D+'geo.json'))
gb = json.load(open(D+'geo_gb.json'))
try: geo_all = json.load(open(D+'geo_all.json'))
except Exception: geo_all = {}

UFFICIALE = {587, 780, 1040, 1119, 1136, 552, 1150, 1096, 1097, 751, 754, 1293, 1111, 558, 1112}
PREC_Z = {559, 647, 786, 805, 812, 813, 815, 847, 1096, 1129, 1130, 1132, 1261, 960, 843, 1090, 114}
PREC_P = {752, 753, 757, 1122, 1135, 1295, 550, 1134, 1132, 420}
OVR = {1039: geo['592'], 843: {'lat': 43.8805, 'lon': 11.0647}, 552: geo['1150'], 114: geo.get('1114')}
TIPCAT = {'Toponimo':'popolare','Borgo':'popolare','Luogo legato a leggende, tradizioni popolari':'leggenda',
  'Colonica':'case','Villa':'case','Villa fattoria':'case','Complesso colonico':'case','Fattoria':'case',
  'Lavatoio':'acqua','Mulino':'acqua','Pozzo':'acqua','Ponte':'acqua','Guado':'acqua','Fonte':'acqua','Pescaia':'acqua','Sorgente':'acqua',
  'Tabernacolo':'sacro','Chiesa':'sacro','Edificio religioso':'sacro',
  'Fabbrica':'lavoro','Fornace':'lavoro','Cava':'lavoro','Ghiacciaia':'lavoro','Frantoio':'lavoro'}

def first_sentences(t, n=320):
    t = t.strip()
    if len(t) <= n: return t
    cut = t[:n]
    k = max(cut.rfind('. '), cut.rfind('; '))
    return (cut[:k+1] if k > 120 else cut.rsplit(' ', 1)[0] + '…')

feats = []; nogeo = []
def add(lat, lon, props):
    geom = {'type':'Point','coordinates':[round(lon,6), round(lat,6)]} if lat is not None else None
    feats.append({'type':'Feature','geometry':geom,'properties':props})

def pos(n):
    k = str(n)
    if k in gb: return gb[k], 'P'
    if n in OVR and OVR[n]: g = OVR[n]
    else: g = geo.get(k)
    if g: return g, ('Z' if n in PREC_Z else ('P' if n in PREC_P else 'V'))
    g = geo_all.get(k)
    if g: return g, ('V' if g.get('how') == 'via' else 'Z')
    return None, None

def tidy(x):
    x = x.strip()
    return x[:1].upper() + x[1:] if x.islower() else x

for n, s in sorted(schede.items()):
    g, prec = pos(n)
    tip = s['tip']
    cat = 'ufficializzato' if n in UFFICIALE else TIPCAT.get(tip, 'memoria')
    nome = re.sub(r'\s*\(\?\)', '', s['nome']).strip() or '(senza nome)'
    props = {'id': f'mc{n}', 'nome': nome, 'cat': cat, 'tipo': tip or 'non indicato',
        'zona': tidy(s['loc']), 'dove': '' if s['ubi'].startswith('Comune:') else re.sub(r'\?+|\(\?\?\)','',s['ubi']).strip(),
        'testo': first_sentences(s['desc']) or '(scheda senza descrizione)', 'stato': s['stato'],
        'prec': prec or 'N', 'fonte': 'Provincia di Prato – Mappe dei Cittadini, scheda %d' % n,
        'url': 'http://mapserver.provincia.prato.it/prv_po/Mappecittadini/pdfs/Mappecittadini_scheda_%d.pdf' % n}
    if g: add(g['lat'], g['lon'], props)
    else: add(None, None, props); nogeo.append(n)
print('senza posizione', nogeo, file=sys.stderr)

# microtoponimi citati nelle testimonianze delle schede
def P(n): return pos(n)[0]
TEST = [
 ('Via della Goraccia', 1084, 'oggi via dell\'Alberaccio, Galciana', 'Vecchio nome di via dell\'Alberaccio: lungo la strada correva una fossa, e la casa colonica del "Cafisso" era il Podere Goraccia.', 'V'),
 ('Il Regnaino', 552, 'Santa Maria a Colonica', 'A Santa Maria a Colonica la via lungo la Gora Bandita era conosciuta come "il Regnaino"; a San Giorgio era via della Gora Bandita.', 'Z'),
 ('Le svolte del Frulla', 561, 'via del Ferro, Santa Maria a Colonica', 'Tratto tortuoso della vecchia via del Ferro, chiamato così dal soprannome del contadino che abitava lì vicino.', 'Z'),
 ('Le Buche', 582, 'dietro la fornace Briganti, via del Popolino (San Giusto)', 'Terreni scavati per prendere la terra dei mattoni; riempiti dalla pioggia, d\'estate ci si andava a fare il bagno.', 'V'),
 ('Le Carra', 1293, 'Grignano, sull\'attuale via Roma', 'Zona di Grignano dove arrivava lo stradello di Cortevecchia.', 'Z'),
 ('Mezzana di sotto', 457, 'Mezzana, via Lunga', 'Il modo in cui si chiamava la parte bassa di Mezzana, che si ritrovava la sera al Pratello.', 'Z'),
]
for i, (nome, n, dove, testo, prec) in enumerate(TEST):
    g = P(n)
    if not g: continue
    add(g['lat'] + 0.0004, g['lon'] - 0.0004, {'id': f'tm{i}', 'nome': nome, 'cat': 'testimonianze', 'tipo': 'Microtoponimo',
        'zona': tidy(schede[n]['loc']), 'dove': dove, 'testo': testo, 'prec': prec,
        'fonte': 'Testimonianze nella scheda %d (%s), Mappe dei Cittadini' % (n, schede[n]['nome']),
        'url': 'http://mapserver.provincia.prato.it/prv_po/Mappecittadini/pdfs/Mappecittadini_scheda_%d.pdf' % n})

W_MURA = 'https://it.wikipedia.org/wiki/Mura_di_Prato'
W_CR = 'https://www.crprato.it/sito/index.php?option=com_content&view=article&id=821:i-valletti-del-comune-di-prato&catid=46:prato-nel-mondo&Itemid=222'
W_TT = 'https://tuttatoscana.net/storia-e-microstoria-2/prato-medievale-lo-sviluppo-urbano/'
W_VIC = 'https://www.welcome2prato.com/2020/05/vicoli-centro-storico-prato.html'
STORICO = [
 ('H1','Borgo al Cornio','via Garibaldi','Il primo nucleo abitato di Prato, attorno alla pieve di Santo Stefano: il toponimo "Cornio" compare già nell\'880 ed è legato alla biforcazione delle strade antiche. L\'attuale via Garibaldi ne ricalca il borgo.','V',W_TT,'tuttatoscana.net – Prato medievale'),
 ('H2','Via del Pozzo Nuovo','oggi via Verdi','Antico nome dell\'attuale via Verdi.','V',W_VIC,'welcome2prato – vicoli del centro storico'),
 ('H3','Porta San Giovanni','di fronte a via Santo Stefano','Una delle otto porte della seconda cerchia (1175–1196). Le porte davano il nome alle otto circoscrizioni della "terra" di Prato.','V',W_MURA,'Wikipedia – Mura di Prato'),
 ('H4','Porta Tiezi','in via Garibaldi','Porta della seconda cerchia; con Capo di Ponte apparteneva al Quartiere di San Marco.','V',W_MURA,'Wikipedia – Mura di Prato'),
 ('H5','Porta Capo di Ponte','in via Cairoli','Porta della seconda cerchia (Quartiere di San Marco).','V',W_MURA,'Wikipedia – Mura di Prato'),
 ('H6','Porta a Corte','tra piazza delle Carceri e viale Piave','Porta della seconda cerchia, aperta davanti alla corte del palazzo dei conti Alberti.','P',W_MURA,'Wikipedia – Mura di Prato'),
 ('H7','Porta Santa Trinita (cerchia del XII sec.)','in via Santa Trinita','Porta della seconda cerchia, da non confondere con l\'omonima porta trecentesca ancora esistente.','V',W_MURA,'Wikipedia – Mura di Prato'),
 ('H8','Porta Fuia','in via del Pellegrino','Porta della seconda cerchia (Quartiere di Santa Maria).','V',W_MURA,'Wikipedia – Mura di Prato'),
 ('H9','Porta Gualdimare','in via Cesare Guasti','Porta della seconda cerchia (Quartiere di Santa Maria), legata alla famiglia dei Gualdimareschi.','V',W_MURA,'Wikipedia – Mura di Prato'),
 ('H10','Porta al Travaglio','in via San Michele','Porta della seconda cerchia (Quartiere di San Giovanni, poi Santo Stefano).','V',W_MURA,'Wikipedia – Mura di Prato'),
 ('H11','Porta di Rusticuzzo','presso piazza Lippi','Porta aggiuntiva aperta nelle mura antiche.','P',W_CR,'crprato.it – Rappresentanza storica della Terra di Prato'),
 ('H12','Porta di San Jacopo','presso via Dante','Porta aggiuntiva aperta nelle mura antiche.','V',W_CR,'crprato.it – Rappresentanza storica della Terra di Prato'),
 ('H13','Porta al Serraglio','dove oggi c\'è la stazione Porta al Serraglio','Porta della cerchia trecentesca demolita nell\'Ottocento per la ferrovia Firenze–Pistoia: la stazione ne ha preso il posto e il nome.','P',W_MURA,'Wikipedia – Mura di Prato'),
 ('H15','Archi di Frascati','tra via Pomeria e via Frascati','Apertura nelle mura del 1934 ("Porta Frascati"), nella zona detta mura del Luterano, in fondo a via dei Sassoli.','P',W_MURA,'Wikipedia – Mura di Prato'),
 ('H16','Spazzavento','Monte Le Coste','Nome con cui i pratesi chiamano il monte Le Coste, dove si trova il mausoleo di Curzio Malaparte.','P','https://www.paolonori.it/argomenti/repertorio-dei-matti-della-citta-di-prato/','Paolo Nori – Repertorio dei matti della città di Prato'),
 ('H18','Bastione di San Giusto','presso via Cavour','Uno dei sei bastioni cinquecenteschi (Forche, Santa Chiara, Santa Trinita, San Giusto, Civette, Giudei).','P',W_MURA,'Wikipedia – Mura di Prato'),
]
off = {}
for hid, nome, dove, testo, prec, url, fonte in STORICO:
    g = geo.get(hid)
    if not g: print('senza coord', hid, file=sys.stderr); continue
    k = (round(g['lat'],4), round(g['lon'],4)); off[k] = off.get(k, -1) + 1
    d = off[k] * 0.00018
    add(g['lat'] + d, g['lon'] + d, {'id': hid.lower(), 'nome': nome, 'cat': 'storico', 'tipo': 'Luogo storico', 'zona': 'Centro storico' if hid != 'H16' else 'Figline / Calvana',
        'dove': dove, 'testo': testo, 'prec': prec, 'fonte': fonte, 'url': url})

# vecchi nomi già taggati in OSM
names = json.load(open(D+'osm/names.json'))['elements']
SKIP_LOC = {'Ponte Datini', 'Duomo', 'Villa del Palco'}
grp = {}
for e in names:
    t = e['tags']
    old, loc = t.get('old_name'), t.get('loc_name')
    if not (old or loc) or (loc in SKIP_LOC and not old): continue
    if 'Protche' in (old or '') or 'Pandolfino' in (old or ''): continue  # solo varianti di grafia
    c = e.get('center') or ({'lat': e['lat'], 'lon': e['lon']} if 'lat' in e else None)
    if not c: continue
    key = (t.get('name', ''), old or '', loc or '')
    grp.setdefault(key, {'pts': [], 'el': e})['pts'].append(c)
for (nm, old, loc), v in grp.items():
    pts = v['pts']; e = v['el']
    lat = sum(p['lat'] for p in pts)/len(pts); lon = sum(p['lon'] for p in pts)/len(pts)
    if nm == 'Viale Leonardo da Vinci':
        lat, lon = 43.8688, 11.0891
    is_street = 'highway' in e['tags']
    vecchio = old or loc
    tipo = 'vecchio nome' if old else 'nome locale'
    attuale = nm or '(senza nome attuale)'
    add(lat, lon, {'id': f"osm{e['type'][0]}{e['id']}", 'nome': vecchio, 'cat': 'osm', 'tipo': tipo,
        'zona': '', 'dove': 'oggi: ' + attuale,
        'testo': f'In OpenStreetMap questo {"tratto di strada" if is_street else "luogo"} ha già il tag {"old_name" if old else "loc_name"} = "{vecchio}".',
        'prec': 'P', 'fonte': f"OpenStreetMap {e['type']} {e['id']}", 'url': f"https://www.openstreetmap.org/{e['type']}/{e['id']}"})

# distanzia i punti che cadono sulla stessa coordinata (stessa via/zona geocodificata)
from collections import defaultdict
grpc = defaultdict(list)
for f in feats:
    if not f['geometry']: continue
    lo, la = f['geometry']['coordinates']; grpc[(round(la,4), round(lo,4))].append(f)
for k, fs in grpc.items():
    if len(fs) < 2: continue
    for i, f in enumerate(fs):
        a = 2*math.pi*i/len(fs) + 0.3; r = 0.0007
        if math.cos(a) < -0.2: f['properties']['side'] = 'L'
        lo, la = f['geometry']['coordinates']
        f['geometry']['coordinates'] = [round(lo + r*math.cos(a)/0.72, 6), round(la + r*math.sin(a), 6)]
for f in feats:
    n = f['properties']['nome']; f['properties']['nome'] = n[:1].upper() + n[1:]
# riclassificazione tematica delle voci OSM (e di alcune storiche)
OSMCAT = {
 'w8024608':'popolare',
 'w26578187':'vie','w31968912':'vie','w32555763':'vie','w32763709':'vie',
 'w282393407':'memoria','w996107453':'memoria',
 'w315505951':'case','w325088199':'case','w691296300':'case','w693893909':'case','w995868456':'case','w1004045103':'case','r12953111':'case',
 'w1008208832':'acqua','w1233821538':'acqua','w1531931926':'acqua',
 'w316236067':'storico','w700927600':'storico','w701080873':'storico','w704641869':'storico','w1132427481':'storico','r9748677':'storico','r14031781':'storico',
 'r5876529':'sacro','r9741504':'sacro',
 'r9754477':'lavoro','r13504226':'lavoro','r13530039':'lavoro'}
for f in feats:
    p = f['properties']
    if p['cat'] == 'osm':
        k = p['id'][3:]
        if k not in OSMCAT: raise SystemExit('voce OSM non classificata: ' + p['id'])
        p['cat'] = OSMCAT[k]
        p['tipo'] = ('Vecchio nome' if p['tipo'] == 'vecchio nome' else 'Nome locale') + ' (OpenStreetMap)'
        if p['cat'] == 'storico': p['zona'] = 'Centro storico'
    if p['id'] in ('h2', 'tm0'): p['cat'] = 'vie'
    if p['id'] == 'h16': p['cat'] = 'popolare'
import os
os.makedirs(OUT, exist_ok=True)
json.dump(base, open(OUT+'base.json', 'w'), separators=(',', ':'), ensure_ascii=False)
json.dump({'type':'FeatureCollection','features':feats}, open(OUT+'luoghi.geojson', 'w'), ensure_ascii=False, indent=0)
from collections import Counter
print('punti', len(feats), Counter(f['properties']['cat'] for f in feats))
print({k: len(v) for k, v in base.items()}, os.path.getsize(OUT+'base.json')//1024, 'KB')
