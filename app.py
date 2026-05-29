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
    <img src="app/static/logo_sogni_numeri.png"
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
