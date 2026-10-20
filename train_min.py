# -*- coding: utf-8 -*-
"""
最小化 LoRA 训练脚本 - 绕过 LLaMA-Factory，直接用 transformers + peft
"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, TaskType

MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
DATA_FILE = "data/shanxi_train.jsonl"
OUTPUT = "./saves/sft_exp1"

print("[1/5] 加载 tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL)
tokenizer.pad_token = tokenizer.eos_token

print("[2/5] 加载数据集...")
dataset = load_dataset("json", data_files=DATA_FILE, split="train")

def format_example(ex):
    messages = [
        {"role": "system", "content": "你是山西省政务服务智能助手。"},
        {"role": "user", "content": ex["instruction"] + (ex["input"] if ex["input"] else "")},
        {"role": "assistant", "content": ex["output"]}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    return tokenizer(text, truncation=True, max_length=256, padding=False)

print("[3/5] 处理数据...")
tokenized = dataset.map(format_example, remove_columns=dataset.column_names)

print("[4/5] 加载模型 + LoRA...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
)

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

print("[5/5] 开始训练...")
training_args = TrainingArguments(
    output_dir=OUTPUT,
    num_train_epochs=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    learning_rate=2e-4,
    logging_steps=1,
    save_strategy="no",
    fp16=True,
    report_to="none",
    remove_unused_columns=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    data_collator=lambda data: {
        "input_ids": torch.tensor([d["input_ids"] for d in data]),
        "attention_mask": torch.tensor([d["attention_mask"] for d in data]),
        "labels": torch.tensor([d["input_ids"] for d in data]),
    },
)

trainer.train()
model.save_pretrained(OUTPUT)
tokenizer.save_pretrained(OUTPUT)
print("训练完成！权重保存在:", OUTPUT)
