'''
This code snippet is designed to find the top 10 most relevant chunks from a FAISS index based on a specific question (SORU 1) extracted from a JSON metadata file. It uses the SentenceTransformer model to embed the question and then searches the FAISS index for the closest matches, printing out the results along with their metadata.
'''


import os, json, faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 📂 Drive dizini
BASE_DIR = "/content/drive/MyDrive/rd_project/faiss_outputs"

# 🔧 MODEL
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 🔍 Soru 1'i JSON'dan çek
with open(os.path.join(BASE_DIR, "metadata_soru_yordam.json"), encoding="utf-8") as f:
    soru_yordam = json.load(f)

soru1 = next((entry for entry in soru_yordam if entry["id"] == 1), None)
if not soru1:
    raise ValueError("SORU 1 bulunamadı.")

query_text = soru1["text"]
print("🔎 SORU 1 METNİ:\n", query_text, "\n")

# 🧠 Embed et
query_embedding = model.encode([query_text], convert_to_numpy=True)

# 📥 Genel FAISS ve metadata'yı yükle
faiss_path = os.path.join(BASE_DIR, "faiss_genel.index")
meta_path = os.path.join(BASE_DIR, "metadata_genel.json")

index = faiss.read_index(faiss_path)
with open(meta_path, encoding="utf-8") as f:
    metadata = json.load(f)

# 🔍 FAISS arama → en yakın 10
D, I = index.search(query_embedding, k=10)

results = []
print("📘 GENEL CHUNK DATASETİNDEN EN YAKIN 10 SONUÇ:\n")
for rank, idx in enumerate(I[0]):
    entry = metadata[idx]
    print(f"🔹 [{rank+1}] Index: {idx}")
    print(f"    → Kaynak dosya: {entry.get('source_file')}")
    print(f"    → Cümle sayısı: {entry.get('sentence_count')}, Karakter: {entry.get('char_len')}")
    print(f"    → Chunk:\n{entry['chunk_text'][:300]}...\n")

    results.append({
        "rank": rank + 1,
        "index": idx,
        "chunk_text": entry["chunk_text"],
        "source_file": entry.get("source_file"),
        "char_len": entry.get("char_len"),
        "sentence_count": entry.get("sentence_count")
    })

# 💾 JSON çıktısı olarak da yaz
with open(os.path.join(BASE_DIR, "soru1_genel_top10.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("✅ JSON dosyasına da yazıldı: soru1_genel_top10.json")
