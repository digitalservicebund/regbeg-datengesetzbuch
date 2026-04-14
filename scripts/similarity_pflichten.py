"""
similarity_pflichten.py

Computes semantic similarity between all Pflichten extracted across the
analyzed CSVs and writes two output files:

  content/analyzed/similarity_matrix.csv   — N×N cosine-similarity matrix
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT_DIR = Path(__file__).parent.parent
ANALYZED_DIR = ROOT_DIR / "docs" / "data"
OUTPUT_MATRIX = ANALYZED_DIR / "similarity_matrix.csv"

# Fields and their weights for the final embedding
FIELD_WEIGHTS = {
    "Art der Pflicht": 0.1,
    "Wer": 0.1,
    "An wen": 0.1,
    "Auslöser": 0.1,
    "Frist": 0.1,
    "Zitat": 0.5,
    "Was gemeldet wird": 0.5,
}
EMBED_FIELDS = list(FIELD_WEIGHTS.keys())

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_pflichten(analyzed_dir: Path, filter_norms: list[str] | None) -> list[dict]:
    """Load all Meldepflichten_LLM_*.csv files from the analyzed directory."""
    pattern = "Meldepflichten_LLM_*.csv"
    files = sorted(analyzed_dir.glob(pattern))

    if not files:
        print(f"[ERROR] No files matching '{pattern}' found in {analyzed_dir}", file=sys.stderr)
        sys.exit(1)

    rows: list[dict] = []
    for f in files:
        if filter_norms:
            norm_slug = f.stem.replace("Meldepflichten_LLM_", "")
            if norm_slug not in filter_norms:
                continue
        print(f"  Loading {f.name}...")
        with open(f, encoding="utf-8-sig") as fh:
            # Try semicolon delimiter (project convention)
            reader = csv.DictReader(fh, delimiter=";")
            file_rows = list(reader)
        print(f"    → {len(file_rows)} rows")
        rows.extend(file_rows)

    print(f"\nTotal Pflichten loaded: {len(rows)}")
    return rows


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed_pflichten(rows: list[dict]) -> np.ndarray:
    """Embed each field separately and combine them using FIELD_WEIGHTS."""
    from sentence_transformers import SentenceTransformer
 
    model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    print(f"\nLoading embedding model '{model_name}'...")
    model = SentenceTransformer(model_name)

    n = len(rows)
    dim = model.get_sentence_embedding_dimension()
    final_embeddings = np.zeros((n, dim))

    print(f"Embedding {n} Pflichten using weighted fields: {FIELD_WEIGHTS}")

    for field, weight in FIELD_WEIGHTS.items():
        if weight == 0: continue
        print(f"  Processing field '{field}' (weight {weight})...")
        texts = [str(row.get(field, "")).strip() for row in rows]
        # Treat empty fields as empty strings (they'll get a neutral embedding)
        embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        final_embeddings += (embeddings * weight)

    # Re-normalize to unit length so cosine similarity is just dot product
    norms = np.linalg.norm(final_embeddings, axis=1, keepdims=True)
    final_embeddings = np.divide(final_embeddings, norms, out=np.zeros_like(final_embeddings), where=norms!=0)

    print(f"Final embeddings shape: {final_embeddings.shape}")
    return final_embeddings


# ---------------------------------------------------------------------------
# Similarity matrix
# ---------------------------------------------------------------------------

def compute_similarity(embeddings: np.ndarray) -> np.ndarray:
    from sklearn.metrics.pairwise import cosine_similarity
    print("\nComputing cosine similarity matrix...")
    matrix = cosine_similarity(embeddings)
    np.fill_diagonal(matrix, 0.0)   # self-similarity → 0 (diagonal shown differently in heatmap)
    return matrix


def make_label(row: dict, idx: int) -> str:
    """Create a unique label: '{Norm}:{Referenz} #{idx}'."""
    norm = str(row.get("Norm", "")).strip()
    ref = str(row.get("Referenz", "")).strip()
    # Adding #idx ensures uniqueness even if multiple rows have the same Referenz
    if norm and ref:
        return f"{norm}:{ref} #{idx}"
    return f"row_{idx}"


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def write_matrix(matrix: np.ndarray, labels: list[str], output_path: Path) -> None:
    print(f"\nWriting similarity matrix to {output_path} ...")
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow([""] + labels)
        for i, label in enumerate(labels):
            row_values = [f"{v:.4f}" for v in matrix[i]]
            writer.writerow([label] + row_values)
    print(f"  → {len(labels)}×{len(labels)} matrix written.")


# ---------------------------------------------------------------------------
# High-similarity pair report
# ---------------------------------------------------------------------------

def report_pairs(matrix: np.ndarray, labels: list[str], threshold: float) -> None:
    n = len(labels)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            score = matrix[i, j]
            if score >= threshold:
                pairs.append((score, labels[i], labels[j]))

    pairs.sort(reverse=True)
    print(f"\n--- Pairs with similarity ≥ {threshold} ({len(pairs)} found) ---")
    for score, a, b in pairs[:50]:   # cap at 50 lines
        print(f"  {score:.4f}  {a}  ↔  {b}")
    if len(pairs) > 50:
        print(f"  ... and {len(pairs) - 50} more.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute semantic similarity between Pflichten and export a heatmap matrix."
    )
    parser.add_argument(
        "--norm",
        metavar="NAME",
        action="append",
        dest="norms",
        help=(
            "Process only this norm slug (e.g. DSA, DSGVO). "
            "Matches the suffix of 'Meldepflichten_LLM_<NAME>.csv'. Can be repeated."
        ),
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Similarity threshold for reporting high-similarity pairs (default: 0.85).",
    )
    args = parser.parse_args()

    print("=== Pflichten Similarity Analysis ===\n")
    print(f"Source directory : {ANALYZED_DIR}")
    print(f"Filter norms     : {args.norms or 'all'}")
    print(f"Report threshold : {args.threshold}\n")

    # 1. Load
    rows = load_pflichten(ANALYZED_DIR, args.norms)

    # 2. Build labels
    labels = [make_label(r, i) for i, r in enumerate(rows)]

    # 3. Embed with weights
    embeddings = embed_pflichten(rows)

    # 4. Compute similarity
    matrix = compute_similarity(embeddings)

    # 5. Write outputs
    write_matrix(matrix, labels, OUTPUT_MATRIX)

    # 6. Print high-similarity pair report
    report_pairs(matrix, labels, args.threshold)

    print("\n=== Done ===")
    print(f"  Matrix  : {OUTPUT_MATRIX}")
    print(f"\nTo view the heatmap, run:")
    print(f"  cd {ROOT_DIR}")
    print(f"  python3 -m http.server 8000")
    print(f"  Then open: http://localhost:8000/docs/")
    print(f"  (GitHub Pages is configured using the docs/ folder)")


if __name__ == "__main__":
    main()
