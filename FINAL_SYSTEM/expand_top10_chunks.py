"""
expand_top10_chunks.py
──────────────────────
Her soru için seçilmiş ilk 10 chunk'ın rapordaki orijinal bağlamını genişletir.

Girdi  : workspace/{rapor_id}/top10/<kategori>/soruX_top10.json
Çıktı  : workspace/{rapor_id}/expanded/<kategori>/soruX_top10.json
"""

import os, json, re
from difflib import SequenceMatcher
from tqdm import tqdm

# 📁 PATH AYARLARI
RAPOR_ID     = "rapor2023"
WORKSPACE    = f"workspace/{RAPOR_ID}"
TXT_DIR      = os.path.join(WORKSPACE, "clean_txt")
TOP10_DIR    = os.path.join(WORKSPACE, "top10")
EXPAND_DIR   = os.path.join(WORKSPACE, "expanded")
os.makedirs(EXPAND_DIR, exist_ok=True)

# 🔧 HER KATEGORİYE ÖZEL GENİŞLETME MİKTARI
EXPANSION_SIZE = {
    "genel":   750,
    "mevzuat": 500,
    "ozel":    300
}

# 🔧 YARDIMCI FONKSİYONLAR
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()

def expand_chunk(chunk_text: str, full_text: str, extra_chars: int) -> str:
    norm_chunk = normalize(chunk_text)
    norm_full  = normalize(full_text)

    idx = norm_full.find(norm_chunk)

    if idx == -1:
        # fuzzy fallback
        best, best_idx = 0, -1
        for i in range(0, len(norm_full) - len(norm_chunk), 100):
            win = norm_full[i:i+len(norm_chunk)+100]
            ratio = SequenceMatcher(None, norm_chunk, win).ratio()
            if ratio > best:
                best, best_idx = ratio, i
        if best < 0.7:
            return clean_text(chunk_text)
        idx = best_idx

    snippet = norm_full[idx:idx+50]
    raw_idx = full_text.lower().find(snippet[:20].strip())
    raw_idx = max(raw_idx, 0)

    start = max(0, raw_idx - extra_chars)
    end   = min(len(full_text), raw_idx + len(chunk_text) + extra_chars)
    return clean_text(full_text[start:end])

# 🔁 HER KATEGORİ İÇİN GİRDİ → ÇIKTI
for category, extra in EXPANSION_SIZE.items():
    in_dir  = os.path.join(TOP10_DIR, category)
    out_dir = os.path.join(EXPAND_DIR, category)
    os.makedirs(out_dir, exist_ok=True)

    for filename in tqdm(os.listdir(in_dir), desc=f"{category} expanding"):
        if not filename.endswith(".json"):
            continue

        with open(os.path.join(in_dir, filename), encoding="utf-8") as f:
            chunks = json.load(f)

        for chunk in chunks:
            source_txt = chunk.get("source_file")
            report_path = os.path.join(TXT_DIR, source_txt)

            if not os.path.isfile(report_path):
                print(f"❌ Kaynak metin yok: {source_txt}")
                chunk["expanded_text"] = clean_text(chunk["chunk_text"])
                continue

            with open(report_path, encoding="utf-8") as rf:
                full_text = rf.read()

            chunk["expanded_text"] = expand_chunk(chunk["chunk_text"], full_text, extra)

        with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as wf:
            json.dump(chunks, wf, ensure_ascii=False, indent=2)

print("\n✅ Tüm genişletilmiş top-10 sonuçlar kaydedildi → workspace/{rapor_id}/expanded/")
