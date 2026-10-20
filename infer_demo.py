# -*- coding: utf-8 -*-
"""
微调后模型推理演示 - 明天答辩用
"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
LORA_PATH = "./saves/sft_exp1"

print("=" * 60)
print("  山西政务小模型微调效果演示")
print("=" * 60)

print("\n[1/3] 加载基座模型...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
)

print("[2/3] 加载微调后 LoRA 权重...")
model = PeftModel.from_pretrained(base_model, LORA_PATH)

print("[3/3] 开始推理\n")

QUESTIONS = [
    "山西政务服务网的网址是什么？",
    "山西省医疗保障局的主要职责是什么？",
    "如何办理山西省居住证？",
]

for q in QUESTIONS:
    print("=" * 60)
    print(f"问: {q}")
    print("-" * 60)
    
    messages = [
        {"role": "system", "content": "你是山西省政务服务智能助手。"},
        {"role": "user", "content": q}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
        )
    
    response = outputs[0][inputs["input_ids"].shape[1]:]
    answer = tokenizer.decode(response, skip_special_tokens=True)
    print(f"答: {answer}")
    print()

print("=" * 60)
print("  演示结束")
print("=" * 60)
