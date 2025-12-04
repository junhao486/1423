# 直接查看content_left.html文件的内容
with open('content_left.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("=== content_left.html的完整内容 ===")
print(content)

# 查找所有的标签
print("\n=== 查找所有的标签 ===")
import re
tags = re.findall(r'<([a-z]+)', content)
print("找到的标签:", set(tags))
