"""
qa_meldepflichten_llm.py

Quality assurance script to evaluate the extracted Meldepflichten from CSV files.
It performs:
1. Manual Check Validation based on a JSON file (fuzzy matching Referenz).
2. LLM Cross-Check by sampling random rows and evaluating them with Sonnet.

Usage:
    python scripts/qa_meldepflichten_llm.py --norm DGA --manual-checks content/analyzed/manual_checks_template.json
"""

import argparse
import csv
import json
import random
import sys
import re
from pathlib import Path
from pydantic import BaseModel, create_model, Field
from typing import List, Dict, Any, Callable, Union

# Add current folder to path to allow importing from extract script
sys.path.append(str(Path(__file__).parent))
from llm_extract_base import get_langdock_token, discover_norm_files, NORMEN_DIR
from extract_meldepflichten_llm import SYSTEM_PROMPT
import requests

COLUMNS_TO_EVALUATE = [
    "Art der Pflicht",
    "Wer",
    "An wen",
    "Auslöser Typ",
    "Frist Typ",
    "Was gemeldet wird"
]

class ColumnEval(BaseModel):
    reasoning: str
    score_percent: int

column_fields = {}
for col in COLUMNS_TO_EVALUATE:
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', col).lower()
    column_fields[safe_name] = (ColumnEval, Field(..., alias=col))

DynamicColumnsModel = create_model("DynamicColumnsModel", **column_fields)

class QAEvaluation(BaseModel):
    is_valid_meldepflicht: bool
    column_evaluations: DynamicColumnsModel

import difflib

def string_similarity(s1: str, s2: str) -> int:
    """Calculate string similarity percentage using SequenceMatcher."""
    if not s1 and not s2:
        return 100
    if not s1 or not s2:
        return 0
    return int(difflib.SequenceMatcher(None, str(s1).strip().lower(), str(s2).strip().lower()).ratio() * 100)

def normalize_referenz(ref: str) -> str:
    """Fuzzy normalize references to help match 'Art. 13 Absatz 3' with 'Artikel 13 Abs. 3'."""
    if not ref:
        return ""
    ref = str(ref).lower()
    ref = ref.replace("artikel", "art")
    ref = ref.replace("absatz", "abs")
    # Remove all non-alphanumeric chars
    ref = re.sub(r'[^a-z0-9]', '', ref)
    return ref

