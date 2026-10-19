# -*- coding: utf-8 -*-
"""
数据集样本导出脚本（对应作业 FR-G3：仓库只保留数据集样本）
从全量数据集中抽取各 50 条样本，存入 project_data/samples/，
供 git 仓库保留（全量数据不入库）。
"""
import json
import os
import random

random.seed(42)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PD = os.path.join(BASE, "project_data")
SAMPLES = os.path.join(PD, "samples")
N = 50

os.makedirs(SAMPLES, exist_ok=True)


def export(name, src_name, out_name, picker):
    src = os.path.join(PD, src_name)
    if not os.path.exists(src):
        print(f"[跳过] 未找到 {src}")
        return
    data = json.load(open(src, encoding="utf-8"))
    sample = random.sample(data, min(len(data), N))
    out = os.path.join(SAMPLES, out_name)
    json.dump(sample, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"已导出 {out_name}：{len(sample)} 条样本（源 {len(data)} 条）")


def main():
    # alpaca 样本
    export("alpaca", "alpaca_zh.json", "alpaca_sample_50.json", None)
    # sharegpt 样本
    export("sharegpt", "sharegpt_zh.json", "sharegpt_sample_50.json", None)
    # dpo 样本
    export("dpo", "dpo_data.json", "dpo_sample_50.json", None)
    # 测试集（50题，全量即样本）
    export("testset", "testset.json", "testset_50.json", None)
    print("样本目录：", SAMPLES)


if __name__ == "__main__":
    main()
