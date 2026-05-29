#!/usr/bin/env python3
"""app.py — Interfaccia web SMORFIA (Streamlit).

Avvio:
    streamlit run app.py

Il modulo importa le funzioni dal chatbot CLI (dream_chatbot.py) e dal livello
esoterico (cabala_layer.py) senza duplicare logica.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import streamlit as st

# ── Percorso radice — aggiunto a sys.path per importare i moduli locali ────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import dream_chatbot as _dc  # noqa: E402

try:
    import cabala_layer as _cabala
    _CABALA_OK = True
except ImportError:
    _CABALA_OK = False

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAZIONE PAGINA
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="SMORFIA — Il Sistema dei Sogni",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS CUSTOM
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

/* ── base ── */
html, body, [data-testid="stApp"] {
    background: #0d0d1a !important;
    color: #e8d5b7 !important;
    font-family: 'Crimson Text', Georgia, serif;
}

/* ── hide default streamlit top padding ── */
[data-testid="stAppViewContainer"] > .main > div:first-child { padding-top: 0 !important; }
[data-testid="stHeader"] { display: none; }

/* ── header ── */
.smorfia-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    border-bottom: 1px solid #c9a84c22;
    margin-bottom: 2rem;
}
.smorfia-title {
    font-family: 'Cinzel', serif;
    font-size: clamp(2.2rem, 5vw, 4rem);
    color: #c9a84c;
    letter-spacing: 0.2em;
    text-shadow: 0 0 40px rgba(201,168,76,0.35), 0 0 80px rgba(201,168,76,0.1);
    margin: 0;
    line-height: 1.1;
}
.smorfia-subtitle {
    font-family: 'Crimson Text', serif;
    font-size: 1.05rem;
    color: #7a6a50;
    font-style: italic;
    margin-top: 0.5rem;
    letter-spacing: 0.05em;
}
.smorfia-stars {
    font-size: 1.2rem;
    letter-spacing: 0.3em;
    color: #c9a84c66;
    margin-bottom: 0.3rem;
}

/* ── dream input area ── */
textarea {
    background: #12122a !important;
    color: #e8d5b7 !important;
    border: 1px solid #c9a84c44 !important;
    border-radius: 10px !important;
    font-family: 'Crimson Text', serif !important;
    font-size: 1.1rem !important;
}
textarea:focus {
    border-color: #c9a84c99 !important;
    box-shadow: 0 0 12px rgba(201,168,76,0.2) !important;
}
textarea::placeholder { color: #5a4a35 !important; }

/* ── primary button ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #8b6914, #c9a84c) !important;
    color: #0d0d1a !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.7rem 2rem !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 20px rgba(201,168,76,0.3) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 6px 30px rgba(201,168,76,0.5) !important;
    transform: translateY(-1px);
}

/* ── secondary button ── */
[data-testid="stButton"] > button:not([kind="primary"]) {
    background: #1a1a2e !important;
    color: #c9a84c !important;
    border: 1px solid #c9a84c55 !important;
    border-radius: 8px !important;
    font-family: 'Cinzel', serif !important;
}

/* ── tabs ── */
[data-testid="stTabs"] [data-testid="stTab"] {
    font-family: 'Cinzel', serif !important;
    font-size: 0.9rem !important;
    color: #7a6a50 !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
    color: #c9a84c !important;
    border-bottom: 2px solid #c9a84c !important;
}
[data-testid="stTabsContent"] {
    background: transparent !important;
    border: none !important;
    padding-top: 1rem !important;
}

/* ── metric ── */
[data-testid="stMetric"] {
    background: #12122a;
    border: 1px solid #c9a84c22;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    text-align: center;
}
[data-testid="stMetricLabel"] p { font-family: 'Cinzel', serif !important; font-size: 0.75rem !important; color: #7a6a50 !important; }
[data-testid="stMetricValue"] { font-family: 'Cinzel', serif !important; color: #c9a84c !important; font-size: 2rem !important; }

/* ── symbol card ── */
.sym-card {
    background: linear-gradient(135deg, #0f0f22 0%, #12122a 100%);
    border-left: 3px solid #c9a84c;
    border-radius: 0 10px 10px 0;
    padding: 0.9rem 1.2rem;
    margin: 0.5rem 0;
    transition: border-color 0.2s;
}
.sym-card:hover { border-left-color: #e8c86c; }
.sym-name {
    font-family: 'Cinzel', serif;
    color: #c9a84c;
    font-weight: 700;
    font-size: 1.05rem;
}
.sym-arrow { color: #5a4a35; }
.sym-nums { color: #8fb3c0; font-size: 0.95rem; }
.badge {
    display: inline-block;
    font-size: 0.7rem;
    padding: 1px 9px;
    border-radius: 20px;
    margin: 0 3px;
}
.badge-gold { background: #c9a84c22; color: #c9a84c; border: 1px solid #c9a84c33; }
.badge-blue { background: #8fb3c022; color: #8fb3c0; border: 1px solid #8fb3c033; }
.sym-detail { color: #7a6a50; font-size: 0.85rem; margin-top: 0.25rem; font-style: italic; }
.sym-reason { color: #5a5a80; font-size: 0.78rem; margin-top: 0.15rem; }
.sym-ronchetti {
    color: #b8a0d0;
    font-size: 0.88rem;
    font-style: italic;
    margin-top: 0.4rem;
    border-top: 1px solid #b8a0d011;
    padding-top: 0.3rem;
}

/* ── numero card ── */
.num-card {
    background: linear-gradient(145deg, #14142e 0%, #1a1a38 100%);
    border: 1px solid #c9a84c33;
    border-radius: 14px;
    text-align: center;
    padding: 1.4rem 0.4rem 1rem;
    margin: 3px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(201,168,76,0.1);
    transition: transform 0.15s, box-shadow 0.15s;
}
.num-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(201,168,76,0.2); }
.num-big {
    font-family: 'Cinzel', serif;
    font-size: 2.8rem;
    color: #c9a84c;
    line-height: 1;
    text-shadow: 0 0 20px rgba(201,168,76,0.4);
}
.num-planet { font-size: 0.72rem; color: #7a6a50; margin-top: 0.4rem; letter-spacing: 0.05em; }
.num-minor { font-size: 0.7rem; color: #5a7a88; margin-top: 0.2rem; font-style: italic; }
.num-origin { font-size: 0.75rem; color: #9e8a6a; margin-top: 0.5rem; }

/* ── score row ── */
.score-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.55rem 0.8rem;
    border-radius: 8px;
    margin: 3px 0;
    background: #0f0f22;
    border: 1px solid #1a1a35;
}
.score-num { font-family: 'Cinzel', serif; color: #c9a84c; font-size: 1.4rem; min-width: 40px; text-align: right; }
.score-bar-wrap { flex: 1; background: #1a1a35; border-radius: 4px; height: 6px; }
.score-bar-fill { height: 6px; background: linear-gradient(90deg, #8b6914, #c9a84c); border-radius: 4px; }
.score-val { color: #5a4a35; font-size: 0.75rem; min-width: 60px; }
.score-sp { color: #7a6a50; font-size: 0.8rem; font-style: italic; flex: 2; }

/* ── combo section ── */
.combo-header {
    font-family: 'Cinzel', serif;
    font-size: 1.1rem;
    color: #c9a84c;
    letter-spacing: 0.1em;
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #c9a84c22;
}
.combo-note {
    color: #5a4a35;
    font-size: 0.78rem;
    font-style: italic;
    margin-top: 0.2rem;
}

/* ── esoteric reading ── */
.eso-section {
    background: #09091a;
    border: 1px solid #c9a84c1a;
    border-radius: 12px;
    padding: 1.4rem 1.8rem;
    margin: 0.8rem 0;
    font-family: 'Crimson Text', serif;
    font-size: 1rem;
    line-height: 1.8;
    white-space: pre-wrap;
    color: #c8b89a;
}
.eso-section-title {
    font-family: 'Cinzel', serif;
    color: #c9a84c;
    font-size: 0.82rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
    opacity: 0.8;
}

/* ── separator ── */
.mystic-sep {
    text-align: center;
    color: #3a3a5a;
    font-size: 1.2rem;
    letter-spacing: 0.5em;
    margin: 1.5rem 0;
}

/* ── source comparison ── */
.comparison-item {
    background: #0f0f22;
    border: 1px solid #1a1a35;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    margin: 0.3rem 0;
    font-size: 0.9rem;
    color: #9e8a6a;
}
.comparison-item strong { color: #c9a84c; }
.shared-nums { color: #8fb3c0; font-weight: 600; }

/* ── notice box ── */
.notice {
    background: #09091a;
    border: 1px solid #c9a84c15;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    font-size: 0.82rem;
    color: #5a4a35;
    font-style: italic;
    text-align: center;
    margin-top: 2rem;
}

/* ── spinner ── */
[data-testid="stSpinner"] > div { color: #c9a84c !important; }

/* ── success/info/warning/error ── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d0d1a; }
::-webkit-scrollbar-thumb { background: #c9a84c44; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #c9a84c88; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="smorfia-header">
  <div class="smorfia-stars">✦ ✦ ✦</div>
  <div class="smorfia-title">🌙 SMORFIA</div>
  <div class="smorfia-subtitle">
    Il sistema dei sogni &nbsp;·&nbsp; Smorfia napoletana &nbsp;·&nbsp; Capacelli 1881
    &nbsp;·&nbsp; Sefer Yetzira &nbsp;·&nbsp; Sepharial &nbsp;·&nbsp; Ronchetti
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CACHE INDICI
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="Caricamento indici simbolici (15.000+ voci)…")
def _load_entries():
    return _dc.load_indexes()


# ══════════════════════════════════════════════════════════════════════════════
# INPUT
# ══════════════════════════════════════════════════════════════════════════════

with st.container():
    dream_input = st.text_area(
        "✍️ Racconta il tuo sogno",
        placeholder="Stamattina mi sono svegliato e ricordavo di aver sognato un cavallo bianco che correva sul mare…",
        height=140,
        help="Descrivi liberamente: persone, luoghi, oggetti, azioni, sensazioni, colori, emozioni.",
    )

    col_l, col_btn, col_r = st.columns([3, 2, 3])
    with col_btn:
        analyze = st.button("🔮  Analizza il sogno", use_container_width=True, type="primary")

st.markdown('<div class="mystic-sep">✦ &nbsp; ✦ &nbsp; ✦</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ANALISI
# ══════════════════════════════════════════════════════════════════════════════

if analyze and dream_input.strip():
    dream = dream_input.strip()

    # ── carica indici (cached dopo il primo avvio) ──────────────────────────
    try:
        with st.spinner("Consultando le 7 fonti esoteriche…"):
            entries = _load_entries()
    except FileNotFoundError as exc:
        st.error(f"⚠️ Indici non trovati.\n\n{exc}")
        st.stop()

    # ── matching e scoring ──────────────────────────────────────────────────
    matches = _dc.find_matches(dream, entries, 24)
    scores = _dc.score_numbers(matches)

    # ── combinazioni ────────────────────────────────────────────────────────
    lotto        = _dc.build_combo(scores, dream, 5, 90)
    millionday   = _dc.build_combo(scores, dream, 5, 55)
    superenalotto = _dc.build_combo(scores, dream, 6, 90)

    # condivide i match con _spiega_combo (usa attributo di funzione)
    _dc._spiega_combo._last_matches = matches  # type: ignore[attr-defined]

    # ── helper Sepharial per numero ─────────────────────────────────────────
    def _sp_info(numero: int) -> tuple[str, str, str]:
        """Restituisce (pianeta, minor_key, cap_xi) da Sepharial."""
        if not _CABALA_OK:
            return "", "", ""
        cifra = _cabala.radice_digitale(numero)
        sp = _cabala.SEPHARIAL_CIFRE.get(cifra)
        pianeta = sp.pianeta if sp else ""
        minor   = sp.significato_minore if sp else ""
        sig_key = numero if 1 <= numero <= 84 else (numero % 84 or 84)
        cap_xi  = _cabala.SEPHARIAL_SIGNIFICATI.get(sig_key, "")
        return pianeta, minor, cap_xi

    # ── mappa numero → simboli che l'hanno generato ─────────────────────────
    from collections import defaultdict
    num_to_simboli: dict[int, list[str]] = defaultdict(list)
    for m in matches:
        for n in m.entry.numbers:
            s = m.entry.symbol
            if s not in num_to_simboli[n]:
                num_to_simboli[n].append(s)

    # ════════════════════════════════════════════════════════════════════════
    # TABS
    # ════════════════════════════════════════════════════════════════════════
    tab_sim, tab_num, tab_combo, tab_eso = st.tabs([
        "🎴  Simboli",
        "🔢  Numeri",
        "🎱  Combinazioni",
        "⚗️  Lettura Esoterica",
    ])

    # ────────────────────────────────────────────────────────────────────────
    # TAB 1 — SIMBOLI
    # ────────────────────────────────────────────────────────────────────────
    with tab_sim:
        if not matches:
            st.warning(
                "Nessuna corrispondenza trovata. "
                "Prova a descrivere il sogno con più dettagli: "
                "oggetti, luoghi, persone, azioni, colori, emozioni."
            )
        else:
            # metriche fonti
            source_counts = Counter(_dc.source_short(m.entry.source) for m in matches)
            met_cols = st.columns(len(source_counts) + 1)
            with met_cols[0]:
                st.metric("Simboli trovati", len(matches))
            for i, (src, cnt) in enumerate(source_counts.items(), 1):
                with met_cols[i]:
                    st.metric(src, cnt)

            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

            # confronto fonti (se ci sono simboli in comune)
            comparison = _dc.build_source_comparison(matches)
            if comparison:
                with st.expander("🔍 Confronto tra fonti — stesse parole, numeri diversi", expanded=False):
                    for line in comparison:
                        # colora i numeri "comuni"
                        # line ex: "- Acqua: Smorfia: 3; Capacelli: 7, 12 | comuni: 3"
                        st.markdown(
                            '<div class="comparison-item">' +
                            line.replace("| comuni: ", '| <span class="shared-nums">comuni: ')
                                .replace(" | comuni:", '</span> | comuni:')
                                .replace("- ", "<strong>") + "</strong>" +
                            "</div>",
                            unsafe_allow_html=True,
                        )

            # lista simboli
            for idx, match in enumerate(matches[:24], 1):
                nums_str = " &nbsp;·&nbsp; ".join(str(n) for n in match.entry.numbers)
                src = _dc.source_short(match.entry.source)
                detail = match.entry.detail or "voce diretta"
                nota_r = _dc._ronchetti_nota(match.entry.symbol)

                ronchetti_html = ""
                if nota_r:
                    nota_breve = (nota_r[:220].rsplit(" ", 1)[0] + "…") if len(nota_r) > 220 else nota_r
                    ronchetti_html = f'<div class="sym-ronchetti">☽ Ronchetti: {nota_breve}</div>'

                st.markdown(f"""
