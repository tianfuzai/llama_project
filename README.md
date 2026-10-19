# 项目04 · 垂直领域小模型微调与偏好对齐（LoRA + DPO + 数据蒸馏）

业务场景：**山西本地政务问答**
小组人数：4 人
基座模型：**Qwen/Qwen2.5-1.5B-Instruct**
训练框架：**LLaMA-Factory**
开发环境：Python 3.10 + CUDA GPU（消费级 8GB 显存）

---

## 一、项目简介

本项目走通「**造数据 → SFT 微调 → DPO 偏好对齐 → 模型加载 → 效果评估**」完整闭环：

1. 用爬虫抓取山西政务服务网公开办事指南，得到原始政务文本；
2. 清洗、分块，并基于分块文本人工/大模型蒸馏出 QA 对；
3. 产出 Alpaca、ShareGPT 两种格式数据集（各 ≥500 条）；
4. 用 LLaMA-Factory 完成 4 组 LoRA 超参对比实验；
5. 构造偏好配对数据（≥200 组），完成一次 DPO 偏好对齐训练；
6. 用 PEFT 加载 LoRA 推理；
7. 在 50 题独立测试集上对「基座 / SFT-LoRA / DPO」三方做人工 + 大模型打分评估。

所有实验配置落盘为 YAML，记录随机种子 `42`，保证可复现。

---

## 二、环境要求（显存门槛）

| 微调方案 | 最低显存 | 本项目实际使用 |
|---|---|---|
| Qwen2.5-1.5B + LoRA（bf16） | 8GB | ✔ |

- 操作系统：Windows 10 / 11
- Python：3.10+
- GPU：NVIDIA，显存 ≥8GB，需 CUDA
- 依赖：`torch`（CUDA版）、`transformers`、`peft`、`accelerate`、`datasets`
- 训练框架：LLaMA-Factory（含 WebUI）
- vLLM（可选，LoRA 部署推理需 Linux 环境，Windows 不支持）

---

## 三、环境安装

```bash
# 1. 创建 conda 虚拟环境
conda create -n nlpbase python=3.10
conda activate nlpbase

# 2. 安装 PyTorch（CUDA 版，请按自己显卡驱动版本调整 cu121/cu118）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. 安装核心依赖
pip install transformers peft accelerate datasets sentencepiece protobuf

# 4. 安装 LLaMA-Factory
pip install llamafactory

# 5. 安装爬虫与数据处理依赖
pip install requests beautifulsoup4
```

> 离线优先：本机已缓存 Qwen2.5-1.5B-Instruct，训练脚本已设置 `HF_HUB_OFFLINE=1`，不会请求外网。

---

## 四、数据准备流程（按顺序执行）

所有脚本都在 `scripts/` 目录，数据处理产物在 `project_data/`。

```bash
# 1. 爬虫：抓取山西政务服务网原始文本
python crawl_shanxi.py

# 2. 清洗 + 文本分块（生成 chunks.txt）
python clean_and_chunk.py

# 3. 数据蒸馏：基于 chunk 生成 QA（需本机 Ollama 已装 qwen2.5:7b）
python auto_gen_sft.py

# 4. 数据清洗统计（去重/去空/过滤过长过短，输出 alpaca_zh.json + 统计报告）
python scripts/clean_sft_data.py

# 5. 生成 ShareGPT 格式数据集（sharegpt_zh.json）
python scripts/convert_to_sharegpt.py

# 6. 人工抽检 50 条（生成抽检表 CSV，人工填写后统计一致率）
python scripts/sample_check.py

# 7. 构造 DPO 偏好配对数据（dpo_data.json，≥200 组）
python scripts/build_dpo_data.py

# 8. 构建 50 题独立测试集（testset.json）
python scripts/build_testset.py
```

> 若 `auto_gen_sft.py` 依赖 Ollama，也可改用大模型 API 批量蒸馏，替换其中的调用函数即可。

---

## 五、训练命令

所有训练配置在 `train_config/`，统一入口 `run_train.py`。

