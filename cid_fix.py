import os
import re

# CID düzeltici fonksiyon
def fix_cid_errors(text):
    cid_map = {
        'cid:62': 'şt',
        'cid:63': 'me',
        'cid:64': 'er',
        'cid:80': 'ti',
        'cid:82': 'f',
        'cid:85': 'ğ',
        'cid:88': 'lı',
        'cid:89': 'şi',
        'cid:90': 'ik',
        'cid:93': 'tf',
        'cid:94': 'tt',
        'cid:95': 'is',
        'cid:97': 'tf',
        'cid:99': 'tt',
        'cid:101': 'tt',
        'cid:102': 'tf',
        'cid:109': 'ş',
        'cid:110': 'ğ',
    }

    for cid_code, replacement in cid_map.items():
        text = text.replace(f"({cid_code})", replacement)

    text = re.sub(r'\(cid:\d+\)', '', text)  # bilinmeyenleri temizle
    return text

# Dosyaları işleyen ana fonksiyon
def clean_txt_files(input_folder="output_birlesik", output_folder="output_temiz"):
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.endswith(".txt"):
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file)

            with open(input_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            cleaned_text = fix_cid_errors(raw_text)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned_text)

            print(f"✅ {file} temizlenip kaydedildi.")

# Kullanım
if __name__ == "__main__":
    clean_txt_files()
