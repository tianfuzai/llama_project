# -*- coding: utf-8 -*-
"""
ShareGPT 格式数据集生成脚本（对应作业 FR-A3）
读取清洗后的 alpaca_zh.json，转换为 ShareGPT messages 多轮对话格式，
产出 project_data/sharegpt_zh.json（≥500条）。

ShareGPT 格式（LLaMA-Factory 兼容）：
[{"messages": [{"role":"user","content":"问题"},{"role":"assistant","content":"回答"}]}]
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "project_data", "alpaca_zh.json")
OUT = os.path.join(BASE, "project_data", "sharegpt_zh.json")


def main():
    if not os.path.exists(SRC):
        print(f"[错误] 未找到 alpaca_zh.json，请先运行 scripts/clean_sft_data.py")
        return

    with open(SRC, "r", encoding="utf-8") as f:
        alpaca_data = json.load(f)

    sharegpt = []
    for item in alpaca_data:
        q = item.get("instruction", "").strip()
        a = item.get("output", "").strip()
        if not q or not a:
            continue
        sharegpt.append({
            "messages": [
                {"role": "user", "content": q},
                {"role": "assistant", "content": a},
            ]
        })

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(sharegpt, f, ensure_ascii=False, indent=2)

    print(f"ShareGPT 格式数据集：{len(sharegpt)} 条")
    print(f"保存至：{OUT}")
    if len(sharegpt) >= 500:
        print("✔ 满足作业要求（≥500条）")
    else:
        print(f"⚠ 仅 {len(sharegpt)} 条，不足500条，建议扩充原始数据后重新蒸馏。")


if __name__ == "__main__":
    main()
