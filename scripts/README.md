# Script

Pipeline usata per generare `data/`. Ordine:

1. `01_scarica_schede.sh` — scarica i PDF delle *Mappe dei Cittadini* e ne estrae il testo
2. `02_leggi_schede.py` — tiene le schede del comune di Prato
3. `03_coordinate_gauss_boaga.py` — converte le coordinate originali (EPSG:3003 → WGS84)
4. `geo.py`, `geo_all.py` — geocodifica con Nominatim delle schede senza coordinate (con correzioni manuali in `geo.py`)
5. `04_scarica_osm.sh` + `roads_fix.py` — dati OpenStreetMap da Overpass (nomi antichi, strade, acque, ferrovia, confine)
6. `build.py` — costruisce `data/base.json` e `data/luoghi.geojson` (classificazione per tema inclusa)

Gli script sono stati scritti per l'ambiente in cui sono stati eseguiti: alcuni percorsi sono assoluti e vanno adattati.
Rispettare le policy d'uso di Nominatim (max 1 richiesta/secondo) e Overpass.
