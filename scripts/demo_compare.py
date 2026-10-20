import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
LORA_PATH = "./saves/sft_exp1"

DEMO_QUESTIONS = [
    "山西省政务服务网的网址是什么？",
    "如何在山西省办理居住证？",
    "山西省医疗保险异地就医怎么备案？",
    "山西省大学生创业补贴申请条件是什么？",
]

def chat(model, tokenizer, question, max_new_tokens=200):
    messages = [
        {"role": "system", "content": "你是山西省政务服务智能助手。"},
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
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    finetuned_model = PeftModel.from_pretrained(base_model, LORA_PATH)

    for i, q in enumerate(DEMO_QUESTIONS, 1):
        print(f"问题 {i}: {q}")
        print("【基座】")
        print(chat(base_model, tokenizer, q)[:300])
        print("【微调后】")
        print(chat(finetuned_model, tokenizer, q)[:300])
        print()

if __name__ == "__main__":
    main()
