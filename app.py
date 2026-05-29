#!/usr/bin/env python3
"""app.py — Interfaccia web Sogni d'Oro (Streamlit).

Design accessibile per utenti over 60:
- Una sola pagina scorrevole, nessun tab
- Step numerati PASSO 1 / PASSO 2 / PASSO 3
- Font minimo 20px, bottoni alti 60px+
- Numeri in grande e subito visibili
- Linguaggio semplice e diretto

Avvio:
    streamlit run app.py
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from datetime import datetime as _dt
from pathlib import Path

import streamlit as st

# ── Percorso radice ─────────────────────────────────────────────────────────
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
    page_title="Sogni e Numeri — Interpreta il tuo sogno",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ══════════════════════════════════════════════════════════════════════════════
# CSS — ACCESSIBILE, FONT GRANDI, BOTTONI ENORMI
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

/* ── base ── */
html, body, [data-testid="stApp"] {
    background: #0d0d1a !important;
    color: #e8d5b7 !important;
    font-family: 'Crimson Text', Georgia, serif;
    font-size: 20px !important;
}

/* ── nascondi decorazioni Streamlit ── */
[data-testid="stHeader"] { display: none; }
[data-testid="stAppViewContainer"] > .main > div:first-child { padding-top: 0 !important; }
footer { display: none !important; }

/* ── header principale ── */
.app-header {
    text-align: center;
    padding: 2.5rem 1rem 2rem;
    border-bottom: 2px solid #c9a84c33;
    margin-bottom: 2.5rem;
}
.app-title {
    font-family: 'Cinzel', serif;
    font-size: clamp(2.4rem, 6vw, 4.5rem);
    color: #c9a84c;
    letter-spacing: 0.15em;
    text-shadow: 0 0 40px rgba(201,168,76,0.4);
    margin: 0;
    line-height: 1.1;
}
.app-tagline {
    font-family: 'Crimson Text', serif;
    font-size: 1.3rem;
    color: #c8b89a;
    margin-top: 0.8rem;
    font-style: italic;
}
.app-welcome {
    font-size: 1.15rem;
    color: #9e8a6a;
    margin-top: 1rem;
    line-height: 1.7;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

/* ── passo / step label ── */
.step-label {
    font-family: 'Cinzel', serif;
    font-size: 1.3rem;
    color: #c9a84c;
    letter-spacing: 0.1em;
    margin: 2rem 0 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #c9a84c;
    color: #0d0d1a;
    font-family: 'Cinzel', serif;
    font-weight: 700;
    font-size: 1.1rem;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    flex-shrink: 0;
}
.step-instruction {
    font-size: 1.1rem;
    color: #9e8a6a;
    margin-bottom: 0.8rem;
    font-style: italic;
}

/* ── textarea grande ── */
textarea {
    background: #12122a !important;
    color: #e8d5b7 !important;
    border: 2px solid #c9a84c55 !important;
    border-radius: 12px !important;
    font-family: 'Crimson Text', serif !important;
    font-size: 1.25rem !important;
    line-height: 1.7 !important;
    padding: 1rem !important;
}
textarea:focus {
    border-color: #c9a84caa !important;
    box-shadow: 0 0 16px rgba(201,168,76,0.25) !important;
}
textarea::placeholder { color: #5a4a35 !important; font-style: italic !important; }

/* ── BOTTONE PRINCIPALE — enorme ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #7a5a10, #c9a84c) !important;
    color: #0d0d1a !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    border: none !important;
    border-radius: 12px !important;
    min-height: 70px !important;
    font-size: 1.4rem !important;
    box-shadow: 0 6px 30px rgba(201,168,76,0.4) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 10px 40px rgba(201,168,76,0.6) !important;
    transform: translateY(-2px) !important;
}

/* ── bottoni secondari ── */
[data-testid="stButton"] > button:not([kind="primary"]) {
    background: #1a1a2e !important;
    color: #c9a84c !important;
    border: 2px solid #c9a84c55 !important;
    border-radius: 10px !important;
    font-family: 'Cinzel', serif !important;
    font-size: 1.1rem !important;
    min-height: 60px !important;
}

/* ── download button ── */
[data-testid="stDownloadButton"] > button {
    background: #1a1a2e !important;
    color: #c9a84c !important;
    border: 2px solid #c9a84c55 !important;
    border-radius: 10px !important;
    font-family: 'Cinzel', serif !important;
    font-size: 1.1rem !important;
    min-height: 60px !important;
    width: 100% !important;
}

/* ── sezione risultati: NUMERI GRANDI ── */
.numeri-header {
    font-family: 'Cinzel', serif;
    font-size: 1.6rem;
    color: #c9a84c;
    text-align: center;
    letter-spacing: 0.12em;
    margin: 2rem 0 0.5rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid #c9a84c33;
}
.numeri-sottotitolo {
    text-align: center;
    color: #9e8a6a;
    font-size: 1rem;
    margin-bottom: 1.5rem;
    font-style: italic;
}

/* ── card numero grande ── */
.num-grande-card {
    background: linear-gradient(145deg, #14142e 0%, #1a1a38 100%);
    border: 2px solid #c9a84c55;
    border-radius: 16px;
    text-align: center;
    padding: 1.6rem 0.5rem 1.2rem;
    margin: 4px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(201,168,76,0.15);
}
.num-grande-cifra {
    font-family: 'Cinzel', serif;
    font-size: 3.5rem;
    color: #c9a84c;
    line-height: 1;
    text-shadow: 0 0 24px rgba(201,168,76,0.5);
    font-weight: 700;
}
.num-grande-da {
    font-size: 0.85rem;
    color: #7a6a50;
    margin-top: 0.6rem;
    font-style: italic;
}

/* ── sezione giochi ── */
.gioco-header {
    font-family: 'Cinzel', serif;
    font-size: 1.1rem;
    color: #c9a84c;
    letter-spacing: 0.08em;
    margin: 1.8rem 0 0.5rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid #c9a84c22;
}
.gioco-nota {
    color: #5a4a35;
    font-size: 0.9rem;
    font-style: italic;
    margin-bottom: 0.8rem;
}

/* ── card numero gioco ── */
.num-gioco-card {
    background: #12122a;
    border: 1px solid #c9a84c33;
    border-radius: 12px;
    text-align: center;
    padding: 1rem 0.3rem 0.8rem;
    margin: 3px;
}
.num-gioco-cifra {
    font-family: 'Cinzel', serif;
    font-size: 2.2rem;
    color: #c9a84c;
    line-height: 1;
    font-weight: 700;
}
.num-gioco-pianeta {
    font-size: 0.72rem;
    color: #5a4a35;
    margin-top: 0.3rem;
}

/* ── sezione simboli ── */
.simboli-header {
    font-family: 'Cinzel', serif;
    font-size: 1.4rem;
    color: #c9a84c;
    letter-spacing: 0.1em;
    margin: 2.5rem 0 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #c9a84c22;
}
.simbolo-riga {
    background: #12122a;
    border-left: 4px solid #c9a84c;
    border-radius: 0 10px 10px 0;
    padding: 0.9rem 1.2rem;
    margin: 0.5rem 0;
    font-size: 1.05rem;
}
.simbolo-nome {
    font-family: 'Cinzel', serif;
    color: #c9a84c;
    font-weight: 700;
    font-size: 1.1rem;
}
.simbolo-numeri {
    color: #8fb3c0;
    font-size: 1rem;
    margin-top: 0.2rem;
}
.simbolo-fonte {
    color: #5a4a35;
    font-size: 0.85rem;
    font-style: italic;
    margin-top: 0.2rem;
}

/* ── sezione esoterica opzionale ── */
.eso-container {
    background: #09091a;
    border: 1px solid #c9a84c22;
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    margin: 0.6rem 0;
    font-family: 'Crimson Text', serif;
    font-size: 1.05rem;
    line-height: 1.85;
    white-space: pre-wrap;
    color: #c8b89a;
}
.eso-titolo-sezione {
    font-family: 'Cinzel', serif;
    color: #c9a84c;
    font-size: 0.85rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
    opacity: 0.8;
}

/* ── expander "Vuoi sapere di più?" ── */
[data-testid="stExpander"] {
    background: #0f0f22 !important;
    border: 1px solid #c9a84c22 !important;
    border-radius: 12px !important;
    margin-top: 2rem !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Cinzel', serif !important;
    color: #c9a84c !important;
    font-size: 1.2rem !important;
    padding: 1rem 1.4rem !important;
}

/* ── avviso / notice ── */
.avviso {
    background: #09091a;
    border: 1px solid #c9a84c11;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    font-size: 0.95rem;
    color: #5a4a35;
    font-style: italic;
    text-align: center;
    margin-top: 2rem;
}

/* ── separatore ── */
.sep {
    text-align: center;
    color: #3a3a5a;
    font-size: 1.3rem;
    letter-spacing: 0.5em;
    margin: 2rem 0;
}

/* ── spinner nativo (nascosto — usiamo il nostro overlay) ── */
[data-testid="stSpinner"] { display: none !important; }

/* ══ LOADING OVERLAY — pioggia dorata ══ */
.sogni-overlay {
    position: fixed;
    inset: 0;
    background: rgba(5, 5, 20, 0.97);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}
.pioggia {
    position: absolute;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
}
@keyframes caduta {
    0%   { transform: translateY(-120px) scale(0.8); opacity: 0; }
    8%   { opacity: 1; }
    85%  { opacity: 0.7; }
    100% { transform: translateY(110vh) scale(1.1); opacity: 0; }
}
.moneta {
    position: absolute;
    top: -80px;
    color: #c9a84c;
    animation: caduta linear infinite;
    user-select: none;
}
@keyframes brilla-msg {
    0%, 100% { opacity: 0.75; text-shadow: 0 0 20px rgba(201,168,76,0.4); }
    50%       { opacity: 1;    text-shadow: 0 0 60px rgba(201,168,76,0.9),
                                            0 0 120px rgba(201,168,76,0.3); }
}
.loading-titolo {
    font-family: 'Cinzel', serif;
    font-size: clamp(1.8rem, 4vw, 3rem);
    color: #c9a84c;
    z-index: 2;
    text-align: center;
    padding: 0 1.5rem;
    animation: brilla-msg 2s ease-in-out infinite;
    line-height: 1.3;
}
.loading-sub {
    font-family: 'Crimson Text', serif;
    font-size: 1.15rem;
    color: #7a6a50;
    font-style: italic;
    z-index: 2;
    margin-top: 1.2rem;
    animation: brilla-msg 2s ease-in-out infinite 0.6s;
}
@keyframes tre-punti {
    0%  { content: ''; }
    25% { content: '.'; }
    50% { content: '..'; }
    75% { content: '...'; }
}
.puntini::after {
    content: '';
    animation: tre-punti 1.4s steps(4, end) infinite;
}
@keyframes cerchio-gira {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
.loading-ruota {
    width: 56px; height: 56px;
    border: 3px solid #c9a84c22;
    border-top-color: #c9a84c;
    border-radius: 50%;
    animation: cerchio-gira 1s linear infinite;
    z-index: 2;
    margin-top: 2rem;
}

/* ── alert ── */
[data-testid="stAlert"] { border-radius: 10px !important; font-size: 1.05rem !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d0d1a; }
::-webkit-scrollbar-thumb { background: #c9a84c44; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #c9a84c88; }

/* ══ BOTTONE FISSO "TORNA SU" ══ */
.btn-torna-su {
    position: fixed;
    bottom: 1.8rem;
    right: 1.8rem;
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #8b6914, #c9a84c);
    color: #0d0d1a !important;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    font-weight: 900;
    text-decoration: none !important;
    box-shadow: 0 4px 24px rgba(201,168,76,0.5);
    z-index: 1000;
    transition: transform 0.2s, box-shadow 0.2s;
    line-height: 1;
}
.btn-torna-su:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(201,168,76,0.7);
}
.btn-torna-su-etichetta {
    position: fixed;
    bottom: 5rem;
    right: 1.3rem;
    font-size: 0.7rem;
    color: #c9a84c88;
    font-family: 'Cinzel', serif;
    letter-spacing: 0.05em;
    text-align: center;
    width: 70px;
    z-index: 1000;
}
</style>
""", unsafe_allow_html=True)

