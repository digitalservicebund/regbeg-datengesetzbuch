#!/usr/bin/env python3
"""
Concatenate all Meldepflichten_LLM_*.csv files into a single master CSV.
"""
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
GENERATED_DIR = BASE_DIR / "docs" / "data"
OUTPUT_FILE = GENERATED_DIR / "Meldepflichten_LLM_All.csv"

def concat_csvs():
    # Find all matching files in the analyzed directory
    csv_files = sorted(list(GENERATED_DIR.glob("Meldepflichten_LLM_*.csv")))
    
    # Exclude the output file itself if it already exists
    csv_files = [f for f in csv_files if f.name != OUTPUT_FILE.name]
    
    if not csv_files:
        print("No Meldepflichten_LLM_*.csv files found.")
        return

    print(f"Found {len(csv_files)} files to concatenate:")
    for f in csv_files:
        print(f"  - {f.name}")

    header_written = False
    total_rows = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as out_f:
        writer = None
        
        for file_path in csv_files:
            with open(file_path, "r", encoding="utf-8") as in_f:
                # Use semicolon as separator based on existing files
                reader = csv.DictReader(in_f, delimiter=";")
                
                if not header_written:
                    # Initialize writer with fieldnames from first file
                    # Expected: ["Norm", "Referenz", "Sektor", "Art der Pflicht", "Wer", "An wen", "Was gemeldet wird"]
                    writer = csv.DictWriter(out_f, fieldnames=reader.fieldnames, delimiter=";")
                    writer.writeheader()
                    header_written = True
                
                rows_in_file = 0
                for row in reader:
                    # Clean up any potential empty rows or trailing whitespace
                    if any(row.values()):
                        writer.writerow(row)
                        rows_in_file += 1
                        total_rows += 1
                
                print(f"    → Added {rows_in_file} rows.")

    print(f"\nSuccessfully created {OUTPUT_FILE.name} with {total_rows} total rows.")

if __name__ == "__main__":
    concat_csvs()
