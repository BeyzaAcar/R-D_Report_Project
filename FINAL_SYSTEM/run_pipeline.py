'''
Bu script, PDF raporunu işleyerek nihai cevap üretir.
Raporu adım adım işler:
1. PDF'den metin çıkarır.
2. CID temizler.
3. Metni cümle cümle chunk'lar.
4. Chunk'ları FAISS ile indeksler.
5. Soruya göre top-k chunk'ları bulur.
#     out_dir = os.path.join(workspace_dir, "chunks")
6. Top-k chunk'ları genişletir.
7. GPT ile nihai cevap oluşturur.
8. Sonucu ekrana yazdırır.
#         raw_text = f.read()
'''

import os, argparse
from pathlib import Path
from dotenv import load_dotenv; load_dotenv() # .env dosyasını yükledik burada

# burada .env dosyasından değişkenleri okuyoruz mesela root degiskenine env dosyasından gelen WORKSPACE_ROOT değerini atıyoruz
ROOT        = Path(os.getenv("WORKSPACE_ROOT", "workspace")) # eger .env yoksa varsayılan "workspace"
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2") # varsayılan model
TOPK       = int(os.getenv("TOPK", 10)) # varsayılan top-k sayısı


# ---- modüller ----
import init_workspace, pdf_to_text, cid_cleaner
import chunk_creator, faiss_creator, soru_yordam_embedder
import search_faiss_top_chunks, expand_top10_chunks
import gpt_amacalismiyor       # hâlâ “stub” durumda

def main(pdf_path: str, question_id: int):
    print("BASLİYORUMMMMM")

    
    print(f"📄 PDF: {pdf_path}")
    # 1) Workspace
    init_workspace.init_workspace(ws)

    # 1.5) Soruları FAISS'e embedle
    txt_path = "QUESTIONS/default_questions_and_yordams.txt"
    soru_yordam_embedder.vectorize_soru_yordam(txt_path, str(ws), EMBED_MODEL)

    print(f"📂 Workspace: {ws}")
    # 2) OCR / PDF to text
    raw_txt = pdf_to_text.pdf_to_txt(pdf_path, ws)

    print(f"📄 Raw text extracted: {len(raw_txt)} characters")
    # 3) CID temizle
    clean_txt = cid_cleaner.clean_txt(raw_txt, ws)

    print(f"📄 Cleaned text: {len(clean_txt)} characters")
    # 4) Chunk
    chunk_creator.create_chunks(clean_txt, ws)

    print(f"📂 Chunks created: {len(os.listdir(ws / 'chunks'))} files")
    # 5) FAISS
    faiss_creator.create_faiss_for_chunks(ws, model_name=EMBED_MODEL)

    print("🔍 FAISS index created")
    # 6) Top-k
    search_faiss_top_chunks.ask_all(ws, top_k=TOPK, model_name=EMBED_MODEL)

    print(f"🔟 Top-10 chunks found for question ID {question_id}")
    # 7) Genişlet
    expand_top10_chunks.expand_chunk(ws)

    print("📈 Expanded top-10 chunks saved")
    # 8) LLM cevap (placeholder)
    answer = gpt_amacalismiyor.generate_prompt(question_id, ws)
    print("\n🟢 FINAL ANSWER\n", answer)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("report_id", help="Örn: rapor2023")
    ap.add_argument("pdf", help="PDF dosyasının yolu")
    ap.add_argument("qid", type=int, help="Soru ID’si (örn: 1)")
    args = ap.parse_args()

    REPORT_ID = args.report_id
    ws = ROOT / REPORT_ID
    main(args.pdf, args.qid)