<div class="sym-card">
  <span class="sym-name">{idx:02d}. {match.entry.symbol}</span>
  &nbsp;<span class="sym-arrow">→</span>&nbsp;
  <span class="sym-nums">{nums_str}</span>
  &nbsp;&nbsp;
  <span class="badge badge-gold">{src}</span>
  <span class="badge badge-blue">score {match.score:.1f}</span>
  <span class="badge" style="background:#1a2a1a;color:#6a8a6a;border:1px solid #2a4a2a;">pag. {match.entry.page}</span>
  <div class="sym-detail">{detail}</div>
  <div class="sym-reason">↳ {match.reason}</div>
  {ronchetti_html}
</div>
""", unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # TAB 2 — NUMERI
    # ────────────────────────────────────────────────────────────────────────
    with tab_num:
        if not scores:
            st.info("Nessun numero rilevato dalle fonti.")
        else:
            top_scores = scores.most_common(20)
            max_score = top_scores[0][1] if top_scores else 1

            for numero, score in top_scores:
                pianeta, minor, cap_xi = _sp_info(numero)
                bar_pct = int(score / max_score * 100)
                src_simboli = ", ".join(num_to_simboli[numero][:3]) if num_to_simboli[numero] else "—"

                sp_text = ""
                if pianeta:
                    sp_text = pianeta
                    if minor:
                        sp_text += f" · {minor}"
                    if cap_xi:
                        sp_text += f" | {cap_xi[:90]}"

                st.markdown(f"""
