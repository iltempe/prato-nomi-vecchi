import json,time,urllib.request,urllib.error,urllib.parse,sys
# id -> list of queries (first hit wins); "x" queries are intersections handled as two streets averaged
Q={
418:["via del Cilianuzzo, Prato"],420:["via Firenze 247, Prato","via Firenze, La Macine, Prato"],
461:["via Roma, Grignano, Prato"],550:["via Strozzi & via Filicaia","via Strozzi, Prato"],
558:["via della Violata, Prato"],559:["San Giorgio a Colonica, Prato"],561:["via della Gora Bandita, Prato"],
587:["via di Turchia, Prato","via Turchia, Prato"],592:["via Cava, San Giusto, Prato"],594:["via del Molinuzzo, Prato","via Molinuzzo, Prato"],
614:["via Becherini, Prato"],626:["via del Ficarello, Prato"],636:["via Bettazzi, Prato"],647:["Vergaio, Prato"],
704:["via Mugellese, La Querce, Prato"],730:["via Matteo degli Organi, Prato"],750:["via dei Trebbi, Prato"],751:["via dei Trebbi, Prato"],
752:["via Lorenzo Ciulli & via Ugo Foscolo","via Lorenzo Ciulli, Prato"],753:["via Matteo degli Organi & via Pieraccioli","via Pieraccioli, Prato"],
754:["via del Fondaccio, Prato"],755:["via del Fondaccio, Prato"],756:["via Isidoro del Lungo, Prato"],
757:["via del Fondaccio & via della Lastruccia","via della Lastruccia, Prato"],780:["via di Popolino, Prato","via Popolino, Prato"],
786:["Le Torri, San Giorgio a Colonica, Prato","via delle Torri, Prato"],805:["Viaccia, Prato"],806:["via di Montemurlo, Viaccia, Prato","via di Montemurlo, Prato"],
807:["via di Montemurlo, Prato"],812:["Castelnuovo, Prato"],813:["Fontanelle, Prato"],814:["via Traversa del Crocifisso, Prato"],815:["Fontanelle, Prato"],
843:["via Pistoiese & via Martino Maliseti","Narnali, Prato"],847:["Iolo, Prato"],865:["via Guazzalotri, Prato"],866:["via Gherardacci, Iolo, Prato","via Gherardacci, Prato"],
960:["via Montalese, Bagnolo, Prato","Bagnolo, Prato"],1038:["via Pollative, Prato"],1039:["via Gora del Pero, Prato"],1040:["via del Malfante, Prato","via Malfante, Prato"],
1082:["via Lorenzo Ciulli, Prato"],1090:["via della Gora, Galciana, Prato","Galciana, Prato"],1096:["Viaccia, Prato"],1097:["via di Valdingole, Prato","via Valdingole, Prato"],
1102:["via Viaccia a Narnali, Prato"],1106:["Ponte Torto, Prato","via Pistoiese, Viaccia, Prato"],1107:["via Pistoiese, Viaccia, Prato"],
1111:["vicolo del Chiassarello, Prato","via del Chiassarello, Prato"],1112:["via Nebbiaia, Prato"],1114:["via Braga, Prato"],1118:["via Mozza, Prato"],
1119:["via delle Colombaie, Prato"],1120:["Ponte a Tigliano"],1121:["Ponte a Tigliano"],1122:["via Braga & via della Fattoria","via della Fattoria, Tavola, Prato"],
1123:["via Pasquinelli, Prato"],1129:["Tavola, Prato"],1130:["Ponte del Manetti","Tavola, Prato"],1131:["via Braga, Prato"],1132:["Cimitero di Tavola, Prato","Tavola, Prato"],
1134:["Golf Club Le Pavoniere, Prato","via Traversa del Crocifisso, Prato"],1135:["via Traversa del Crocifisso & via Braga","via Braga, Prato"],1136:["via Nebbiaia, Prato"],
1139:["via Pasquinelli, Prato"],1142:["via Braga, Prato"],1150:["via della Gora Bandita, Prato"],1261:["Paperino, Prato"],
1293:["via di Cortevecchia, Prato","via Cortevecchia, Prato"],1295:["via Marco Roncioni & via Galcianese","via Galcianese, Prato"],
# storico
"H1":["via Giuseppe Garibaldi, Prato"],"H2":["via Giuseppe Verdi, Prato"],"H3":["via Santo Stefano, Prato"],"H4":["via Giuseppe Garibaldi, Prato"],
"H5":["via Benedetto Cairoli, Prato"],"H6":["piazza delle Carceri, Prato"],"H7":["via Santa Trinita, Prato"],"H8":["via del Pellegrino, Prato"],
"H9":["via Cesare Guasti, Prato"],"H10":["via San Michele, Prato"],"H11":["piazza Filippino Lippi, Prato","piazza Lippi, Prato"],"H12":["via Dante Alighieri, Prato"],
"H13":["Stazione di Prato Porta al Serraglio"],"H14":["via del Cassero, Prato"],"H15":["via Frascati & via Pomeria","via Frascati, Prato"],
"H16":["Mausoleo di Curzio Malaparte","Monte Le Coste, Prato"],"H17":["piazza San Marco, Prato"],
}
CACHE={}
def nom(q):
  if q in CACHE: return CACHE[q]
  for att in range(6):
    try:
      return _nom(q)
    except urllib.error.HTTPError as e:
      if e.code==429: time.sleep(10*(att+1)); continue
      raise
  return None
def _nom(q):
  url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode(dict(q=q,format='json',limit=1,countrycodes='it',viewbox='10.98,43.95,11.20,43.78',bounded=1))
  r=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'prato-vecchi-nomi/0.1 (civic map)'}),timeout=30))
  time.sleep(1.5)
  CACHE[q]=r[0] if r else None
  return CACHE[q]
out={}
for k,qs in Q.items():
  hit=None;used=None
  for q in qs:
    if '&' in q:
      a,b=[s.strip()+', Prato' for s in q.split('&')]
      ra,rb=nom(a),nom(b)
      if ra and rb:
        hit=dict(lat=(float(ra['lat'])+float(rb['lat']))/2,lon=(float(ra['lon'])+float(rb['lon']))/2,display=ra['display_name']+' / '+rb['display_name'],osm=f"{ra['osm_type']}/{ra['osm_id']}");used=q;break
    else:
      r=nom(q)
      if r: hit=dict(lat=float(r['lat']),lon=float(r['lon']),display=r['display_name'],osm=f"{r['osm_type']}/{r['osm_id']}");used=q;break
  out[str(k)]=dict(q=used,**hit) if hit else None
  print(k,used,(hit or {}).get('display','—')[:90],flush=True)
json.dump(out,open('/home/claude/data/geo.json','w'),ensure_ascii=False,indent=1)
