#!/bin/sh
# Scarica i PDF delle schede "Mappe dei Cittadini" (Provincia di Prato) ed estrae il testo.
# Richiede curl e pdftotext (poppler-utils).
mkdir -p data/schede && cd data/schede
seq 1 1500 | xargs -P 6 -I{} sh -c 'curl -s -m 60 -f -o s_{}.pdf "http://mapserver.provincia.prato.it/prv_po/Mappecittadini/pdfs/Mappecittadini_scheda_{}.pdf" || rm -f s_{}.pdf'
for f in s_*.pdf; do pdftotext -layout "$f" "${f%.pdf}.txt"; done
