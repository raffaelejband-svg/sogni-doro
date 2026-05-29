#!/usr/bin/env python3
"""Motore statistico per generare combinazioni Lotto-like.

Il modulo non promette previsioni certe: le estrazioni sono eventi casuali.
Serve a creare combinazioni bilanciate usando frequenze, ritardi e vincoli
combinatori, con la possibilita di caricare uno storico CSV.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import re
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class GameConfig:
    key: str
    label: str
    pool_size: int
    pick_count: int
    output_name: str

    @property
    def numbers(self) -> range:
        return range(1, self.pool_size + 1)

    @property
    def exact_probability(self) -> int:
        return math.comb(self.pool_size, self.pick_count)


@dataclass(frozen=True)
class Candidate:
    numbers: tuple[int, ...]
    score: float
    reasons: tuple[str, ...]


GAMES: dict[str, GameConfig] = {
    "superenalotto": GameConfig(
        key="superenalotto",
        label="SuperEnalotto",
        pool_size=90,
        pick_count=6,
        output_name="sestina",
    ),
    "lotto": GameConfig(
        key="lotto",
        label="Lotto",
        pool_size=90,
        pick_count=5,
        output_name="cinquina",
    ),
    "millionday": GameConfig(
        key="millionday",
        label="MillionDAY",
        pool_size=55,
        pick_count=5,
        output_name="cinquina",
    ),
}


def parse_columns(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def load_history(
    path: Path | None,
    config: GameConfig,
    columns: list[str] | None = None,
) -> list[tuple[int, ...]]:
    if path is None:
        return []
    if not path.exists():
        raise FileNotFoundError(f"Storico non trovato: {path}")

    draws: list[tuple[int, ...]] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return draws
        selected_columns = columns or infer_number_columns(reader.fieldnames, config)

        for row in reader:
            values: list[int] = []
            for column in selected_columns:
                cell = row.get(column, "")
                values.extend(extract_numbers(cell, config.pool_size))

            unique_in_order = tuple(dict.fromkeys(values))
            if len(unique_in_order) >= config.pick_count:
                draws.append(tuple(sorted(unique_in_order[: config.pick_count])))

    return draws


def infer_number_columns(fieldnames: Iterable[str], config: GameConfig) -> list[str]:
    names = list(fieldnames)
    exact_patterns = {
        f"n{index}" for index in range(1, config.pick_count + 1)
    } | {f"num{index}" for index in range(1, config.pick_count + 1)}
    excluded_patterns = {
        "data",
        "date",
        "giorno",
        "mese",
        "anno",
        "concorso",
        "id",
        "ruota",
        "superstar",
        "jolly",
    }

    inferred = [
        name
        for name in names
        if normalized(name) in exact_patterns
        or normalized(name) in {str(index) for index in range(1, config.pick_count + 1)}
        or normalized(name).startswith("numero")
        or normalized(name).startswith("estratto")
    ]
    if inferred:
        return inferred[: config.pick_count]

    playable_like = [
        name
        for name in names
        if normalized(name) not in excluded_patterns
        and not normalized(name).endswith("date")
        and not normalized(name).endswith("data")
    ]
    return playable_like or names


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def extract_numbers(value: str, pool_size: int) -> list[int]:
    found = []
    for match in re.findall(r"\d+", str(value)):
        number = int(match)
        if 1 <= number <= pool_size:
            found.append(number)
    return found


def build_number_weights(
    draws: list[tuple[int, ...]],
    config: GameConfig,
    hot_weight: float,
    delay_weight: float,
    cold_weight: float,
) -> dict[int, float]:
    if not draws:
        return {number: 1.0 for number in config.numbers}

    frequency = Counter(number for draw in draws for number in draw)
    max_frequency = max(frequency.values(), default=1)
    total_draws = len(draws)
    last_seen = {number: None for number in config.numbers}

    for index, draw in enumerate(draws):
        for number in draw:
            last_seen[number] = index

    weights: dict[int, float] = {}
    for number in config.numbers:
        hot_score = frequency[number] / max_frequency
        if last_seen[number] is None:
            delay_score = 1.0
        else:
            delay_score = (total_draws - 1 - last_seen[number]) / max(total_draws - 1, 1)
        cold_score = 1.0 - hot_score

        weights[number] = max(
            0.01,
            1.0
            + hot_weight * hot_score
            + delay_weight * delay_score
            + cold_weight * cold_score,
        )

    return weights


def weighted_sample_without_replacement(
    weights: dict[int, float],
    count: int,
    rng: random.Random,
) -> tuple[int, ...]:
    keys = []
    for number, weight in weights.items():
        priority = rng.random() ** (1.0 / weight)
        keys.append((priority, number))
    return tuple(sorted(number for _, number in sorted(keys, reverse=True)[:count]))


def candidate_score(
    numbers: tuple[int, ...],
    weights: dict[int, float],
    config: GameConfig,
) -> Candidate:
    base = statistics.fmean(weights[number] for number in numbers)
    reasons: list[str] = []

    odd_count = sum(number % 2 for number in numbers)
    ideal_odd = config.pick_count / 2
    odd_penalty = abs(odd_count - ideal_odd) / ideal_odd
    odd_score = 1.0 - min(odd_penalty, 1.0)
    reasons.append(f"pari/dispari {config.pick_count - odd_count}/{odd_count}")

    decades = {((number - 1) // 10) for number in numbers}
    decade_score = len(decades) / min(config.pick_count, math.ceil(config.pool_size / 10))
    reasons.append(f"{len(decades)} fasce numeriche")

    consecutive_pairs = sum(
        1 for left, right in zip(numbers, numbers[1:]) if right - left == 1
    )
    consecutive_score = 1.0 - min(consecutive_pairs / max(config.pick_count - 1, 1), 1.0)
    if consecutive_pairs:
        reasons.append(f"{consecutive_pairs} coppie consecutive")
    else:
        reasons.append("nessuna coppia consecutiva")

    total = sum(numbers)
    expected_sum = config.pick_count * (config.pool_size + 1) / 2
    max_distance = expected_sum * 0.55
    sum_score = 1.0 - min(abs(total - expected_sum) / max_distance, 1.0)
    reasons.append(f"somma {total}")

    spread = numbers[-1] - numbers[0]
    ideal_spread = config.pool_size * 0.65
    spread_score = 1.0 - min(abs(spread - ideal_spread) / ideal_spread, 1.0)
    reasons.append(f"apertura {spread}")

    score = (
        base * 0.52
        + odd_score * 0.12
        + decade_score * 0.12
        + consecutive_score * 0.10
        + sum_score * 0.08
        + spread_score * 0.06
    )
    return Candidate(numbers=numbers, score=score, reasons=tuple(reasons))


def generate_candidates(
    config: GameConfig,
    draws: list[tuple[int, ...]],
    count: int,
    attempts: int,
    seed: int | None,
    fixed_numbers: Iterable[int],
    hot_weight: float,
    delay_weight: float,
    cold_weight: float,
) -> list[Candidate]:
    fixed = tuple(sorted(set(fixed_numbers)))
    validate_fixed_numbers(fixed, config)

    rng = random.Random(seed)
    weights = build_number_weights(draws, config, hot_weight, delay_weight, cold_weight)
    for number in fixed:
        weights[number] = weights[number] * 3.0

    unique: dict[tuple[int, ...], Candidate] = {}
    sample_size = max(config.pick_count - len(fixed), 0)
    available_weights = {
        number: weight for number, weight in weights.items() if number not in fixed
    }

    for _ in range(attempts):
        sampled = weighted_sample_without_replacement(available_weights, sample_size, rng)
        numbers = tuple(sorted(fixed + sampled))
        unique[numbers] = candidate_score(numbers, weights, config)

    ranked = sorted(unique.values(), key=lambda candidate: candidate.score, reverse=True)
    return ranked[:count]


def validate_fixed_numbers(numbers: tuple[int, ...], config: GameConfig) -> None:
    if len(numbers) > config.pick_count:
        raise ValueError(
            f"Troppi numeri fissi: {len(numbers)} per una {config.output_name} "
            f"da {config.pick_count} numeri."
        )
    invalid = [number for number in numbers if number not in config.numbers]
    if invalid:
        raise ValueError(
            f"Numeri fissi fuori range per {config.label}: {invalid}. "
            f"Usa 1-{config.pool_size}."
        )


def format_candidate(candidate: Candidate) -> str:
    numbers = " ".join(f"{number:02d}" for number in candidate.numbers)
    reasons = "; ".join(candidate.reasons)
    return f"{numbers}  | score {candidate.score:.3f} | {reasons}"


def parse_fixed_numbers(value: str | None) -> list[int]:
    if not value:
        return []
    return [int(item) for item in re.findall(r"\d+", value)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Genera sestine/cinquine statistiche per SuperEnalotto, Lotto e MillionDAY."
    )
    parser.add_argument(
        "gioco",
        choices=sorted(GAMES),
        help="Gioco da generare: superenalotto, lotto o millionday.",
    )
    parser.add_argument(
        "-n",
        "--numero",
        type=int,
        default=10,
        help="Numero di combinazioni da produrre. Default: 10.",
    )
    parser.add_argument(
        "--storico",
        type=Path,
        help="CSV opzionale con estrazioni passate.",
    )
    parser.add_argument(
        "--colonne",
        help="Colonne CSV dei numeri, separate da virgola. Esempio: n1,n2,n3,n4,n5,n6.",
    )
    parser.add_argument(
        "--tentativi",
        type=int,
        default=6000,
        help="Combinazioni simulate prima del ranking. Default: 6000.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed riproducibile per ottenere lo stesso output.",
    )
    parser.add_argument(
        "--fissi",
        help="Numeri da includere sempre, separati liberamente. Esempio: 7,22,88.",
    )
    parser.add_argument(
        "--peso-frequenti",
        type=float,
        default=0.45,
        help="Peso dei numeri frequenti nello storico. Default: 0.45.",
    )
    parser.add_argument(
        "--peso-ritardi",
        type=float,
        default=0.35,
        help="Peso dei numeri in ritardo nello storico. Default: 0.35.",
    )
    parser.add_argument(
        "--peso-freddi",
        type=float,
        default=0.15,
        help="Peso dei numeri poco frequenti nello storico. Default: 0.15.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = GAMES[args.gioco]
    draws = load_history(args.storico, config, parse_columns(args.colonne))
    candidates = generate_candidates(
        config=config,
        draws=draws,
        count=max(args.numero, 1),
        attempts=max(args.tentativi, args.numero * 20),
        seed=args.seed,
        fixed_numbers=parse_fixed_numbers(args.fissi),
        hot_weight=args.peso_frequenti,
        delay_weight=args.peso_ritardi,
        cold_weight=args.peso_freddi,
    )

    print(f"{config.label}: {config.output_name} da {config.pick_count} numeri su {config.pool_size}")
    print(f"Storico caricato: {len(draws)} estrazioni")
    print(f"Probabilita combinazione esatta: 1 su {config.exact_probability:,}".replace(",", "."))
    print("Nota: output statistico/simulativo, non previsione certa di eventi casuali.")
    print()

    for index, candidate in enumerate(candidates, start=1):
        print(f"{index:02d}. {format_candidate(candidate)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
