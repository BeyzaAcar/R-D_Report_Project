import os
import re

def extract_cids_per_file(input_folder="output_birlesik", output_folder="cid_cumleleri"):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(input_folder, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().replace('\n', ' ')
            sentences = re.split(r'(?<=[.!?])\s+', text)

        seen_cids = set()
        found = {}

        for sentence in sentences:
            cids_in_sentence = re.findall(r'\(cid:\d+\)', sentence)
            for cid in cids_in_sentence:
                if cid not in seen_cids:
                    seen_cids.add(cid)
                    found[cid] = sentence.strip()

        output_name = os.path.splitext(filename)[0] + "_cid.txt"
        output_path = os.path.join(output_folder, output_name)

        with open(output_path, "w", encoding="utf-8") as out:
            for cid in sorted(found.keys(), key=lambda x: int(re.findall(r'\d+', x)[0])):
                out.write(f"{cid} -> {found[cid]}\n")

        print(f"✅ {filename} için {len(found)} CID bulundu → {output_name}")

# Kullanım
if __name__ == "__main__":
    extract_cids_per_file()
