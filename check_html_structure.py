# 查看保存的HTML文件结构
with open('baidu_news_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 查找所有包含result的class
print("=== 查找所有包含result的class ===")
import re
result_classes = re.findall(r'class=["\']([^"\']*result[^"\']*)["\']', html)
print("找到的result类:", result_classes)

# 查找所有div的class
print("\n=== 查找所有div的class ===")
div_classes = re.findall(r'<div[^>]*class=["\']([^"\']*)["\'][^>]*>', html)
# 只显示前20个
print("前20个div类:", div_classes[:20])

# 查找所有h3标签
print("\n=== 查找所有h3标签 ===")
h3_tags = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
print(f"找到 {len(h3_tags)} 个h3标签")
# 显示前3个h3标签
for i, h3 in enumerate(h3_tags[:3]):
    print(f"第{i+1}个h3标签:", h3)

# 查找包含href的a标签
print("\n=== 查找包含href的a标签 ===")
a_tags = re.findall(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
print(f"找到 {len(a_tags)} 个带href的a标签")
# 显示前5个a标签
for i, (href, text) in enumerate(a_tags[:5]):
    print(f"第{i+1}个a标签:")
    print(f"  href: {href}")
    print(f"  text: {text[:50]}...")
