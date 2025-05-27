'''
This code snippet is designed to vectorize text chunks from JSON files stored in a Google Drive folder using the SentenceTransformer model. It processes each category of reports, generates embeddings for the text chunks, and saves the FAISS index and metadata in a specified output directory.
'''


import os, json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# 🔧 Model yükle
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# 📁 Drive'daki klasör konumu
BASE_DIR = "/content/drive/MyDrive/rd_project"
OUTPUT_DIR = os.path.join(BASE_DIR, "faiss_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🔍 Kategoriye göre tüm JSON chunk dosyalarını oku
def load_chunks_by_category(base_dir, category):
    all_chunks = []
    for report_folder in os.listdir(base_dir):
        report_path = os.path.join(base_dir, report_folder)
        category_path = os.path.join(report_path, category)

        if not os.path.isdir(category_path):
            continue

        for filename in os.listdir(category_path):
            if filename.endswith(".json"):
                file_path = os.path.join(category_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if data["category"] == category:
                            all_chunks.append(data)
                    except Exception as e:
                        print(f"❌ Hatalı dosya: {file_path} → {e}")
    return all_chunks

# 🧠 Embed et
def vectorize_chunks(chunks):
    texts = [c["chunk_text"] for c in chunks]
    return model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# 💾 FAISS index + metadata yaz
def save_index_and_metadata(embeddings, metadata, category):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss_path = os.path.join(OUTPUT_DIR, f"faiss_{category}.index")
    meta_path = os.path.join(OUTPUT_DIR, f"metadata_{category}.json")

    faiss.write_index(index, faiss_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ {category.upper()} → {len(embeddings)} adet vektör kaydedildi.")

# 🔁 Tüm kategorileri işle
for category in ["genel", "ozel", "mevzuat"]:
    print(f"\n📂 Kategori işleniyor: {category.upper()}")
    chunks = load_chunks_by_category(BASE_DIR, category)
    if not chunks:
        print(f"⚠️ {category} için veri bulunamadı.")
        continue

    embeddings = vectorize_chunks(chunks)
    save_index_and_metadata(embeddings, chunks, category)