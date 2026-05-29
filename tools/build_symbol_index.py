#!/usr/bin/env python3
"""Extract a first symbol-number index from the Smorfia raw note."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "Obsidian Vault SMORFIA"
RAW = VAULT / "02_Raw" / "Smorfia napoletana - La vera cabala del lotto RAW.md"
CSV_OUT = VAULT / "06_Output" / "smorfia_symbol_index_v0.csv"
NOTE_OUT = VAULT / "03_Note" / "Indice simboli smorfia v0.md"

ENTRY_RE = re.compile(r"^([A-ZÀ-Ü][A-ZÀ-Ü0-9' -]{2,}):\s*(.*)$")
PAGE_RE = re.compile(r"^## Pagina\s+(\d+)")


def numbers_from(text: str) -> list[int]:
    nums = []
    for match in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", text):
        value = int(match)
        if 1 <= value <= 90:
            nums.append(value)
    return nums


def normalize_space(text: str) -> str:
    return " ".join(text.replace("|", "/").split())


def parse_entries() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current_symbol = ""
    page = ""

    for raw_line in RAW.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        page_match = PAGE_RE.match(line)
        if page_match:
            page = page_match.group(1)
            continue
        if line.startswith("---") or line.startswith("#") or line.startswith("Fonte:"):
            continue

        entry_match = ENTRY_RE.match(line)
        if entry_match:
            current_symbol = normalize_space(entry_match.group(1).title())
            detail = normalize_space(entry_match.group(2))
        elif line.startswith("-") and current_symbol:
            detail = normalize_space(line.lstrip("- "))
        else:
            continue

        nums = numbers_from(detail)
        if not nums:
            continue
        rows.append(
            {
                "symbol": current_symbol,
                "detail": detail,
                "numbers": " ".join(str(num) for num in nums),
                "page": page,
                "source": "Smorfia napoletana - La vera cabala del lotto",
            }
        )

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

    samples = rows[:30]
    lines = [
        "# Indice simboli smorfia v0",
        "",
        "#smorfia #sogni #lotto #dataset",
        "",
        f"Righe estratte: {len(rows)}",
        "",
        f"CSV completo: [[06_Output/{CSV_OUT.name}]]",
        "",
        "Questo e un primo indice automatico. Va revisionato, ma e gia utile per un prototipo di chatbot sogno -> simboli -> numeri.",
        "",
        "| Simbolo | Dettaglio | Numeri | Pagina |",
        "|---|---|---:|---:|",
    ]
    for row in samples:
        lines.append(
            f"| {row['symbol']} | {row['detail'][:120]} | {row['numbers']} | {row['page']} |"
        )
    NOTE_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Extracted {len(rows)} rows to {CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
