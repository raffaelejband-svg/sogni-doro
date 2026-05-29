# Recap progetto SMORFIA

Data: 2026-05-28

## Obiettivo

Creare una base di lavoro per trasformare testi su Smorfia, sogni, cabala e simboli in uno strumento pratico:

- racconti un sogno
- il sistema riconosce simboli e immagini
- consulta le fonti caricate
- propone numeri motivati
- genera cinquine o sestine
- salva i risultati nel vault Obsidian

Nota: il sistema produce letture simboliche e combinazioni ragionate. Non prevede con certezza estrazioni casuali.

## Fonti caricate

Nella cartella principale sono presenti:

- `Smorfia napoletana La vera cabala del lotto .pdf` -- 5.470 voci
- `1881__capacelli___il_vero_libro_dei_sogni.pdf` -- 9.733 voci
- `semprini.pdf` -- studio filosofico-linguistico (72 pp.)
- `sefer_yetzira_(traduzione).pdf` -- testo fondamentale (14 pp.)
- `René Guénon, Esoterismo ed exoterismo.pdf` -- framework (4 pp.)
- `The Kabala Of Numbers (Sepharial, 1920).pdf` -- numerologia planetaria (206 pp.)
- `dizionarioillust00roncuoft.pdf` -- Ronchetti, Dizionario Illustrato dei Simboli (1.212 pp.)

## Vault Obsidian

Creato il vault:

```text
Obsidian Vault SMORFIA/
```

File di ingresso:

```text
Obsidian Vault SMORFIA/Home.md
```

Struttura principale:

```text
00_Inbox/
01_Fonti/
02_Raw/
03_Note/
04_Grafo/
05_Progetti/
06_Output/
99_Allegati/PDF/
```

Contenuti importanti:

- `01_Fonti/Indice fonti.md`
- `02_Raw/Metodo raw Karpathy.md`
- `04_Grafo/Grafo iniziale.md`
- `05_Progetti/Chatbot sogni e numeri.md`
- `06_Output/Studio preliminare dei testi.md`
- `06_Output/Plan opzioni e sbocchi.md`

## Raw extraction

Tutti i PDF sono stati copiati dentro:

```text
Obsidian Vault SMORFIA/99_Allegati/PDF/
```

Ed estratti in markdown dentro:

```text
Obsidian Vault SMORFIA/02_Raw/
```

Script usato:

```text
tools/ingest_pdfs_to_obsidian.py
```

Risultato ingestione:

- Capacelli 1881: 238 pagine, circa 212.989 caratteri
- Smorfia napoletana: 325 pagine, circa 272.330 caratteri
- Semprini: 72 pagine, circa 178.578 caratteri
- Guenon: 4 pagine, circa 15.689 caratteri
- Sefer Yetzira: 14 pagine, circa 21.394 caratteri
- Sepharial: 206 pagine, circa 257.532 caratteri
- Ronchetti: 1.212 pagine, circa 1.702.643 caratteri

Report:

```text
Obsidian Vault SMORFIA/06_Output/Report ingestione PDF.md
```

## Dataset creati

### Smorfia

Script:

```text
tools/build_symbol_index.py
```

Output:

```text
Obsidian Vault SMORFIA/06_Output/smorfia_symbol_index_v0.csv
Obsidian Vault SMORFIA/03_Note/Indice simboli smorfia v0.md
```

Righe estratte:

```text
5.470
```

Struttura:

```text
symbol, detail, numbers, page, source
```

Esempio:

```text
Acqua, sporca: precauzione; 34, 34, pagina 8, Smorfia
```

### Capacelli 1881

Script:

```text
tools/build_capacelli_index.py
```

Output:

```text
Obsidian Vault SMORFIA/06_Output/capacelli_symbol_index_v0.csv
Obsidian Vault SMORFIA/03_Note/Indice simboli Capacelli v0.md
```

Righe estratte:

```text
9.733
```

Nota: Capacelli ha OCR piu sporco e struttura piu storica. Per questo viene trattato come fonte secondaria di confronto.

## Chatbot sogni -> numeri

Creato:

```text
dream_chatbot.py
```

Uso:

```bash
python3 dream_chatbot.py "Ho sognato acqua torbida, una casa vecchia, mio padre e un cane solo"
```

Funzioni attuali:

- legge indice Smorfia
- legge indice Capacelli
- riconosce simboli e sinonimi base
- mostra fonte, pagina, simbolo, dettaglio e numeri
- confronta Smorfia e Capacelli
- evidenzia numeri comuni tra fonti
- mantiene un minimo di risultati per fonte quando sono disponibili
- aggiunge note Ronchetti sui simboli
- aggiunge lettura Sepharial sui numeri
- aggiunge livello Sefer Yetzira / Semprini / Guenon tramite `cabala_layer.py`
- propone Cinquina Lotto
- propone Cinquina MillionDAY
- propone Sestina SuperEnalotto
- salva il responso nel vault

Output salvati in:

```text
Obsidian Vault SMORFIA/06_Output/Sogni analizzati/
```

Esempio di confronto:

```text
Casa:
Capacelli 1881: 4, 34, 59, 66, 71
Smorfia: 59, 60, 64
comuni: 59

Padre:
Capacelli 1881: 9
Smorfia: 9, 66, 87
comuni: 9
```

## Motore combinatorio

Creato:

```text
smorfia_predictor.py
```

Uso:

```bash
python3 smorfia_predictor.py superenalotto
python3 smorfia_predictor.py lotto
python3 smorfia_predictor.py millionday
```

