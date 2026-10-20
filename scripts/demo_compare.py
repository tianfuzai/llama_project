# -*- coding: utf-8 -*-
"""
答辩现场演示：基座模型 vs 微调后模型 对比
用法：python scripts/demo_compare.py
"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
LORA_PATH = "./saves/sft_exp1"  # 微调后的LoRA权重

# 山西政务问题（现场演示用）
DEMO_QUESTIONS = [
    "山西省政务服务网的网址是什么？",
    "如何在山西省办理居住证？",
    "山西省医疗保险异地就医怎么备案？",
    "山西省大学生创业补贴申请条件是什么？",
]

def chat(model, tokenizer, question, max_new_tokens=200):
    messages = [
        {"role": "system", "content": "你是山西省政务服务智能助手，专注回答山西省政务相关问题。"},
        {"role": "user", "content": question}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
        )
    response = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(response, skip_special_tokens=True)

def main():
    print("=" * 60)
    print("  山西政务小模型微调演示")
    print("=" * 60)

    # 加载基座模型
    print("\n[1/3] 加载基座模型...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    # 加载微调后模型
    print("[2/3] 加载微调后 LoRA 模型...")
    finetuned_model = PeftModel.from_pretrained(base_model, LORA_PATH)

    print("[3/3] 开始对比演示\n")

    for i, q in enumerate(DEMO_QUESTIONS, 1):
        print("=" * 60)
        print(f"问题 {i}: {q}")
        print("-" * 60)
        print("【基座模型回答】")
        base_ans = chat(base_model, tokenizer, q)
        print(base_ans[:300])
        print("-" * 60)
        print("【微调后模型回答】")
        ft_ans = chat(finetuned_model, tokenizer, q)
        print(ft_ans[:300])
        print()

    print("=" * 60)
    print("  演示结束")
    print("=" * 60)

if __name__ == "__main__":
    main()
