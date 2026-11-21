"""Legge i testi delle schede e produce data/schede_prato_all.json (solo comune di Prato)."""
import re, glob, json
out = []
for f in sorted(glob.glob('data/schede/s_*.txt'), key=lambda x: int(re.findall(r'\d+', x)[0])):
    t = open(f, errors='ignore').read()
    def g(k):
        m = re.search(r'^\s*' + k + r':[ \t]*(.*)$', t, re.M)
        return m.group(1).strip() if m else ''
    if g('Comune') != 'Prato':
        continue
    m = re.search(r'Descrizione:(.*?)(?:\n\s*Riferimenti:|\n\s*Fonti archivistiche:|\n\s*Fonti bibliografiche:|\n\s*Fonti orali:|\Z)', t, re.S)
    desc = re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''
    out.append(dict(n=int(g('Numero scheda') or re.findall(r'\d+', f)[0]), nome=g('Nome Scheda'), loc=g('Localita'),
                    ubi=g('Ubicazione'), tip=g('Tipologia'), stato=g('Stato attuale'), desc=desc, full=t))
json.dump(out, open('data/schede_prato_all.json', 'w'), ensure_ascii=False)
print(len(out), 'schede del comune di Prato')
