import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "project_data", "alpaca_zh.json")
OUT = os.path.join(BASE, "project_data", "dpo_data.json")

TARGET = 200


def make_rejected(q, a):
    a = a.strip()
    if len(a) > 30:
        rejected = a[: len(a) // 2].rstrip() + "。"
    else:
        rejected = "我也不太清楚，建议你自己去查一下官网。" + a
    rejected += "（大概是这样吧，我也不是特别确定哦）"
    return rejected


def main():
    if not os.path.exists(SRC):
        print(f"未找到 alpaca_zh.json")
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


if __name__ == "__main__":
    main()
