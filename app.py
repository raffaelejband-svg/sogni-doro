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