```bash
# 1. 4 组 SFT 超参对比实验
python run_train.py train_config/sft_exp1.yaml   # rank=8,  alpha=16, lr=2e-5  基准组
python run_train.py train_config/sft_exp2.yaml   # rank=16, alpha=32, lr=2e-5  rank增大
python run_train.py train_config/sft_exp3.yaml   # rank=8,  alpha=8,  lr=2e-5  alpha同比例
python run_train.py train_config/sft_exp4.yaml   # rank=8,  alpha=16, lr=1e-4  学习率增大

# 2. DPO 偏好对齐训练（在 sft_exp1 结果基础上继续）
python run_train.py train_config/dpo.yaml

# 3. 统计 LoRA 权重与基座体积对比（FR-C5）
python scripts/compare_size.py
```

> 每组实验输出到独立目录 `saves/sft_exp1~4` 与 `saves/dpo`，训练日志包含 train loss 与 val loss，可用于绘制 loss 曲线。

**显存不足时的降级方案（按优先级）：**
1. 降低 `cutoff_len`（如 1024 → 512）；
2. 减小 `per_device_train_batch_size`（1）并调大 `gradient_accumulation_steps`；
3. 改用 QLoRA 4bit（`quantization_bit: 4`）；
4. 削减 `max_samples`；
5. 换更小基座模型。

---

## 六、推理与评估命令

```bash
# 1. PEFT 加载 LoRA 推理（基座 + LoRA 对照，FR-E1/E3）
python scripts/infer_peft.py saves/sft_exp1 "哪个网站属于山西省行政审批服务管理局主办和运行维护？"

# 2. 三方效果评估（基座 / SFT / DPO），生成回答 + 人工打分表 + 大模型打分提示词
python scripts/evaluate.py
```

> vLLM 说明：vLLM 加载 LoRA 并暴露 OpenAI 兼容接口需要 **GPU / Linux** 环境；本组在 Windows 本地完成，vLLM 路线作为可选，未完成时在文档中说明客观原因，以 PEFT 路线作为替代验证。

---

## 七、项目目录结构

```
llama_project/
├─ crawl_shanxi.py          # 爬虫：抓取山西政务服务网原始文本
├─ clean_and_chunk.py       # 清洗 + 滑动窗口分块
├─ auto_gen_sft.py          # 数据蒸馏：基于 chunk 生成 QA
├─ run_train.py             # 统一训练入口（SFT / DPO）
├─ train_lora.py            # 训练入口（读 train_lora_clean.yaml）
├─ train_lora.yaml          # 7B QLoRA 配置（备用）
├─ train_lora_clean.yaml    # 1.5B LoRA 主配置
├─ data/
│  └─ dataset_info.json     # 数据集登记（alpaca/sharegpt/dpo）
├─ project_data/            # 原始文本、chunk、train/val、各数据集
├─ scripts/                 # 数据处理 / 推理 / 评估 / 统计脚本
├─ train_config/            # 4 组超参 yaml + dpo yaml
├─ saves/                   # LoRA 训练产出（.gitignore 排除）
└─ docs/                    # 项目文档
   ├─ 架构说明.md           # 流水线架构
   ├─ 数据说明.md           # 数据来源与清洗/抽检
   ├─ 训练实验报告.md       # 4 组超参实验 + loss 曲线 + 显存降级
   ├─ 偏好对齐说明.md       # DPO 数据构造 + 训练 + 原理
   ├─ 效果评估报告.md       # 三方对比表 + 结论
   ├─ 部署说明.md           # 环境/硬件/命令
   └─ 复现指南.md           # 从零复现步骤
```

---

## 八、四人小组分工

> 完整版见 `docs/分工说明.md`（含每人所写的全部代码文件清单）。以下为概要。

