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
        print(f"未找到 alpaca_zh.json")
        return

    with open(SRC, "r", encoding="utf-8") as f:
        data = json.load(f)

    if len(data) < N:
        N_sample = len(data)
    else:
        N_sample = N

    sample = random.sample(data, N_sample)

    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "问题(instruction)", "答案(output)", "与原文一致(是/否)", "答案可用(是/否)", "格式合规(是/否)"])
        for i, item in enumerate(sample, 1):
            writer.writerow([i, item["instruction"], item["output"], "", "", ""])

    print(f"已抽取 {N_sample} 条样本，保存至：{OUT}")


if __name__ == "__main__":
    main()
