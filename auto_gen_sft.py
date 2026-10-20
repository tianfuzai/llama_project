import json
import os
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"
QA_PER_CHUNK = 3

ANGLES = [
    "从办理流程与操作步骤的角度提问",
    "从所需材料与办理条件的角度提问",
    "从办理时限与政策要求的角度提问",
]


def build_prompt(chunk_text, angle):
    prompt = f"""
你是政务领域数据标注专家。根据下面的政务原文，生成1条高质量的问答对。
要求：
1. instruction：{angle}，基于原文内容，不要编造
2. output：使用原文内容简洁准确回答
3. 输出严格是JSON，只有instruction和output两个字段

原文：
{chunk_text}

输出示例：
{{"instruction": "xxx？", "output": "xxx"}}
"""
    return prompt


def call_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    res_json = resp.json()
    return res_json["response"]


def load_existing(out_jsonl):
    seen = set()
    if os.path.exists(out_jsonl):
        with open(out_jsonl, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    if item.get("instruction"):
                        seen.add(item["instruction"].strip())
                except Exception:
                    continue
    return seen


def main():
    chunk_file = "project_data/chunks.txt"
    out_jsonl = "project_data/sft_data.jsonl"

    with open(chunk_file, "r", encoding="utf-8") as f:
        all_content = f.read()
    chunks = [c.strip() for c in all_content.split("=====") if c.strip()]
    print(f"待处理chunk：{len(chunks)}，每块生成 {QA_PER_CHUNK} 条")

    seen = load_existing(out_jsonl)

    total_success = len(seen)
    for idx, text in enumerate(chunks):
        for k in range(QA_PER_CHUNK):
            angle = ANGLES[k % len(ANGLES)]
            try:
                prompt = build_prompt(text, angle)
                raw_ans = call_ollama(prompt)
                qa = json.loads(raw_ans)
                instruction = qa["instruction"].strip()
                output = qa["output"].strip()
                if not instruction or not output:
                    continue
                if instruction in seen:
                    continue
                seen.add(instruction)
                qa_line = {"instruction": instruction, "input": "", "output": output}
                with open(out_jsonl, "a", encoding="utf-8") as fw:
                    json.dump(qa_line, fw, ensure_ascii=False)
                    fw.write("\n")
                total_success += 1
                print(f"累计{total_success}条：{instruction}")
            except Exception as e:
                continue

    print(f"\n完成，累计 {total_success} 条，输出：{out_jsonl}")


if __name__ == "__main__":
    main()
