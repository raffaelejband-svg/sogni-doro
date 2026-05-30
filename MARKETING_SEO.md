# Sogni e Numeri — Piano Community, Social & SEO

Guida operativa per portare il progetto su tutte le piattaforme e farlo trovare su Google.
Brand ufficiale: **Sogni e Numeri** · Dominio: **sognienumeri.space**

---

## 0. Cosa è già stato fatto nel codice

- ❌ Rimosso "Offrimi un caffè" (ko-fi) ovunque (app + footer).
- ✅ Aggiunto pannello **"Iscriviti alla community"** (newsletter + social) nell'app.
- ✅ Creata **landing page statica SEO** (`landing/`): andrà su `sognienumeri.space`, l'app su `app.sognienumeri.space`.
- ✅ Meta tag, Open Graph, Twitter Card, **dati strutturati JSON-LD** (FAQ, Organizzazione).
- ✅ `robots.txt` + `sitemap.xml`.
- ✅ Link social centralizzati in un solo punto (`SOCIAL_LINKS` in `app.py`, `NEWSLETTER_URL` in `app.py` e `index.html`).

> **Tutti i link sono segnaposto** (`@sognienumeri`). Vanno sostituiti con gli account reali. Vedi §2 e §4.

---

## 1. Newsletter / Community (priorità 1)

Scelta consigliata: **beehiiv** (gratis fino a 2.500 iscritti, ottimo per crescere) o **Substack**.

### Setup beehiiv
1. Crea l'account su <https://beehiiv.com> → nome pubblicazione "Sogni e Numeri".
2. Imposta il sottodominio: `sognienumeri.beehiiv.com`.
3. Copia l'URL di iscrizione (es. `https://sognienumeri.beehiiv.com/subscribe`).
4. Incollalo in **due** punti:
   - `app.py` → `NEWSLETTER_URL = "..."`
   - `landing/index.html` → `const NEWSLETTER_URL = "..."`
5. (Opzionale) Embed nativo in landing → vedi `landing/README_LANDING.md`.

### Idea editoriale newsletter (1 email/settimana)
- "Il sogno della settimana" + numeri commentati.
- Un simbolo dalla tradizione (Smorfia/Capacelli) spiegato.
- Una curiosità esoterica (Sefer Yetzira, Sepharial, Ronchetti).
- CTA: "Hai fatto un sogno strano? Interpretalo qui → sognienumeri.space".

---

## 2. Account social (priorità 1)

Handle consigliato ovunque: **@sognienumeri** (coerente col dominio).

| Piattaforma | Handle | Ruolo |
|-------------|--------|-------|
| Instagram | @sognienumeri | Caroselli "sogno → numeri", reel, estetica onirica/dorata |
| TikTok | @sognienumeri | Video brevi: massima portata organica |
| Facebook | /sognienumeri (Pagina + Gruppo) | Pubblico over 40/50, community Smorfia/lotto |
| YouTube | @sognienumeri | Short + video lunghi (anche SEO video) |
| Telegram | t.me/sognienumeri | Canale: numeri e novità quotidiane |

Dopo averli creati, aggiorna gli URL in:
- `app.py` → dizionario `SOCIAL_LINKS`
- `landing/index.html` → sezione `.social` **e** blocco JSON-LD `sameAs`

**Asset visivi coerenti:** usa il logo luna dorata (`static/logo_pergamena.png`),
palette pergamena/oro (#ece0c4 / #9a7b2e), font Cinzel per i titoli. Stessa identità
ovunque (foto profilo = emblema luna, copertina = slogan).

### Idee di contenuto (riproducibili in serie)
- **"Stanotte ho sognato…"**: 1 sogno → simboli → numeri (formato fisso, fa volume).
- **"La Smorfia spiega"**: 1 simbolo classico al giorno (47 morto che parla, ecc.).
- **"Numero del giorno"**: estetica tarocchi/pergamena.
- **Duetti/stitch su TikTok** con racconti di sogni dei follower.
- Invito costante: *"Provalo gratis su sognienumeri.space"*.

---

## 3. SEO Google (priorità 1)

### Passi immediati dopo il deploy della landing
1. **Google Search Console** <https://search.google.com/search-console>
   - Aggiungi la proprietà `sognienumeri.space` (verifica via DNS TXT o file HTML).
   - *Sitemap* → invia `https://sognienumeri.space/sitemap.xml`.
   - *Controllo URL* → richiedi indicizzazione della home.
2. **Bing Webmaster Tools** <https://www.bing.com/webmasters> (import da GSC in 1 clic).
3. **Google Business / Knowledge**: opzionale, non necessario per un'app.

### Parole chiave su cui puntare (alto volume in Italia)
- "smorfia napoletana", "numeri smorfia", "significato sogni numeri",
  "sognare [X] numeri", "interpretazione sogni", "libro dei sogni".
- La landing già le include in title/description/H1/FAQ.

### Crescita SEO nel tempo (contenuti = ranking)
Ottimo motore: una **sezione articoli** (anche su beehiiv, che è indicizzabile) tipo:
- "Sognare l'acqua: significato e numeri"
- "Sognare i morti: cosa dice la Smorfia"
- "Sognare i soldi: interpretazione e numeri"

Ogni articolo intercetta ricerche specifiche e rimanda all'app. Questa è la leva
SEO più forte nel medio periodo.

---

## 4. Checklist "vai in produzione"

- [ ] Creato account beehiiv/Substack → URL inserito in `app.py` e `landing/index.html`.
- [ ] Creati gli account social → handle aggiornati in `app.py` e `landing/index.html` (anche `sameAs`).
- [ ] og-image 1200×630 definitiva in `landing/assets/og-image.png`.
- [ ] App su `app.sognienumeri.space` (Streamlit Cloud → Custom domain + CNAME DNS).
- [ ] Landing pubblicata su `sognienumeri.space` (Cloudflare Pages → vedi `landing/README_LANDING.md`).
- [ ] Verificato: home `/`, app `app.`, `/sitemap.xml`, `/robots.txt`.
- [ ] Search Console: proprietà verificata + sitemap inviata.
- [ ] Anteprima social testata su opengraph.xyz.
- [ ] Primo post pubblicato su ogni piattaforma con link a sognienumeri.space.

---

## 5. Architettura e costi

**Scelta: opzione B — costo €0.**

```
sognienumeri.space      →  landing SEO statica  (Cloudflare Pages, gratis)
app.sognienumeri.space  →  app Streamlit        (Streamlit Cloud, come ora)
```

Questa configurazione dà SEO forte e immagine professionale **senza pagare nulla**
e senza manutenzione di server. **Un VPS (Hostinger) NON è necessario.**

Valuta un VPS solo in futuro se vuoi: tutto su un unico dominio sotto il tuo
controllo, una newsletter self-hosted (Listmonk), o funzioni server custom.
In quel caso nella cartella `vps/` c'è già un kit completo (nginx + systemd + deploy).
