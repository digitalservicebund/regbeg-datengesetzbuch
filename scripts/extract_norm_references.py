import os
import re
import csv
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent.parent / "content" / "norms-plain"
    output_csv = Path(__file__).resolve().parent.parent / "content" / "analyzed" / "ReferencedNorms.csv"
    
    # regex for EU Regulations and Directives
    eu_ref_pattern = re.compile(
        r'\b(?:Verordnung|Richtlinie|VO|RL)\s*(?:\(EU\)|EU)?\s*(?:Nr\.\s*)?(\d+(?:/\d+)+(?:/?[A-Z]+)?)\b',
        re.IGNORECASE
    )
    
    # Generic German Law name pattern
    de_law_pattern = re.compile(
        r'\b[A-Z][a-zßüäö]+(?:[A-Z][a-zßüäö-]+)*'
        r'(?:gesetz(?:es|en)?|gesetzbuch(?:es)?|ordnung(?:en)?)\b'
    )
    
    # Common acronyms and specific names
    common_acronyms = [
        "DSGVO", "GDPR", "BDSG", "TKG", "TDDDG", "GDNG", "NIS2", "Data Act", "AI Act", 
        "AEUV", "EUV", "GrCh", "BGB", "StGB", "SGB", "VwVfG", "EnWG", "PostG", "KrWG", "WHG", "TrinkwV"
    ]
    acronym_pattern = re.compile(r'\b(?:' + '|'.join(common_acronyms) + r')\b')

    # Generic terms to filter out if they are alone
    generic_noise = {
        "verordnung", "richtlinie", "gesetz", "gesetzes", "ordnung", "verordnungen", 
        "richtlinien", "gesetze", "anordnung", "anordnungen", "rechtsverordnung", "rechtsverordnungen"
    }
    
    results = []
    
    for root_dir, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith("_Plaintext.txt"):
                file_path = Path(root_dir) / file
                source_norm = file.replace("_Volltext_Plaintext.txt", "").replace("_Plaintext.txt", "")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                blocks = content.split('\n\n')
                
                current_paragraph = ""
                current_absatz = ""
                
                for block in blocks:
                    block = block.strip()
                    if not block:
                        continue
                    
                    heading_matches = list(re.finditer(r'(?:^|\n|---)\s*(§\s*\w+|Art(?:ikel|\.)?\s*\w+)\b', block))
                    if heading_matches:
                        current_paragraph = heading_matches[-1].group(1).replace(" ", " ")
                        current_absatz = ""
                        
                    absatz_matches = list(re.finditer(r'(?:^|\s)\((\d+[a-z]?)\)\s', block))
                    if absatz_matches:
                        current_absatz = absatz_matches[-1].group(1)
                    
                    block_flat = block.replace('\n', ' ')
                    sentences = re.split(r'(?<=[.!?])\s+', block_flat)
                    
                    for sentence in sentences:
                        # Collect all matches with their spans
                        all_matches = []
                        
                        for m in eu_ref_pattern.finditer(sentence):
                            all_matches.append((m.start(), m.end(), m.group(0)))
                            
                        for m in de_law_pattern.finditer(sentence):
                            all_matches.append((m.start(), m.end(), m.group(0)))
                            
                        for m in acronym_pattern.finditer(sentence):
                            all_matches.append((m.start(), m.end(), m.group(0)))
                        
                        # Sort by start position, then by length (descending)
                        all_matches.sort(key=lambda x: (x[0], -(x[1]-x[0])))
                        
                        # Remove overlaps (keep longest)
                        filtered_refs = []
                        last_end = -1
                        for start, end, text in all_matches:
                            if start >= last_end:
                                # Check if it's just generic noise
                                if text.lower() in generic_noise:
                                    continue
                                # Check if it's a self reference
                                if text.lower() in ["dieses gesetz", "dem gesetz", "das gesetz"]:
                                    continue
                                # Skip source norm
                                if text.lower() == source_norm.lower():
                                    continue
                                    
                                filtered_refs.append(text)
                                last_end = end
                        
                        for ref in sorted(set(filtered_refs)):
                            loc_str = current_paragraph
                            if current_absatz:
                                loc_str += f" Abs. {current_absatz}"
                            
                            results.append({
                                "SourceNorm": source_norm,
                                "Location": loc_str.strip(),
                                "ReferencedNorm": ref,
                                "Context": sentence.strip()
                            })
                            
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as csvfile:
        fieldnames = ["SourceNorm", "Location", "ReferencedNorm", "Context"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for row in results:
            writer.writerow(row)
            
    print(f"Extraction completed. Found {len(results)} filtered references.")
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    main()
