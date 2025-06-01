"""
faiss_creator.py
────────────────
Bir rapora ait chunk JSON'larını okuyarak her kategori (genel, ozel, mevzuat) için
embedding ve FAISS index oluşturur.
"""

import os
import json
import faiss
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

DATASETS = ["genel", "ozel", "mevzuat"]

def create_faiss_for_chunks(workspace_dir: str):
    """
    Parameters
    ----------
    workspace_dir : str
        Bu rapora ait ana klasör (ör: workspace/rapor2023)
    """
    chunk_root = os.path.join(workspace_dir, "chunks")
    output_dir = os.path.join(workspace_dir, "faiss")
    os.makedirs(output_dir, exist_ok=True)

    model = SentenceTransformer("intfloat/multilingual-e5-large")

    for ds in DATASETS:
        print(f"\n🔧 {ds.upper()} için FAISS oluşturuluyor...")

        ds_folder = os.path.join(chunk_root, ds)
        json_files = [f for f in os.listdir(ds_folder) if f.endswith(".json")]

        metadata = []
        texts = []

        for jf in json_files:
            path = os.path.join(ds_folder, jf)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                metadata.append(data)
                texts.append(data["chunk_text"])

        if not texts:
            print(f"⚠️ Veri yok: {ds_folder}")
            continue

        # 🧠 Embedding
        embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

        # 📈 FAISS index
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)

        # 📤 Kaydet
        faiss.write_index(index, os.path.join(output_dir, f"faiss_{ds}.index"))
        with open(os.path.join(output_dir, f"metadata_{ds}.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✅ {ds} → index ve metadata kaydedildi: {output_dir}")

# Test
if __name__ == "__main__":
    report_name = "rapor2023"
    create_faiss_for_chunks(f"workspace/{report_name}")
