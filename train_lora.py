# 新增：禁用huggingface联网检查，优先读取本地缓存
import os
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'

from llamafactory.cli import main
import sys

# 等价命令：llamafactory-cli train train_lora_clean.yaml
if __name__ == "__main__":
    sys.argv = [
        "llamafactory-cli",
        "train",
        "train_lora_clean.yaml"
    ]
    main()
