---
name: Sogni e Numeri
description: Interpretazione simbolica dei sogni ispirata alla Smorfia napoletana e a sette fonti storiche/esoteriche
colors:
  amber-antica: "#b0892e"
  amber-bruciata-profonda: "#7a5e18"
  amber-legacy: "#9a7b2e"
  paper-crema: "#f3e8cf"
  paper-crema-mid: "#efe2c6"
  paper-crema-profondo: "#e9dcc0"
  avorio-superficie: "#f5ecd6"
  avorio-superficie-alt: "#f6eed8"
  inchiostro: "#2b2114"
  inchiostro-tenue: "#5c4a30"
  inchiostro-tenue-legacy: "#6f5a3a"
  lavanda-enfasi: "#b8a0d0"
  errore: "#e05a5a"
typography:
  display:
    fontFamily: "Cinzel, Georgia, serif"
    fontSize: "clamp(2.8rem, 5vw, 4rem)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "0.2em"
  headline:
    fontFamily: "Cinzel, Georgia, serif"
    fontSize: "clamp(2rem, 4vw, 2.8rem)"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.12em"
  title:
    fontFamily: "Cinzel, Georgia, serif"
    fontSize: "clamp(1.5rem, 3vw, 2rem)"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.08em"
  body:
    fontFamily: "'Crimson Text', Georgia, serif"
    fontSize: "1.2rem"
    fontWeight: 400
    lineHeight: 1.8
    letterSpacing: "0.015em"
  label:
    fontFamily: "Cinzel, Georgia, serif"
    fontSize: "1.1rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.06em"
rounded:
  sm: "12px"
  md: "14px"
  lg: "16px"
  xl: "18px"
  pill: "999px"
spacing:
  sm: "0.5rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2rem"
components:
  button-primary:
    backgroundColor: "{colors.amber-antica}"
    textColor: "{colors.inchiostro}"
    typography: "{typography.label}"
    rounded: "{rounded.lg}"
    padding: "1rem 2.8rem"
    height: "64px"
  button-primary-hover:
    backgroundColor: "{colors.amber-bruciata-profonda}"
    textColor: "{colors.inchiostro}"
  button-secondary:
    backgroundColor: "{colors.avorio-superficie}"
    textColor: "{colors.inchiostro}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    height: "52px"
  input-textarea:
    backgroundColor: "{colors.avorio-superficie}"
    textColor: "{colors.inchiostro}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "1rem 1.2rem"
  card-numero:
    backgroundColor: "{colors.avorio-superficie-alt}"
    textColor: "{colors.amber-antica}"
    rounded: "{rounded.xl}"
    padding: "1.4rem 1.2rem 1rem"
  chip-fiducia:
    backgroundColor: "{colors.avorio-superficie}"
    textColor: "{colors.inchiostro}"
    rounded: "{rounded.pill}"
    padding: "0.35rem 0.7rem"
---

# Design System: Sogni e Numeri

## 1. Overview

**Creative North Star: "Il Libro dei Sogni Antico"**

Sogni e Numeri si presenta come un volume rilegato consultato con cura, non come un'app o un gioco. Ogni schermata rievoca la pagina di un libro storico dei sogni: fondo carta color crema, testo inchiostro scuro, titoli in oro inciso, margini generosi che invitano a leggere con calma. Il sistema esiste per servire un pubblico over-60 che deve sentirsi accolto da una fonte autorevole, non intrattenuto da un'interfaccia ludica.

Il sistema rifiuta esplicitamente due estremi: l'**esoterismo da bancarella** (sfere di cristallo pacchiane, font horror, decorazioni new-age a buon mercato) e l'**estetica da casinò/lotteria** (monete lampeggianti, linguaggio da scommessa, urgenza al gioco — vincolo anche legale, non solo di gusto). Tra questi due poli, il sistema sceglie la terza via: la serietà calda di un testo di riferimento.

**Key Characteristics:**
- Palette crema/oro (Ambra Antica) che richiama pagine antiche e inchiostro dorato, mai neon né pastello.
- Serif per tutto: Cinzel per i titoli (autorevole, incisa), Crimson Text per il corpo (leggibile, calda).
- Bagliore, non ombra: l'elevazione si esprime con luce calda diffusa attorno agli elementi, mai con ombre grigie neutre.
- Densità bassa, spaziatura generosa: pensata per occhi e mani over-60, non per la densità informativa di un tool tecnico.

## 2. Colors

Palette calda a bassa saturazione: crema come fondo dominante, oro (Ambra Antica) come unico accento ad alta presenza, inchiostro scuro per il testo — mai grigio neutro.