<div class="score-row">
  <div class="score-num">{numero:02d}</div>
  <div class="score-bar-wrap">
    <div class="score-bar-fill" style="width:{bar_pct}%"></div>
  </div>
  <div class="score-val">score {score:.0f}</div>
  <div class="score-sp">{sp_text}</div>
</div>
<div style="padding: 0 0 4px 56px; font-size:0.75rem; color:#3a3a5a;">
  ← {src_simboli}
</div>
""", unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # TAB 3 — COMBINAZIONI
    # ────────────────────────────────────────────────────────────────────────
    with tab_combo:

        def _render_combo(label: str, combo: tuple[int, ...], note: str = "") -> None:
            """Disegna un blocco con nome, cards numeri, e dettaglio per-numero."""
            st.markdown(f'<div class="combo-header">🎱 {label}</div>', unsafe_allow_html=True)
            if note:
                st.markdown(f'<div class="combo-note">{note}</div>', unsafe_allow_html=True)

            # cards
            cols = st.columns(len(combo))
            for col, n in zip(cols, combo):
                pianeta, minor, _ = _sp_info(n)
                with col:
                    st.markdown(f"""
<div class="num-card">
  <div class="num-big">{n:02d}</div>
  <div class="num-planet">{pianeta if pianeta else "&nbsp;"}</div>
  <div class="num-minor">{minor[:30] if minor else "&nbsp;"}</div>
