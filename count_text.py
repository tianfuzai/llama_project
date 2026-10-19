import os

file_path = "project_data/raw_docs/all_raw_text.txt"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 总字符（含换行分隔符）
total_chars = len(content)
# 纯中文字符简易统计
import re
chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
total_cn = len(chinese_chars)

print(f"文件全部字符数：{total_chars}")
print(f"纯中文字符数量：{total_cn}")
