# -*- coding: utf-8 -*-
"""
PEFT 加载 LoRA 推理脚本（对应作业 FR-E1 / FR-E3）
用法：
  python scripts/infer_peft.py [lora路径] ["测试问题"]
示例：
  python scripts/infer_peft.py saves/sft_exp1 "哪个网站属于山西省行政审批服务管理局主办和运行维护？"

功能：
  1. 用 PeftModel 加载基座模型 + LoRA 权重，完成一次推理；
  2. 同时打印"仅基座模型"与"基座+LoRA"两个回答，做直观对比（FR-E3）。
"""
import os
import sys

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


def main():
    lora_path = sys.argv[1] if len(sys.argv) > 1 else "./saves/sft_exp1"
    question = sys.argv[2] if len(sys.argv) > 2 else "哪个网站属于山西省行政审批服务管理局主办和运行维护？"

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import torch

    print("▶ 加载基座模型与分词器（本地缓存模式）...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True
    )

    print("▶ 加载 LoRA 权重...")
    model = PeftModel.from_pretrained(base_model, lora_path)

    def generate(m):
        messages = [{"role": "user", "content": question}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        outputs = m.generate(**inputs, max_new_tokens=128, do_sample=False)
        return tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

    print("\n========== 基座 + LoRA 回答 ==========")
    print(generate(model))

    print("\n========== 仅基座模型回答（对照）==========")
    print(generate(base_model))


if __name__ == "__main__":
    main()
