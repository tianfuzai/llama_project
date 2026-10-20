import os
import sys

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'


def main():
    if len(sys.argv) < 2:
        print("用法：python run_train.py <yaml配置路径>")
        sys.exit(1)

    config_path = sys.argv[1]
    if not os.path.exists(config_path):
        print(f"配置文件不存在：{config_path}")
        sys.exit(1)

    print(f"开始训练: {config_path}")

    from llamafactory.cli import main as llamafactory_main
    sys.argv = ["llamafactory-cli", "train", config_path]
    llamafactory_main()


if __name__ == "__main__":
    main()
