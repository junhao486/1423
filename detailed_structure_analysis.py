# 详细分析HTML结构
with open('baidu_news_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 查找content_left容器
print("=== 查找content_left容器 ===")
import re
content_left_match = re.search(r'<div[^>]*id=["\']content_left["\'][^>]*>(.*?)</div>', html, re.DOTALL)

if content_left_match:
    content_left = content_left_match.group(1)
    print("找到content_left容器")
    
    # 保存content_left内容以便查看
    with open('content_left.html', 'w', encoding='utf-8') as f:
        f.write(content_left)
    
    # 查找所有的div
    print("\n=== 查找content_left中的所有div ===")
    divs = re.findall(r'<div[^>]*>(.*?)</div>', content_left, re.DOTALL)
    print(f"找到 {len(divs)} 个div")
    
    # 查找所有的h3和后面的元素
    print("\n=== 查找h3和后面的元素 ===")
    h3_with_following = re.findall(r'<h3[^>]*>(.*?)</h3>(.*?)(?:<h3[^>]*>|$)', content_left, re.DOTALL)
    print(f"找到 {len(h3_with_following)} 个h3及其后续内容")
    
    # 显示第一个h3及其后续内容
    if h3_with_following:
        first_h3, first_following = h3_with_following[0]
        print("第一个h3:", first_h3[:100], "...")
        print("后续内容:", first_following[:200], "...")
    
    # 查找包含class的元素
    print("\n=== 查找content_left中的所有class ===")
    all_classes = re.findall(r'class=["\']([^"\']*)["\']', content_left)
    print("所有class:", all_classes)
    
else:
    print("没有找到content_left容器")
