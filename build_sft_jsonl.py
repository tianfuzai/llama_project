def clean_text(text: str) -> str:
    lines = text.splitlines()
    new_lines = []
    # 只要一行包含下面任意关键词，直接丢弃这一行
    garbage_words = ["晋ICP备", "网站标识码", "晋公网安备", "Chrome、360", "主办单位：山西省行政审批服务局"]
    for line in lines:
        line_stripped = line.strip()
        skip = False
        for w in garbage_words:
            if w in line_stripped:
                skip = True
                break
        if not skip:
            new_lines.append(line_stripped)
    # 合并，去掉空行
    res = "\n".join([x for x in new_lines if len(x) > 6])
    return res


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

    print(f"生成chunk数量：{len(chunk_list)}")

    with open(out_chunk_path, "w", encoding="utf-8") as fw:
        for ck in chunk_list:
            fw.write(ck + "\n=====\n")
    print(f"chunk保存至 {out_chunk_path}")
