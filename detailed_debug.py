import re

# 读取保存的百度新闻HTML内容
with open('baidu_news_debug.txt', 'r', encoding='utf-8') as f:
    html = f.read()

print("详细分析百度新闻页面结构...")

# 1. 查找所有包含"news"的类名
print("\n1. 查找所有包含'news'的类名:")
news_classes = re.findall(r'class="([^"]*news[^"]*)"', html)
news_classes = list(set(news_classes))
print(f"找到{len(news_classes)}个相关类名:")
for cls in news_classes[:20]:  # 只显示前20个
    print(f"  - {cls}")

# 2. 查找所有h3标签及其内容
print("\n2. 查找所有h3标签及其内容:")
h3_tags = re.findall(r'(<h3[^>]*>.*?</h3>)', html, re.DOTALL)
print(f"找到{len(h3_tags)}个h3标签")

if h3_tags:
    print("\n前3个h3标签的内容:")
    for i, tag in enumerate(h3_tags[:3]):
        print(f"\n第{i+1}个h3标签:")
        print(tag)

# 3. 查找包含链接的h3标签
print("\n3. 查找包含链接的h3标签:")
h3_links = re.findall(r'<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>', html, re.DOTALL)
print(f"找到{len(h3_links)}个包含链接的h3标签")

if h3_links:
    print("\n前3个包含链接的h3标签:")
    for i, (link, text) in enumerate(h3_links[:3]):
        print(f"\n第{i+1}个:")
        print(f"  链接: {link}")
        print(f"  文本: {text}")

# 4. 查找新闻条目容器
print("\n4. 查找新闻条目容器:")
# 尝试匹配包含h3标签的div
news_containers = re.findall(r'(<div[^>]*>.*?<h3[^>]*>.*?</h3>.*?</div>)', html, re.DOTALL)
print(f"找到{len(news_containers)}个包含h3的div容器")

if news_containers:
    print("\n第一个包含h3的div容器:")
    container = news_containers[0]
    print(container[:1000])  # 只显示前1000个字符
    
    # 提取该容器的class
    container_class = re.search(r'class="([^"]*)"', container)
    if container_class:
        print(f"\n容器类名: {container_class.group(1)}")

# 5. 尝试直接提取所有链接和标题
print("\n5. 尝试直接提取所有链接和标题:")
all_links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html)
print(f"找到{len(all_links)}个链接")

# 过滤可能的新闻链接
print("\n过滤可能的新闻链接:")
news_links = []
for link, text in all_links:
    # 过滤掉百度内部链接，保留外部新闻链接
    if link.startswith('http') and len(text) > 5:
        news_links.append((link, text))

print(f"找到{len(news_links)}个可能的新闻链接")
if news_links:
    print("\n前5个可能的新闻链接:")
    for i, (link, text) in enumerate(news_links[:5]):
        print(f"\n第{i+1}个:")
        print(f"  链接: {link}")
        print(f"  标题: {text}")

# 6. 查找新闻摘要
print("\n6. 查找新闻摘要:")
summaries = re.findall(r'<span[^>]*class="[^"]*text[^"]*"[^>]*>(.*?)</span>', html)
print(f"找到{len(summaries)}个可能的摘要")

if summaries:
    print("\n前5个摘要:")
    for i, summary in enumerate(summaries[:5]):
        print(f"\n第{i+1}个:")
        print(f"  {summary}")
