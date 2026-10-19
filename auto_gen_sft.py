# -*- coding: utf-8 -*-
"""
数据蒸馏脚本（对应作业 FR-A2 / FR-A3）
基于 chunks.txt 的分块文本，调用本地 Ollama 大模型批量抽取 QA 对。

【增强1】每个 chunk 默认生成 3 条 QA，显著扩充样本规模；
【增强2】3 条 QA 从不同角度提问（流程 / 材料 / 时限政策），避免同 chunk 高度重复；
【增强3】启动时加载已有 sft_data.jsonl，增量续写，不丢失已生成样本。

满足作业要求：Alpaca / ShareGPT 各 ≥500 条。
依赖：本机已安装并启动 Ollama，且已拉取 qwen2.5:7b 模型。
"""
import json
import os
import requests

# Ollama 默认本地地址
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"
# 每个 chunk 生成的 QA 条数
QA_PER_CHUNK = 3

# 不同角度的提问要求，减少同 chunk 重复
ANGLES = [
    "从办理流程与操作步骤的角度提问",
    "从所需材料与办理条件的角度提问",
    "从办理时限与政策要求的角度提问",
]


def build_prompt(chunk_text, angle):
    prompt = f"""
你是政务领域数据标注专家。根据下面的政务原文，生成1条高质量的问答对，用于大模型SFT微调。
要求：
1. instruction：{angle}，基于原文内容，不要编造原文不存在的信息
2. output：使用原文内容简洁准确回答，不要额外编造
3. 输出严格是JSON，只有instruction和output两个字段，不要多余解释、markdown。

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
    """加载已有样本的 instruction 作为去重基线，实现增量续写。"""
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
    print(f"待处理chunk总数：{len(chunks)}，每块生成 {QA_PER_CHUNK} 条（不同角度）")

    seen = load_existing(out_jsonl)
    print(f"已加载已有样本 {len(seen)} 条作为去重基线（增量续写）")

    total_success = len(seen)
    for idx, text in enumerate(chunks):
        for k in range(QA_PER_CHUNK):
            angle = ANGLES[k % len(ANGLES)]
            print(f"\n==== 第{idx+1}/{len(chunks)}块，角度[{k+1}] {angle[:12]}... ====")
            try:
                prompt = build_prompt(text, angle)
                raw_ans = call_ollama(prompt)
                qa = json.loads(raw_ans)
                instruction = qa["instruction"].strip()
                output = qa["output"].strip()
                if not instruction or not output:
                    continue
                if instruction in seen:
                    print("⚠ 与已生成问题重复，跳过")
                    continue
                seen.add(instruction)
                qa_line = {"instruction": instruction, "input": "", "output": output}
                with open(out_jsonl, "a", encoding="utf-8") as fw:
                    json.dump(qa_line, fw, ensure_ascii=False)
                    fw.write("\n")
                total_success += 1
                print(f"✅ 生成成功(累计{total_success}条)：{instruction}")
            except Exception as e:
                print(f"❌ 生成失败，跳过，错误：{str(e)}")
                continue

    print(f"\n全部任务结束！累计 {total_success} 条，输出文件：{out_jsonl}")
    if total_success >= 500:
        print("✔ 样本量充足，运行 scripts/clean_sft_data.py 清洗后即可达到 ≥500 条。")


if __name__ == "__main__":
    main()