</div>
""", unsafe_allow_html=True)

            # dettaglio per-numero
            with st.expander("Dettaglio per numero", expanded=False):
                for n in combo:
                    pianeta, minor, cap_xi = _sp_info(n)
                    src_sim = ", ".join(num_to_simboli[n][:4]) if num_to_simboli[n] else "fill deterministico"
                    parts = []
                    if pianeta:
                        parts.append(f"**{pianeta}**")
                    if minor:
                        parts.append(minor)
                    if cap_xi:
                        parts.append(f"Cap.XI: _{cap_xi[:100]}_")
                    sp_md = " · ".join(parts) if parts else "—"
                    st.markdown(
                        f"**`{n:02d}`** &nbsp;← {src_sim}  \n"
                        f"&nbsp;&nbsp;Sepharial: {sp_md}"
                    )

            st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

        _render_combo(
            "Cinquina Lotto",
            lotto,
            "5 numeri · ruota 1-90",
        )
        _render_combo(
            "Cinquina MillionDAY",
            millionday,
            "5 numeri · pool 1-55",
        )
        _render_combo(
            "Sestina SuperEnalotto",
            superenalotto,
            "6 numeri · pool 1-90",
        )

        st.markdown("""
<div class="notice">
  ✦ &nbsp; Questa è una lettura simbolica basata sui testi del vault. Non è una previsione di estrazioni casuali. &nbsp; ✦
