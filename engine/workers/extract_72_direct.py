
import sys
import re
from pypdf import PdfReader

def extract_chapter_72(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    
    # Try to find Chapter 72 start and end
    # Note: The pattern might need adjustment based on PDF content structure seen previously
    # Looking for "72:1" style or "Chapter 72"
    
    # Simple regex to capture 72:1 onwards until 73:1 or end
    # Based on previous view, text looked like "1. 72:1 ..."
    
    match = re.search(r'(72:1.*?)(?=73:1|$)', full_text, re.DOTALL)
    if match:
        print(match.group(1))
    else:
        # Fallback: look for typical chapter header if "72:1" not found directly
        match_alt = re.search(r'(Chapter\s*72.*?)(?=Chapter\s*73|$)', full_text, re.DOTALL | re.IGNORECASE)
        if match_alt:
            print(match_alt.group(1))
        else:
            print("Could not isolate Chapter 72. Dumping raw text around where it might be.")
            # Dump a chunk if specific match fails, for debugging
            start_idx = full_text.find("72:1")
            if start_idx != -1:
                print(full_text[start_idx:start_idx+5000])
            else:
                print("72:1 not found in text.")

if __name__ == "__main__":
    extract_chapter_72(r"C:\Users\sasch\visionexe\docs\ethiopic_1enoch_p\Henoch_from_Geez_text.pdf")
