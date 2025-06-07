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

import os, sys, argparse
from pathlib import Path
from dotenv import load_dotenv

# 1) Ortam değişkenlerini yükle
load_dotenv()
ROOT       = Path(os.getenv("WORKSPACE_ROOT", "workspace"))
REPORT_ID  = os.getenv("REPORT_ID", "demo")
ws         = ROOT / REPORT_ID               # workspace/rapor123

# 2) Proje modüllerini içe aktar
import init_workspace, pdf_to_text, cid_cleaner
import chunk_creator, faiss_creator, search_faiss_top_chunks
import expand_top10_chunks, gpt_amacalismiyor

def main(pdf_path:str, question_id:int):
    # A. klasörleri aç
    init_workspace.prepare_workspace(ws)      # fonksiyon isimleri örnek
    
    # B. PDF -> RAW TEXT
    raw_txt = pdf_to_text.convert(pdf_path, ws)
    
    # C. CID temizle
    clean_txt = cid_cleaner.clean(raw_txt, ws)
    
    # D. Chunk’la & metadata
    chunk_creator.make_chunks(clean_txt, ws)
    
    # E. FAISS
    faiss_creator.build_indexes(ws)
    
    # F. Soru sor – top-k chunk
    search_faiss_top_chunks.ask_all(ws)
    
    # G. Chunk genişlet
    expand_top10_chunks.expand(ws)
    
    # H. GPT ile nihai cevap
    answer = gpt_amacalismiyor.answer(question_id, ws)
    print("\n---- FINAL ANSWER ----\n", answer)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf",        help="path/to/report.pdf")
    ap.add_argument("questionid", help="metadata_soru_yordam içindeki sıra", type=int)
    args = ap.parse_args()
    main(args.pdf, args.questionid)
