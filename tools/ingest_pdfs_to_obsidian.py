#!/usr/bin/env python3
"""Build raw Obsidian notes from the local PDF corpus."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "Obsidian Vault SMORFIA"


@dataclass(frozen=True)
class Source:
    filename: str
    slug: str
    title: str
    tags: tuple[str, ...]
    role: str


SOURCES = (
    Source(
        filename="1881__capacelli___il_vero_libro_dei_sogni.pdf",
        slug="1881 Capacelli - Il vero libro dei sogni",
        title="1881 Capacelli - Il vero libro dei sogni",
        tags=("fonte", "raw", "sogni", "lotto", "cabala"),
        role="Fonte storica per interpretazioni dei sogni, numeri e contesto del Lotto ottocentesco.",
    ),
    Source(
        filename="Smorfia napoletana La vera cabala del lotto .pdf",
        slug="Smorfia napoletana - La vera cabala del lotto",
        title="Smorfia napoletana - La vera cabala del lotto",
        tags=("fonte", "raw", "smorfia", "sogni", "lotto"),
        role="Fonte primaria operativa per associare immagini oniriche e numeri.",
    ),
    Source(
        filename="semprini.pdf",
        slug="Semprini",
        title="Danilo Semprini - Sefer Yetzirah",
        tags=("fonte", "raw", "cabala", "linguaggio", "simboli"),
        role="Studio interpretativo sul Sefer Yetzirah, utile per un livello simbolico e linguistico.",
    ),
    Source(
        filename="René Guénon, Esoterismo ed exoterismo.pdf",
        slug="Rene Guenon - Esoterismo ed exoterismo",
        title="Rene Guenon - Esoterismo ed exoterismo",
        tags=("fonte", "raw", "esoterismo", "tradizione", "simboli"),
        role="Cornice teorica sulla distinzione tra livello esteriore e interiore della dottrina.",
    ),
    Source(
        filename="sefer_yetzira_(traduzione).pdf",
        slug="Sefer Yetzira traduzione",
        title="Sefer Yetzira - traduzione",
        tags=("fonte", "raw", "cabala", "sefer-yetzira", "simboli"),
        role="Testo di riferimento su lettere, sefirot e formazione simbolica.",
    ),
    Source(
        filename="The Kabala Of Numbers (Sepharial, 1920).pdf",
        slug="Sepharial - The Kabala Of Numbers",
        title="Sepharial - The Kabala Of Numbers",
        tags=("fonte", "raw", "cabala", "numerologia", "sepharial", "simboli"),
        role="Fonte numerologica per cifre, pianeti e significati dei numeri.",
    ),
    Source(
        filename="dizionarioillust00roncuoft.pdf",
        slug="Ronchetti - Dizionario Illustrato dei Simboli",
        title="Ronchetti - Dizionario Illustrato dei Simboli",
        tags=("fonte", "raw", "simboli", "iconologia", "ronchetti"),
        role="Dizionario iconologico per arricchire la lettura simbolica dei sogni.",
    ),
)


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def extract_pdf(path: Path) -> tuple[int, str]:
    chunks: list[str] = []
    with fitz.open(path) as doc:
        page_count = doc.page_count
        for index, page in enumerate(doc, start=1):
            text = clean_text(page.get_text("text"))
            if text:
                chunks.append(f"## Pagina {index}\n\n{text}")
            else:
                chunks.append(f"## Pagina {index}\n\n[Pagina senza testo estraibile]")
    return page_count, "\n\n".join(chunks)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def frontmatter(tags: tuple[str, ...], source_file: str | None = None) -> str:
    lines = ["---", "tags:"]
    lines.extend(f"  - {tag}" for tag in tags)
    if source_file:
        lines.append(f"source_file: {source_file}")
    lines.append("---")
    return "\n".join(lines)


def main() -> int:
    attachment_dir = VAULT / "99_Allegati" / "PDF"
    source_dir = VAULT / "01_Fonti"
    raw_dir = VAULT / "02_Raw"
    attachment_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    for source in SOURCES:
        pdf_path = ROOT / source.filename
        if not pdf_path.exists():
            print(f"Missing: {pdf_path}")
            continue

        copied_pdf = attachment_dir / source.filename
        shutil.copy2(pdf_path, copied_pdf)

        page_count, raw_text = extract_pdf(pdf_path)
        raw_note = raw_dir / f"{source.slug} RAW.md"
        source_note = source_dir / f"{source.slug}.md"

        raw_content = (
            f"{frontmatter(source.tags, source.filename)}\n\n"
            f"# {source.title} RAW\n\n"
            f"Fonte: [[{source.slug}]]\n\n"
            f"PDF: [[99_Allegati/PDF/{source.filename}]]\n\n"
            f"Pagine: {page_count}\n\n"
            f"{raw_text}\n"
        )
        write(raw_note, raw_content)

        source_content = (
            f"{frontmatter(source.tags, source.filename)}\n\n"
            f"# {source.title}\n\n"
            f"Ruolo: {source.role}\n\n"
            f"PDF: [[99_Allegati/PDF/{source.filename}]]\n\n"
            f"Raw: [[02_Raw/{source.slug} RAW]]\n\n"
            f"Pagine: {page_count}\n\n"
            "## Collegamenti\n\n"
            "- [[Home]]\n"
            "- [[04_Grafo/Grafo iniziale]]\n"
            "- [[05_Progetti/Chatbot sogni e numeri]]\n"
        )
        write(source_note, source_content)
        summary_rows.append((source.title, page_count, len(raw_text)))
        print(f"Ingested: {source.title} ({page_count} pages, {len(raw_text)} chars)")

    summary = ["# Report ingestione PDF", "", "| Fonte | Pagine | Caratteri estratti |", "|---|---:|---:|"]
    summary.extend(f"| {title} | {pages} | {chars} |" for title, pages, chars in summary_rows)
    write(VAULT / "06_Output" / "Report ingestione PDF.md", "\n".join(summary) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
