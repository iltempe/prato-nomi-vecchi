#!/bin/sh
# Scarica da Overpass i nomi antichi/locali e gli strati della base cartografica nel comune di Prato.
# Le strade si scaricano a riquadri (roads_fix.py) perché i server Overpass vanno spesso in timeout.
OV=https://maps.mail.ru/osm/tools/overpass/api/interpreter
mkdir -p data/osm
A='area["boundary"="administrative"]["admin_level"="8"]["name"="Prato"]->.a;'
curl -s -m 180 --data-urlencode "data=[out:json][timeout:120];$A(nwr(area.a)[\"old_name\"];nwr(area.a)[\"loc_name\"];nwr(area.a)[\"alt_name\"];nwr(area.a)[\"place\"~\"locality|neighbourhood|quarter|hamlet|suburb|village\"];);out center tags;" $OV -o data/osm/names.json
curl -s -m 300 --data-urlencode "data=[out:json][timeout:180];$A(way(area.a)[\"waterway\"~\"river|canal|stream|ditch|drain\"];way(area.a)[\"railway\"=\"rail\"];rel[\"boundary\"=\"administrative\"][\"admin_level\"=\"8\"][\"name\"=\"Prato\"];way(area.a)[\"leisure\"=\"park\"];way(area.a)[\"natural\"=\"water\"];);out geom qt;" $OV -o data/osm/other.json
