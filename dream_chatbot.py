#!/usr/bin/env python3
"""Chatbot CLI sogno -> simboli -> numeri.

Usa il primo indice estratto dalla Smorfia napoletana e produce combinazioni
motivate. Non e una previsione certa: e una lettura simbolica delle fonti.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

try:
    import yaml
    _YAML_OK = True
except ImportError:
    _YAML_OK = False

try:
    import cabala_layer as _cabala
    _CABALA_OK = True
except ImportError:
    _CABALA_OK = False


ROOT = Path(__file__).resolve().parent
VAULT = ROOT / "Obsidian Vault SMORFIA"


def _find_index(filename: str) -> Path:
    """Cerca il CSV prima in data/ (cloud/produzione), poi nel vault Obsidian (locale)."""
    cloud_path = ROOT / "data" / filename
    vault_path = VAULT / "06_Output" / filename
    return cloud_path if cloud_path.exists() else vault_path


INDEXES = (
    _find_index("smorfia_symbol_index_v0.csv"),
    _find_index("capacelli_symbol_index_v0.csv"),
)
REPORT_DIR = VAULT / "06_Output" / "Sogni analizzati"
SYNONYMS_PATH = ROOT / "synonyms.yml"

STOPWORDS = {
    "a",
    "ad",
    "al",
    "alla",
    "alle",
    "allo",
    "anche",
    "che",
    "chi",
    "ci",
    "col",
    "con",
    "da",
    "dal",
    "dalla",
    "delle",
    "di",
    "e",
    "era",
    "ero",
    "gli",
    "ha",
    "ho",
    "i",
    "il",
    "in",
    "io",
    "la",
    "le",
    "lo",
    "ma",
    "mi",
    "mia",
    "mio",
    "nel",
    "nella",
    "non",
    "o",
    "per",
    "poi",
    "si",
    "sono",
    "su",
    "tra",
    "un",
    "una",
    "uno",
    "vedere",
    "vedevo",
    "visto",
    "sognato",
    "sognavo",
    "sogno",
}

def _carica_sinonimi() -> dict[str, set[str]]:
    """Carica il dizionario sinonimi da synonyms.yml se disponibile.

    Fallback: dizionario base hardcoded per compatibilità.
    """
    if _YAML_OK and SYNONYMS_PATH.exists():
        with SYNONYMS_PATH.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        aliases: dict[str, set[str]] = {}
        for canonical, variants in raw.items():
            if isinstance(variants, list):
                aliases[str(canonical)] = {str(v) for v in variants}
        return aliases

    return {
        "acqua": {"mare", "pioggia", "fiume", "lago", "rubinetto", "bagnato", "bagnarsi"},
        "abitazione": {"casa", "appartamento", "stanza", "palazzo", "edificio"},
        "abbracciare": {"abbraccio", "abbracciavo", "abbracciato"},
        "accendere": {"luce", "fuoco", "candela", "camino", "sigaretta"},
        "amico": {"amica", "amici", "compagno", "conoscente"},
        "bambino": {"bimba", "bimbo", "figlio", "figlia", "neonato"},
        "cane": {"cani", "cucciolo", "cagnolino", "abbaiare"},
        "denaro": {"soldi", "monete", "banconote", "ricchezza"},
        "donna": {"ragazza", "moglie", "femmina", "signora"},
        "fuoco": {"fiamma", "incendio", "bruciare", "bruciava"},
        "padre": {"papa", "papà", "babbo"},
        "madre": {"mamma", "mammà"},
        "morte": {"morto", "morta", "defunto", "cadavere", "funerale"},
        "nemico": {"rivale", "avversario"},
        "strada": {"via", "cammino", "sentiero", "viaggio"},
    }


ALIASES = _carica_sinonimi()


@dataclass(frozen=True)
class SymbolEntry:
    symbol: str
    detail: str
    numbers: tuple[int, ...]
    page: str
    source: str
    symbol_norm: str
    searchable: str


@dataclass(frozen=True)
class Match:
    entry: SymbolEntry
    score: float
    reason: str


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    ascii_text = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    ascii_text = re.sub(r"[^a-z0-9 ]+", " ", ascii_text)
    return re.sub(r"\s+", " ", ascii_text).strip()


def tokens(text: str) -> set[str]:
    return {token for token in normalize(text).split() if token not in STOPWORDS and len(token) > 2}


def expanded_tokens(text: str) -> set[str]:
    result = set(tokens(text))
    for canonical, variants in ALIASES.items():
        norm_canonical = normalize(canonical)
        norm_variants = {normalize(item) for item in variants}
        if norm_canonical in result or result.intersection(norm_variants):
            result.add(norm_canonical)
            result.update(norm_variants)
    return result


def source_weight(source: str) -> float:
    if "Capacelli" in source:
        return 0.82
    return 1.0


def source_short(source: str) -> str:
    if "Capacelli" in source:
        return "Capacelli 1881"
    if "Smorfia" in source:
        return "Smorfia"
    return source


def load_indexes(paths: tuple[Path, ...] = INDEXES) -> list[SymbolEntry]:
    missing = [path for path in paths if not path.exists()]
    if missing:
        missing_list = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(
            "Indici non trovati:\n"
            f"{missing_list}\n"
            "Esegui tools/build_symbol_index.py e tools/build_capacelli_index.py."
        )

    entries: list[SymbolEntry] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                numbers = tuple(int(item) for item in row["numbers"].split() if item.isdigit())
                symbol = row["symbol"].strip()
                detail = row["detail"].strip()
                symbol_norm = normalize(symbol)
                searchable = normalize(f"{symbol} {detail}")
                entries.append(
                    SymbolEntry(
                        symbol=symbol,
                        detail=detail,
                        numbers=numbers,
                        page=row["page"],
                        source=row["source"],
                        symbol_norm=symbol_norm,
                        searchable=searchable,
                    )
                )
    return entries


def find_matches(dream: str, entries: list[SymbolEntry], limit: int) -> list[Match]:
    dream_norm = normalize(dream)
    base_tokens = tokens(dream)
    dream_tokens = expanded_tokens(dream)
    matches: list[Match] = []

    for entry in entries:
        symbol_tokens = set(entry.symbol_norm.split())
        detail_tokens = tokens(entry.detail)
        score = 0.0
        reasons: list[str] = []

        if entry.symbol_norm and re.search(rf"\b{re.escape(entry.symbol_norm)}\b", dream_norm):
            score += 9.0
            reasons.append("simbolo esatto")

        symbol_overlap = dream_tokens.intersection(symbol_tokens)
        if symbol_overlap:
            score += 5.0 + len(symbol_overlap)
            reasons.append("parole nel simbolo: " + ", ".join(sorted(symbol_overlap)))

        detail_overlap = base_tokens.intersection(detail_tokens)
        if detail_overlap:
            score += min(4.0, len(detail_overlap) * 0.8)
            reasons.append("dettaglio affine: " + ", ".join(sorted(detail_overlap)[:4]))

        if not symbol_overlap and not detail_overlap and entry.symbol_norm:
            best_ratio = max(
                (SequenceMatcher(None, token, entry.symbol_norm).ratio() for token in dream_tokens),
                default=0.0,
            )
            if best_ratio >= 0.82:
                score += 3.0 * best_ratio
                reasons.append("somiglianza lessicale")

        if score > 0:
            score *= source_weight(entry.source)
            matches.append(Match(entry=entry, score=score, reason="; ".join(reasons)))

    matches.sort(key=lambda item: (item.score, max(item.entry.numbers, default=0)), reverse=True)
    return dedupe_matches(matches, limit)


def dedupe_matches(matches: list[Match], limit: int) -> list[Match]:
    seen = set()
    per_symbol: Counter[tuple[str, str]] = Counter()
    deduped = []

    def can_add(match: Match) -> bool:
        key = (match.entry.source, match.entry.symbol, match.entry.detail, match.entry.numbers)
        if key in seen:
            return False
        max_for_symbol = 3 if match.score >= 9 else 2
        symbol_key = (match.entry.source, match.entry.symbol)
        if per_symbol[symbol_key] >= max_for_symbol:
            return False
        return True

    def add(match: Match) -> bool:
        if not can_add(match):
            return False
        key = (match.entry.source, match.entry.symbol, match.entry.detail, match.entry.numbers)
        symbol_key = (match.entry.source, match.entry.symbol)
        seen.add(key)
        per_symbol[symbol_key] += 1
        deduped.append(match)
        return True

    sources = []
    for match in matches:
        short = source_short(match.entry.source)
        if short not in sources:
            sources.append(short)

    if len(sources) > 1:
        min_per_source = 2 if limit >= 12 else 1
        for source in sources:
            added_for_source = 0
            for match in matches:
                if source_short(match.entry.source) != source:
                    continue
                if add(match):
                    added_for_source += 1
                if added_for_source >= min_per_source or len(deduped) >= limit:
                    break
            if len(deduped) >= limit:
                return sorted(deduped, key=lambda item: item.score, reverse=True)

    for match in matches:
        add(match)
        if len(deduped) >= limit:
            break
    return sorted(deduped, key=lambda item: item.score, reverse=True)


def score_numbers(matches: list[Match]) -> Counter[int]:
    scores: Counter[int] = Counter()
    for match in matches:
        for number in match.entry.numbers:
            scores[number] += match.score
    return scores


def deterministic_fill(dream: str, pool_size: int) -> list[int]:
    digest = hashlib.sha256(dream.encode("utf-8")).digest()
    numbers = []
    cursor = 0
    while len(numbers) < pool_size:
        value = digest[cursor % len(digest)]
        candidate = value % pool_size + 1
        if candidate not in numbers:
            numbers.append(candidate)
        cursor += 1
        if cursor > 512:
            break
    return numbers


def build_combo(
    scores: Counter[int],
    dream: str,
    pick_count: int,
    pool_size: int,
) -> tuple[int, ...]:
    ranked = [number for number, _ in scores.most_common() if 1 <= number <= pool_size]
    selected = []

    for number in ranked:
        if number not in selected:
            selected.append(number)
        if len(selected) == pick_count:
            return tuple(sorted(selected))

    for number in deterministic_fill(dream, pool_size):
        if number not in selected:
            selected.append(number)
        if len(selected) == pick_count:
            return tuple(sorted(selected))

    return tuple(sorted(selected))


def format_combo(numbers: tuple[int, ...]) -> str:
    return " ".join(f"{number:02d}" for number in numbers)


def _ronchetti_nota(simbolo: str) -> str | None:
    """Restituisce la nota Ronchetti per un simbolo, se disponibile."""
    if not _CABALA_OK:
        return None
    from re import sub as _re_sub
    import unicodedata as _ud
    def _norm(t: str) -> str:
        d = _ud.normalize("NFD", t.lower())
        a = "".join(ch for ch in d if _ud.category(ch) != "Mn")
        return _re_sub(r"[^a-z0-9 ]+", " ", a).strip()
    return _cabala.RONCHETTI_SIMBOLI.get(_norm(simbolo))


def _sepharial_lettura_numero(numero: int) -> str:
    """Produce la lettura Sepharial compatta per un numero."""
    if not _CABALA_OK:
        return ""
    cifra = _cabala.radice_digitale(numero)
    sp = _cabala.SEPHARIAL_CIFRE.get(cifra)
    sig_key = numero if 1 <= numero <= 84 else (numero % 84 or 84)
    sig = _cabala.SEPHARIAL_SIGNIFICATI.get(sig_key, "")

    parts = []
    if sp:
        parts.append(f"cifra {cifra}→{sp.pianeta}")
        parts.append(sp.significato_minore)
    if sig:
        parts.append(f"Cap.XI: {sig}")
    return " | ".join(parts)


def _spiega_combo(combo: tuple[int, ...], scores: Counter) -> list[str]:
    """Per ogni numero della combinazione: origine simbolica + lettura Sepharial."""
    if not _CABALA_OK:
        return []

    # mappa numero → simboli che l'hanno generato
    from collections import defaultdict
    origine: dict[int, list[str]] = defaultdict(list)
    for match in _spiega_combo._last_matches:  # type: ignore[attr-defined]
        for n in match.entry.numbers:
            if n in combo:
                sym = match.entry.symbol
                if sym not in origine[n]:
                    origine[n].append(sym)

    righe = []
    for n in sorted(combo):
        simboli_src = ", ".join(origine[n][:3]) if origine[n] else "fill deterministico"
        sp_riga = _sepharial_lettura_numero(n)
        righe.append(f"  {n:02d}  ← {simboli_src}")
        if sp_riga:
            righe.append(f"      Sepharial: {sp_riga}")
    return righe


# slot condiviso per i match correnti (usato da _spiega_combo)
_spiega_combo._last_matches = []  # type: ignore[attr-defined]


def render_response(dream: str, matches: list[Match]) -> str:
    scores = score_numbers(matches)
    lotto = build_combo(scores, dream, 5, 90)
    millionday = build_combo(scores, dream, 5, 55)
    superenalotto = build_combo(scores, dream, 6, 90)
    source_counts = Counter(source_short(match.entry.source) for match in matches)

    # rendi i match disponibili a _spiega_combo
    _spiega_combo._last_matches = matches  # type: ignore[attr-defined]

    lines = [
        "SMORFIA DREAM CHATBOT",
        "",
        "Sogno:",
        dream,
        "",
        "Fonti consultate:",
        ", ".join(f"{source}: {count}" for source, count in source_counts.items())
        if source_counts
        else "nessuna corrispondenza",
    ]

    # ------------------------------------------------------------------ simboli
    lines.append("")
    lines.append("Simboli trovati:")

    if not matches:
        lines.extend(
            [
                "- Nessuna corrispondenza forte trovata nel dataset v0.",
                "- Prova a raccontare il sogno con piu dettagli concreti: oggetti, luoghi, persone, azioni, colori.",
            ]
        )
    else:
        for index, match in enumerate(matches[:24], start=1):
            nums = ", ".join(str(number) for number in match.entry.numbers)
            lines.append(
                f"{index:02d}. {match.entry.symbol} -> {nums} "
                f"({source_short(match.entry.source)}, score {match.score:.1f}, pag. {match.entry.page})"
            )
            detail = match.entry.detail or "voce diretta"
            lines.append(f"    {detail}")
            lines.append(f"    motivo: {match.reason}")

            # Ronchetti: lettura iconologica del simbolo
            nota_r = _ronchetti_nota(match.entry.symbol)
            if nota_r:
                # Tronca a 180 caratteri per leggibilità
                nota_breve = nota_r[:180].rsplit(" ", 1)[0] + "…" if len(nota_r) > 180 else nota_r
                lines.append(f"    ☽ Ronchetti: {nota_breve}")

    # ------------------------------------------------------------------ confronto fonti
    comparison = build_source_comparison(matches)
    if comparison:
        lines.extend(["", "Confronto tra fonti:"])
        lines.extend(comparison)

    # ------------------------------------------------------------------ numeri forti con Sepharial
    lines.append("")
    lines.append("Numeri piu forti — lettura:")
    if scores:
        for numero, score in scores.most_common(12):
            sp_riga = _sepharial_lettura_numero(numero)
            base = f"  {numero:02d} (score {score:.1f})"
            if sp_riga:
                lines.append(f"{base} | {sp_riga}")
            else:
                lines.append(base)
    else:
        lines.append("  nessuno")

    # ------------------------------------------------------------------ combinazioni con lettura
    lines.append("")
    lines.append(f"Numeri 1-90 (5 numeri): {format_combo(lotto)}")
    righe_lotto = _spiega_combo(lotto, scores)
    if righe_lotto:
        lines.extend(righe_lotto)

    lines.append("")
    lines.append(f"Numeri 1-55 (5 numeri): {format_combo(millionday)}")
    righe_md = _spiega_combo(millionday, scores)
    if righe_md:
        lines.extend(righe_md)

    lines.append("")
    lines.append(f"Numeri 1-90 (6 numeri): {format_combo(superenalotto)}")
    righe_se = _spiega_combo(superenalotto, scores)
    if righe_se:
        lines.extend(righe_se)

    # ------------------------------------------------------------------ lettura esoterica profonda
    if _CABALA_OK and scores:
        numeri_top = [n for n, _ in scores.most_common(10)]
        simboli_unici = list({m.entry.symbol for m in matches[:12]})
        lettura = _cabala.leggi_sogno(dream, simboli_unici, numeri_top)
        lines.append(_cabala.formatta_lettura(lettura))
    else:
        lines.append("")

    lines.append(
        "Nota: questa e una lettura simbolica e culturale basata su tradizioni popolari. Non costituisce pubblicita di giochi, consulenza di gioco, ne previsione di estrazioni. Il gioco e vietato ai minori di 18 anni. Numero Verde: 800 274 274."
    )
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# LETTURA NARRATIVA DEL SOGNO (interpretazione che precede i numeri)
# ──────────────────────────────────────────────────────────────────────────────

# Aperture evocative — scelte in modo deterministico dal testo del sogno
_APERTURE = [
    "Il tuo sogno non è muto: ha parlato, e la tradizione ha ascoltato.",
    "Ogni sogno è un messaggio cifrato. Ecco cosa sussurrano le sue immagini.",
    "Le immagini che hai visto nel sonno portano con sé un significato antico.",
    "C'è una voce dentro il tuo sogno. Proviamo a darle parole.",
    "Dietro le immagini del tuo sogno si nasconde una trama di significati.",
]

# Connettivi narrativi per introdurre ogni simbolo
_CONNETTIVI = [
    "Al centro della scena appare {sim}.",
    "Il tuo sogno si accende attorno a {sim}.",
    "Tra le immagini emerge con forza {sim}.",
    "Un segno parla più forte degli altri: {sim}.",
    "La tradizione si ferma su {sim}.",
    "Ritorna, nel racconto, l'immagine di {sim}.",
]

# Frasi di chiusura/ponte verso i numeri
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


def build_interpretation(dream: str, matches: list[Match]) -> dict:
    """Costruisce una lettura narrativa del sogno a partire dai simboli riconosciuti.

    Ritorna un dizionario pronto per essere reso a schermo:
        {
          "apertura": str,                       # frase d'apertura evocativa
          "simboli":  [(nome, frase), ...],      # i simboli principali, narrati
          "sintesi":  str,                       # messaggio complessivo del sogno
          "ponte":    str,                       # frase di passaggio verso i numeri
          "n_simboli": int,                      # quanti simboli totali riconosciuti
        }
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
    principali: list[Match] = []
    visti: set[str] = set()
    for m in matches:
        chiave = normalize(m.entry.symbol)
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
            # Ripulisci e accorcia il dettaglio della fonte
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

    # Sintesi: intreccia i nomi dei simboli principali in un messaggio unico
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


