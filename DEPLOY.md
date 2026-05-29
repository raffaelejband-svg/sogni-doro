# Guida al Deploy — SMORFIA su Streamlit Community Cloud

Questa guida ti porta dal codice locale all'app pubblica gratuita in ~15 minuti.

---

## Prerequisiti

- Account GitHub gratuito
- Account Streamlit Community Cloud gratuito (signup con GitHub su [share.streamlit.io](https://share.streamlit.io))
- `gh` CLI installato (opzionale, per creare il repo da terminale)

---

## 1. Crea il repository GitHub

### Via terminale (gh CLI)

```bash
cd /Users/raffaelesantonastaso/Desktop/SMORFIA

# Inizializza git se non lo hai già fatto
git init
git add app.py dream_chatbot.py cabala_layer.py smorfia_predictor.py
git add requirements.txt .gitignore README.md
git add .streamlit/config.toml .streamlit/secrets.toml.example
git add data/smorfia_symbol_index_v0.csv data/capacelli_symbol_index_v0.csv
git add synonyms.yml cabala_sources.yml
git commit -m "Sogni d'Oro v1.0 — deploy iniziale"

# Crea il repo pubblico su GitHub e fai push
gh repo create sogni-doro --public --source=. --remote=origin --push
```

### Via browser (alternativa)
1. Vai su [github.com/new](https://github.com/new)
2. Nome repo: `sogni-doro` (o nome a tua scelta)
3. Visibilità: **Public**
4. NON aggiungere README/gitignore (li hai già)
5. Crea il repo, poi copia i comandi push suggeriti da GitHub

---

## 2. Connetti a Streamlit Community Cloud

1. Vai su [share.streamlit.io](https://share.streamlit.io) e accedi con GitHub
2. Clicca **"New app"**
3. Scegli:
   - **Repository**: `tuousername/sogni-doro`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Clicca **"Advanced settings"** → inserisci i secrets (vedi sezione 3)
5. Clicca **"Deploy!"**

L'app sarà disponibile a un URL del tipo:
`https://tuousername-sogni-doro-app-XXXXX.streamlit.app`

---

## 3. Configura i Secrets (Ko-fi URL e nome app)

Nella dashboard di Streamlit Community Cloud:
**App → Settings → Secrets**

Incolla e adatta questo contenuto:

```toml
KOFI_URL = "https://ko-fi.com/TUO_USERNAME_KOFI"
APP_NAME = "SMORFIA — Il Sistema dei Sogni"
APP_VERSION = "1.0"
```

> **Nota**: Il file `.streamlit/secrets.toml.example` contiene il template.
> Non committare mai `.streamlit/secrets.toml` su Git (è già in `.gitignore`).

---

## 4. Come aggiornare il tuo URL Ko-fi

Il link Ko-fi è attualmente hardcoded in `app.py` come `https://ko-fi.com/smorfiasogni`.
Per personalizzarlo senza modificare il codice, hai due opzioni:

### Opzione A — Modifica diretta in app.py (più semplice)
Cerca e sostituisci `ko-fi.com/smorfiasogni` con il tuo URL in `app.py`:
```bash
grep -n "ko-fi.com/smorfiasogni" app.py
```
Le righe da modificare sono circa la 697, 748 e 779.

### Opzione B — Usa st.secrets (più flessibile)
Nel codice, sostituisci le occorrenze dell'URL con:
```python
kofi_url = st.secrets.get("KOFI_URL", "https://ko-fi.com/smorfiasogni")
```
Poi aggiungi `KOFI_URL` nei secrets di Streamlit Cloud (vedi sezione 3).

---

## 5. Come aggiornare il nome dell'app

Il titolo della pagina è impostato in `app.py` alla riga 35:
```python
st.set_page_config(
    page_title="SMORFIA — Il Sistema dei Sogni",
    ...
)
```
Modifica la stringa `page_title` con il nome che preferisci.

---

## 6. Aggiornamenti successivi

Ogni volta che fai push su GitHub, Streamlit Community Cloud aggiorna l'app automaticamente:

```bash
# Modifica i file, poi:
git add -p                  # aggiungi solo i file modificati
git commit -m "descrizione modifica"
git push
```

L'app si riavvia entro ~30 secondi.

---

## 7. Troubleshooting comuni

### L'app non parte — "ModuleNotFoundError: yaml"
Il pacchetto `PyYAML` manca da `requirements.txt`.
Verifica che `requirements.txt` contenga:
```
streamlit==1.53.0
PyYAML==6.0.3
```

### L'app non trova i CSV — "FileNotFoundError"
Assicurati che i file `data/smorfia_symbol_index_v0.csv` e `data/capacelli_symbol_index_v0.csv`
siano committati su GitHub. Controlla con:
```bash
git ls-files data/
```

### L'app crasha sulla tab "Lettura Esoterica"
Il modulo `cabala_layer.py` deve essere presente nella root del repo.
Verifica con `git ls-files | grep cabala`.

### Errore "Resource limits exceeded" su Streamlit Cloud
L'app usa `@st.cache_resource` per caricare i CSV una sola volta.
Se il problema persiste, considera di ridurre `find_matches(dream, entries, 24)` a un numero minore.

### Il tema non appare correttamente
Verifica che `.streamlit/config.toml` sia committato su GitHub:
```bash
git ls-files .streamlit/
```

### Devo aggiungere un dominio personalizzato
Streamlit Community Cloud supporta domini personalizzati dal piano a pagamento.
Per il gratuito, l'URL è fisso (ma condivisibile).

---

## Struttura file necessari per il deploy

```
sogni-doro/
├── app.py                          ← entry point (obbligatorio nella root)
├── dream_chatbot.py                ← logica principale
├── cabala_layer.py                 ← livello esoterico
├── requirements.txt                ← dipendenze Python
├── .gitignore                      ← esclude vault, PDF, secrets
├── synonyms.yml                    ← sinonimi per il matching
├── cabala_sources.yml              ← sorgenti cabala
├── data/
│   ├── smorfia_symbol_index_v0.csv
│   └── capacelli_symbol_index_v0.csv
└── .streamlit/
    ├── config.toml                 ← tema dark, headless=true
    └── secrets.toml.example        ← template secrets (NON secrets.toml)
```

---

## Risorse utili

- Documentazione Streamlit Cloud: https://docs.streamlit.io/deploy/streamlit-community-cloud
- Gestione secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- Limiti gratuiti: 1 app pubblica, 1GB RAM, storage illimitato per repo < 1GB
