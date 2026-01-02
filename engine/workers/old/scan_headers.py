import re

filename = 'Exploring Egyptian Antiquities and Research'

print("Scanning for Henoch headers...")
count = 0
with open(filename, 'r', encoding='utf-8') as f:
    for line in f:
        if 'Henoch' in line and len(line) < 100:
            print(line.strip())
            count += 1
            if count > 50:
                break

print("\nScanning for Quran headers...")
count = 0
with open(filename, 'r', encoding='utf-8') as f:
    for line in f:
        if ('Quran' in line or 'Koran' in line or 'Sure' in line or 'Sura' in line) and len(line) < 100:
            print(line.strip())
            count += 1
            if count > 50:
                break
