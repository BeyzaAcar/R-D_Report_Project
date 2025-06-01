"""
top10_chunk_retriever.py
────────────────────────
Her soru için FAISS indekslerinde arama yapar ve en alakalı 10 chunk'ı
(genel, mevzuat, ozel kategorilerinden) çıkarır. Sonuçları ayrı JSON dosyalarına kaydeder.
"""

import os, json, faiss, numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# 📁 Giriş / Çıkış dizinleri
RAPOR_ID  = "rapor2023"
WORKSPACE = f"workspace/{RAPOR_ID}"

FAISS_DIR = os.path.join(WORKSPACE, "faiss")
TOPK_DIR  = os.path.join(WORKSPACE, "top10")
os.makedirs(TOPK_DIR, exist_ok=True)

# 🔧 FAISS eşlemeleri
DATASETS = {
    "genel":   {"index": "faiss_genel.index",   "meta": "metadata_genel.json"},
    "mevzuat": {"index": "faiss_mevzuat.index", "meta": "metadata_mevzuat.json"},
    "ozel":    {"index": "faiss_ozel.index",    "meta": "metadata_ozel.json"},
}

TOP_K = 10
model = SentenceTransformer("intfloat/multilingual-e5-large")

# ❓ Soru-Yordam
soru_path = os.path.join(FAISS_DIR, "metadata_soru_yordam.json")
with open(soru_path, encoding="utf-8") as f:
    sorular = json.load(f)

def ensure_dir(p): os.makedirs(p, exist_ok=True)

def search_faiss(query, faiss_index, k):
    embedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    _, top_indices = faiss_index.search(embedding, k)
    return top_indices[0]

# 🔄 Dataset bazlı döngü
for ds, files in DATASETS.items():
    print(f"\n🔍 Dataset: {ds.upper()}")
    out_dir = os.path.join(TOPK_DIR, ds)
    ensure_dir(out_dir)

    # 🔧 FAISS + metadata
    idx_path  = os.path.join(FAISS_DIR, files["index"])
    meta_path = os.path.join(FAISS_DIR, files["meta"])

    index = faiss.read_index(idx_path)
    with open(meta_path, encoding="utf-8") as f:
        metadata = json.load(f)

    # 🔁 Her soru için top-k chunk seç
    for soru in tqdm(sorular, desc=f"{ds} sorular"):
        qid   = soru["id"]
        qtext = soru["text"]

        top_idxs = search_faiss(qtext, index, TOP_K)

        results = []
        for rank, idx in enumerate(top_idxs, 1):
            entry = metadata[idx]
            results.append({
                "rank":           rank,
                "index":          int(idx),
                "chunk_text":     entry["chunk_text"],
                "source_file":    entry.get("source_file"),
                "char_len":       int(entry.get("char_len", 0)),
                "sentence_count": int(entry.get("sentence_count", 0)),
            })

        # ✅ Kaydet
        out_file = os.path.join(out_dir, f"soru{qid}_top10.json")
        with open(out_file, "w", encoding="utf-8") as jf:
            json.dump(results, jf, ensure_ascii=False, indent=2)

        if qid == 1:
            print(f"  • soru{qid}: ilk chunk → {results[0]['chunk_text'][:100]}…")

print("\n✅ Tüm sorular için top-10 sonuçlar kaydedildi.")
