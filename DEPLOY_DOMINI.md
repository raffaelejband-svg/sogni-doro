# Guida domini & deploy — Sogni e Numeri

Dominio registrato su **Hostinger**. Obiettivo finale:

```
sognienumeri.space        →  landing SEO (Cloudflare Pages)  ← la homepage che Google indicizza
app.sognienumeri.space    →  app Streamlit (Streamlit Cloud) ← lo strumento
```

Si fa in 4 fasi, **in quest'ordine**, così il sito resta sempre online (zero downtime).

---

## FASE 1 — Sposta il DNS su Cloudflare (una volta sola)

> Serve perché i domini "nudi" (senza www) non si collegano bene ai servizi di pagine
> se il DNS resta su Hostinger. Cloudflare risolve tutto ed è gratis.

1. Crea account su **dash.cloudflare.com** (gratis).
2. **Add a site** → `sognienumeri.space` → piano **Free**.
3. Cloudflare **scansiona e copia i record DNS attuali** (così non si rompe nulla). Verifica
   che nell'elenco compaia il record che fa funzionare l'app oggi.
4. Cloudflare ti mostra **2 nameserver** (es. `lia.ns.cloudflare.com`, `rob.ns.cloudflare.com`).
5. Vai su **Hostinger → hPanel → Domini → sognienumeri.space → DNS / Nameserver**.
6. Scegli **"Usa nameserver personalizzati / Change nameservers"** e incolla i 2 di Cloudflare
   (cancellando quelli di Hostinger). Salva.
7. La propagazione richiede da pochi minuti a qualche ora. Cloudflare ti manda un'email
   "Great news! …active" quando è pronto. **Da qui in poi gestisci tutto su Cloudflare.**

---

## FASE 2 — App su app.sognienumeri.space (Streamlit Cloud)

1. Vai sulla dashboard **share.streamlit.io** → la tua app → **Settings**.
2. Cerca **Custom domain** → inserisci `app.sognienumeri.space`.
3. Streamlit ti dà un valore **CNAME** (es. `<qualcosa>.streamlit.app`). Copialo.
4. Su **Cloudflare → DNS → Add record**:
   - Type: **CNAME** · Name: **app** · Target: *(il valore dato da Streamlit)*
   - Proxy status: **DNS only** (nuvoletta grigia, non arancione) — importante per Streamlit.
5. Attendi qualche minuto → apri `https://app.sognienumeri.space`: deve mostrare l'app.

> Nota: NON impostare `baseUrlPath` in `.streamlit/config.toml`. Con il sottodominio non serve
> e su Streamlit Cloud romperebbe l'app.

---

## FASE 3 — Landing su sognienumeri.space (Cloudflare Pages)

1. Su **Cloudflare → Workers & Pages → Create → Pages**.
2. Opzione consigliata: **Connect to Git** → collega il repo GitHub `sogni-doro`.
   - **Build command:** *(lascia vuoto)*
   - **Build output directory:** `landing`
   - (In alternativa "Direct Upload": carica il contenuto della cartella `landing/`.)
3. Deploy. Cloudflare pubblica su un indirizzo `*.pages.dev`.
4. Nel progetto Pages → **Custom domains** → **Set up a domain** → `sognienumeri.space`
   e poi anche `www.sognienumeri.space`. Cloudflare crea i record da solo (DNS già da loro).
5. Apri `https://sognienumeri.space`: deve apparire la landing.

✅ Risultato: homepage = landing (indicizzabile), app = sottodominio.

---

## FASE 4 — Google (indicizzazione)

1. **Google Search Console** → search.google.com/search-console → **Add property** →
   `sognienumeri.space` (verifica con record TXT su Cloudflare, guidato).
2. **Sitemaps** → invia `https://sognienumeri.space/sitemap.xml`.
3. **Controllo URL** → incolla la home e gli articoli → *Richiedi indicizzazione*.
4. (Bonus) **Bing Webmaster Tools** → importa da Search Console in 1 clic.

I primi risultati su Google compaiono in genere in **alcuni giorni/settimane**: è normale, l'indicizzazione non è immediata.

---

## Prima di tutto: sostituisci i segnaposto

Quando hai gli account reali, aggiorna **2 file** e fai `git push` (l'app si aggiorna da sola):

- `app.py` → `NEWSLETTER_URL`, dizionario `SOCIAL_LINKS`
- `landing/index.html` → `const NEWSLETTER_URL`, sezione `.social`, blocco JSON-LD `sameAs`

(Posso farlo io: mandami gli URL e ci penso.)

---

## Riassunto "chi fa cosa"

| Cosa | Chi | Tempo |
|------|-----|-------|
| Account Cloudflare + nameserver su Hostinger | Tu (ti guido) | 10 min |
| Custom domain Streamlit + CNAME | Tu (ti guido) | 5 min |
| Cloudflare Pages + dominio | Tu (ti guido) | 10 min |
| Search Console + sitemap | Tu (ti guido) | 5 min |
| Codice, landing, articoli, SEO, immagini | **Fatto ✅** | — |
