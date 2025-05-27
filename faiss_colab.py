'''
This code snippet is designed to perform a semantic search using FAISS (Facebook AI Similarity Search) with a pre-trained SentenceTransformer model. It retrieves the top 10 most similar chunks from multiple datasets based on a given query (SORU 1) and saves the results in JSON format for each category (genel, ozel, mevzuat).
'''


import os, json, faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 📁 YOL AYARLARI
BASE_DIR = "/content/drive/MyDrive/rd_project/faiss_outputs"
SONUC_KLASORU = os.path.join(BASE_DIR, "sonuclar", "soru_1")
os.makedirs(SONUC_KLASORU, exist_ok=True)

# 🔧 MODEL
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 📥 SORU 1'i çek
with open(os.path.join(BASE_DIR, "metadata_soru_yordam.json"), encoding="utf-8") as f:
    soru_yordam = json.load(f)

soru1 = next((entry for entry in soru_yordam if entry["id"] == 1), None)
if not soru1:
    raise ValueError("SORU 1 bulunamadı.")

query_text = soru1["text"]
query_embedding = model.encode([query_text], convert_to_numpy=True)

# 🔁 TÜM DATASETLERİ DOLAŞ
for category in ["genel", "ozel", "mevzuat"]:
    print(f"🔎 {category.upper()} dataseti taranıyor...")

    # index ve metadata yükle
    faiss_path = os.path.join(BASE_DIR, f"faiss_{category}.index")
    meta_path = os.path.join(BASE_DIR, f"metadata_{category}.json")

    index = faiss.read_index(faiss_path)
    with open(meta_path, encoding="utf-8") as f:
        metadata = json.load(f)

    # FAISS arama
    D, I = index.search(query_embedding, k=10)
    results = []
    for idx in I[0]:
        entry = metadata[idx]
        results.append({
            "index": idx,
            "chunk_text": entry["chunk_text"],
            "source_file": entry.get("source_file"),
            "category": entry.get("category"),
            "char_len": entry.get("char_len"),
            "sentence_count": entry.get("sentence_count")
        })

    # Sonuçları dosyaya yaz
    out_path = os.path.join(SONUC_KLASORU, f"{category}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ {category}.json → ilk 10 sonuç yazıldı.")
