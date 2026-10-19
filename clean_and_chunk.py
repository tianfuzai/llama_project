import re

def clean_text(text: str) -> str:
    # 去除多空白、多余换行
    text = re.sub(r"\s+", "\n", text)
    lines = []
    for line in text.splitlines():
        line = line.strip()
        # 过滤太短的垃圾行
        if len(line) > 6:
            lines.append(line)
    return "\n".join(lines)

def split_chunk(text: str, chunk_size=512, overlap=64):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

if __name__ == "__main__":
    raw_path = "project_data/raw_docs/all_raw_text.txt"
    out_chunk_path = "project_data/chunks.txt"

    with open(raw_path, "r", encoding="utf-8") as f:
        raw = f.read()

    clean = clean_text(raw)
    chunk_list = split_chunk(clean, chunk_size=512, overlap=64)
    print(f"生成文本块数量：{len(chunk_list)}")

    with open(out_chunk_path, "w", encoding="utf-8") as fw:
        for ck in chunk_list:
            fw.write(ck + "\n=====\n")
    print(f"分块结果保存至 {out_chunk_path}")
