# Landing page SEO — Sogni e Numeri

Pagina **statica** che si posiziona su Google. L'app Streamlit da sola non è
indicizzabile: questa landing è ciò che Google legge e mostra nei risultati.

## Architettura scelta (opzione B — costo €0)

```
sognienumeri.space         →  questa landing (Cloudflare Pages, gratis)
app.sognienumeri.space     →  l'app Streamlit (Streamlit Cloud, dominio custom)
```

## File

```
landing/
├── index.html        ← landing completa (SEO + Open Graph + JSON-LD + FAQ)
├── robots.txt
├── sitemap.xml
└── assets/
    ├── logo.png      ← logo / emblema
    ├── og-image.png  ← anteprima social (consigliato 1200×630 — vedi sotto)
    └── favicon.png
```

## Cosa modificare prima di pubblicare

1. **URL newsletter** — in `index.html`, in fondo:
   ```js
   const NEWSLETTER_URL = "https://sognienumeri.beehiiv.com/subscribe";
   ```
2. **Link social** — sezione `.social` **e** blocco JSON-LD `sameAs`: metti gli handle reali.
3. (Se cambi dominio) find-and-replace di `sognienumeri.space` in tutti i file.

---

## Deploy — passo per passo

### A) App su sottodominio (Streamlit Cloud)
1. Dashboard Streamlit Cloud → la tua app → **Settings → Custom domain**.
2. Imposta `app.sognienumeri.space`.
3. Streamlit ti indica un record DNS **CNAME** (`app` → valore fornito da Streamlit):
   crealo dove gestisci il DNS del dominio.

### B) Landing sul dominio principale (Cloudflare Pages — gratis)
1. Account su <https://pages.cloudflare.com> (gratis).
2. **Crea progetto**:
   - *Direct Upload*: carica il contenuto della cartella `landing/`, **oppure**
   - *Da GitHub*: collega il repo, build command vuoto, output directory `landing`.
3. Aggiungi il **dominio personalizzato** `sognienumeri.space` (e `www`) nel progetto.
4. Segui le istruzioni DNS di Cloudflare per puntare il dominio.

> In alternativa vanno bene anche **Netlify** o **GitHub Pages**: stesso principio
> (sito statico + dominio custom).

### C) Verifica finale
- `https://sognienumeri.space/` → landing
- `https://app.sognienumeri.space/` → app
- `/sitemap.xml` e `/robots.txt` raggiungibili
- Anteprima social su <https://www.opengraph.xyz>

---

## og-image (anteprima social)

Per ora `og-image.png` è una copia del logo. Per un risultato professionale crea
un'immagine **1200×630 px** con logo + slogan e sostituisci `assets/og-image.png`.
