import re
import json

source_files = ["Exploring Egyptian Antiquities and Research", "1.md", "2.md", "3.md"]
output_file = "Henoch_Analyse.md"

def clean_line(line):
    line = line.strip()
    # JSON cleaning
    if line.startswith('"text": "'):
        line = line[9:]
        if line.endswith('",'):
            line = line[:-2]
        elif line.endswith('"'):
            line = line[:-1]
        try:
            line = json.loads(f'"{line}"')
        except:
            line = line.replace('\\"', '"').replace('\\n', '\n').replace('\\u0027', "'")
    return line

def extract_content():
    content = {} # Key: Chapter Number (int), Value: Text
    current_chapter = None
    current_text = []
    
    quran_content = []
    in_quran_section = False

    # Regex for Henoch headers
    henoch_pattern = re.compile(r'Henoch\s*\**(\d+)(?::(\d+)(?:-(\d+))?)?', re.IGNORECASE)
    
    # Regex for Quran/Sure headers
    quran_pattern = re.compile(r'(?:Sure|Sura|Quran|Koran)\s*\**(\d+)', re.IGNORECASE)

    for source_file in source_files:
        print(f"Processing {source_file}...")
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                for line in f:
                    text = clean_line(line)
                    
                    # Check for Henoch Header
                    match = henoch_pattern.search(text)
                    if match:
                        if current_chapter is not None:
                            if current_chapter not in content:
                                content[current_chapter] = []
                            # Avoid duplicates if possible, or just append
                            # Simple check: if exact text already exists, skip
                            text_block = "\n".join(current_text)
                            if not content[current_chapter] or text_block not in content[current_chapter]:
                                content[current_chapter].append(text_block)
                        
                        current_chapter = int(match.group(1))
                        current_text = [text]
                        in_quran_section = False
                        continue

                    # Check for Quran Header
                    q_match = quran_pattern.search(text)
                    if q_match:
                        if current_chapter is not None:
                            if current_chapter not in content:
                                content[current_chapter] = []
                            text_block = "\n".join(current_text)
                            if not content[current_chapter] or text_block not in content[current_chapter]:
                                content[current_chapter].append(text_block)
                            current_chapter = None
                        
                        in_quran_section = True
                        current_text = [text]
                        quran_content.append(text)
                        continue

                    # Collect text
                    if current_chapter is not None:
                        current_text.append(text)
                    elif in_quran_section:
                        quran_content.append(text)
            
            # Save last chapter of file
            if current_chapter is not None:
                if current_chapter not in content:
                    content[current_chapter] = []
                text_block = "\n".join(current_text)
                if not content[current_chapter] or text_block not in content[current_chapter]:
                    content[current_chapter].append(text_block)
                current_chapter = None # Reset for next file
                current_text = []

        except Exception as e:
            print(f"Error reading {source_file}: {e}")

    return content, quran_content

def write_markdown(content, quran_content):
    sorted_chapters = sorted(content.keys())
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Analyse von Henoch und Quran\n\n")
        
        f.write("## Buch Henoch\n\n")
        for chapter in sorted_chapters:
            f.write(f"### Henoch Kapitel {chapter}\n\n")
            for text_block in content[chapter]:
                f.write(text_block + "\n\n")
            f.write("---\n\n")
            
        f.write("## Quranische Verse\n\n")
        if quran_content:
            for line in quran_content:
                f.write(line + "\n\n")
        else:
            f.write("Keine spezifischen Quran-Verse im Quelltext gefunden.\n")

if __name__ == "__main__":
    print("Extracting content...")
    content, quran_content = extract_content()
    print(f"Found {len(content)} Henoch chapters.")
    print(f"Found {len(quran_content)} lines of Quran content.")
    write_markdown(content, quran_content)
    print(f"Written to {output_file}")
