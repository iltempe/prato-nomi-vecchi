import json,time,re,urllib.request,urllib.parse,urllib.error
D='/home/claude/data/'
sch=json.load(open(D+'schede_prato_all.json'))
old=json.load(open(D+'geo.json'))
gb=json.load(open(D+'geo_gb.json'))
try: out=json.load(open(D+'geo_all.json'))
except: out={}
def nom(q):
  for att in range(6):
    try:
      url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode(dict(q=q,format='json',limit=1,countrycodes='it',viewbox='10.98,43.95,11.20,43.78',bounded=1))
      r=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'prato-vecchi-nomi/0.1 (civic map)'}),timeout=30))
      time.sleep(1.3); return r[0] if r else None
    except urllib.error.HTTPError as e:
      if e.code==429: time.sleep(10*(att+1)); continue
      raise
    except Exception: time.sleep(5)
  return None
def clean(s):
  s=re.sub(r'\(.*?\)|\?+','',s); s=s.replace('Comune: Prato','').strip(' ,;/-')
  return s
for s in sch:
  k=str(s['n'])
  if k in out or k in gb: continue
  if k in old and old[k]: out[k]=dict(old[k],how='manuale'); continue
  ubi=clean(s['ubi']); loc=clean(s['loc'])
  qs=[]
  if ubi:
    first=re.split(r'[/;]| angolo | ang\. | e via ',ubi)[0].strip()
    if loc: qs.append(f'{first}, {loc}, Prato')
    qs.append(f'{first}, Prato')
  if loc:
    for l in re.split(r'[/,]',loc): 
      if l.strip(): qs.append(f'{l.strip()}, Prato')
  hit=None
  for q in qs:
    r=nom(q)
    if r and '59100' in r.get('display_name','') or (r and 'Prato' in r.get('display_name','')):
      hit=dict(q=q,lat=float(r['lat']),lon=float(r['lon']),display=r['display_name'],how='via' if q.startswith(('via','Via','piazza','Piazza','viale','Viale','vicolo','Vicolo','strada','Strada')) or (ubi and q.startswith(first)) else 'zona'); break
  out[k]=hit
  print(k,s['nome'][:30],'|',(hit or {}).get('q'),'|',(hit or {}).get('display','—')[:70],flush=True)
  json.dump(out,open(D+'geo_all.json','w'),ensure_ascii=False)
json.dump(out,open(D+'geo_all.json','w'),ensure_ascii=False)
print('done',sum(1 for v in out.values() if v),'/',len(out))
