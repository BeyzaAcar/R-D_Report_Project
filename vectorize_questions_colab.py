'''
This code snippet is designed to vectorize questions and their corresponding aids (yordam) from a text file using the SentenceTransformer model. It reads the text file, processes the content to extract questions and aids, generates embeddings for each entry, and saves the embeddings in a FAISS index along with metadata in a JSON file. The output is stored in a specified directory on Google Drive.
'''


import re, os, json
import numpy as np
from tqdm import tqdm
import faiss
from sentence_transformers import SentenceTransformer

# 🔧 Model
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 📁 Yol tanımları
txt_path = "/content/drive/MyDrive/rd_project/soru_yordam_listesi.txt"

# ✅ Google Drive üzerine yazılacak dizin
BASE_DIR = "/content/drive/MyDrive/rd_project"
output_dir = os.path.join(BASE_DIR, "faiss_outputs")
os.makedirs(output_dir, exist_ok=True)

# 📄 SORU + YORDAM'ları oku
with open(txt_path, "r", encoding="utf-8") as f:
    content = f.read()

# 🔍 Bloklara ayır
blocks = content.strip().split("-" * 30)

# 📦 Hazırlık
entries = []

for block in blocks:
    block = block.strip()
    if not block:
        continue

    match = re.search(r"SORU\s+(\d+):\s*(.*?)\nYORDAM\s+\1:\s*(.*)", block, re.DOTALL)
    if match:
        idx, soru, yordam = match.groups()
        soru = soru.strip().replace("\n", " ")
        yordam = yordam.strip().replace("\n", " ")

        # Boşsa sadece soruyu al
        combined_text = f"SORU: {soru}" if "[Boş]" in yordam else f"SORU: {soru}\nYORDAM: {yordam}"

        entries.append({
            "id": int(idx),
            "soru": soru,
            "yordam": yordam if "[Boş]" not in yordam else "",
            "text": combined_text.strip()
        })

print(f"🔎 Toplam {len(entries)} soru-yordam çifti bulundu.")

# 🧠 Embedding üret
texts = [entry["text"] for entry in entries]
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# 💾 FAISS index oluştur
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# 📤 Kaydet
faiss.write_index(index, os.path.join(output_dir, "faiss_soru_yordam.index"))
with open(os.path.join(output_dir, "metadata_soru_yordam.json"), "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"✅ FAISS ve metadata başarıyla Google Drive'a yazıldı → {output_dir}")
