import fitz  # PyMuPDF
import os

def convert_all_pdfs_in_folder(pdf_folder, output_base="output"):
    # Klasör var mı kontrolü
    if not os.path.exists(pdf_folder):
        print("PDF klasörü bulunamadı:", pdf_folder)
        return

    # Klasördeki tüm .pdf dosyalarını bul
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

    if not pdf_files:
        print("Hiç PDF bulunamadı.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]  # uzantısız isim
        output_dir = os.path.join(output_base, pdf_name)
        os.makedirs(output_dir, exist_ok=True)

        print(f"📄 {pdf_file} işleniyor...")

        try:
            pdf = fitz.open(pdf_path)

            for page_num in range(len(pdf)):
                page = pdf.load_page(page_num)
                text = page.get_text()

                output_file = os.path.join(output_dir, f"page_{page_num + 1}.txt")

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text)

            pdf.close()
            print(f"✅ {pdf_name} tamamlandı, çıktı klasörü: {output_dir}\n")

        except Exception as e:
            print(f"⚠️ {pdf_file} işlenirken hata oluştu: {e}")

# Örnek kullanım
if __name__ == "__main__":
    pdf_klasoru = "pdf_klasoru"  # PDF'leri koyduğun klasör
    convert_all_pdfs_in_folder(pdf_klasoru)
