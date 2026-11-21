import urllib.request,urllib.parse,json,time
OV='https://maps.mail.ru/osm/tools/overpass/api/interpreter'
els={e['id']:e for e in json.load(open('roads.json'))}
lat0,lat1,lon0,lon1=43.79,43.95,10.99,11.18
n=4
miss=[(3,1),(3,2),(2,3),(2,0)]
for i,j in miss:
  B=(lat0+(lat1-lat0)*i/n,lon0+(lon1-lon0)*j/n,lat0+(lat1-lat0)*(i+1)/n,lon0+(lon1-lon0)*(j+1)/n)
  for a in range(2):
    for b in range(2):
      la=B[0]+(B[2]-B[0])*a/2; lo=B[1]+(B[3]-B[1])*b/2
      bb=(la,lo,la+(B[2]-B[0])/2,lo+(B[3]-B[1])/2)
      q='[out:json][timeout:90];way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|pedestrian|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link)$"](%f,%f,%f,%f);out geom tags;'%bb
      for att in range(5):
        try:
          d=json.load(urllib.request.urlopen(OV,data=urllib.parse.urlencode({'data':q}).encode(),timeout=150))
          for e in d['elements']: els[e['id']]=e
          print(i,j,a,b,len(d['elements']),flush=True);break
        except Exception as ex:
          print('retry',i,j,a,b,ex,flush=True);time.sleep(8)
      json.dump(list(els.values()),open('roads.json','w'))
print('total',len(els))
