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
import hashlib
import html as _html
import re
import time
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
/* ── logo (st.image) — incorniciato come medaglione luminoso ── */
[data-testid="stImage"] img {
    border-radius: 24px;
    border: 1px solid #c9a84c44;
    box-shadow: 0 10px 50px rgba(201,168,76,0.28), 0 0 0 6px rgba(13,13,26,0.6);
    margin-top: 1.5rem;
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

/* ── INTERPRETAZIONE DEL SOGNO (prima dei numeri) ── */
@keyframes interpret-entra {
    0%   { opacity: 0; transform: translateY(18px); }
    100% { opacity: 1; transform: translateY(0); }
}
.interpret-wrap {
    background: radial-gradient(circle at 50% 0%, #1a1838 0%, #0c0c1e 70%);
    border: 1px solid #c9a84c33;
    border-radius: 20px;
    padding: 2.2rem 2rem 2rem;
    margin: 1rem 0 1.5rem;
    box-shadow: 0 10px 50px rgba(0,0,0,0.5), inset 0 0 60px rgba(201,168,76,0.04);
    animation: interpret-entra 0.7s ease both;
    position: relative;
    overflow: hidden;
}
.interpret-wrap::before {
    content: "☽";
    position: absolute;
    top: -10px; right: 14px;
    font-size: 6rem;
    color: #c9a84c0d;
    pointer-events: none;
}
.interpret-kicker {
    font-family: 'Cinzel', serif;
    font-size: 0.8rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #c9a84c;
    opacity: 0.75;
    text-align: center;
    margin-bottom: 0.6rem;
}
.interpret-apertura {
    font-family: 'Cinzel', serif;
    font-size: clamp(1.3rem, 3.4vw, 1.8rem);
    color: #e8d5b7;
    text-align: center;
    line-height: 1.45;
    margin: 0 auto 1.6rem;
    max-width: 560px;
    text-shadow: 0 0 30px rgba(201,168,76,0.18);
}
.interpret-simbolo {
    font-family: 'Crimson Text', serif;
    font-size: 1.18rem;
    line-height: 1.85;
    color: #d8c6a6;
    padding: 0.9rem 0 0.9rem 1.3rem;
    border-left: 3px solid #c9a84c55;
    margin: 0.5rem 0;
    animation: interpret-entra 0.7s ease both;
}
.interpret-simbolo b {
    color: #c9a84c;
    font-family: 'Cinzel', serif;
    font-weight: 600;
}
.interpret-sintesi {
    font-family: 'Crimson Text', serif;
    font-size: 1.22rem;
    line-height: 1.9;
    color: #e8d5b7;
    font-style: italic;
    text-align: center;
    margin: 1.8rem auto 0.5rem;
    max-width: 580px;
    padding-top: 1.4rem;
    border-top: 1px solid #c9a84c22;
}
.interpret-ponte {
    font-family: 'Cinzel', serif;
    font-size: 1.05rem;
    letter-spacing: 0.04em;
    color: #c9a84c;
    text-align: center;
    margin: 1.6rem auto 0;
    opacity: 0.9;
}
.reveal-arrow {
    text-align: center;
    font-size: 2rem;
    color: #c9a84c;
    margin: 0.8rem 0 0.4rem;
    animation: reveal-bob 1.8s ease-in-out infinite;
}
@keyframes reveal-bob {
    0%, 100% { transform: translateY(0); opacity: 0.6; }
    50%      { transform: translateY(8px); opacity: 1; }
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

st.markdown("""
<style>
/* ═════════════════════════════════════════════════════════════════════════════
   Product polish layer — portale web premium, mobile-first
   ═════════════════════════════════════════════════════════════════════════════ */

html, body, [data-testid="stApp"] {
    background:
        linear-gradient(180deg, #10122a 0%, #171023 42%, #21131a 100%) !important;
    color: #fff3dc !important;
    font-family: "Crimson Text", Georgia, serif !important;
}

[data-testid="stAppViewContainer"] > .main {
    max-width: 1040px !important;
}

[data-testid="stAppViewContainer"] .block-container {
    max-width: 980px !important;
    padding-top: 1rem !important;
    padding-bottom: 2.5rem !important;
}

.element-container:has(style),
.element-container:has(.btn-torna-su) {
    margin-bottom: 0 !important;
}

.app-header {
    position: relative;
    padding: 1.35rem 1.2rem 1.55rem !important;
    margin: 0 0 2rem !important;
    border: 1px solid rgba(231, 190, 92, 0.22) !important;
    border-radius: 22px;
    background:
        linear-gradient(135deg, rgba(255, 244, 214, 0.08), rgba(111, 206, 198, 0.06)),
        repeating-linear-gradient(90deg, rgba(255,255,255,0.025) 0 1px, transparent 1px 34px),
        #111328;
    box-shadow: 0 24px 80px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.08);
    overflow: hidden;
}

.app-header > div:first-child {
    display: none !important;
}

.app-header::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, transparent 0%, rgba(235, 197, 98, 0.18) 50%, transparent 100%);
    transform: translateX(-100%);
    animation: scan-luce 8s ease-in-out infinite;
    pointer-events: none;
}

.app-header::after {
    display: none;
}

@keyframes scan-luce {
    0%, 20% { transform: translateX(-100%); opacity: 0; }
    35%, 70% { opacity: 1; }
    100% { transform: translateX(100%); opacity: 0; }
}

.app-title {
    font-size: clamp(2.15rem, 6vw, 3.35rem) !important;
    letter-spacing: 0.045em !important;
    color: #f1c85b !important;
    white-space: nowrap;
}

.app-tagline {
    color: #93ddd2 !important;
    font-size: clamp(1.1rem, 3.8vw, 1.45rem) !important;
    font-style: normal !important;
}

.app-welcome {
    color: #f8e7c7 !important;
    font-size: clamp(1.02rem, 3.3vw, 1.18rem) !important;
    max-width: 720px !important;
    line-height: 1.5 !important;
}

.trust-strip {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.55rem;
    margin-top: 0.8rem;
}

.trust-pill {
    border: 1px solid rgba(147, 221, 210, 0.35);
    color: #c8fff7;
    background: rgba(14, 31, 43, 0.64);
    border-radius: 999px;
    padding: 0.35rem 0.7rem;
    font-size: 0.85rem;
    line-height: 1.2;
}

.dream-console {
    border: 1px solid rgba(241, 200, 91, 0.24);
    background:
        linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015)),
        rgba(9, 12, 29, 0.74);
    border-radius: 18px;
    padding: 1.1rem;
    box-shadow: 0 18px 60px rgba(0,0,0,0.26);
    margin-bottom: 1rem;
}

.micro-title {
    color: #f1c85b;
    font-family: "Cinzel", serif;
    font-weight: 700;
    letter-spacing: 0.04em;
    font-size: 1rem;
    margin-bottom: 0.25rem;
}

.micro-copy {
    color: #ddc9a6;
    font-size: 0.98rem;
    line-height: 1.55;
    margin-bottom: 0.8rem;
}

.step-label {
    color: #f1c85b !important;
    letter-spacing: 0.04em !important;
}

.step-num {
    background: linear-gradient(135deg, #f1c85b, #93ddd2) !important;
}

.step-instruction {
    color: #d9c5a0 !important;
    font-style: normal !important;
}

textarea {
    background: rgba(7, 10, 28, 0.92) !important;
    color: #fff4dc !important;
    border: 2px solid rgba(241, 200, 91, 0.38) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06) !important;
}

textarea:focus {
    border-color: #93ddd2 !important;
    box-shadow: 0 0 0 4px rgba(147, 221, 210, 0.14), 0 18px 50px rgba(0,0,0,0.22) !important;
}

[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #f1c85b, #93ddd2) !important;
    color: #111328 !important;
    letter-spacing: 0.06em !important;
    border-radius: 16px !important;
    box-shadow: 0 14px 44px rgba(147, 221, 210, 0.22), 0 10px 38px rgba(241, 200, 91, 0.28) !important;
}

[data-testid="stButton"] > button[kind="primary"] p {
    color: #111328 !important;
    font-weight: 800 !important;
}

[data-testid="stButton"] > button:not([kind="primary"]),
[data-testid="stDownloadButton"] > button {
    background: rgba(14, 21, 44, 0.82) !important;
    border-color: rgba(147, 221, 210, 0.34) !important;
    color: #c8fff7 !important;
}

[data-testid="stButton"] > button:not([kind="primary"]) p,
[data-testid="stDownloadButton"] > button p {
    color: #c8fff7 !important;
}

.quick-prompts {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.55rem;
    margin: 0.7rem 0 1rem;
}

.quick-label {
    color: #93ddd2;
    font-size: 0.92rem;
    margin-bottom: -0.2rem;
}

.sogni-overlay {
    background:
        linear-gradient(180deg, rgba(7, 8, 22, 0.98), rgba(22, 14, 28, 0.98)) !important;
}

.loading-titolo {
    color: #f1c85b !important;
    max-width: 780px;
}

.loading-sub {
    color: #c8fff7 !important;
    font-size: 1.12rem !important;
    max-width: 720px;
    text-align: center;
}

.dream-reader {
    width: min(760px, 88vw);
    z-index: 2;
    margin-top: 1.6rem;
    border: 1px solid rgba(147, 221, 210, 0.24);
    border-radius: 18px;
    overflow: hidden;
    background: rgba(255,255,255,0.045);
    box-shadow: 0 20px 70px rgba(0,0,0,0.38);
}

.dream-reader-head {
    color: #ddc9a6;
    font-size: 0.86rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.65rem 0.9rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.dream-stream {
    overflow: hidden;
    white-space: nowrap;
    padding: 0.95rem 0;
}

.stream-track {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    min-width: 200%;
    animation: parole-scorrono 13s linear infinite;
}

.stream-word {
    display: inline-flex;
    align-items: center;
    min-height: 42px;
    border: 1px solid rgba(241, 200, 91, 0.28);
    border-radius: 999px;
    padding: 0.35rem 0.75rem;
    color: #fff4dc;
    background: rgba(13, 18, 42, 0.82);
    font-size: clamp(1rem, 3.5vw, 1.25rem);
}

@keyframes parole-scorrono {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
}

.result-spotlight {
    text-align: center;
    border: 1px solid rgba(241, 200, 91, 0.26);
    border-radius: 20px;
    padding: 1.25rem 1rem;
    background:
        linear-gradient(145deg, rgba(241, 200, 91, 0.09), rgba(147, 221, 210, 0.055)),
        rgba(10, 13, 31, 0.8);
    box-shadow: 0 24px 70px rgba(0,0,0,0.28);
    margin: 1rem 0 1.4rem;
}

.result-kicker {
    color: #93ddd2;
    text-transform: uppercase;
    font-family: "Cinzel", serif;
    font-size: 0.9rem;
    letter-spacing: 0.08em;
}

.num-grande-card,
.num-gioco-card,
.simbolo-riga {
    background: rgba(10, 14, 34, 0.88) !important;
    border-color: rgba(241, 200, 91, 0.28) !important;
    box-shadow: 0 18px 44px rgba(0,0,0,0.23), inset 0 1px 0 rgba(255,255,255,0.06) !important;
}

.number-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(128px, 1fr));
    gap: 0.75rem;
    align-items: stretch;
    margin: 0.9rem 0 1.2rem;
}

.number-grid.compact {
    grid-template-columns: repeat(auto-fit, minmax(96px, 1fr));
    gap: 0.55rem;
}

.number-grid .num-grande-card,
.number-grid .num-gioco-card {
    margin: 0 !important;
    min-width: 0;
    height: 100%;
}

.num-grande-cifra,
.num-gioco-cifra {
    color: #f1c85b !important;
}

.num-grande-da,
.num-gioco-pianeta,
.simbolo-fonte,
.gioco-nota {
    color: #bda986 !important;
}

.simbolo-numeri {
    color: #93ddd2 !important;
}

.share-panel {
    border: 1px solid rgba(147, 221, 210, 0.26);
    border-radius: 18px;
    background: rgba(9, 16, 34, 0.78);
    padding: 1rem;
    margin: 1.2rem 0;
}

.responsible-note {
    border: 1px solid rgba(241, 200, 91, 0.22);
    border-left: 5px solid #93ddd2;
    background: rgba(255,255,255,0.045);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    color: #e8d5b7;
    font-size: 0.9rem;
    line-height: 1.55;
    margin-top: 1rem;
}

@media (max-width: 760px) {
    [data-testid="stAppViewContainer"] > .main {
        padding: 1rem 0.85rem !important;
    }
    .app-header {
        border-radius: 16px;
        padding: 1.4rem 0.85rem 1.7rem !important;
    }
    .quick-prompts {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .btn-torna-su,
    .btn-torna-su-etichetta {
        display: none !important;
    }
    .num-grande-card {
        padding: 1rem 0.25rem 0.8rem !important;
    }
    .num-grande-cifra {
        font-size: 2.45rem !important;
    }
    .number-grid,
    .number-grid.compact {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
</style>
""", unsafe_allow_html=True)

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


def _dream_words_for_animation(dream: str, limit: int = 16) -> list[str]:
    """Estrae parole leggibili da mostrare nell'animazione di elaborazione."""
    seen: set[str] = set()
    words: list[str] = []
    for raw in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]{3,}", dream):
        norm = _dc.normalize(raw)
        if not norm or norm in _dc.STOPWORDS or norm in seen:
            continue
        seen.add(norm)
        words.append(raw.strip()[:26])
        if len(words) >= limit:
            break
    return words or ["sogno", "simboli", "numeri", "messaggio"]


def _word_stream_html(dream: str) -> str:
    words = _dream_words_for_animation(dream)
    chips = "".join(f'<span class="stream-word">{_html.escape(word)}</span>' for word in words)
    return chips + chips


def _format_interpret_frase(nome: str, frase: str) -> str:
    """Rende sicura la frase narrativa e mette in risalto il nome del simbolo «Nome»."""
    safe = _html.escape(frase)
    nome_safe = _html.escape(nome)
    # il builder racchiude il nome tra «virgolette»: lo trasformiamo in grassetto dorato
    return safe.replace(f"«{nome_safe}»", f"<b>{nome_safe}</b>")


# ══════════════════════════════════════════════════════════════════════════════
# LETTURA NARRATIVA DEL SOGNO (definita qui, non importata, così l'hot-reload
# di Streamlit Cloud la aggiorna sempre a ogni push senza bisogno di reboot)
# ══════════════════════════════════════════════════════════════════════════════

_APERTURE = [
    "Il tuo sogno non è muto: ha parlato, e la tradizione ha ascoltato.",
    "Ogni sogno è un messaggio cifrato. Ecco cosa sussurrano le sue immagini.",
    "Le immagini che hai visto nel sonno portano con sé un significato antico.",
    "C'è una voce dentro il tuo sogno. Proviamo a darle parole.",
    "Dietro le immagini del tuo sogno si nasconde una trama di significati.",
]
_CONNETTIVI = [
    "Al centro della scena appare {sim}.",
    "Il tuo sogno si accende attorno a {sim}.",
    "Tra le immagini emerge con forza {sim}.",
    "Un segno parla più forte degli altri: {sim}.",
    "La tradizione si ferma su {sim}.",
    "Ritorna, nel racconto, l'immagine di {sim}.",
]
_PONTI = [
    "Da queste immagini la tradizione fa nascere i numeri. Eccoli.",
    "Ogni simbolo porta con sé una cifra. È il momento di scoprirle.",
    "Ora le immagini si trasformano in numeri. Guarda cosa ne emerge.",
    "I simboli hanno parlato: adesso lasciamo che diventino numeri.",
    "Dalla lettura del sogno ai suoi numeri il passo è breve. Eccoli.",
]


def _seed_from_dream(dream: str) -> int:
    """Seme deterministico: lo stesso sogno produce sempre la stessa lettura."""
    return int(hashlib.sha256(dream.strip().lower().encode("utf-8")).hexdigest(), 16)


def _pick(options: list[str], seed: int, salt: int = 0) -> str:
    return options[(seed + salt) % len(options)]


def build_interpretation(dream: str, matches: list) -> dict:
    """Lettura narrativa del sogno a partire dai simboli riconosciuti.

    Non è una previsione: è una lettura simbolica e culturale delle fonti.
    """
    seed = _seed_from_dream(dream)

    if not matches:
        return {
            "apertura": "Il tuo racconto è ancora avvolto nel mistero.",
            "simboli": [],
            "sintesi": (
                "Non ho riconosciuto immagini abbastanza nitide in questo sogno. "
                "Prova a raccontarlo con qualche dettaglio in più: una persona, un animale, "
                "un luogo, un oggetto, un colore. Più immagini offri, più la lettura diventa ricca."
            ),
            "ponte": "",
            "n_simboli": 0,
        }

    # I simboli principali (i primi per rilevanza), deduplicati per nome
    principali = []
    visti: set[str] = set()
    for m in matches:
        chiave = _dc.normalize(m.entry.symbol)
        if chiave in visti:
            continue
        visti.add(chiave)
        principali.append(m)
        if len(principali) >= 4:
            break

    simboli_narrati: list[tuple[str, str]] = []
    for i, m in enumerate(principali):
        nome = m.entry.symbol.strip().capitalize()
        connettivo = _pick(_CONNETTIVI, seed, salt=i).format(sim=f"«{nome}»")
        dettaglio = (m.entry.detail or "").strip()
        if dettaglio:
            dettaglio = dettaglio[0].upper() + dettaglio[1:]
            if len(dettaglio) > 220:
                dettaglio = dettaglio[:220].rsplit(" ", 1)[0] + "…"
            frase = f"{connettivo} {dettaglio}"
        else:
            frase = (
                f"{connettivo} Un'immagine che la tradizione popolare custodisce da generazioni, "
                f"carica di un significato che attraversa il tempo."
            )
        if not frase.rstrip().endswith((".", "…", "!", "?")):
            frase += "."
        simboli_narrati.append((nome, frase))

    nomi = [n for n, _ in simboli_narrati]
    if len(nomi) == 1:
        elenco = nomi[0]
    elif len(nomi) == 2:
        elenco = f"{nomi[0]} e {nomi[1]}"
    else:
        elenco = ", ".join(nomi[:-1]) + f" e {nomi[-1]}"

    chiusure = [
        f"Messi insieme, {elenco.lower()} disegnano un sogno che invita a guardare dentro di sé "
        "con fiducia: la tradizione legge in queste immagini un segno di attesa e di possibilità.",
        f"Il filo che unisce {elenco.lower()} parla di un passaggio, di qualcosa che si muove nella "
        "tua vita e chiede attenzione. È un sogno che porta energia.",
        f"Tra {elenco.lower()} si intravede un messaggio di speranza: la tradizione invita a coltivare "
        "ciò che hai visto nel sonno, perché i segni non arrivano mai per caso.",
        f"Le immagini di {elenco.lower()} compongono un racconto interiore: un richiamo a fidarti del "
        "tuo istinto e a riconoscere i segnali che la vita ti manda.",
    ]
    sintesi = _pick(chiusure, seed, salt=7)

    return {
        "apertura": _pick(_APERTURE, seed),
        "simboli": simboli_narrati,
        "sintesi": sintesi,
        "ponte": _pick(_PONTI, seed, salt=3),
        "n_simboli": len(matches),
    }


def _format_share_text(dream: str, combo: tuple[int, ...], matches: list[_dc.Match]) -> str:
    numeri = " - ".join(f"{n:02d}" for n in combo)
    simboli = ", ".join(m.entry.symbol for m in matches[:5])
    return (
        "Ho raccontato questo sogno a Sogni e Numeri:\n"
        f"\"{dream}\"\n\n"
        f"Numeri simbolici: {numeri}\n"
        f"Simboli trovati: {simboli if simboli else 'nessuno'}\n\n"
        "Lettura culturale e ricreativa, non predittiva."
    )


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
    cards: list[str] = []
    for n in combo:
        pianeta, _, _ = _sp_info(n)
        cards.append(f"""
<div class="num-gioco-card">
  <div class="num-gioco-cifra">{n:02d}</div>
  <div class="num-gioco-pianeta">{_html.escape(pianeta) if pianeta else "&nbsp;"}</div>
</div>
""")
    st.markdown(f'<div class="number-grid compact">{"".join(cards)}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

# ── Logo: caricato dal file (st.image è affidabile su Streamlit Cloud,
#    a differenza del base64 inline che veniva scartato nel rendering HTML) ──
_logo_file = ROOT / "static" / "logo_sogni_numeri.png"
_lc1, _lc2, _lc3 = st.columns([1, 2, 1])
with _lc2:
    if _logo_file.exists():
        st.image(str(_logo_file), use_container_width=True)

st.markdown("""
<div class="app-header" style="padding-top:0.8rem; border-top:none;">
  <div class="app-tagline">Racconta il sogno. Guarda i simboli. Scopri i numeri.</div>
  <div class="app-welcome">
    Un'esperienza web ispirata alla Smorfia, alla tradizione popolare e ai testi simbolici antichi.
    Scrivi anche poche parole: persone, luoghi, animali, oggetti o sensazioni.
    Il resto lo fa il motore di lettura.
  </div>
  <div class="trust-strip">
    <span class="trust-pill">Nessuna registrazione</span>
    <span class="trust-pill">Funziona da telefono</span>
    <span class="trust-pill">Lettura immediata</span>
    <span class="trust-pill">Tradizione e simboli</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PASSO 1 — SCRIVI IL TUO SOGNO
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="step-label">
  <span class="step-num">1</span>
  &nbsp;Racconta il sogno
</div>
<div class="dream-console">
  <div class="micro-title">Bastano poche parole</div>
  <div class="micro-copy">
    Scrivi quello che ricordi: una persona, un luogo, un animale, un colore, una sensazione.
    Il motore riconosce i simboli e costruisce la lettura.
  </div>
</div>
""", unsafe_allow_html=True)

if "dream_text" not in st.session_state:
    st.session_state.dream_text = ""

st.markdown('<div class="quick-label">Non sai da dove partire? Prova un esempio:</div>', unsafe_allow_html=True)
example_cols = st.columns(4)
_EXAMPLES = [
    ("Acqua", "Ho sognato acqua chiara, una casa vecchia e mia madre che mi chiamava."),
    ("Padre", "Ho sognato mio padre sorridente davanti a una porta illuminata."),
    ("Cane", "Ho sognato un cane bianco che correva in una strada lunga."),
    ("Mare", "Ho sognato il mare di notte, una barca e tante monete."),
]
for col, (label, text) in zip(example_cols, _EXAMPLES):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state.dream_text = text

dream_input = st.text_area(
    label="Il tuo sogno",
    label_visibility="collapsed",
    placeholder="Per esempio: ho sognato un cavallo bianco che correva sul mare, c'era anche mia madre…",
    height=180,
    key="dream_text",
)


# ══════════════════════════════════════════════════════════════════════════════
# PASSO 2 — PREMI IL BOTTONE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="step-label">
  <span class="step-num">2</span>
  &nbsp;Avvia la lettura
</div>
""", unsafe_allow_html=True)

analyze = st.button("GENERA LA LETTURA DEL SOGNO", type="primary", use_container_width=True)

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
    _stream_html = _word_stream_html(dream)
    _loading = st.empty()
    _loading.markdown(f"""
<div class="sogni-overlay">
  <div class="pioggia">{_pioggia_html}</div>
  <div class="loading-titolo">Sto leggendo il tuo sogno<span class="puntini"></span></div>
  <div class="loading-sub">Le parole diventano simboli, i simboli diventano numeri.</div>
  <div class="dream-reader">
    <div class="dream-reader-head">Parole individuate nel sogno</div>
    <div class="dream-stream"><div class="stream-track">{_stream_html}</div></div>
  </div>
  <div class="loading-ruota"></div>
</div>
""", unsafe_allow_html=True)
    time.sleep(1.1)

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
  &nbsp;La tua lettura è pronta
</div>
""", unsafe_allow_html=True)

    if not matches:
        st.warning(
            "Non ho trovato simboli corrispondenti al tuo sogno. "
            "Prova a scrivere con più parole: nomi di persone, animali, oggetti, luoghi, colori."
        )
        st.stop()

    # ────────────────────────────────────────────────────────────────────────
    # SEZIONE 0 — L'INTERPRETAZIONE DEL SOGNO (prima dei numeri)
    # ────────────────────────────────────────────────────────────────────────

    interpretazione = build_interpretation(dream, matches)

    _simboli_html = "".join(
        f'<div class="interpret-simbolo" style="animation-delay:{0.15 * (i + 1):.2f}s;">'
        f'{_format_interpret_frase(nome, frase)}'
        f'</div>'
        for i, (nome, frase) in enumerate(interpretazione["simboli"])
    )

    st.markdown(f"""
<div class="interpret-wrap">
  <div class="interpret-kicker">La lettura del tuo sogno</div>
  <div class="interpret-apertura">{_html.escape(interpretazione["apertura"])}</div>
  {_simboli_html}
  <div class="interpret-sintesi">{_html.escape(interpretazione["sintesi"])}</div>
  <div class="interpret-ponte">{_html.escape(interpretazione["ponte"])}</div>
</div>
<div class="reveal-arrow">⌄</div>
""", unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # SEZIONE A — I TUOI NUMERI DI OGGI (top 10 per score)
    # ────────────────────────────────────────────────────────────────────────

    st.markdown("""
<div class="result-spotlight">
  <div class="result-kicker">E adesso… i numeri</div>
  <div class="numeri-header">I numeri del tuo sogno</div>
<div class="numeri-sottotitolo">
  I numeri più forti emersi dai simboli che hai scritto
</div>
</div>
""", unsafe_allow_html=True)

    top_scores = scores.most_common(10)
    if top_scores:
        # prima riga: primi 5 numeri in grande
        primo_blocco = top_scores[:5]
        cards = []
        for numero, _score in primo_blocco:
            simboli_origine = ", ".join(num_to_simboli[numero][:2]) if num_to_simboli[numero] else "—"
            cards.append(f"""
<div class="num-grande-card">
  <div class="num-grande-cifra">{numero:02d}</div>
  <div class="num-grande-da">{_html.escape(simboli_origine)}</div>
</div>
""")
        st.markdown(f'<div class="number-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

        # seconda riga: numeri 6-10 (leggermente più piccoli)
        if len(top_scores) > 5:
            secondo_blocco = top_scores[5:]
            st.markdown(
                '<div style="font-size:0.9rem; color:#5a4a35; text-align:center; margin-top:0.8rem; font-style:italic;">'
                'Altri numeri suggeriti dal sogno:'
                '</div>',
                unsafe_allow_html=True,
            )
            cards2 = []
            for numero, _score in secondo_blocco:
                simboli_origine = ", ".join(num_to_simboli[numero][:2]) if num_to_simboli[numero] else "—"
                cards2.append(f"""
<div class="num-grande-card" style="padding:1rem 0.3rem 0.8rem;">
  <div class="num-grande-cifra" style="font-size:2.6rem;">{numero:02d}</div>
  <div class="num-grande-da">{_html.escape(simboli_origine)}</div>
</div>
""")
            st.markdown(f'<div class="number-grid compact">{"".join(cards2)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sep">· · ·</div>', unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # SEZIONE B — COMBINAZIONI PER GIOCO
    # ────────────────────────────────────────────────────────────────────────

    st.markdown("""
<div class="numeri-header" style="font-size:1.3rem;">Sequenze simboliche del sogno</div>
<div class="numeri-sottotitolo">
  Tre sequenze pronte, generate dai simboli più rilevanti
</div>
""", unsafe_allow_html=True)

    _render_combo_gioco("5 numeri tradizionali — 1-90", lotto)
    _render_combo_gioco("5 numeri compatti — 1-55", millionday)
    _render_combo_gioco("6 numeri tradizionali — 1-90", superenalotto)

    st.markdown("""
<div class="responsible-note">
  Lettura culturale e ricreativa: i numeri non sono una previsione e non garantiscono alcun risultato.
  Usali come curiosità legata alla tradizione, sempre con equilibrio.
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="sep">✦ &nbsp; ✦ &nbsp; ✦</div>', unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # SEZIONE C — I SIMBOLI DEL TUO SOGNO
    # ────────────────────────────────────────────────────────────────────────

    st.markdown("""
<div class="simboli-header">I simboli riconosciuti</div>
<div style="color:#9e8a6a; font-size:1.05rem; margin-bottom:1.5rem; font-style:italic; line-height:1.7;">
  Qui vedi da quali immagini del sogno nasce la lettura. Ogni simbolo porta con sé
  una o più corrispondenze numeriche nella tradizione.
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
    {_html.escape(match.entry.detail) if match.entry.detail else
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

    share_text = _format_share_text(dream, lotto, matches)
    st.markdown("""
<div class="share-panel">
  <div class="micro-title">Vuoi condividerlo?</div>
  <div class="micro-copy">
    Qui sotto trovi un testo già pronto da copiare e mandare su WhatsApp o salvare nelle note.
  </div>
</div>
""", unsafe_allow_html=True)
    st.text_area(
        "Testo pronto da copiare",
        value=share_text,
        height=160,
        label_visibility="collapsed",
        key=f"share_{timestamp_fn}",
    )

    col_dl, col_kofi = st.columns(2)
    with col_dl:
        st.download_button(
            label="Salva l'analisi",
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