### Primary
- **Ambra Antica** (`#b0892e`): accento dominante — titoli principali, bottone primario, badge dei passi, micro-titoli. È il colore che porta l'attenzione dell'utente.
- **Ambra Bruciata Profonda** (`#7a5e18`): estremo scuro dei gradienti oro (bottoni, cerchi-passo); usata anche per il testo del sottotitolo (tagline) su fondo chiaro.

### Secondary
- **Ambra Legacy** (`#9a7b2e`): variante più antica dello stesso oro, ancora presente su componenti non ancora migrati al layer di rifinitura più recente (badge, nomi simbolo, numeri delle card). Convergerà verso Ambra Antica nelle prossime iterazioni.

### Neutral
- **Carta Crema** (`#f3e8cf` → `#efe2c6` → `#e9dcc0`): gradiente di sfondo dell'intera app, dall'alto verso il basso — la "pagina" su cui tutto poggia.
- **Superficie Avorio** (`#f5ecd6` / `#f6eed8`): sfondo di textarea, card dei numeri, contenitori del testo — leggermente più chiaro della pagina per suggerire un foglio posato sopra il libro.
- **Inchiostro** (`#2b2114`): colore di testo primario su tutta l'app — mai un grigio, sempre questo bruno-nero caldo.
- **Inchiostro Tenue** (`#5c4a30` / legacy `#6f5a3a`): testo secondario, didascalie, note — stesso bruno dell'inchiostro ma diluito, non un grigio diverso.
- **Lavanda Enfasi** (`#b8a0d0`): unico accento freddo del sistema, riservato al corsivo/enfasi nel testo lungo (es. le note Ronchetti) per distinguerlo visivamente senza introdurre un secondo colore caldo in competizione con l'oro.
- **Errore** (`#e05a5a`): riservato esclusivamente agli alert di errore.

### Named Rules
**La Regola dell'Unico Oro.** Un solo accento ad alta presenza (Ambra Antica) per schermata. Non introdurre un secondo colore saturo per "variare"; la varietà viene da tipografia e spaziatura, non da una seconda tinta calda.

## 3. Typography

**Display/Headline/Title Font:** Cinzel (con fallback Georgia, serif)
**Body Font:** Crimson Text (con fallback Georgia, serif)

**Character:** Cinzel è la voce incisa e cerimoniale — usata solo per titoli, numeri-passo e bottoni, mai per paragrafi lunghi. Crimson Text è la voce di lettura — pensata per essere scorsa a lungo senza affaticare, con line-height generoso (1.7–1.9) e dimensione base 20px, ben sopra lo standard web.

### Hierarchy
- **Display** (700, `clamp(2.8rem, 5vw, 4rem)`, line-height 1.15): titolo principale dell'app (h1, `.smorfia-title`).
- **Headline** (600, `clamp(2rem, 4vw, 2.8rem)`, line-height 1.2): titoli di sezione (h2).
- **Title** (600, `clamp(1.5rem, 3vw, 2rem)`, line-height 1.2): sottotitoli, etichette dei passi, micro-titoli dei box.
- **Body** (400, `1.2rem`, line-height 1.8–1.9, max 72ch): testo dei paragrafi, letture simboliche, note. Larghezza massima 72 caratteri per non affaticare la lettura over-60.
- **Label** (700, `1.1rem`, letter-spacing `0.06–0.08em`): testo dei bottoni e delle etichette dei campi, sempre in Cinzel per coerenza con i titoli.

### Named Rules
**La Regola del Serif Doppio.** Mai un sans-serif nell'interfaccia. Cinzel per ciò che va "annunciato" (titoli, bottoni, numeri), Crimson Text per ciò che va "letto" (corpo, spiegazioni). Un font sans-serif in qualunque punto rompe immediatamente la metafora del libro antico.

## 4. Elevation

Il sistema non usa ombre grigie neutre. La profondità si esprime con **bagliore caldo diffuso**: ombre colorate nella tonalità dell'oro (`rgba(150,118,40,...)` / `rgba(154,123,46,...)`), più ampie e più diffuse di un'ombra materiale standard. Un bottone o una card "premono" verso l'utente con luce, non con un'ombra scura sotto di loro.

### Shadow Vocabulary
- **Bagliore riposo** (`0 4px 24px rgba(150,118,40,0.35)` / `0 16px 44px rgba(80,60,35,0.16)`): stato di default di bottoni primari e contenitori principali (header, dream-console).
- **Bagliore hover** (`0 8px 36-40px rgba(150,118,40,0.55-0.60)`): intensificazione al passaggio del mouse/tocco, accompagnata da un lieve sollevamento (`translateY(-2px/-3px)`).
- **Bagliore attivo** (`0 2px 12-14px rgba(150,118,40,0.4-0.45)`): compressione al click, coerente con il sollevamento che rientra.

