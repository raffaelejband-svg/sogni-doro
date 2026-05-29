#!/usr/bin/env python3
"""Extract a first symbol-number index from Capacelli 1881.

Capacelli is OCR-heavy and often formatted as "voice + numbers" rather than
full dream interpretation. This parser intentionally creates a conservative v0
index that can be improved by manual review.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "Obsidian Vault SMORFIA"
RAW = VAULT / "02_Raw" / "1881 Capacelli - Il vero libro dei sogni RAW.md"
CSV_OUT = VAULT / "06_Output" / "capacelli_symbol_index_v0.csv"
NOTE_OUT = VAULT / "03_Note" / "Indice simboli Capacelli v0.md"

PAGE_RE = re.compile(r"^## Pagina\s+(\d+)")
NUM_RE = re.compile(r"(?<!\d)(\d{1,2})(?!\d)")
LETTER_RE = re.compile(r"[A-Za-zÀ-Üà-ü]")


SKIP_WORDS = {
    "indice",
    "generale",
    "pagina",
    "appendice",
    "combinazioni",
    "quantita",
    "numeri",
    "sumeri",
    "giuocau",
}


def clean_line(line: str) -> str:
    line = line.replace("—", "-")
    line = line.replace("«", "").replace("»", "")
    line = line.replace("_", " ")
    line = re.sub(r"\s+", " ", line)
    return line.strip(" ,.;:\t")


def numbers_from(text: str) -> list[int]:
    numbers = []
    for match in NUM_RE.findall(text):
        value = int(match)
        if 1 <= value <= 90:
            numbers.append(value)
    return numbers


def remove_numbers(text: str) -> str:
    text = NUM_RE.sub(" ", text)
    text = re.sub(r"\bv\.?\s+.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -,.")


def is_noise(text: str) -> bool:
    lowered = text.lower()
    if not text or not LETTER_RE.search(text):
        return True
    if any(word in lowered for word in SKIP_WORDS):
        return True
    if len(text) <= 1:
        return True
    if sum(ch.isalpha() for ch in text) < 2:
        return True
    return False


def titleish(text: str) -> str:
    fixed = []
    for word in text.split():
        if word == "-":
            continue
        fixed.append(word[:1].upper() + word[1:].lower())
    return " ".join(fixed)


def split_symbol_detail(text: str, current_symbol: str | None) -> tuple[str, str]:
    text = clean_line(text)
    if text.startswith("-"):
        detail = clean_line(text[1:])
        return current_symbol or detail, detail

    if " - " in text:
        symbol, detail = text.split(" - ", 1)
        return titleish(symbol), clean_line(detail)

    if current_symbol and text and text[0].islower():
        return current_symbol, text

    words = text.split()
    if len(words) > 1 and current_symbol:
        first = titleish(words[0])
        if first == current_symbol:
            return current_symbol, " ".join(words[1:])

    return titleish(text), ""


def parse_entries() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    page = ""
    current_symbol: str | None = None
    pending_text = ""
    in_index = False

    def emit(text: str, nums: list[int]) -> None:
        nonlocal current_symbol
        clean = remove_numbers(text)
        if is_noise(clean) or not nums:
            return
        symbol, detail = split_symbol_detail(clean, current_symbol)
        symbol = titleish(symbol)
        detail = clean_line(detail)
        if symbol == "Acqua Di Cedro":
            detail = detail or "di cedro"
            symbol = "Acqua"
        if not symbol or is_noise(symbol):
            return
        if not detail and len(symbol.split()) > 4:
            return
        current_symbol = symbol
        rows.append(
            {
                "symbol": symbol,
                "detail": detail,
                "numbers": " ".join(str(num) for num in nums),
                "page": page,
                "source": "1881 Capacelli - Il vero libro dei sogni",
            }
        )

    for raw_line in RAW.read_text(encoding="utf-8").splitlines():
        line = clean_line(raw_line)
        if not line:
            continue

        page_match = PAGE_RE.match(line)
        if page_match:
            page = page_match.group(1)
            if int(page) >= 45:
                in_index = True
            continue
        if not in_index:
            continue
        if line.startswith("---") or line.startswith("#") or line.startswith("Fonte:"):
            continue

        nums = numbers_from(line)
        text_without_nums = remove_numbers(line)

        if nums and text_without_nums:
            if pending_text and text_without_nums[:1].islower():
                candidate = f"{pending_text} - {text_without_nums}"
                pending_text = ""
            elif pending_text:
                candidate = f"{pending_text} {text_without_nums}"
                pending_text = ""
            else:
                candidate = text_without_nums
            emit(candidate, nums)
            continue

        if nums and pending_text:
            emit(pending_text, nums)
            pending_text = ""
            continue

        if not nums and LETTER_RE.search(line):
            if is_noise(line):
                pending_text = ""
                continue
            if pending_text and line[:1].islower():
                pending_text = f"{pending_text} {line}"
            else:
                pending_text = line

    return rows


def main() -> int:
    rows = parse_entries()
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("symbol", "detail", "numbers", "page", "source"),
        )
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Indice simboli Capacelli v0",
        "",
        "#capacelli #sogni #lotto #dataset",
        "",
        f"Righe estratte: {len(rows)}",
        "",
        f"CSV completo: [[06_Output/{CSV_OUT.name}]]",
        "",
        "Questo indice e storico e OCR-heavy: va considerato fonte secondaria, utile per confronto e conferma.",
        "",
        "| Simbolo | Dettaglio | Numeri | Pagina |",
        "|---|---|---:|---:|",
    ]
    for row in rows[:40]:
        detail = row["detail"] or "-"
        lines.append(f"| {row['symbol']} | {detail[:100]} | {row['numbers']} | {row['page']} |")
    NOTE_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Extracted {len(rows)} rows to {CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
