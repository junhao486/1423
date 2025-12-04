import requests
import sys
import os
from bs4 import BeautifulSoup

# 设置项目路径
sys.path.append('e:\\舆情系统')

# 获取百度新闻页面的HTML内容
keyword = '成都'
url = f'https://www.baidu.com/s?wd={keyword}&tn=news'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)
html = response.text

# 保存HTML到文件以便详细分析
with open('baidu_news_debug_detailed.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML文件已保存到 baidu_news_debug_detailed.html")

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(html, 'html.parser')

# 查找所有h3标签（通常包含新闻标题）
h3_tags = soup.find_all('h3')
print(f"找到 {len(h3_tags)} 个h3标签")

# 详细分析每个h3标签及其父容器
for i, h3_tag in enumerate(h3_tags[:5]):  # 只分析前5个
    print(f"\n=== 分析第 {i+1} 个h3标签 ===")
    
    # 打印h3标签的完整HTML
    print("h3标签内容:")
    print(h3_tag.prettify())
    
    # 找到父容器
    parent_div = h3_tag.find_parent('div')
    if parent_div:
        print("\n父容器div内容:")
        print(parent_div.prettify())
        
        # 查找所有子元素
        print("\n父容器的所有子元素:")
        for child in parent_div.children:
            if child.name:
                print(f"- 标签: {child.name}, class: {child.get('class')}")
                
        # 查找所有可能包含来源信息的元素
        print("\n查找所有可能包含来源的元素:")
        # 查找所有包含"来源"或"source"的元素
        source_candidates = parent_div.find_all(['a', 'span', 'div'], text=lambda text: text and ('来源' in text or 'source' in text.lower()))
        for candidate in source_candidates:
            print(f"- 元素: {candidate.name}, 内容: {candidate.get_text()}, class: {candidate.get('class')}")
        
        # 查找所有链接
        print("\n父容器中的所有链接:")
        links = parent_div.find_all('a')
        for j, link in enumerate(links):
            print(f"- 链接 {j+1}: {link.get('href')}, 文本: {link.get_text()}, class: {link.get('class')}")

print("\n详细分析完成！请查看 baidu_news_debug_detailed.html 文件获取完整HTML结构。")