### Named Rules
**La Regola della Luce Calda.** Nessuna ombra grigia neutra, mai. Ogni elevazione nel sistema è un bagliore nella tonalità dell'oro o, al massimo, un bruno caldissimo (`rgba(80,60,35,...)`) per le ombre più strutturali e diffuse. Se un'ombra sembra "fredda" o grigia, è sbagliata per questo sistema.

## 5. Components

### Buttons
- **Shape:** angoli generosi, 16px sul bottone primario, 12px sul secondario — mai spigoli vivi.
- **Primary:** gradiente Ambra Antica → Ambra Bruciata Profonda (`135deg`), testo inchiostro in grassetto, altezza minima 60–64px, bagliore caldo di riposo, si solleva e si illumina di più all'hover.
- **Secondary/Ghost:** superficie avorio semi-trasparente, bordo oro sottile (`rgba(154,123,46,0.34)`), testo inchiostro; nessun bagliore di riposo, solo un lieve scurimento del bordo all'hover.
- **Touch target:** ogni bottone e link rispetta un minimo di 48×48px — requisito non negoziabile per l'utenza over-60.

### Chips (trust-pill)
- **Style:** sfondo avorio semi-trasparente, bordo oro sottile, forma a pillola (radius 999px), testo inchiostro compatto.
- **Uso:** badge di fiducia sotto l'header ("Nessuna registrazione", "Funziona da telefono") — informativi, non interattivi.

### Cards / Containers
- **Corner Style:** 14–22px a seconda del ruolo (textarea/alert 14px, header/risultati 18–22px).
- **Background:** superficie avorio o gradiente carta-crema; **attenzione**: alcune card legacy (`.numero-lotto`, `.risultato-principale`) portano ancora un secondo estremo di gradiente verso un blu-notte (`#1e1e40` / `#16163a`), residuo del tema scuro precedente — da correggere in una prossima iterazione, stona su fondo chiaro.
- **Shadow Strategy:** bagliore caldo (vedi Elevation), mai ombra grigia.
- **Border:** 1–2px, sempre nella tonalità oro a opacità variabile, mai un grigio neutro.
- **Internal Padding:** generoso, 1.2–2.4rem a seconda della prominenza del contenuto.

### Inputs / Fields
- **Style:** superficie avorio, bordo oro 2px, radius 14px, font Crimson Text a 1.2rem (24px effettivi) per leggibilità over-60.
- **Focus:** bordo oro pieno + bagliore soffuso (`0 0 18px rgba(150,118,40,0.3)`), nessun outline blu di sistema.
- **Placeholder:** corsivo, tonalità inchiostro-tenue — mai un grigio placeholder generico.

### Navigation
- Non esiste una navigazione a tab tradizionale nel flusso principale: l'app è un percorso lineare a passi numerati (cerchio Ambra Antica con numero in Cinzel), non un pannello con sezioni parallele. Dove i tab esistono ancora (viste secondarie), sono ingranditi (min-height 48px) con indicatore di selezione in oro pieno sotto la tab attiva.

## 6. Do's and Don'ts

### Do:
- **Do** usare Cinzel esclusivamente per titoli, numeri-passo e testo dei bottoni; Crimson Text per tutto il resto del testo leggibile.
- **Do** esprimere ogni elevazione con bagliore caldo nella tonalità dell'oro (`rgba(150,118,40,...)`), mai con un'ombra grigia neutra.
- **Do** mantenere un solo accento saturo per schermata (Ambra Antica); la varietà viene da tipografia e spaziatura.
- **Do** garantire touch target minimo 48×48px e focus visibile in oro pieno (`outline: 3px solid #9a7b2e`) su ogni elemento interattivo, per navigazione da tastiera e screen reader.
- **Do** mantenere line-height generoso (1.7–1.9) e corpo testo ≥20px equivalenti, coerente col target over-60.

### Don't:
- **Don't** introdurre sfere di cristallo, font "horror" o decorazioni new-age a buon mercato — è l'anti-riferimento esplicito "esoterismo da bancarella" di PRODUCT.md.
- **Don't** usare linguaggio, iconografia o animazioni da slot machine/casinò (monete che lampeggiano, urgenza al gioco) — vincolo legale (Decreto Dignità D.L. 87/2018), non solo estetico.
- **Don't** introdurre dashboard asettiche, card identiche ripetute o una palette blu-corporate da tool B2B — l'utente deve sentirsi accolto da un libro, non da un pannello di controllo.
- **Don't** usare ombre grigie neutre (`rgba(0,0,0,...)` piatto) in nessun punto del sistema: rompe la Regola della Luce Calda.
- **Don't** lasciare gradienti residui verso il blu-notte (`#1e1e40`, `#16163a`) nelle card: sono un artefatto del vecchio tema scuro e stonano sul fondo crema attuale.
- **Don't** usare font sans-serif in qualunque punto dell'interfaccia: rompe la metafora del libro antico.