def save_markdown(dream: str, response: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORT_DIR / f"sogno_{timestamp}.md"
    content = (
        "---\n"
        "tags:\n"
        "  - sogni\n"
        "  - simboli\n"
        "  - lettura-simbolica\n"
        "  - output\n"
        "---\n\n"
        "# Sogno analizzato\n\n"
        f"Creato: {datetime.now().isoformat(timespec='seconds')}\n\n"
        "Collegamenti: [[Home]] · [[03_Note/Indice simboli smorfia v0]] · [[05_Progetti/Chatbot sogni e numeri]]\n\n"
        "```text\n"
        f"{response}\n"
        "```\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analizza un sogno e propone numeri secondo il dataset Smorfia v0."
    )
    parser.add_argument("sogno", nargs="*", help="Testo del sogno da analizzare.")
    parser.add_argument("--limit", type=int, default=24, help="Numero massimo di corrispondenze. Default: 24.")
    parser.add_argument("--no-save", action="store_true", help="Non salvare il responso nel vault Obsidian.")
    return parser


def build_source_comparison(matches: list[Match]) -> list[str]:
    by_symbol: dict[str, dict[str, set[int]]] = defaultdict(lambda: defaultdict(set))
    for match in matches:
        symbol = match.entry.symbol.lower()
        for number in match.entry.numbers:
            by_symbol[symbol][source_short(match.entry.source)].add(number)

    lines = []
    for symbol, sources in sorted(by_symbol.items()):
        if len(sources) < 2:
            continue
        readable = symbol[:1].upper() + symbol[1:]
        parts = []
        for source, numbers in sorted(sources.items()):
            parts.append(f"{source}: {', '.join(str(num) for num in sorted(numbers))}")
        shared = set.intersection(*sources.values()) if len(sources) > 1 else set()
        shared_text = f" | comuni: {', '.join(str(num) for num in sorted(shared))}" if shared else ""
        lines.append(f"- {readable}: {'; '.join(parts)}{shared_text}")
        if len(lines) >= 8:
            break
    return lines


def main() -> int:
    args = build_parser().parse_args()
    dream = " ".join(args.sogno).strip()
    if not dream:
        dream = input("Raccontami il sogno: ").strip()
    if not dream:
        print("Serve almeno una frase di sogno da analizzare.")
        return 2

    entries = load_indexes()
    matches = find_matches(dream, entries, max(args.limit, 1))
    response = render_response(dream, matches)
    print(response)

    if not args.no_save:
        path = save_markdown(dream, response)
        print()
        print(f"Salvato nel vault: {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
