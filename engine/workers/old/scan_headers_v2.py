import re

filename = 'Exploring Egyptian Antiquities and Research'

def scan_pattern(pattern_name, pattern_regex):
    print(f"\nScanning for {pattern_name}...")
    count = 0
    regex = re.compile(pattern_regex, re.IGNORECASE)
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            # Basic cleaning for JSON
            clean_text = line.strip()
            if clean_text.startswith('"text": "'):
                clean_text = clean_text[9:-2]
            
            match = regex.search(clean_text)
            if match:
                print(f"Found: {clean_text[:100]}...") # Print first 100 chars
                count += 1
                if count > 20:
                    print("... (limit reached)")
                    break

scan_pattern("Henoch", r'Henoch\s*\**\d+')
scan_pattern("Chapter", r'Chapter\s*\**\d+')
scan_pattern("Kapitel", r'Kapitel\s*\**\d+')
scan_pattern("1 Enoch", r'1\s*Enoch\s*\**\d+')
scan_pattern("Generic Number Header", r'^\s*\**\d+\.\s+[A-Z]')
