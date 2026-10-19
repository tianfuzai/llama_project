# -*- coding: utf-8 -*-
"""
人工抽检脚本（对应作业 FR-A4）
从 alpaca_zh.json 中随机抽取 50 条，生成抽检表 CSV（带空列，供人工标注）。
人工逐条对照原文，填写：
  与原文一致(是/否)、答案可用(是/否)、格式合规(是/否)
最后统计三个指标的一致率。
"""
import json
import os
import random
import csv

random.seed(42)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "project_data", "alpaca_zh.json")
OUT = os.path.join(BASE, "project_data", "sample_check_50.csv")

N = 50


def main():
    if not os.path.exists(SRC):
        print(f"[错误] 未找到 alpaca_zh.json，请先运行 scripts/clean_sft_data.py")
        return

    with open(SRC, "r", encoding="utf-8") as f:
        data = json.load(f)

    if len(data) < N:
        print(f"[警告] 数据集仅 {len(data)} 条，不足50条，将抽取全部样本。")
        N_sample = len(data)
    else:
        N_sample = N

    sample = random.sample(data, N_sample)

    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "问题(instruction)", "答案(output)", "与原文一致(是/否)", "答案可用(是/否)", "格式合规(是/否)"])
        for i, item in enumerate(sample, 1):
            writer.writerow([i, item["instruction"], item["output"], "", "", ""])

    print(f"已随机抽取 {N_sample} 条样本，抽检表保存至：{OUT}")
    print("请人工打开 CSV，逐条对照山西政务原文填写三个判定列，再手工统计一致率（目标≥90%）。")


if __name__ == "__main__":
    main()
