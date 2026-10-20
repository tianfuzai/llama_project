import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def fmt(b):
    if b >= 1024 ** 3:
        return f"{b / 1024**3:.2f} GB"
    if b >= 1024 ** 2:
        return f"{b / 1024**2:.2f} MB"
    return f"{b / 1024:.1f} KB"


def main():
    cache_root = os.path.expanduser(r"~\.cache\huggingface\hub\models--Qwen--Qwen2.5-1.5B-Instruct")
    base_size = folder_size(cache_root) if os.path.exists(cache_root) else None

    lora_dirs = [d for d in os.listdir(os.path.join(BASE, "saves")) if os.path.isdir(os.path.join(BASE, "saves", d))]
    lora_dirs = sorted(lora_dirs)

    print("========== 权重体积对比 ==========")
    if base_size is not None:
        print(f"基座模型 Qwen2.5-1.5B-Instruct：{fmt(base_size)}")
    else:
        print("基座模型缓存目录未找到")

    for name in lora_dirs:
        p = os.path.join(BASE, "saves", name)
        s = folder_size(p)
        print(f"LoRA 权重  saves/{name}：{fmt(s)}")


if __name__ == "__main__":
    main()
