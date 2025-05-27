'''
This code snippet is designed to convert PDF files into text files using the pdfplumber library. It reads each PDF file in a specified folder, extracts the text from each page, and saves the combined text into a new text file in an output folder. The code handles errors gracefully and provides feedback on the processing status of each PDF file.
'''


import os
import pdfplumber

def convert_pdfs_with_pdfplumber(pdf_folder, output_folder="output_birlesik"):
    if not os.path.exists(pdf_folder):
        print("❌ PDF klasörü bulunamadı:", pdf_folder)
        return

    os.makedirs(output_folder, exist_ok=True)

    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("❌ PDF bulunamadı.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]
        output_path = os.path.join(output_folder, f"{pdf_name}.txt")

        print(f"📄 {pdf_file} işleniyor...")

        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            print(f"✅ {pdf_name} yazıldı -> {output_path}")

        except Exception as e:
            print(f"⚠️ HATA ({pdf_file}): {e}")

# Örnek kullanım
if __name__ == "__main__":
    pdf_klasoru = "pdf_klasoru"  # PDF dosyalarının bulunduğu klasör
    convert_pdfs_with_pdfplumber(pdf_klasoru)



'''
this code converts pdf files to text files using pdfplumber library.
it reads each page of the pdf and extracts the text, then saves it to a text file.
'''