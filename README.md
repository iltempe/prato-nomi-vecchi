# Prato coi nomi vecchi

Mappa di Prato con i nomi che i pratesi usano (o usavano) e che non sono nella toponomastica ufficiale: toponimi popolari, case e ville conosciute col nome dei contadini, mulini, tabernacoli, porte della città medievale, vecchi nomi di strade.

**Mappa:** https://iltempe.github.io/prato-nomi-vecchi/

421 punti: le 370 schede del comune di Prato delle *Mappe dei Cittadini*, 6 microtoponimi citati nelle testimonianze, 16 luoghi della città medievale, 29 elementi OpenStreetMap che hanno già `old_name`/`loc_name`.

## Dataset

| File | Contenuto |
|---|---|
| [`data/luoghi.geojson`](data/luoghi.geojson) | I 421 punti (GeoJSON, WGS84) |
| [`data/luoghi.csv`](data/luoghi.csv) | Gli stessi dati in CSV |
| [`data/base.json`](data/base.json) | Base cartografica semplificata estratta da OpenStreetMap (strade, gore e corsi d'acqua, ferrovia, parchi, confine comunale) |

### Campi

| Campo | Significato |
|---|---|
| `id` | `mcNNN` = scheda NNN delle Mappe dei Cittadini · `tmN` = microtoponimo dalle testimonianze · `hN` = città medievale · `osm…` = elemento OSM |
| `nome` | Il nome vecchio o popolare |
| `cat` | `popolare`, `testimonianze`, `leggenda`, `case`, `acqua`, `sacro`, `lavoro`, `memoria`, `storico`, `ufficializzato` (toponimo popolare poi diventato nome di via), `osm` |
| `tipo` | Tipologia della scheda (Toponimo, Colonica, Mulino, Tabernacolo…) |
| `zona`, `dove` | Località e ubicazione come indicate nella fonte |
| `stato` | `esistente` / `nonesistente` (dalla scheda) |
| `prec` | Precisione della posizione: `P` punto (coordinate originali della scheda o luogo preciso), `V` lungo la via indicata, `Z` centro della frazione |
| `testo` | Descrizione abbreviata dalla fonte |
| `fonte`, `url` | Fonte e link al documento originale |

### Come sono state calcolate le posizioni

1. **Coordinate originali**: 226 schede riportano coordinate Gauss-Boaga (Monte Mario / Italy zone 1, EPSG:3003), convertite in WGS84 con `pyproj`.
2. **Geocodifica**: per le altre (incluse 27 con coordinate in un formato non riconoscibile) la via o la località indicata nella scheda è stata geocodificata con Nominatim, con alcune correzioni manuali.
3. Quando più punti cadono sulla stessa coordinata sono stati distanziati di qualche decina di metri.

Le posizioni con precisione `V` e `Z` vanno verificate sul posto prima di riusarle (ad esempio per caricarle in OpenStreetMap).

## Fonti

- **Provincia di Prato – Servizio Sistemi informativi, Ufficio SIT, *Mappe dei Cittadini*.** Schede di censimento partecipato del patrimonio e della memoria locale, compilate con i circoli e le testimonianze orali degli abitanti. Ogni punto rimanda al PDF della scheda (`http://mapserver.provincia.prato.it/prv_po/Mappecittadini/pdfs/Mappecittadini_scheda_NNN.pdf`). I testi sono riportati in forma abbreviata e attribuiti; la licenza delle schede non è indicata dalla fonte.
- **© OpenStreetMap contributors**, dati disponibili con licenza [ODbL 1.0](https://opendatacommons.org/licenses/odbl/): base cartografica, tag `old_name`/`loc_name`, geocodifica tramite [Nominatim](https://nominatim.openstreetmap.org/).
- [Wikipedia – Mura di Prato](https://it.wikipedia.org/wiki/Mura_di_Prato) (CC BY-SA): porte della seconda cerchia, Porta al Serraglio, Archi di Frascati, bastioni.
- [Corteo storico di Prato – Rappresentanza storica della Terra di Prato](https://www.crprato.it/sito/index.php?option=com_content&view=article&id=821:i-valletti-del-comune-di-prato&catid=46:prato-nel-mondo&Itemid=222): porte di Rusticuzzo e di San Jacopo, quartieri e porte.
- [tuttatoscana – Prato medievale: lo sviluppo urbano](https://tuttatoscana.net/storia-e-microstoria-2/prato-medievale-lo-sviluppo-urbano/): Borgo al Cornio.
- [welcome2prato – 16 vicoli caratteristici nel centro storico di Prato](https://www.welcome2prato.com/2020/05/vicoli-centro-storico-prato.html): via del Pozzo Nuovo (oggi via Verdi).
- [Paolo Nori – Repertorio dei matti della città di Prato](https://www.paolonori.it/argomenti/repertorio-dei-matti-della-citta-di-prato/): Spazzavento.

## Licenze

- **Codice** (`index.html`): MIT.
- **Dataset** (`data/`): contiene dati derivati da OpenStreetMap, quindi è distribuito con licenza [ODbL 1.0](https://opendatacommons.org/licenses/odbl/) — © OpenStreetMap contributors. I contenuti tratti dalle schede *Mappe dei Cittadini* restano della Provincia di Prato e dei testimoni che li hanno raccontati: vanno citati come tali.
- Leaflet (`leaflet.css`, e lo script da cdnjs): BSD-2-Clause, © Volodymyr Agafonkin.

## Contribuire

Conosci un nome che manca (tipo *i' Perugio*)? Apri una issue con il nome, dove si trova e da chi l'hai sentito. In OpenStreetMap i nomi vecchi si mettono con `old_name=*` o `loc_name=*`, senza toccare `name=*`.

Progetto di [Matteo Tempestini](https://github.com/iltempe).
