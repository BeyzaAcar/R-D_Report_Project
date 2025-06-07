📘 R&D Report Processing Pipeline
This project provides a complete pipeline for extracting, cleaning, chunking, embedding, searching, and expanding text from R&D Center reports (PDF format). The system is designed to work modularly and supports multi-question semantic retrieval over categorized document chunks.

📂 Folder Structure

workspace/
└── <report_id>/                  # Unique folder per uploaded report
    ├── raw_txt/                  # Raw text extracted from PDF
    ├── clean_txt/                # Text after CID cleaning
    ├── chunks/                   # Chunked sentences (by category)
    │   ├── genel/
    │   ├── ozel/
    │   └── mevzuat/
    ├── faiss/                    # FAISS index + metadata
    │   ├── faiss_genel.index
    │   ├── metadata_genel.json
    │   └── metadata_soru_yordam.json
    ├── top10/                    # Top-10 chunks per question
    │   ├── genel/
    │   ├── ozel/
    │   └── mevzuat/
    └── expanded/                # Expanded chunks with original context
        ├── genel/
        ├── ozel/
        └── mevzuat/
🧩 Module Overview
1. pdf_to_txt.py
Purpose: Converts a single PDF file to plain UTF-8 text using pdfplumber.

Input: user_uploads/report.pdf

Output: workspace/<report_id>/raw_txt/<report_id>.txt

2. cid_cleaner.py
Purpose: Replaces problematic (cid:NN) character encodings with correct characters based on a predefined CID mapping.

Input: Raw .txt file

Output: Cleaned .txt file inside clean_txt/

3. chunk_creator.py
Purpose: Splits the cleaned text into overlapping sentence chunks by category.

Categories:

genel (general): 5-sentence chunks, 3 overlap

ozel (special): 2-sentence chunks, 1 overlap

mevzuat (regulatory): 6-sentence chunks, 4 overlap

Output: JSON chunks with metadata stored under chunks/<category>/

4. faiss_creator.py
Purpose: Embeds all chunks using multilingual-e5-large and creates FAISS indexes per category.

Output: faiss_<category>.index and corresponding metadata JSONs

5. top10_retriever.py
Purpose: Finds the top 10 most relevant chunks for each question across each dataset.

Input: A question list (metadata_soru_yordam.json)

Output: One soru{ID}_top10.json per dataset (in top10/<category>/)

6. expand_top10_chunks.py
Purpose: Expands each top-10 chunk by locating it in the original report and including ±N characters of surrounding context.

7. soru_yordam_embedder.py  
Purpose: Default `QUESTIONS/default_questions_and_yordams.txt` dosyasını okuyup, soru + yordam çiftlerini gömmer ve FAISS indeksine ekler.  
Output: `workspace/<report_id>/faiss/metadata_soru_yordam.json`

8. run_pipeline.pyPurpose: Main orchestrator script. Runs the entire pipeline end-to-end from PDF to final GPT-ready prompt.
Usage:
"python run_pipeline.py <report_id> <pdf_path> <question_id>"

Example:
python run_pipeline.py rapor2023 uploads/rapor2023.pdf 3

THIS RUN THE FOLLOWING:

1. Initializes workspace folder structure
2. Extracts text from the given PDF
3. Cleans CID characters
4. Creates chunks (genel, ozel, mevzuat)
5. Embeds chunks using SentenceTransformer
6. Embeds default questions and yordams
7. Searches for top-10 chunks for each question
8. Expands retrieved chunks for context
9. Generates GPT prompt for specified question

Expansion size per category:

genel: ±750

mevzuat: ±500

ozel: ±300

Output: Same structure as top10/, stored in expanded/<category>/

⚙️ Workflow Summary
User uploads a PDF

pdf_to_txt.py → Extract raw text

cid_cleaner.py → Clean formatting/CID codes

chunk_creator.py → Create sentence chunks by category

faiss_creator.py → Build FAISS indexes

soru_yordam_embedder.py → Vectorize questions + yordams

top10_retriever.py → Find top-10 chunks per question

expand_top10_chunks.py → Expand those chunks for richer context

(Optional) Send expanded chunks to GPT API for answer generation.

🧠 Model Used (SentenceTransformer modeli parametre ile verilir.  )
intfloat/multilingual-e5-large: used for both chunk embedding and query embedding.

Sentence embeddings are L2-normalized and FAISS uses IndexFlatIP (cosine similarity).

✅ Notes
The system is modular. Each script can be run independently or integrated into an automated backend.

It supports multi-report processing by isolating outputs under workspace/<report_id>/.