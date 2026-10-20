import os
import sys
import json
import csv

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTSET = os.path.join(BASE, "project_data", "testset.json")
OUT_RESULTS = os.path.join(BASE, "project_data", "evaluation_results.json")
OUT_MANUAL = os.path.join(BASE, "project_data", "evaluation_manual.csv")
OUT_PROMPT = os.path.join(BASE, "project_data", "evaluation_llm_prompt.txt")

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


def generate_answer(model, tokenizer, question):
    messages = [{"role": "user", "content": question}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    out = model.generate(**inputs, max_new_tokens=128, do_sample=False)
    return tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)


def main():
    if not os.path.exists(TESTSET):
        print(f"未找到测试集")
        return

    with open(TESTSET, "r", encoding="utf-8") as f:
        testset = json.load(f)

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import torch

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True)

    sft_model = PeftModel.from_pretrained(base_model, os.path.join(BASE, "saves", "sft_exp1"))

    if os.path.exists(os.path.join(BASE, "saves", "dpo")):
        dpo_model = PeftModel.from_pretrained(base_model, os.path.join(BASE, "saves", "dpo"))
    else:
        dpo_model = None

    results = []
    for i, item in enumerate(testset, 1):
        q = item["question"]
        results.append({
            "question": q,
            "reference": item["answer"],
            "base": generate_answer(base_model, tokenizer, q),
            "sft": generate_answer(sft_model, tokenizer, q),
            "dpo": generate_answer(dpo_model, tokenizer, q) if dpo_model else "",
        })

    with open(OUT_RESULTS, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with open(OUT_MANUAL, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["题号", "问题", "参考答案要点", "基座-准确性", "基座-专业性", "基座-格式",
                         "SFT-准确性", "SFT-专业性", "SFT-格式", "DPO-准确性", "DPO-专业性", "DPO-格式"])
        for i, r in enumerate(results, 1):
            writer.writerow([i, r["question"], r["reference"], "", "", "", "", "", "", "", "", ""])

    prompt = (
        "你是一名政务问答评估专家。请对下面三个模型对同一问题的回答打分。\n"
        "评分维度：准确性(1-5)、专业性(1-5)、格式规范性(1-5)。\n"
        "输出JSON：{\"base\":{...},\"sft\":{...},\"dpo\":{...}, \"reason\":\"简要理由\"}\n\n"
        f"问题：{testset[0]['question']}\n"
        "基座回答：...\nSFT回答：...\nDPO回答：...\n"
    )
    with open(OUT_PROMPT, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"评估结果：{OUT_RESULTS}")
    print(f"人工打分表：{OUT_MANUAL}")


if __name__ == "__main__":
    main()
