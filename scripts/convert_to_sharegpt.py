import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "project_data", "alpaca_zh.json")
OUT = os.path.join(BASE, "project_data", "sharegpt_zh.json")


def main():
    if not os.path.exists(SRC):
        print(f"未找到 alpaca_zh.json")
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


if __name__ == "__main__":
    main()