def find_context_window(text: str, referenz: str, zitat: str, window_size: int = 8000) -> tuple[str, str, int]:
    """
    Locate the best context window in the full text using a density-based search.
    """
    zitat_words = [w for w in re.findall(r'\w{4,}', (zitat or "").lower())]
    
    # Use a set for scoring unique word matches
    unique_zitat_words = set(zitat_words)
    
    match_positions = []
    if len(unique_zitat_words) >= 2:
        # Find all occurrences of each unique word
        for word in unique_zitat_words:
            # We use word boundaries to avoid partial matches
            for m in re.finditer(rf'\b{re.escape(word)}\b', text.lower()):
                match_positions.append(m.start())
        
    match_positions.sort()
    
    best_center = -1
    best_count = -1
    method = "default"

    if match_positions:
        # Find 1000-char window with most unique word matches
        cluster_size = 1000
        for i, pos in enumerate(match_positions):
            end_pos = pos + cluster_size
            count = 0
            for j in range(i, len(match_positions)):
                p = match_positions[j]
                if p > end_pos:
                    break
                count += 1
            
            if count > best_count:
                best_count = count
                best_center = pos + (cluster_size // 2)
        
        method = f"zitat (density match: {best_count} points)"
    
    density_match_points = best_count if best_count >= 0 else 0

    # Only trust the zitat density match if it covers at least 60% of unique zitat words
    zitat_word_count = int(len(unique_zitat_words))
    minimum_words = min(5, zitat_word_count)
    min_required = max(minimum_words, int(zitat_word_count * 0.6))
    if best_count < min_required:
        best_center = -1
    
    # Fallback to Referenz parsing if no good zitat cluster found
    if best_center == -1:
        referenz_str = referenz or ""
        match = re.search(r'(?:Artikel|Art\.|§|\()?\s*(\d+)\s*(?:\)|Absatz|Abs\.)?', referenz_str, re.IGNORECASE)
        if match:
            num = match.group(1)
            patterns = [
                re.compile(rf'\b(?:Artikel|Art\.)\s*{num}\b', re.IGNORECASE),
                re.compile(rf'§\s*{num}\b', re.IGNORECASE),
                re.compile(rf'\n\s*\({num}\)\s*\n', re.IGNORECASE)
            ]
            for pattern in patterns:
                found = pattern.search(text)
                if found:
                    best_center = found.start()
                    method = f"referenz (matched {num})"
                    break
                
    if best_center == -1:
        best_center = len(text) // 2
        method = "default (center of document)"
                
    start = max(0, best_center - window_size // 2)
    end = min(len(text), start + window_size)
    return text[start:end], method, density_match_points

def run_manual_checks(csv_rows: List[Dict[str, str]], manual_checks: List[Dict[str, Any]], norm: str):
    print("\n" + "="*60)
    print(f"--- MANUAL CHECKS FOR NORM: {norm} ---")
    
    # Filter checks to only those for the current norm
    checks_for_norm = [c for c in manual_checks if c.get("Norm") == norm]
    if not checks_for_norm:
        print(f"No manual checks found for Norm '{norm}'. Skipping.")
        return

    for check in checks_for_norm:
        ref_expected = str(check.get("Referenz", ""))
        print(f"\nEvaluating expected Pflicht: {ref_expected}")
        
        # We need to find the BEST matching row in the CSV to evaluate against
        best_row = None
        best_ref_score = -1
        best_row_idx = -1
        
        norm_ref_expected = normalize_referenz(ref_expected)
        
        for i, row in enumerate(csv_rows):
            if row.get("Norm") != norm:
                continue
                
            actual_ref = str(row.get("Referenz", ""))
            norm_ref_actual = normalize_referenz(actual_ref)
            
            # Use normalization for high-confidence match
            if norm_ref_expected == norm_ref_actual:
                score = 100
            elif norm_ref_expected in norm_ref_actual or norm_ref_actual in norm_ref_expected:
                score = 90
            else:
                score = string_similarity(ref_expected, actual_ref)
                
            if score > best_ref_score:
                best_ref_score = score
                best_row = row
                best_row_idx = i + 2
                
        if not best_row or best_ref_score < 30: # Threshold for "found at all"
            print(f"  ❌ FAILED: No row found clearly matching Referenz '{ref_expected}' (Best match score: {best_ref_score}%)")
            continue
            
        print(f"  ✓ Closest match found at row {best_row_idx} (Referenz similarity: {best_ref_score}%)")
        
        # Calculate scores for all fields present in the JSON check
        fields_to_check = [k for k in check.keys()] # Include Norm and Referenz
        total_score = 0
        
        for field in fields_to_check:
            expected_val = str(check[field])
            actual_val = str(best_row.get(field, ""))
            
            if field == "Referenz":
                col_score = best_ref_score
            elif field == "Norm":
                col_score = 100 if expected_val == actual_val else 0
            else:
                col_score = string_similarity(expected_val, actual_val)
            
            print(f"    - {field}: {col_score}% (Expected: \"{expected_val[:40]}{'...' if len(expected_val)>40 else ''}\")")
            total_score += col_score
            
        avg_score = total_score / len(fields_to_check)
        print(f"  -> Total Validation Score: {avg_score:.1f}%")

def run_llm_checks(csv_rows: List[Dict[str, str]], sampled_indices: List[int], norm_text: Union[str, Callable[[Dict[str, str]], str]], verbose: bool = False, csv_output_path: Path = None):
    print("\n" + "="*60)
    print(f"--- LLM CROSS-CHECKS (Sample Size: {len(sampled_indices)}) ---")
    if not csv_rows or not sampled_indices:
        print("No CSV rows selected for LLM checks.")
        return

    qa_results: List[Dict[str, Any]] = []

    token = get_langdock_token()
    # Dynamic tool schema for Anthropic (does not support $defs, so we build it manually)
    tool_input_schema = {
        "type": "object",
        "properties": {
            "is_valid_meldepflicht": {"type": "boolean"},
            "column_evaluations": {
                "type": "object",
                "properties": {
                    col: { 
                        "type": "object",
                        "properties": {
                            "reasoning": {"type": "string"},
                            "score_percent": {"type": "integer"}
                        },
                        "required": ["reasoning", "score_percent"]
                    } for col in COLUMNS_TO_EVALUATE
                },
                "required": COLUMNS_TO_EVALUATE
            }
        },
        "required": ["is_valid_meldepflicht", "column_evaluations"]
    }
    
    total_score = 0
    
    for idx in sampled_indices:
        row = csv_rows[idx]
        row_num = idx + 2
        
        # Dynamically extract context window
        zitat = row.get("Zitat") or ""
        referenz = row.get("Referenz") or ""
        row_norm_text = norm_text(row) if callable(norm_text) else norm_text
        context_window, method, density_match_points = find_context_window(row_norm_text, referenz, zitat)

        print(f"\nEvaluating Row {row_num}: Norm={row.get('Norm')}, Referenz={referenz}")
        print(f"  Context found via: {method}")
        
        if verbose:
            print("-" * 30)
            print(f"CONTEXT WINDOW:\n{context_window}")
            print("-" * 30)
        
        prompt = (
            "Du bist eine Qualitätsicherungs-KI, die extrahierte 'Meldepflichten' und andere Informationspflichten im Datenrecht überprüft.\n\n"
            "Im Folgenden findest du die Originalrichtlinie, die für die Extraktion verwendet wurde:\n"
            "----------------------------------------------------\n"
            f"{SYSTEM_PROMPT}\n"
            "----------------------------------------------------\n\n"
            "Hier ist der Original-Textauszug um die Extraktion herum:\n"
            "----------------------------------------------------\n"
            f"{context_window}\n"
            "----------------------------------------------------\n\n"
            "Betrachte nun diese spezifische extrahierte Zeile:\n"
            f"Textauszug (Zitat): \"{row.get('Zitat')}\"\n\n"
            "Auswahl an extrahierten Spalten:\n"
        )
        for col in COLUMNS_TO_EVALUATE:
            prompt += f"- {col}: {row.get(col, '')}\n"
            
        prompt += (
            "\nAufgabe:\n"
            "1. Beurteile, ob der Textauszug tatsächlich eine gültige Pflicht gemäß den Richtlinien enthält.\n"
            f"2. Beurteile für die extrahierten Spalten ({', '.join(COLUMNS_TO_EVALUATE)}), "
            "ob sie genau das widerspiegeln, was im Original-Textauszug steht.\n"
            "3. Nutze das Tool 'submit_evaluation', um deine Begründung (reasoning) sowie eine Prozentzahl (score_percent) für die Qualität und Genauigkeit jeder Spalte anzugeben.\n"
        )
        
        payload = {
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 2000,
            "temperature": 0.0,
            "tools": [
                {
                    "name": "submit_evaluation",
                    "description": "Submit a QA evaluation for a Meldepflicht extraction row.",
                    "input_schema": tool_input_schema
                }
            ],
            "tool_choice": {"type": "tool", "name": "submit_evaluation"},
            "messages": [{"role": "user", "content": prompt}]
        }
        
        headers = {
            "x-api-key": token,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        try:
            response = requests.post(
                "https://api.langdock.com/anthropic/eu/v1/messages", 
                json=payload, 
                headers=headers
            )
            response.raise_for_status()
            response_json = response.json()
            
            # Use the tool use block
            tool_use = next((c for c in response_json.get("content", []) if c.get("type") == "tool_use"), None)
            if not tool_use:
                raise ValueError("LLM returned no structured evaluation via tool use.")
            
            # Pydantic validation handles aliases automatically for model_validate
            parsed = QAEvaluation.model_validate(tool_use.get("input", {}))
            
            print(f"  Valid Meldepflicht: {parsed.is_valid_meldepflicht}")
            
            row_score_sum = 0
            
            evals_dict = parsed.column_evaluations.model_dump(by_alias=True)
            result_row: Dict[str, Any] = {
                "norm": row.get("Norm", ""),
                "reference": referenz,
                "context_found_via": method,
                "density_match": density_match_points,
                "valid_meldepflicht": 1 if parsed.is_valid_meldepflicht else 0,
            }
            for col in COLUMNS_TO_EVALUATE:
                col_eval = evals_dict.get(col, {})
                reasoning = col_eval.get('reasoning', "Keine Begründung gegeben.")
                score = col_eval.get('score_percent', 0)
                print(f"  - {col}: {score}% | {reasoning}")
                row_score_sum += score
                result_row[col] = round(score / 100, 2)
            
            row_avg = row_score_sum / len(COLUMNS_TO_EVALUATE) if COLUMNS_TO_EVALUATE else 0
            print(f"  -> Durchschnittliche Zeilenqualität: {row_avg:.1f}%")
            total_score += row_avg
            qa_results.append(result_row)
                
        except Exception as e:
            print(f"  [ERROR] LLM Evaluation failed for row {row_num}: {e}")

    if sampled_indices:
        avg_score = total_score / len(sampled_indices)
        print("\n" + "="*60)
        print(f"AVERAGE LLM QUALITY SCORE: {avg_score:.1f}%")

    if qa_results and csv_output_path:
        fieldnames = ["norm", "reference", "context_found_via", "density_match", "valid_meldepflicht"] + COLUMNS_TO_EVALUATE
        with open(csv_output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(qa_results)
        print(f"QA results written to {csv_output_path}")

def main():
    parser = argparse.ArgumentParser(description="QA limits for extracted Meldepflichten CSV files.")
    parser.add_argument("--norm", default=None, help="The Norm identifier (e.g., DGA). If omitted, all Meldepflichten CSVs in docs/data/ are loaded.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling rows.")
    parser.add_argument("--manual-checks", default=None, help="Path to JSON file containing manual checks.")
    parser.add_argument("--num-samples", type=int, default=0, help="Number of random rows to cross-check with the LLM.")
    parser.add_argument("--rows", help="Specific row numbers or ranges (e.g., '10-20,35'). Refers to row numbers in the CSV file (2-indexed for first data row).")
    parser.add_argument("--verbose", action="store_true", help="Output the full context window for each row.")
    parser.add_argument("--skip-llm-checks", action="store_true", help="Skip the LLM evaluation phase entirely.")
    parser.add_argument("--qa-output", default=None, help="Path to write QA results CSV (default: docs/data/QA_LLM_{NORM}.csv).")
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / "docs" / "data"

    if args.norm:
        csv_paths = [data_dir / f"Meldepflichten_LLM_{args.norm}.csv"]
        if not csv_paths[0].exists():
            print(f"Error: CSV file not found at {csv_paths[0]}")
            sys.exit(1)
        default_qa_output = data_dir / f"QA_LLM_{args.norm}.csv"
    else:
        csv_paths = sorted(data_dir.glob("Meldepflichten_LLM_*.csv"))
        if not csv_paths:
            print(f"Error: No Meldepflichten_LLM_*.csv files found in {data_dir}")
            sys.exit(1)
        default_qa_output = data_dir / "QA_LLM_All.csv"
        
    # Read CSV
    csv_rows = []
    for csv_path in csv_paths:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                # Skip rows that are just exact copies of the header
                if row.get("Referenz") == "Referenz":
                    continue
                csv_rows.append(row)
        
    print(f"Loaded {len(csv_rows)} data rows (skipped potential header duplicates) from {len(csv_paths)} file(s)")
    
    # Define eligible indices
    eligible_indices = []
    if args.rows:
        for part in args.rows.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    start_row, end_row = map(int, part.split('-'))
                    # CSV Row 2 -> Index 0. Row start-end -> Index start-2 to end-1
                    eligible_indices.extend(range(start_row - 2, end_row - 1 + 1)) # +1 to make end_row inclusive
                except ValueError:
                    print(f"[ERROR] Invalid range: {part}")
            else:
                try:
                    eligible_indices.append(int(part) - 2)
                except ValueError:
                    print(f"[ERROR] Invalid row number: {part}")
    else:
        eligible_indices = list(range(len(csv_rows)))

    # Dedup and bound check
    eligible_indices = sorted(list(set([i for i in eligible_indices if 0 <= i < len(csv_rows)])))

    # Select final indices
    if args.num_samples > 0:
        random.seed(args.seed)
        selected_indices = sorted(random.sample(eligible_indices, min(args.num_samples, len(eligible_indices))))
    else:
        # If num-samples is 0, take all eligible rows
        selected_indices = eligible_indices

    # Run Checks
    if args.manual_checks:
        mc_path = Path(args.manual_checks)
        if mc_path.exists():
            with open(mc_path, "r", encoding="utf-8") as f:
                manual_checks = json.load(f)
            norms_to_check = [args.norm] if args.norm else list({r.get("Norm") for r in csv_rows if r.get("Norm")})
            for norm in norms_to_check:
                run_manual_checks(csv_rows, manual_checks, norm)
        else:
            print(f"[WARN] Manual checks file {mc_path} not found. Skipping.")
            
    # Load the original text for QA context extraction
    norm_text = ""
    # We use discover_norm_files to find the correct text file
    norms_to_discover = [args.norm] if args.norm else list({r.get("Norm") for r in csv_rows if r.get("Norm")})
    norm_texts: Dict[str, str] = {}
    for norm_name in norms_to_discover:
        norm_files = discover_norm_files(NORMEN_DIR, [norm_name])
        if norm_files:
            _norm_name, file_path = norm_files[0]
            with open(file_path, "r", encoding="utf-8") as f:
                norm_texts[norm_name] = f.read()
            print(f"Loaded {len(norm_texts[norm_name])} characters from original norm text ({file_path.name}).")
        else:
            print(f"[WARN] Could not find original text for norm {norm_name} in {NORMEN_DIR}. Context matching may fail.")
    
    # Build combined norm_text lookup for run_llm_checks — pass per-row lookup via a wrapper
    def get_norm_text_for_row(row: Dict[str, str]) -> str:
        return norm_texts.get(row.get("Norm", ""), "")
    
    if selected_indices and not args.skip_llm_checks:
        qa_output_path = Path(args.qa_output) if args.qa_output else default_qa_output
        run_llm_checks(csv_rows, selected_indices, get_norm_text_for_row, args.verbose, csv_output_path=qa_output_path)
    elif args.skip_llm_checks:
        print("\nSkipping LLM checks as requested.")

if __name__ == "__main__":
    main()
