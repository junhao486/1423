# 检查保存的HTML文件中是否存在新闻标题类
with open('baidu_news_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

# 搜索特定的类名
print("=== 搜索特定的类名 ===")
target_class = 'news-title-font_1xS-F'
if target_class in html:
    print(f"找到类名 {target_class}！")
    # 显示包含这个类名的完整标签
    matches = re.findall(r'<[^>]*class=["\'].*?' + target_class + '.*?["\'][^>]*>', html)
    print(f"找到 {len(matches)} 个匹配的标签:")
    for match in matches:
        print(match)
else:
    print(f"没有找到类名 {target_class}")

# 搜索所有的a标签
print("\n=== 搜索所有的a标签 ===")
a_tags = re.findall(r'<a[^>]*>(.*?)</a>', html, re.DOTALL)
print(f"找到 {len(a_tags)} 个a标签")

# 搜索所有的h3标签
print("\n=== 搜索所有的h3标签 ===")
h3_tags = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
print(f"找到 {len(h3_tags)} 个h3标签")
for i, h3 in enumerate(h3_tags[:5]):
    print(f"第{i+1}个h3标签:")
    print(h3[:200], "...")

# 搜索所有的class
print("\n=== 搜索所有的class ===")
all_classes = re.findall(r'class=["\']([^"\']*)["\']', html)
print(f"找到 {len(all_classes)} 个class")
# 显示包含news的class
news_classes = [c for c in all_classes if 'news' in c.lower()]
print("包含news的class:", news_classes)
