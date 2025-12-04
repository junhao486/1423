import re

# 读取保存的百度新闻HTML内容
with open('baidu_news_debug.txt', 'r', encoding='utf-8') as f:
    html = f.read()

print("查找新闻列表容器...")

# 1. 查找可能的新闻列表容器
print("\n1. 查找可能的新闻列表容器:")
# 查找包含多个新闻条目的容器
possible_containers = [
    r'(<div[^>]*id="[^"]*news[^"]*"[^>]*>.*?</div>)',
    r'(<div[^>]*class="[^"]*news-list[^"]*"[^>]*>.*?</div>)',
    r'(<div[^>]*class="[^"]*result[^"]*"[^>]*>.*?</div>)',
    r'(<div[^>]*class="[^"]*content[^"]*"[^>]*>.*?</div>)',
]

for pattern in possible_containers:
    containers = re.findall(pattern, html, re.DOTALL)
    print(f"模式 '{pattern[:50]}...' 找到 {len(containers)} 个容器")
    
    if containers:
        print("\n容器内容预览:")
        print(containers[0][:500])
        break

# 2. 查找所有包含时间的元素（新闻通常包含发布时间）
print("\n2. 查找包含时间的元素:")
time_patterns = [
    r'<span[^>]*class="[^"]*time[^"]*"[^>]*>(.*?)</span>',
    r'<span[^>]*class="[^"]*date[^"]*"[^>]*>(.*?)</span>',
    r'<span[^>]*class="[^"]*c-color-gray2[^"]*"[^>]*>(.*?)</span>',
]

for pattern in time_patterns:
    times = re.findall(pattern, html)
    print(f"模式 '{pattern}' 找到 {len(times)} 个时间元素")
    
    if times:
        print("前10个时间:")
        for time in times[:10]:
            if len(time.strip()) > 0:
                print(f"  - {time.strip()}")
        break

# 3. 尝试直接查找新闻内容模式
print("\n3. 尝试直接查找新闻内容:")
# 查找包含标题、链接、时间的完整新闻条目
news_item_pattern = re.compile(r'((?:<a[^>]*href="([^"]*)".*?>(.*?)</a>.*?<span[^>]*>(.*?)</span>.*?)+)', re.DOTALL)
news_items = news_item_pattern.findall(html)

print(f"找到 {len(news_items)} 个可能的新闻条目")
if news_items:
    print("\n前3个可能的新闻条目:")
    for i, (item, link, title, time) in enumerate(news_items[:3]):
        print(f"\n第{i+1}个:")
        print(f"  标题: {title.strip()[:50]}...")
        print(f"  链接: {link}")
        print(f"  时间: {time.strip()}")
        print(f"  完整内容: {item[:200]}...")

# 4. 查找所有可能的新闻标题
print("\n4. 查找所有可能的新闻标题:")
# 查找长度适中且包含中文的链接文本
all_links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html)

possible_news_titles = []
for link, text in all_links:
    # 过滤条件：
    # 1. 链接是外部链接（不是百度内部链接）
    # 2. 文本长度在5-100个字符之间
    # 3. 包含中文
    if (not link.startswith('http://www.baidu.com') and not link.startswith('https://www.baidu.com')) and \
       5 < len(text.strip()) < 100 and \
       re.search(r'[\u4e00-\u9fa5]', text):
        possible_news_titles.append((link, text.strip()))

print(f"找到 {len(possible_news_titles)} 个可能的新闻标题")
if possible_news_titles:
    print("\n前10个可能的新闻标题:")
    for i, (link, title) in enumerate(possible_news_titles[:10]):
        print(f"\n第{i+1}个:")
        print(f"  标题: {title}")
        print(f"  链接: {link}")
