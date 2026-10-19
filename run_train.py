# -*- coding: utf-8 -*-
"""
统一训练入口脚本（支持 SFT / DPO）
用法：
  python run_train.py train_config/sft_exp1.yaml          # 跑某组 SFT 超参实验
  python run_train.py train_config/dpo.yaml               # 跑 DPO 偏好对齐训练
等价于：
  llamafactory-cli train <yaml路径>
"""
import os
import sys

# 禁用 huggingface 联网，优先读取本地缓存
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'


def main():
    if len(sys.argv) < 2:
        print("用法：python run_train.py <yaml配置路径>")
        print("示例：python run_train.py train_config/sft_exp1.yaml")
        sys.exit(1)

    config_path = sys.argv[1]
    if not os.path.exists(config_path):
        print(f"[错误] 配置文件不存在：{config_path}")
        sys.exit(1)

    print(f"▶ 开始训练，配置文件：{config_path}")

    from llamafactory.cli import main as llamafactory_main
    sys.argv = ["llamafactory-cli", "train", config_path]
    llamafactory_main()


if __name__ == "__main__":
    main()