# CSS accessibilità over 60 (file esterno)
_css60_path = ROOT / "static" / "style_60plus.css"
if _css60_path.exists():
    st.markdown(f"<style>{_css60_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ── Bottone fisso "Torna su" — sempre visibile ────────────────────────────────
st.markdown("""
<a href="#" class="btn-torna-su" title="Torna all'inizio">▲</a>
<div class="btn-torna-su-etichetta">Torna su</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CACHE INDICI
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="Caricamento in corso, attendi qualche secondo…")
def _load_entries():
    return _dc.load_indexes()


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: info Sepharial per un numero
# ══════════════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: disegna cards numeri di una combinazione gioco
# ══════════════════════════════════════════════════════════════════════════════

def _render_combo_gioco(label: str, combo: tuple[int, ...], nota: str = "") -> None:
    st.markdown(f'<div class="gioco-header">🎱 {label}</div>', unsafe_allow_html=True)
    if nota:
        st.markdown(f'<div class="gioco-nota">{nota}</div>', unsafe_allow_html=True)
    cols = st.columns(len(combo))
    for col, n in zip(cols, combo):
        pianeta, _, _ = _sp_info(n)
        with col:
            st.markdown(f"""
<div class="num-gioco-card">
  <div class="num-gioco-cifra">{n:02d}</div>
  <div class="num-gioco-pianeta">{pianeta if pianeta else "&nbsp;"}</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="app-header">
  <div style="display:flex; justify-content:center; margin-bottom:1.2rem;">
    <img src="data:image/png;base64,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"
         style="width:200px; height:200px; object-fit:contain; filter:drop-shadow(0 0 30px rgba(201,168,76,0.35));"
         alt="Sogni e Numeri">
  </div>
  <div class="app-title">Sogni e Numeri</div>
  <div class="app-tagline">✨ Ogni sogno porta un messaggio — scopri cosa ti vuole dire</div>
  <div class="app-welcome">
    Benvenuto nel portale dell'interpretazione onirica. Racconta il tuo sogno con parole semplici:
    persone, animali, luoghi, oggetti, sensazioni. Il sistema consulterà sette fonti antiche
    — dalla Smorfia napoletana alla Cabala ebraica — per restituirti il significato simbolico
    nascosto nella tua notte.
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PASSO 1 — SCRIVI IL TUO SOGNO
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="step-label">
  <span class="step-num">1</span>
  &nbsp;Scrivi il tuo sogno qui sotto
</div>
<div class="step-instruction">
  Usa parole semplici. Puoi scrivere liberamente: persone, animali, luoghi,
  oggetti, colori, sensazioni. Anche un solo elemento va bene.
</div>
""", unsafe_allow_html=True)

dream_input = st.text_area(
    label="Il tuo sogno",
    label_visibility="collapsed",
    placeholder="Per esempio: ho sognato un cavallo bianco che correva sul mare, c'era anche mia madre…",
    height=180,
)


# ══════════════════════════════════════════════════════════════════════════════
# PASSO 2 — PREMI IL BOTTONE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="step-label">
  <span class="step-num">2</span>
  &nbsp;Premi il bottone qui sotto
</div>
""", unsafe_allow_html=True)

analyze = st.button("🔮  GENERA LA TUA LETTURA SIMBOLICA", type="primary", use_container_width=True)

st.markdown('<div class="sep">✦ &nbsp; ✦ &nbsp; ✦</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MESSAGGIO SE BOTTONE PREMUTO SENZA TESTO
# ══════════════════════════════════════════════════════════════════════════════

if analyze and not dream_input.strip():
    st.warning("Scrivi qualcosa nel box qui sopra — anche solo poche parole del tuo sogno — poi premi di nuovo il bottone.")


# ══════════════════════════════════════════════════════════════════════════════
# ANALISI PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

if analyze and dream_input.strip():
    dream = dream_input.strip()

    # ── SCHERMATA DI CARICAMENTO — pioggia dorata ────────────────────────────
    _MONETE = [
        # (left%, simbolo, font-size, delay-s, duration-s)
        ( 3, "✦",  "1.3rem", 0.0, 2.8), ( 9, "7",   "2.2rem", 0.5, 3.4),
        (15, "☽",  "1.6rem", 1.0, 2.5), (21, "★",   "2.0rem", 1.7, 3.1),
        (27, "22", "1.5rem", 0.2, 2.9), (33, "✨",  "2.4rem", 1.3, 3.6),
        (39, "90", "1.8rem", 0.8, 2.7), (45, "☆",   "1.4rem", 2.0, 3.2),
        (51, "33", "2.1rem", 0.4, 2.6), (57, "✦",   "1.6rem", 1.5, 3.0),
        (63, "★",  "1.9rem", 0.9, 2.4), (69, "☽",   "2.3rem", 2.2, 3.5),
        (75, "77", "1.7rem", 0.3, 2.8), (81, "✨",  "1.5rem", 1.1, 3.3),
        (87, "13", "2.0rem", 1.8, 2.6), (93, "✦",   "1.4rem", 0.6, 3.1),
        ( 6, "★",  "1.8rem", 2.5, 2.9), (12, "☆",   "2.2rem", 2.8, 3.4),
        (18, "7",  "1.5rem", 2.1, 2.5), (24, "✦",   "1.9rem", 3.0, 3.2),
        (30, "☽",  "1.6rem", 2.4, 2.7), (36, "★",   "2.0rem", 3.2, 3.6),
        (42, "44", "1.7rem", 2.7, 2.8), (48, "✨",  "1.4rem", 3.4, 3.0),
        (54, "☆",  "2.1rem", 2.9, 3.3), (60, "90",  "1.8rem", 3.1, 2.6),
        (66, "✦",  "1.5rem", 3.5, 2.9), (72, "★",   "2.3rem", 2.6, 3.5),
        (78, "☽",  "1.6rem", 3.3, 2.7), (84, "7",   "2.0rem", 2.3, 3.1),
        (90, "✦",  "1.7rem", 3.8, 2.8), (96, "✨",  "1.9rem", 3.6, 3.4),
    ]
    _pioggia_html = "".join(
        f'<span class="moneta" style="left:{l}%;font-size:{fs};'
        f'animation-delay:{d}s;animation-duration:{dur}s">{ch}</span>'
        for l, ch, fs, d, dur in _MONETE
    )
    _loading = st.empty()
    _loading.markdown(f"""
<div class="sogni-overlay">
  <div class="pioggia">{_pioggia_html}</div>
  <div class="loading-titolo">🌙 Sto leggendo i tuoi sogni<span class="puntini"></span></div>
  <div class="loading-sub">Consultando le 7 fonti antiche</div>
  <div class="loading-ruota"></div>
</div>
""", unsafe_allow_html=True)

    # ── carica indici (cache dopo il primo avvio) ────────────────────────────
    try:
        entries = _load_entries()
    except FileNotFoundError as exc:
        _loading.empty()
        st.error(f"Non riesco a trovare i file con i simboli.\n\n{exc}")
        st.stop()

    # ── matching, scoring, combinazioni ─────────────────────────────────────
    matches = _dc.find_matches(dream, entries, 24)
    scores  = _dc.score_numbers(matches)

    lotto         = _dc.build_combo(scores, dream, 5, 90)
    millionday    = _dc.build_combo(scores, dream, 5, 55)
    superenalotto = _dc.build_combo(scores, dream, 6, 90)

    _dc._spiega_combo._last_matches = matches  # type: ignore[attr-defined]

    # ── mappa numero → simboli di origine ───────────────────────────────────
    num_to_simboli: dict[int, list[str]] = defaultdict(list)
    for m in matches:
        for n in m.entry.numbers:
            s = m.entry.symbol
            if s not in num_to_simboli[n]:
                num_to_simboli[n].append(s)

    # ── RIMUOVI LA SCHERMATA DI CARICAMENTO ─────────────────────────────────
    _loading.empty()

    # ════════════════════════════════════════════════════════════════════════
    # PASSO 3 — I TUOI RISULTATI
    # ════════════════════════════════════════════════════════════════════════

    st.markdown("""
<div class="step-label">
  <span class="step-num">3</span>
  &nbsp;Ecco i tuoi risultati
</div>
""", unsafe_allow_html=True)

    if not matches:
        st.warning(
            "Non ho trovato simboli corrispondenti al tuo sogno. "
            "Prova a scrivere con più parole: nomi di persone, animali, oggetti, luoghi, colori."
        )
        st.stop()

    # ────────────────────────────────────────────────────────────────────────
    # SEZIONE A — I TUOI NUMERI DI OGGI (top 10 per score)
    # ────────────────────────────────────────────────────────────────────────

    st.markdown("""
<div class="numeri-header">✦ I NUMERI DEL TUO SOGNO ✦</div>
<div class="numeri-sottotitolo">
  Ogni simbolo onirico porta con sé un numero — radice della sua energia nella tradizione simbolica
</div>
""", unsafe_allow_html=True)

    top_scores = scores.most_common(10)
    if top_scores:
        # prima riga: primi 5 numeri in grande
        primo_blocco = top_scores[:5]
        cols = st.columns(len(primo_blocco))
        for col, (numero, _score) in zip(cols, primo_blocco):
            simboli_origine = ", ".join(num_to_simboli[numero][:2]) if num_to_simboli[numero] else "—"
            with col:
                st.markdown(f"""
<div class="num-grande-card">
  <div class="num-grande-cifra">{numero:02d}</div>
  <div class="num-grande-da">{simboli_origine}</div>
</div>
""", unsafe_allow_html=True)

        # seconda riga: numeri 6-10 (leggermente più piccoli)
        if len(top_scores) > 5:
            secondo_blocco = top_scores[5:]
            st.markdown(
                '<div style="font-size:0.9rem; color:#5a4a35; text-align:center; margin-top:0.8rem; font-style:italic;">'
                'Altri numeri suggeriti dal sogno:'
                '</div>',
                unsafe_allow_html=True,
            )
            cols2 = st.columns(len(secondo_blocco))
            for col, (numero, _score) in zip(cols2, secondo_blocco):
                simboli_origine = ", ".join(num_to_simboli[numero][:2]) if num_to_simboli[numero] else "—"
                with col:
                    st.markdown(f"""
<div class="num-grande-card" style="padding:1rem 0.3rem 0.8rem;">
  <div class="num-grande-cifra" style="font-size:2.6rem;">{numero:02d}</div>
  <div class="num-grande-da">{simboli_origine}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="sep">· · ·</div>', unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # SEZIONE B — COMBINAZIONI PER GIOCO
    # ────────────────────────────────────────────────────────────────────────

    st.markdown("""
<div class="numeri-header" style="font-size:1.3rem;">🔢 SEQUENZE SIMBOLICHE DEL SOGNO</div>
<div class="numeri-sottotitolo">
  Combinazioni numeriche generate dall'energia simbolica dei tuoi elementi onirici
</div>
""", unsafe_allow_html=True)

    _render_combo_gioco("Sequenza di 5 numeri — radici 1–90", lotto)
    _render_combo_gioco("Sequenza di 5 numeri — radici 1–55", millionday)
    _render_combo_gioco("Sequenza di 6 numeri — radici 1–90", superenalotto)

    st.markdown("""
<div class="avviso">
  ✦ &nbsp; Questa è una lettura simbolica basata su tradizioni esoteriche antiche. &nbsp; ✦
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="sep">✦ &nbsp; ✦ &nbsp; ✦</div>', unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # SEZIONE C — I SIMBOLI DEL TUO SOGNO
    # ────────────────────────────────────────────────────────────────────────

    st.markdown("""
<div class="simboli-header">🎴 I simboli del tuo sogno</div>
<div style="color:#9e8a6a; font-size:1.05rem; margin-bottom:1.5rem; font-style:italic; line-height:1.7;">
  Il sogno parla per immagini. Ogni elemento che hai vissuto stanotte — una figura, un luogo,
  un animale, un colore — è un simbolo che le tradizioni esoteriche interpretano da secoli.
  Qui trovi la lettura di ciascuno, con i numeri che gli appartengono.
</div>
""", unsafe_allow_html=True)

    # Mappa fonte → descrizione narrativa
    _fonte_desc = {
        "smorfia":    "Smorfia Napoletana — la voce del popolo del Sud",
        "capacelli":  "Capacelli 1881 — il grande libro dei sogni dell'Ottocento",
        "sepharial":  "Sepharial 1920 — numerologia planetaria",
        "ronchetti":  "Ronchetti 1922 — dizionario illustrato dei simboli",
        "cabala":     "Cabala — tradizione esoterica ebraica",
        "sefer":      "Sefer Yetzira — il Libro della Formazione",
    }

    for idx, match in enumerate(matches[:15], 1):
        nums_str = "  ·  ".join(f"<strong>{n}</strong>" for n in match.entry.numbers)
        src_raw  = _dc.source_short(match.entry.source).lower()
        src_desc = next((v for k, v in _fonte_desc.items() if k in src_raw), f"Fonte: {_dc.source_short(match.entry.source)}")
        simbolo  = match.entry.symbol.capitalize()

        st.markdown(f"""
<div class="simbolo-riga" style="padding:1.2rem 1.4rem; margin-bottom:1rem;
     border-left:3px solid #c9a84c55; border-radius:0 12px 12px 0;">
  <div class="simbolo-nome" style="font-size:1.25rem; margin-bottom:0.4rem;">
    <span style="color:#c9a84c44; font-size:0.9rem; margin-right:0.5rem;">{idx:02d}</span>
    {simbolo}
  </div>
  <div style="font-family:'Crimson Text',serif; font-size:1rem; color:#c8b89a;
              line-height:1.7; margin-bottom:0.5rem; font-style:italic;">
    {match.entry.definition if hasattr(match.entry, 'definition') and match.entry.definition else
     f"Simbolo onirico tramandato dalla tradizione — {simbolo.lower()} porta con sé un'energia numerica precisa."}
  </div>
  <div class="simbolo-numeri" style="margin-bottom:0.3rem;">
    Numeri associati: {nums_str}
  </div>
  <div class="simbolo-fonte" style="font-size:0.85rem; color:#5a4a35;">
    📖 {src_desc}
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="sep">✦ &nbsp; ✦ &nbsp; ✦</div>', unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # SCARICA + KO-FI
    # ────────────────────────────────────────────────────────────────────────

    full_response = _dc.render_response(dream, matches)
    md_content = (
        "---\n"
        "tags: [sogni, numeri, lettura-simbolica, output]\n"
        f"data: {_dt.now().isoformat(timespec='seconds')}\n"
        "---\n\n"
        "# Sogno analizzato — Sogni d'Oro\n\n"
        f"> {dream}\n\n"
        "```\n"
        f"{full_response}\n"
        "```\n"
    )
    timestamp_fn = _dt.now().strftime("%Y%m%d_%H%M%S")

    col_dl, col_kofi = st.columns(2)
    with col_dl:
        st.download_button(
            label="📥  Salva l'analisi sul tuo computer",
            data=md_content.encode("utf-8"),
            file_name=f"sogno_{timestamp_fn}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_kofi:
        st.markdown(
            """<a href="https://ko-fi.com/sognienumeri" target="_blank"
               style="display:flex; align-items:center; justify-content:center;
                      min-height:60px; text-align:center;
                      background:linear-gradient(135deg,#7a5a10,#c9a84c);
                      color:#0d0d1a; font-family:'Cinzel',serif; font-weight:700;
                      font-size:1.1rem; padding:0.8rem 1rem; border-radius:10px;
                      text-decoration:none; box-shadow:0 4px 20px rgba(201,168,76,0.3);">
               ☕ Offrimi un caffè — grazie!
            </a>""",
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # SEZIONE D — OPZIONALE: "Vuoi sapere di più?"
    # ────────────────────────────────────────────────────────────────────────

    with st.expander("✦  Vuoi sapere di più?  —  Lettura simbolica approfondita"):
        st.markdown(
            '<div style="color:#9e8a6a; font-size:1rem; margin-bottom:1rem; font-style:italic;">'
            'Questa sezione è per chi è curioso: contiene una lettura più approfondita '
            'basata su testi esoterici e cabalistici. È facoltativa — i numeri che ti '
            'servono li hai già visti qui sopra.'
            '</div>',
            unsafe_allow_html=True,
        )

        if not _CABALA_OK:
            st.warning("Il modulo per la lettura esoterica non è disponibile (cabala_layer.py mancante).")
        elif not scores:
            st.info("Non ci sono dati sufficienti per la lettura approfondita.")
        else:
            numeri_top  = [n for n, _ in scores.most_common(10)]
            simboli_unici = list({m.entry.symbol for m in matches[:12]})

            with st.spinner("Elaborazione lettura esoterica…"):
                lettura = _cabala.leggi_sogno(dream, simboli_unici, numeri_top)

            testo_grezzo = _cabala.formatta_lettura(lettura)

            def _split_sections(testo: str) -> list[tuple[str, str]]:
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
                st.code(testo_grezzo, language=None)
            else:
                if sections and sections[0][0] == "":
                    st.markdown(f"""
<div class="eso-container" style="border-color:#c9a84c44; text-align:center;">
{sections[0][1]}
</div>
""", unsafe_allow_html=True)
                    sections = sections[1:]

                for title, content in sections:
                    if not content.strip():
                        continue
                    st.markdown(
                        f'<div class="eso-titolo-sezione">{"✦ " + title if title else "✦ Lettura"}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f'<div class="eso-container">{content}</div>', unsafe_allow_html=True)

            if hasattr(lettura, "albero_ascii") and lettura.albero_ascii:
                st.markdown(
                    '<div class="eso-titolo-sezione">🌳 Albero della Vita — Sefirot</div>',
                    unsafe_allow_html=True,
                )
                st.code(lettura.albero_ascii, language=None)

    # ── BOTTONE: ANALIZZA UN ALTRO SOGNO ────────────────────────────────────
    st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
    st.markdown("""
<div style="text-align:center; font-family:'Crimson Text',serif; font-size:1.1rem;
            color:#7a6a50; font-style:italic; margin-bottom:1rem;">
  Vuoi analizzare un altro sogno?
</div>
""", unsafe_allow_html=True)
    col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
    with col_r2:
        if st.button("🔄  Analizza un altro sogno", use_container_width=True):
            st.rerun()
    st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)




# ══════════════════════════════════════════════════════════════════════════════
# DISCLAIMER COMPLETO
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div style="height: 2rem"></div>', unsafe_allow_html=True)

with st.expander("⚖️  Note legali e informazioni"):
    st.markdown("""
<div style="font-family:'Crimson Text',Georgia,serif; font-size:1rem;
            color:#9e8a6a; line-height:1.8;">

<p><strong style="color:#c9a84c;">1. Scopo culturale e ricreativo</strong><br>
Sogni e Numeri è un'applicazione a scopo <em>puramente culturale ed esplorativo</em>.
Le corrispondenze tra sogni e numeri si basano su tradizioni popolari italiane e testi
di pubblico dominio (Smorfia napoletana, Capacelli 1881, Sefer Yetzira,
Sepharial 1920, Ronchetti 1922). I numeri prodotti sono frutto di lettura simbolica
e non hanno alcuna valenza predittiva.</p>

<p><strong style="color:#c9a84c;">2. Privacy e dati personali</strong><br>
Sogni e Numeri <em>non raccoglie, non archivia e non trasmette</em> dati personali.
Il testo del sogno viene elaborato in tempo reale e non viene conservato.
Non utilizziamo cookie di profilazione. La piattaforma di hosting è Streamlit
Community Cloud (Snowflake Inc.) —
<a href="https://streamlit.io/privacy-policy" target="_blank" style="color:#c9a84c;">Privacy Policy</a>.</p>

<p><strong style="color:#c9a84c;">3. Proprietà intellettuale</strong><br>
Le fonti (Smorfia napoletana, Capacelli 1881, Sefer Yetzira, Sepharial 1920, Ronchetti 1922)
sono opere di pubblico dominio. Il codice e la grafica sono di proprietà del gestore.
È vietata la riproduzione senza autorizzazione scritta.</p>

<p><strong style="color:#c9a84c;">4. Legge applicabile</strong><br>
L'applicazione è gestita dall'Italia. Si applica la legge italiana.</p>

<p style="color:#5a4a35; font-size:0.85rem; margin-top:1.5rem; border-top:1px solid #2a2a3a; padding-top:1rem;">
  <em>Ultimo aggiornamento: 2026.</em>
</p>

</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BANNER GIOCO RESPONSABILE (fisso in fondo — sempre visibile)
# ══════════════════════════════════════════════════════════════════════════════



# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div style="height: 1rem"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#2a2a4a; font-size:0.82rem; font-style:italic;
            border-top:1px solid #1a1a35; padding-top:1.2rem; line-height:2.2;">
  🌙 Sogni e Numeri — Lettura simbolica dei sogni<br>
  7 fonti esoteriche &nbsp;·&nbsp; Smorfia napoletana &nbsp;·&nbsp; Capacelli 1881
  &nbsp;·&nbsp; Sefer Yetzira &nbsp;·&nbsp; Sepharial (1920) &nbsp;·&nbsp; Ronchetti (1922)<br>
  <a href="https://ko-fi.com/sognienumeri" target="_blank"
     style="color:#c9a84c55; text-decoration:none; font-size:0.75rem;">
    ☕ Sostieni il progetto — ko-fi.com/sognienumeri
  </a>
</div>
""", unsafe_allow_html=True)
