import os
import re
import json
from tqdm import tqdm

# CHUNK AYARLARI
CHUNK_CONFIG = {
    "genel": {"size": 5, "overlap": 3},
    "ozel": {"size": 2, "overlap": 1},
    "mevzuat": {"size": 6, "overlap": 4}
}

# BAŞLIK KONTROL DESENİ (ör: 1.2, 2.1.3)
HEADER_PATTERN = re.compile(r"^\d+(\.\d+)*(\s+|$)")

def smart_sentence_split(text):
    text = text.replace('\n', ' ')

    # Sayılardaki noktaları koru
    text = re.sub(r'(?<=\d)\.(?=\d)', '__DOT__', text)

    # Kısaltmalardaki noktaları koru (ör: vb., vs.)
    text = re.sub(r'\b([A-Za-zÇĞİÖŞÜçğıöşü]{1,4})\.', r'\1__DOT__', text)

    # Cümleleri böl
    raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ])', text)

    # Başlıkları tek cümle olarak alma
    cleaned = []
    for s in raw_sentences:
        s = s.replace('__DOT__', '.').strip()
        if HEADER_PATTERN.match(s) and len(s.split()) <= 10:
            cleaned.append(s)  # başlık
        elif len(s) > 10:
            cleaned.append(s)
    return cleaned

def chunk_sentences(sentences, size, overlap):
    chunks = []
    for i in range(0, len(sentences), size - overlap):
        chunk = sentences[i:i + size]
        if chunk:
            chunks.append(chunk)
    return chunks

def create_chunks_from_birlesik_txts(input_folder="output_temiz", output_folder="chunks_birlesik"):
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if not file.endswith(".txt"):
            continue

        file_path = os.path.join(input_folder, file)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        sentences = smart_sentence_split(text)
        base_name = os.path.splitext(file)[0]

        for category, config in CHUNK_CONFIG.items():
            category_folder = os.path.join(output_folder, base_name, category)
            os.makedirs(category_folder, exist_ok=True)

            chunks = chunk_sentences(sentences, config["size"], config["overlap"])

            for i, chunk in enumerate(chunks):
                chunk_text = " ".join(chunk)
                metadata = {
                    "source_file": file,
                    "category": category,
                    "chunk_index": i + 1,
                    "chunk_text": chunk_text,
                    "char_len": len(chunk_text),
                    "sentence_count": len(chunk)
                }

                chunk_path = os.path.join(category_folder, f"{category}_chunk_{i+1}.json")
                with open(chunk_path, "w", encoding="utf-8") as out_file:
                    json.dump(metadata, out_file, ensure_ascii=False, indent=2)

        print(f"✅ {file} için chunk ve metadata üretildi.")

if __name__ == "__main__":
    create_chunks_from_birlesik_txts()
