import json
import random

random.seed(42)

def split():
    all_data = []
    with open("project_data/sft_data.jsonl","r",encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                all_data.append(json.loads(line))
    random.shuffle(all_data)
    # 9:1分割
    split_idx = int(len(all_data)*0.9)
    train = all_data[:split_idx]
    val = all_data[split_idx:]
    def save(path,data):
        with open(path,"w",encoding="utf-8") as fw:
            for item in data:
                json.dump(item,fw,ensure_ascii=False)
                fw.write("\n")
    save("project_data/train.jsonl",train)
    save("project_data/val.jsonl",val)
    print(f"训练集{len(train)}条，验证集{len(val)}条")

if __name__=="__main__":
    split()
