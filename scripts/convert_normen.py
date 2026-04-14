import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

def clean_txt_content(content):
    # Normalize non-breaking spaces and other weirdness
    content = content.replace('\xa0', ' ')
    content = content.replace('\f', '\n')
    
    # Remove page footer/header patterns
    content = re.sub(r'ELI: http://\S+\s+\d+/\d+', '', content)
    content = re.sub(r'([A-Z]{2}\s+)?ABl\. [LCS] vom \d+\.\d+\.\d+(\s+[A-Z]{2})?', '', content)
    content = re.sub(r'Amtsblatt\s+[A-Z]{2}', '', content)
    content = re.sub(r'der Europäischen Union\s+Reihe [LCS]', '', content)
    content = re.sub(r'Reihe [LCS]\s+Amtsblatt', '', content)
    content = re.sub(r'\d{4}/[A-Z\d/]+\s+\d{1,2}\.\d{1,2}\.\d{4}', '', content)
    
    # Split by double newlines to identify paragraphs/blocks
    paragraphs = re.split(r'\n\s*\n', content)
    cleaned_paragraphs = []
    
    for p in paragraphs:
        # Within each block, join lines with space to remove layout line breaks
        lines = p.split('\n')
        # Clean each line: strip and collapse internal spaces
        cleaned_lines = [re.sub(r' {2,}', ' ', l.strip()) for l in lines]
        # Filter out truly empty lines if any leaked in
        cleaned_lines = [l for l in cleaned_lines if l]
        
        if not cleaned_lines:
            continue
            
        # Join lines within the block with a single space
        joined_p = " ".join(cleaned_lines)
        # Final space collapse
        joined_p = re.sub(r' {2,}', ' ', joined_p).strip()
        if joined_p:
            cleaned_paragraphs.append(joined_p)
    
    return "\n\n".join(cleaned_paragraphs)

def process_xml_node(node):
    """Recursively extract text from XML nodes while keeping some structure."""
    text_parts = []
    
    if node.text:
        # Flatten internal line breaks in the text of this node
        clean_text = node.text.replace('\xa0', ' ').replace('\n', ' ')
        text_parts.append(clean_text)
    
    for child in node:
        child_text = process_xml_node(child)
        if child_text:
            text_parts.append(child_text)
        if child.tail:
            # Flatten internal line breaks in the tail
            clean_tail = child.tail.replace('\xa0', ' ').replace('\n', ' ')
            text_parts.append(clean_tail)
            
    # Remove namespace if present
    tag = node.tag.split('}')[-1].lower()
    
    # Join parts - internal block newlines are already in child_text
    result = "".join(text_parts)
    # Collapse multiple spaces but preserve existing newlines
    result = re.sub(r' +', ' ', result).strip()
    
    block_tags = ['p', 'la', 'titel', 'title', 'ident', 'enbez', 'entry', 'row', 'table', 'content', 'gliederungseinheit']
    if tag in block_tags:
        # Ensure block-level elements start on new lines
        return "\n\n" + result + "\n"
    if tag == 'dt':
        return "\n" + result + " "
    if tag == 'dd':
        return result
    
    return result

def clean_xml_to_txt(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        full_text = []
        for norm in root.findall('.//norm'):
            metadaten = norm.find('metadaten')
            if metadaten is not None:
                enbez = metadaten.find('enbez')
                titel = metadaten.find('titel')
                
                heading = ""
                enbez_text = enbez.text if enbez is not None else None
                if enbez_text is not None:
                    heading += f"--- {enbez_text.strip()} ---"
                
                titel_text = titel.text if titel is not None else None
                if titel_text is not None:
                    padding = " " if heading else ""
                    heading += f"{padding}{titel_text.strip()}"
                
                if heading:
                    full_text.append(f"\n\n{heading}\n")
            
            textdaten = norm.find('textdaten')
            if textdaten is not None:
                text_node = textdaten.find('.//text')
                if text_node is not None:
                    txt = process_xml_node(text_node)
                    if txt.strip():
                        full_text.append(txt)
        
        content = "".join(full_text)
        # Final cleanup
        content = content.replace('\xa0', ' ')
        content = re.sub(r' {2,}', ' ', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content.strip()
    except Exception as e:
        print(f"Error parsing XML {xml_path}: {e}")
        return None

def main():
    base_dir = Path(__file__).resolve().parent.parent / "content" / "norms-plain"
    
    for root_dir, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = Path(root_dir) / file
            
            # Skip already cleaned files to avoid infinite loops or reprocessing
            if file.endswith("_Plaintext.txt"):
                continue

            if file.endswith(".txt"):
                print(f"Processing TXT: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    cleaned = clean_txt_content(content)
                    
                    output_path = file_path.with_name(file_path.stem + "_Plaintext.txt")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned)
                    print(f"Created: {output_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    
            elif file.endswith(".xml"):
                print(f"Converting XML: {file_path}")
                cleaned = clean_xml_to_txt(file_path)
                
                if cleaned:
                    output_path = file_path.with_name(file_path.stem + "_Plaintext.txt")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned)
                    print(f"Created: {output_path}")

if __name__ == "__main__":
    main()