Funzioni:

- genera sestine SuperEnalotto
- genera cinquine Lotto
- genera cinquine MillionDAY
- supporta seed riproducibile
- supporta numeri fissi
- supporta storico CSV opzionale
- stampa probabilita teorica della combinazione esatta

Esempio:

```bash
python3 smorfia_predictor.py superenalotto --fissi 7,22 --seed 20260528
```

## File principali del progetto

```text
README.md
RECAP_PROGETTO.md
dream_chatbot.py
smorfia_predictor.py
cabala_layer.py
cabala_sources.yml
synonyms.yml
tools/ingest_pdfs_to_obsidian.py
tools/build_symbol_index.py
tools/build_capacelli_index.py
Obsidian Vault SMORFIA/Home.md
```

## Stato attuale

Completato:

- vault Obsidian
- raw extraction dei PDF
- grafo iniziale
- dataset Smorfia v0
- dataset Capacelli v0
- chatbot CLI comparativo
- salvataggio automatico dei sogni analizzati
- generatore cinquine/sestine
- README e note progetto

Completato 2026-05-28 (prima sessione):

- synonyms.yml: 75 simboli canonici con varianti, caricato dinamicamente
- cabala_layer.py: Sefirot, Lettere Madri/Doppie/Semplici, gematria, elementi
- dream_chatbot.py aggiornato: usa YAML + mostra lettura cabalistica
- Vault aggiornato: nota Livello cabalistico, grafo v1

Completato 2026-05-28 (seconda sessione):

- Sepharial (1920) - The Kabala Of Numbers: analizzato e integrato
  * raw: 02_Raw/Sepharial - The Kabala Of Numbers RAW.md
  * fonte: 01_Fonti/Sepharial - The Kabala Of Numbers.md
  * integrazione: SEPHARIAL_CIFRE (0-9 planetari), SEPHARIAL_SIGNIFICATI (1-84)
  * output: sezione SEPHARIAL nel formatta_lettura()
- Ronchetti (1922) - Dizionario Illustrato dei Simboli: analizzato e integrato
  * raw: 02_Raw/Ronchetti - Dizionario Illustrato dei Simboli RAW.md
  * fonte: 01_Fonti/Ronchetti - Dizionario Illustrato dei Simboli.md
  * integrazione: RONCHETTI_SIMBOLI (30+ voci), sezione nel formatta_lettura()
  * synonyms.yml: aggiunte ~15 voci iconologiche da Ronchetti
- Grafo v2: aggiornato con tutte le 7 fonti in Mermaid completo
- Indice fonti: aggiornato con tabella completa delle 7 fonti
- PDF copiati in 99_Allegati/PDF/

Completato 2026-05-28 (consolidamento):

- `tools/ingest_pdfs_to_obsidian.py` aggiornato con tutte le 7 fonti
- report ingestione rigenerato su Smorfia, Capacelli, Semprini, Guenon, Sefer Yetzira, Sepharial, Ronchetti
- ranking del chatbot riequilibrato: anche con limiti bassi mantiene risultati da piu fonti
- `cabala_layer.py`: rimossa ambiguita della mappa zodiacale sul simbolo `fuoco`
- `cabala_sources.yml` creato come primo file di provenance per le tabelle simboliche
- `README.md` aggiornato con livello cabalistico e pipeline completa

Da migliorare:

- pulizia manuale/semiautomatica del dataset Capacelli
- note Obsidian automatiche per i numeri 1-90
- note Obsidian automatiche per i simboli piu frequenti
- grafo avanzato simbolo -> fonte -> numero nel vault
- interfaccia web o app locale (Streamlit)
- espandere synonyms.yml in modo iterativo
- indice CSV per Ronchetti (ronchetti_symbol_index_v0.csv)
- metadata pagina-per-pagina per le tabelle cabalistiche
- Bot Telegram

## Prossimi passi consigliati

1. Creare note automatiche per i numeri 1-90.
2. Creare note automatiche per i simboli piu ricorrenti.
3. Estendere `cabala_sources.yml` con riferimenti pagina-per-pagina.
4. Migliorare il chatbot con una modalita:

```text
lettura pratica
lettura simbolica
lettura comparativa
```

5. Creare indice CSV per Ronchetti.
6. Creare una piccola web app locale.

## Comandi utili

Rigenerare raw dai PDF:

```bash
python3 tools/ingest_pdfs_to_obsidian.py
```

Rigenerare dataset Smorfia:

```bash
python3 tools/build_symbol_index.py
```

Rigenerare dataset Capacelli:

```bash
python3 tools/build_capacelli_index.py
```

Usare chatbot:

```bash
python3 dream_chatbot.py "racconta qui il sogno"
```

Usare chatbot senza salvataggio:

```bash
python3 dream_chatbot.py "racconta qui il sogno" --no-save
```

Generare combinazioni:

```bash
python3 smorfia_predictor.py lotto
python3 smorfia_predictor.py millionday
python3 smorfia_predictor.py superenalotto
```

## Direzione del progetto

La direzione piu forte e costruire un assistente personale dei sogni:

```text
sogno raccontato
-> simboli riconosciuti
-> confronto tra fonti
-> numeri motivati
-> combinazioni
-> nota salvata nel vault
-> grafo consultabile
```

La Smorfia resta la fonte pratica principale. Capacelli aggiunge profondita storica. Sefer Yetzira, Semprini, Guenon, Sepharial e Ronchetti formano il livello simbolico/esoterico.
