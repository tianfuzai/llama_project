import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "project_data", "sft_data.jsonl")
OUT_ALPACA = os.path.join(BASE, "project_data", "alpaca_zh.json")
OUT_REPORT = os.path.join(BASE, "project_data", "clean_report.txt")


def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    table = {ord(c): ord(cc) for c, cc in zip("，。：；！？（）【】“”‘’、", ",.:;!?()[]\"\"''、")}
    s = s.translate(table)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def main():
    if not os.path.exists(SRC):
        print(f"未找到源文件：{SRC}")
        return

    raw_items = []
    with open(SRC, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw_items.append(json.loads(line))
            except Exception:
                pass

    raw_count = len(raw_items)
    dup_count = 0
    empty_count = 0
    short_count = 0
    long_count = 0
    seen = set()
    cleaned = []

    for item in raw_items:
        instruction = normalize_text(item.get("instruction", ""))
        output = normalize_text(item.get("output", ""))
        input_ = item.get("input", "")

        if not instruction or not output:
            empty_count += 1
            continue

        if len(output) < 10:
            short_count += 1
            continue
        if len(output) > 800:
            long_count += 1
            continue

        key = (instruction, output)
        if key in seen:
            dup_count += 1
            continue
        seen.add(key)

        cleaned.append({
            "instruction": instruction,
            "input": input_ if isinstance(input_, str) else "",
            "output": output,
        })

    cleaned_count = len(cleaned)

    with open(OUT_ALPACA, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    lines = [
        "========== 数据清洗统计报告 ==========",
        f"源文件：{SRC}",
        f"清洗前样本数：{raw_count}",
        f"清洗后样本数：{cleaned_count}",
        f"删除样本总数：{raw_count - cleaned_count}",
        f"  其中 - 重复样本：{dup_count}",
        f"  其中 - 空内容样本：{empty_count}",
        f"  其中 - 答案过短(<10字)：{short_count}",
        f"  其中 - 答案过长(>800字)：{long_count}",
        "",
        "输出文件：",
        f"  Alpaca格式数据集：{OUT_ALPACA}",
        "",
    ]
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))


if __name__ == "__main__":
    main()