</div>
""", unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # TAB 4 — LETTURA ESOTERICA
    # ────────────────────────────────────────────────────────────────────────
    with tab_eso:
        if not _CABALA_OK:
            st.warning("Modulo cabala_layer non disponibile. Verifica che cabala_layer.py sia nella stessa cartella.")
        elif not scores:
            st.info("Nessun simbolo riconosciuto — la lettura esoterica richiede almeno un numero.")
        else:
            numeri_top = [n for n, _ in scores.most_common(10)]
            simboli_unici = list({m.entry.symbol for m in matches[:12]})

            with st.spinner("Elaborazione lettura esoterica…"):
                lettura = _cabala.leggi_sogno(dream, simboli_unici, numeri_top)

            testo_grezzo = _cabala.formatta_lettura(lettura)

            # splitta in sezioni dal separatore "──"
            def _split_sections(testo: str) -> list[tuple[str, str]]:
                """Divide il testo in coppie (titolo, contenuto)."""
                sections: list[tuple[str, str]] = []
                current_title = ""
                current_lines: list[str] = []
                for line in testo.splitlines():
                    if line.startswith("──"):
                        if current_lines:
                            sections.append((current_title, "\n".join(current_lines).strip()))
                        current_title = line.replace("─", "").strip()
                        current_lines = []
                    else:
                        current_lines.append(line)
                if current_lines:
                    sections.append((current_title, "\n".join(current_lines).strip()))
                return sections

            sections = _split_sections(testo_grezzo)

            if not sections:
                # fallback: mostra testo raw
                st.code(testo_grezzo, language=None)
            else:
                # prima sezione = intestazione generale
                if sections and sections[0][0] == "":
                    st.markdown(f"""
<div class="eso-section" style="border-color:#c9a84c44; text-align:center;">
{sections[0][1]}
</div>
""", unsafe_allow_html=True)
                    sections = sections[1:]

                for title, content in sections:
                    if not content.strip():
                        continue
                    with st.expander(f"✦ {title}" if title else "✦ Lettura", expanded=True):
                        st.markdown(f"""
