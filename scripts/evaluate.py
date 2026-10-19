# -*- coding: utf-8 -*-
"""
效果评估脚本（对应作业 FR-F2 / FR-F3 / FR-F4）
对 基座模型 / SFT-LoRA模型 / DPO模型 在 50 题测试集上分别生成回答，
并输出：
  - 三方回答结果文件 evaluation_results.json
  - 人工打分表 evaluation_manual.csv（准确性/专业性/格式规范性三列待填）
  - 大模型打分提示词模板 evaluation_llm_prompt.txt

说明：
  1. 运行本脚本需要本机已具备三个模型的权重（SFT、DPO 已训练产出）；
  2. 人工打分：打开 evaluation_manual.csv 人工填分；
  3. 大模型打分：使用 evaluation_llm_prompt.txt 中的提示词调用强模型打分。
"""
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
        print(f"[错误] 未找到测试集，请先运行 scripts/build_testset.py")
        return

    with open(TESTSET, "r", encoding="utf-8") as f:
        testset = json.load(f)

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import torch

    print("▶ 加载基座模型...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True)

    print("▶ 加载 SFT-LoRA 模型（saves/sft_exp1）...")
    sft_model = PeftModel.from_pretrained(base_model, os.path.join(BASE, "saves", "sft_exp1"))

    print("▶ 加载 DPO 模型（saves/dpo）...")
    if os.path.exists(os.path.join(BASE, "saves", "dpo")):
        dpo_model = PeftModel.from_pretrained(base_model, os.path.join(BASE, "saves", "dpo"))
    else:
        print("⚠ 未找到 DPO 权重 saves/dpo，跳过 DPO 模型评估。")
        dpo_model = None

    results = []
    for i, item in enumerate(testset, 1):
        q = item["question"]
        print(f"▶ 评估第 {i}/{len(testset)} 题：{q[:20]}...")
        results.append({
            "question": q,
            "reference": item["answer"],
            "base": generate_answer(base_model, tokenizer, q),
            "sft": generate_answer(sft_model, tokenizer, q),
            "dpo": generate_answer(dpo_model, tokenizer, q) if dpo_model else "",
        })

    with open(OUT_RESULTS, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 生成人工打分表
    with open(OUT_MANUAL, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["题号", "问题", "参考答案要点", "基座-准确性", "基座-专业性", "基座-格式",
                         "SFT-准确性", "SFT-专业性", "SFT-格式", "DPO-准确性", "DPO-专业性", "DPO-格式"])
        for i, r in enumerate(results, 1):
            writer.writerow([i, r["question"], r["reference"], "", "", "", "", "", "", "", "", ""])

    # 生成大模型打分提示词模板
    prompt = (
        "你是一名政务问答评估专家。请对下面三个模型对同一问题的回答打分。\n"
        "评分维度：准确性(1-5)、专业性(1-5)、格式规范性(1-5)。\n"
        "输出JSON：{\"base\":{...},\"sft\":{...},\"dpo\":{...}, \"reason\":\"简要理由\"}\n\n"
        f"问题：{testset[0]['question']}\n"
        "基座回答：...\nSFT回答：...\nDPO回答：...\n"
    )
    with open(OUT_PROMPT, "w", encoding="utf-8") as f:
        f.write(prompt)

    print("\n✔ 评估结果已生成：")
    print(f"  三方回答：{OUT_RESULTS}")
    print(f"  人工打分表：{OUT_MANUAL}")
    print(f"  大模型打分提示词：{OUT_PROMPT}")
    print("\n后续步骤：人工填分 + 大模型打分后，汇总三方对比表并给出结论。")


if __name__ == "__main__":
    main()
