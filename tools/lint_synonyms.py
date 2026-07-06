#!/usr/bin/env python3
"""Lint per synonyms.yml.

Controlli:
- chiavi top-level duplicate (bloccante)
- valori non-lista / liste vuote (bloccante)
- duplicati nella stessa lista (warning)
- collisioni cross-key (warning, opzionalmente bloccante)
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def find_duplicate_top_level_keys(path: Path) -> list[tuple[str, int, int]]:
    key_re = re.compile(r"^([^\s#][^:]*):\s*$")
    seen: dict[str, int] = {}
    dups: list[tuple[str, int, int]] = []

    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        m = key_re.match(raw)
        if not m:
            continue
        key = m.group(1).strip()
        first = seen.get(key)
        if first is None:
            seen[key] = line_no
        else:
            dups.append((key, first, line_no))
    return dups


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint synonyms.yml")
    parser.add_argument(
        "--file",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "synonyms.yml",
        help="Percorso del file synonyms.yml",
    )
    parser.add_argument(
        "--strict-collisions",
        action="store_true",
        help="Tratta le collisioni cross-key come errore bloccante.",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"[ERR] file non trovato: {args.file}")
        return 2

    duplicate_keys = find_duplicate_top_level_keys(args.file)
    if duplicate_keys:
        print("[ERR] Chiavi top-level duplicate:")
        for key, first, second in duplicate_keys:
            print(f"  - {key}: righe {first} e {second}")

    raw = yaml.safe_load(args.file.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        print("[ERR] Il file deve contenere una mappa top-level key -> lista.")
        return 2

    blocking_errors = len(duplicate_keys)
    warnings = 0

    owners: dict[str, set[str]] = defaultdict(set)

    for canonical, variants in raw.items():
        c = str(canonical).strip()
        if not isinstance(variants, list):
            print(f"[ERR] '{c}' non ha una lista di varianti.")
            blocking_errors += 1
            continue
        if not variants:
            print(f"[ERR] '{c}' ha una lista vuota.")
            blocking_errors += 1
            continue

        norm_variants = [normalize(str(v)) for v in variants if str(v).strip()]
        counts = Counter(norm_variants)
        intra_dups = [v for v, n in counts.items() if n > 1]
        if intra_dups:
            warnings += 1
            print(f"[WARN] Duplicati interni per '{c}': {', '.join(intra_dups)}")

        for v in set(norm_variants):
            owners[v].add(c)

    collisions = {v: sorted(list(keys)) for v, keys in owners.items() if len(keys) > 1}
    if collisions:
        print(f"[WARN] Collisioni cross-key: {len(collisions)}")
        for variant, keys in sorted(collisions.items(), key=lambda item: (-len(item[1]), item[0]))[:40]:
            print(f"  - {variant}: {', '.join(keys)}")
        warnings += 1
        if args.strict_collisions:
            blocking_errors += 1

    print(
        f"[SUMMARY] canonici={len(raw)} duplicate_keys={len(duplicate_keys)} "
        f"collisions={len(collisions)} warnings={warnings}"
    )
    return 1 if blocking_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

