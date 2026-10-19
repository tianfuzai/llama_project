# -*- coding: utf-8 -*-
"""
DPO 偏好配对数据集构造脚本（对应作业 FR-D1 / FR-D2）

说明（数据来源，写进偏好对齐说明文档）：
1. 同一 prompt 下，原始蒸馏得到的 output 作为优质回答（chosen）；
2. 通过"劣化规则"程序化生成一个较差回答（rejected）：例如删除关键信息、
   缩短答案、加入口语化冗余，确保 rejected 明显劣于 chosen；
3. 构造消息为 ShareGPT messages 格式：
   {"messages":[{"role":"user","content":"问题"}],
    "chosen":{"role":"assistant","content":"优质回答"},
    "rejected":{"role":"assistant","content":"较差回答"}}

输出：project_data/dpo_data.json（目标 ≥200 组）
"""
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "project_data", "alpaca_zh.json")
OUT = os.path.join(BASE, "project_data", "dpo_data.json")

TARGET = 200


def make_rejected(q, a):
    """程序化生成一个明显较差的回答，供 rejected 使用。"""
    a = a.strip()
    # 若答案较长，截断前半段，丢失关键信息
    if len(a) > 30:
        rejected = a[: len(a) // 2].rstrip() + "。"
    else:
        rejected = "我也不太清楚，建议你自己去查一下官网。" + a
    # 人为加入口语化、不规范的尾巴
    rejected += "（大概是这样吧，我也不是特别确定哦）"
    return rejected


def main():
    if not os.path.exists(SRC):
        print(f"[错误] 未找到 alpaca_zh.json，请先运行 scripts/clean_sft_data.py")
        return

    with open(SRC, "r", encoding="utf-8") as f:
        data = json.load(f)

    dpo_list = []
    for item in data:
        q = (item.get("instruction") or "").strip()
        a = (item.get("output") or "").strip()
        if not q or not a:
            continue
        rejected = make_rejected(q, a)
        # chosen 与 rejected 不得完全一致
        if rejected == a:
            continue
        dpo_list.append({
            "messages": [{"role": "user", "content": q}],
            "chosen": {"role": "assistant", "content": a},
            "rejected": {"role": "assistant", "content": rejected},
        })
        if len(dpo_list) >= TARGET:
            break

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(dpo_list, f, ensure_ascii=False, indent=2)

    print(f"DPO 偏好配对数据：{len(dpo_list)} 组")
    print(f"保存至：{OUT}")
    if len(dpo_list) >= TARGET:
        print("✔ 满足作业要求（≥200组）")
    else:
        print(f"⚠ 仅 {len(dpo_list)} 组，不足200组，建议扩充数据后重新构造。")


if __name__ == "__main__":
    main()
