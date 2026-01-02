import re
import json
import os

# Configuration
source_files = ["Exploring Egyptian Antiquities and Research", "1.md", "2.md", "3.md"]
ethiopic_dir = "ethiopic_1enoch_p"
output_file = "Henoch_Series_Bible.md"

# Data Structure
# chapters[1] = {
#   "ethiopic": "...",
#   "arabic": "...", # Placeholder
#   "analysis": ["line 1", "line 2"]
# }
chapters = {}

def init_chapters():
    # Initialize for 110 chapters (covering the user's request)
    for i in range(1, 111):
        chapters[i] = {
            "ethiopic": "",
            "arabic": "*(Arabic text to be inserted)*",
            "analysis": []
        }

def load_ethiopic_text():
    print("Loading Ethiopic texts...")
    if not os.path.exists(ethiopic_dir):
        print(f"Warning: Directory {ethiopic_dir} not found.")
        return

    for filename in os.listdir(ethiopic_dir):
        if filename.startswith("chapter_") and filename.endswith(".txt"):
            try:
                # Extract chapter number from filename "chapter_01.txt"
                num_part = filename.replace("chapter_", "").replace(".txt", "")
                chapter_num = int(num_part)
                
                with open(os.path.join(ethiopic_dir, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    if chapter_num in chapters:
                        chapters[chapter_num]["ethiopic"] = content.strip()
            except ValueError:
                continue

def clean_line(line):
    line = line.strip()
    # Skip JSON structural lines that are likely noise
    if line in ['{', '}', '],', '},', '[', ']', '}, {']:
        return ""
    if line.startswith('"role":') or line.startswith('"tokenCount":') or line.startswith('"isThought":') or line.startswith('"thinkingBudget":'):
        return ""
    
    # JSON content extraction
    if line.startswith('"text": "'):
        line = line[9:]
        if line.endswith('",'):
            line = line[:-2]
        elif line.endswith('"'):
            line = line[:-1]
        try:
            # Handle escaped characters
            line = json.loads(f'"{line}"')
        except:
            # Fallback cleanup
            line = line.replace('\\"', '"').replace('\\n', '\n').replace('\\u0027', "'")
    
    return line

def extract_analysis():
    print("Extracting analysis from chat logs...")
    
    # Regex patterns
    # Matches: "Henoch 1", "1 Enoch 1", "Chapter 1", "Kapitel 1"
    # We look for the number.
    patterns = [
        re.compile(r'Henoch\s*\**(\d+)', re.IGNORECASE),
        re.compile(r'1\s*Enoch\s*\**(\d+)', re.IGNORECASE),
        re.compile(r'Chapter\s*\**(\d+)', re.IGNORECASE),
        re.compile(r'Kapitel\s*\**(\d+)', re.IGNORECASE)
    ]
    
    current_chapter = None
    
    for source_file in source_files:
        if not os.path.exists(source_file):
            continue
            
        print(f"Scanning {source_file}...")
        with open(source_file, 'r', encoding='utf-8') as f:
            for line in f:
                text = clean_line(line)
                if not text:
                    continue
                
                # Check for headers
                found_header = False
                for pattern in patterns:
                    match = pattern.search(text)
                    if match:
                        # Validate it's a standalone header or start of a section
                        # Heuristic: Length shouldn't be too long (avoid capturing random mentions in sentences)
                        if len(text) < 100: 
                            try:
                                chap_num = int(match.group(1))
                                if 1 <= chap_num <= 110:
                                    current_chapter = chap_num
                                    found_header = True
                                    # Add the header itself as a separator
                                    chapters[current_chapter]["analysis"].append(f"\n### Source Header: {text}\n")
                            except ValueError:
                                pass
                        break # Stop checking other patterns if one matched
                
                if not found_header and current_chapter:
                    # Append content to current chapter
                    # Filter out some common noise if needed
                    chapters[current_chapter]["analysis"].append(text)

def generate_bible():
    print(f"Generating {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Henoch Series Bible / Regie-Skript\n\n")
        f.write("Zusammenstellung der äthiopischen Originaltexte, Analysen und visuellen Konzepte.\n\n")
        
        for i in range(1, 111):
            chap_data = chapters[i]
            
            # Only write chapters that have content (Ethiopic or Analysis)
            has_ethiopic = bool(chap_data["ethiopic"])
            has_analysis = len(chap_data["analysis"]) > 0
            
            if not has_ethiopic and not has_analysis:
                continue
                
            f.write(f"## Kapitel {i}\n\n")
            
            f.write("### 📜 Äthiopisches Original\n")
            if has_ethiopic:
                f.write("```text\n")
                f.write(chap_data["ethiopic"])
                f.write("\n```\n\n")
            else:
                f.write("*(Kein Text gefunden)*\n\n")
                
            f.write("### 🕌 Arabische Version\n")
            f.write(chap_data["arabic"] + "\n\n")
            
            f.write("### 🧠 Tech-Exegese & Analyse\n")
            if has_analysis:
                # Join and clean up multiple newlines
                content = "\n".join(chap_data["analysis"])
                # Simple markdown cleanup
                content = re.sub(r'\n{3,}', '\n\n', content)
                f.write(content)
                f.write("\n\n")
            else:
                f.write("*(Keine Analyse extrahiert)*\n\n")
                
            f.write("### 🎬 Regie-Anweisungen & Visual Prompts\n")
            f.write("**Setting:** [Hier Setting einfügen]\n")
            f.write("**Actor (Henoch):** [Aktion definieren]\n")
            f.write("**Visuals:** [Prompt-Ideen]\n")
            f.write("**Sound:** [Audio-Design]\n\n")
            f.write("---\n\n")

if __name__ == "__main__":
    init_chapters()
    load_ethiopic_text()
    extract_analysis()
    generate_bible()
    print("Done.")
