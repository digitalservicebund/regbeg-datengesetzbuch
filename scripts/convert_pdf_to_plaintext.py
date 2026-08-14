"""Convert a PDF norm to plaintext, joining wrapped lines within paragraphs.

Usage:
    uv run python scripts/convert_pdf_to_plaintext.py --norm DGA

The PDF is read from content/norms-pdf/<NORM>.pdf and the output is written to
content/norms-plain/<NORM>/<NORM>_Volltext_Plaintext.txt.
"""

import argparse
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF


def _join_block(lines: list[str]) -> str:
    """Join wrapped lines in a paragraph block into a single line."""
    result = []
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if not stripped:
            continue
        # Soft hyphen at end of line: remove it and join without space
        if stripped.endswith("\xad"):
            result.append(stripped[:-1])
        # Hard hyphen at end of line: join without space if next non-empty line
        # starts with a lowercase letter (line-break hyphenation), otherwise keep
        elif stripped.endswith("-"):
            next_line = next(
                (l.lstrip() for l in lines[i + 1:] if l.strip()), ""
            )
            if next_line and next_line[0].islower():
                result.append(stripped[:-1])
            else:
                result.append(stripped + " ")
        else:
            result.append(stripped + " ")
    return "".join(result).rstrip()


def _collapse_spaced_text(text: str) -> str:
    """Collapse 'G e s p e r r t e r  S a t z' back into normal words.

    Matches runs of 3+ single characters each separated by exactly one space,
    e.g. 'T e i l' → 'Teil'. Leaves normal prose untouched.
    """
    collapsed = re.sub(r"(?<!\w)(\w(?: \w){1,})(?!\w)", lambda m: m.group(0).replace(" ", ""), text)
    # Normalise any leftover multiple spaces (e.g. gaps between spaced words) to one space
    return re.sub(r"  +", " ", collapsed)


def pdf_to_plaintext(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    paragraphs: list[str] = []

    for page in doc:
        blocks = page.get_text("blocks")
        for block in blocks:
            # block: (x0, y0, x1, y1, text, block_no, block_type)
            # block_type 1 = image, skip those
            if block[6] != 0:
                continue
            raw_text: str = block[4]
            lines = raw_text.split("\n")
            joined = _join_block(lines)
            if joined:
                paragraphs.append(_collapse_spaced_text(joined))

    return "\n\n".join(paragraphs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a PDF norm to plaintext.")
    parser.add_argument("--norm", required=True, help="Norm identifier, e.g. DGA")
    args = parser.parse_args()

    norm = args.norm
    pdf_path = Path("content/norms-pdf") / f"{norm}.pdf"
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path("content/norms-plain") / norm
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{norm}_Volltext_Plaintext.txt"

    text = pdf_to_plaintext(pdf_path)
    output_path.write_text(text, encoding="utf-8")
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