### 成员1 —— 数据工程（模块 A + B）
- 编写 `crawl_shanxi.py` 爬虫，采集山西政务服务网原始文本；
- 编写 `clean_and_chunk.py` 清洗与文本分块；
- 设计 QA 蒸馏提示词，运行 `auto_gen_sft.py` 生成 QA；
- 运行 `scripts/clean_sft_data.py` 清洗统计、`scripts/convert_to_sharegpt.py` 生成 ShareGPT 格式；
- 运行 `scripts/sample_check.py` 人工抽检 50 条；
- 登记 `data/dataset_info.json`，验证两种格式可被 LLaMA-Factory 解析；
- 输出：`数据说明.md`、抽检表、清洗统计报告。

### 成员2 —— SFT 微调与超参实验（模块 C）
- 部署 LLaMA-Factory、下载基座模型、启动 WebUI；
- 设计并运行 4 组超参实验（`train_config/sft_exp1~4`）；
- 记录 loss 曲线，分析欠拟合 / 过拟合；
- 完成一次显存降级试验；
- 运行 `scripts/compare_size.py` 统计 LoRA 体积；
- 输出：`训练实验报告.md`、loss 曲线、LoRA 体积对比。

### 成员3 —— DPO 偏好对齐 + 模型推理（模块 D + E）
- 运行 `scripts/build_dpo_data.py` 构造偏好配对数据（≥200 组）；
- 运行 `python run_train.py train_config/dpo.yaml` 完成 DPO 训练；
- 编写 `scripts/infer_peft.py`，PEFT 加载 LoRA 推理；
- 记录 DPO loss 曲线，解释 DPO 原理与 KL 散度作用；
- 输出：`偏好对齐说明.md`、DPO loss 曲线、基座 vs LoRA 对比样例。

### 成员4 —— 效果评估 + 工程协作 + 文档整合（模块 F + G）
- 运行 `scripts/build_testset.py` 构建 50 题测试集；
- 运行 `scripts/evaluate.py`，人工打分 + 大模型打分；
- 汇总三方对比表，给出结论；
- Git 分支管理（main/dev/feature）、PR 评审、.gitignore 配置；
- 编写 README、`复现指南.md`、`部署说明.md`，整合全部文档与答辩材料。

---

## 九、Git 协作规范（FR-G）

- 分支策略：`main` / `dev` / `feature/*`；
- 提交信息遵循 Conventional Commits（`feat:`、`fix:`、`docs:`、`refactor:`）；
- 每人至少 1 个 PR，并完成 1 次他人代码评审；
- 模型权重、checkpoint、大体积数据集由 `.gitignore` 排除，不入库；仓库仅保留脚本、配置、文档与数据样本；
- 全量数据 / 权重存放网盘或校内共享，README 中注明地址。

---

## 十、验收自查对照（核心项）

- 数据集：Alpaca 与 ShareGPT 各 ≥500 条，字段完整，能被 LLaMA-Factory 解析；
- 数据真实：来源于山西政务服务网原文抽取，抽查 10 条可与原文对应；
- 人工抽检 50 条，与原文一致率 ≥90%，有抽检表；
- 清洗前后条数、去重数量有记录；
- 4 组 LoRA 超参对比实验完成，每组有 loss 曲线，覆盖 rank/alpha/lr；
- 显存降级试验记录解决手段与效果；
- LoRA 权重体积远小于基座，有数字对比；
- DPO 训练完成，偏好配对 ≥200 组，有 DPO loss 曲线；
- PEFT 加载 LoRA 推理成功，基座 vs LoRA 对照；
- 测试集 ≥50 题且与训练无重叠；
- 基座/SFT-LoRA/DPO 三方评估完成，含人工与大模型打分；
- 三方对比表含平均分、胜出次数、明显错误数，结论明确。

---

## 十一、参考资料

- LLaMA-Factory 官方仓库：https://github.com/hiyouga/LLaMA-Factory
- LLaMA-Factory 中文文档：https://llamafactory.readthedocs.io/zh-cn/latest/
- PEFT 文档：https://huggingface.co/docs/peft/index
- LoRA 论文：https://arxiv.org/abs/2106.09685
- DPO 论文：https://arxiv.org/abs/2305.18290
- 山西省人民政府：https://www.shanxi.gov.cn/