<div class="eso-section">
{content}
</div>
""", unsafe_allow_html=True)

            # Albero della Vita separato (sempre aperto)
            if hasattr(lettura, "albero_ascii") and lettura.albero_ascii:
                with st.expander("🌳 Albero della Vita — Sefirot", expanded=False):
                    st.code(lettura.albero_ascii, language=None)

    # ════════════════════════════════════════════════════════════════════════
    # DOWNLOAD + SUPPORTO
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="mystic-sep">✦ &nbsp; ✦ &nbsp; ✦</div>', unsafe_allow_html=True)

    from datetime import datetime as _dt
    full_response = _dc.render_response(dream, matches)
    md_content = (
        "---\n"
        "tags: [sogni, smorfia, output]\n"
        f"data: {_dt.now().isoformat(timespec='seconds')}\n"
        "---\n\n"
        "# Sogno analizzato — SMORFIA\n\n"
        f"> {dream}\n\n"
        "```\n"
        f"{full_response}\n"
        "```\n"
    )
    timestamp_fn = _dt.now().strftime("%Y%m%d_%H%M%S")

    col_dl_l, col_dl, col_kofi, col_dl_r = st.columns([2, 2, 2, 2])
    with col_dl:
        st.download_button(
            label="📥  Scarica l'analisi (.md)",
            data=md_content.encode("utf-8"),
            file_name=f"smorfia_sogno_{timestamp_fn}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_kofi:
        st.markdown(
            """<a href="https://ko-fi.com/smorfiasogni" target="_blank"
               style="display:block; text-align:center; background:linear-gradient(135deg,#8b6914,#c9a84c);
                      color:#0d0d1a; font-family:'Cinzel',serif; font-weight:700; font-size:0.95rem;
                      padding:0.6rem 1rem; border-radius:8px; text-decoration:none;
                      box-shadow:0 4px 20px rgba(201,168,76,0.3);">
               ☕ Offrimi un caffè
            </a>""",
            unsafe_allow_html=True,
        )

elif analyze and not dream_input.strip():
    st.warning("Scrivi almeno qualche parola del sogno prima di analizzare.")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Info & Supporto
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
<div style="text-align:center; padding:1rem 0;">
  <div style="font-family:'Cinzel',serif; color:#c9a84c; font-size:1.3rem;">🌙 SMORFIA</div>
  <div style="color:#5a4a35; font-size:0.8rem; font-style:italic; margin-top:0.3rem;">Il sistema dei sogni</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("### 📚 Le 7 Fonti")
    st.markdown("""
- 📖 **Smorfia napoletana** — 5.470 voci
- 📜 **Capacelli 1881** — 9.733 voci
- 🔯 **Sefer Yetzira** — Kabala ebraica
- 📐 **Semprini** — 5 gradi ermeneutici
- 🔮 **Guénon** — Framework esoterico
- 🪐 **Sepharial (1920)** — Numerologia planetaria
- 🏛️ **Ronchetti (1922)** — Iconologia italiana
""")

    st.markdown("---")
    st.markdown("### 💡 Come usarlo")
    st.markdown("""
1. Racconta il tuo sogno nel box di testo
2. Premi **Analizza il sogno**
3. Esplora i tab per simboli, numeri e lettura esoterica
4. Scarica l'analisi in Markdown
""")

    st.markdown("---")
    st.markdown("""
<div style="text-align:center;">
  <a href="https://ko-fi.com/smorfiasogni" target="_blank"
     style="display:block; background:linear-gradient(135deg,#8b6914,#c9a84c);
            color:#0d0d1a; font-family:'Cinzel',serif; font-weight:700;
            padding:0.6rem; border-radius:8px; text-decoration:none; font-size:0.9rem;">
    ☕ Supporta il progetto
  </a>
  <div style="color:#3a3a5a; font-size:0.7rem; margin-top:0.5rem;">
    Ogni caffè aiuta a mantenere vivo il sistema ✦
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<div style="color:#2a2a4a; font-size:0.7rem; text-align:center;">'
        'v1.0 · 7 fonti integrate<br>'
        'Smorfia napoletana · Cabala · Sepharial · Ronchetti'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div style="height: 3rem"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#2a2a4a; font-size:0.75rem; font-style:italic;
            border-top:1px solid #1a1a35; padding-top:1rem; line-height:2;">
  🌙 SMORFIA — Il Sistema dei Sogni<br>
  Smorfia napoletana · Capacelli 1881 · Sefer Yetzira · Semprini · Guénon · Sepharial (1920) · Ronchetti (1922)<br>
  <span style="color:#1a1a35;">─────────────────────────────────</span><br>
  <a href="https://ko-fi.com/smorfiasogni" target="_blank"
     style="color:#c9a84c44; text-decoration:none; font-size:0.7rem;">
    ☕ ko-fi.com/smorfiasogni
  </a>
</div>
""", unsafe_allow_html=True)
