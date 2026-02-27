import json
import re


def extract_topics(desc):
    """从 desc 中提取话题，格式为 #话题[话题]#"""
    pattern = r'#([^#\[]+)\[话题\]#'
    matches = re.findall(pattern, desc)
    return matches


# 读取 JSON 文件
json_file = "/Users/zhaozhenfang/Documents/work/sohu/python/media_crawler/data/xhs/json-1/search_contents_2026-01-30.json"
output_file = "/Users/zhaozhenfang/Documents/work/sohu/python/media_crawler/data/xhs/json-1/topic/extracted_topics.txt"

try:
    with open(json_file, "r", encoding="utf-8") as f:
        posts = json.load(f)
except FileNotFoundError:
    print(f"错误：文件 {json_file} 不存在！")
    exit(1)
except json.JSONDecodeError:
    print(f"错误：文件 {json_file} 不是有效的 JSON 格式！")
    exit(1)

# 提取所有帖子的话题
all_topics = []
for post in posts:
    desc = post.get("desc", "")
    topics = extract_topics(desc)
    all_topics.extend(topics)

# 去重并保持顺序
unique_topics = []
for topic in all_topics:
    if topic not in unique_topics:
        unique_topics.append(topic)

# 输出到文件
with open(output_file, "w", encoding="utf-8") as f:
    for topic in unique_topics:
        f.write(topic + "\n")

# 终端打印
print("提取的话题（已去重）：")
for i, topic in enumerate(unique_topics, 1):
    print(f"{i}. {topic}")

print(f"\n话题已保存到文件：{output_file}")
