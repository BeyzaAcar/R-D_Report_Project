'''
This code snippet is designed to extract questions and their corresponding aids (yordam) from a PDF file containing exam questions. It reads the PDF, processes the text to separate questions and aids, and saves them into a structured text file. The code handles cases where questions and aids are concatenated without proper separation, ensuring each question and aid is on its own line.
'''

import re
from PyPDF2 import PdfReader

input_path = "prompt-faaliyet-donemi-sorulari.pdf"
output_path = "soru_yordam_listesi.txt"

# 📖 PDF oku
reader = PdfReader(input_path)
raw_text = "\n".join([page.extract_text() for page in reader.pages])

# ✅ EK: SORU–YORDAM yapışık gelenleri ayır
raw_text = re.sub(r"(YORDAM\s+\d+:)\s*(SORU\s+\d+:)", r"\1\n\2", raw_text)
raw_text = re.sub(r"(SORU\s+\d+:)\s*(YORDAM\s+\d+:)", r"\1\n\2", raw_text)

# 🔧 Temizlik: her SORU ve YORDAM kendi satırında olsun
fixed_text = re.sub(r"(YORDAM\s+\d+:)", r"\n\1", raw_text)
fixed_text = re.sub(r"(SORU\s+\d+:)", r"\n\1", fixed_text)

# 🧠 Satır satır işlemeye başla
lines = fixed_text.strip().splitlines()

sorular = {}
current_idx = None
current_soru = ""
current_yordam = ""
mode = None

for line in lines:
    line = line.strip()
    if not line:
        continue

    soru_match = re.match(r"SORU\s+(\d+):\s*(.*)", line)
    yordam_match = re.match(r"YORDAM\s+(\d+):\s*(.*)", line)

    if soru_match:
        if current_idx:
            sorular[current_idx] = {
                "soru": current_soru.strip(),
                "yordam": current_yordam.strip() if current_yordam.strip() else "[Boş]"
            }
        current_idx = soru_match.group(1)
        current_soru = soru_match.group(2)
        current_yordam = ""
        mode = "soru"
        continue

    if yordam_match:
        idx = yordam_match.group(1)
        if idx != current_idx:
            print(f"⚠️ Uyuşmazlık: {idx} ≠ {current_idx}")
        current_yordam = yordam_match.group(2)
        mode = "yordam"
        continue

    if mode == "soru":
        current_soru += " " + line
    elif mode == "yordam":
        current_yordam += " " + line

# 🔚 Sonuncuyu ekle
if current_idx:
    sorular[current_idx] = {
        "soru": current_soru.strip(),
        "yordam": current_yordam.strip() if current_yordam.strip() else "[Boş]"
    }

# 💾 Yazdır
with open(output_path, "w", encoding="utf-8") as f:
    for idx in sorted(sorular.keys(), key=int):
        f.write(f"SORU {idx}: {sorular[idx]['soru']}\n")
        f.write(f"YORDAM {idx}: {sorular[idx]['yordam']}\n")
        f.write("-" * 50 + "\n")

print(f"✅ {len(sorular)} SORU+YORDAM çifti başarıyla yazıldı → {output_path}")
