#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分析百度新闻HTML页面结构的脚本
"""

import os
from bs4 import BeautifulSoup

def analyze_html_structure(html_file):
    """分析HTML文件的结构"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"页面总长度: {len(content)} 字符")
    print("=" * 50)
    
    # 创建BeautifulSoup对象
    soup = BeautifulSoup(content, 'html.parser')
    
    # 查看页面标题
    title = soup.title.string if soup.title else "无标题"
    print(f"页面标题: {title}")
    print()
    
    # 查找所有div标签的类名
    print("页面中包含的div类名:")
    div_classes = set()
    for div in soup.find_all('div'):
        if div.get('class'):
            div_classes.add(' '.join(div.get('class')))
    
    if div_classes:
        for cls in sorted(div_classes):
            print(f"  - {cls}")
    else:
        print("  没有找到带类名的div标签")
    print()
    
    # 查找所有h3标签
    h3_tags = soup.find_all('h3')
    print(f"找到 {len(h3_tags)} 个h3标签:")
    for i, h3 in enumerate(h3_tags[:5]):  # 只显示前5个
        print(f"  {i+1}. {h3.get_text(strip=True)[:50]}...")
    print()
    
    # 查找所有a标签
    a_tags = soup.find_all('a')
    print(f"找到 {len(a_tags)} 个a标签")
    print()
    
    # 查找所有img标签
    img_tags = soup.find_all('img')
    print(f"找到 {len(img_tags)} 个img标签")
    for i, img in enumerate(img_tags[:5]):  # 只显示前5个
        src = img.get('src', '')
        print(f"  {i+1}. src: {src[:100]}...")
    print()
    
    # 查找可能的新闻列表容器
    print("可能的新闻列表容器:")
    possible_containers = []
    
    # 查找包含多个h3标签的div
    for div in soup.find_all('div'):
        if len(div.find_all('h3')) > 2:
            div_class = ' '.join(div.get('class')) if div.get('class') else '无类名'
            possible_containers.append((div_class, len(div.find_all('h3'))))
    
    if possible_containers:
        for container in possible_containers:
            print(f"  - 类名: {container[0]}, 包含h3标签数: {container[1]}")
    else:
        print("  没有找到包含多个h3标签的div")
    print()
    
    # 查找包含a标签的h3标签的父容器
    print("包含链接的h3标签的父容器:")
    h3_with_links = soup.find_all('h3')
    parent_containers = set()
    
    for h3 in h3_with_links:
        a_tag = h3.find('a')
        if a_tag and a_tag.get('href'):
            parent = h3.parent
            if parent.name == 'div':
                parent_class = ' '.join(parent.get('class')) if parent.get('class') else '无类名'
                parent_containers.add(parent_class)
    
    if parent_containers:
        for container in sorted(parent_containers):
            print(f"  - {container}")
    else:
        print("  没有找到包含链接的h3标签的div父容器")
    print()
    
    # 查找所有包含"新闻"或"news"的文本
    print("包含'新闻'或'news'的文本:")
    all_text = soup.get_text()
    if '新闻' in all_text or 'news' in all_text.lower():
        print("  页面中包含'新闻'或'news'关键词")
    else:
        print("  页面中不包含'新闻'或'news'关键词")
    print()
    
    # 保存前5000个字符到文件以便详细查看
    with open('html_preview.txt', 'w', encoding='utf-8') as f:
        f.write(content[:5000])
    print(f"已将页面前5000个字符保存到 html_preview.txt")

if __name__ == "__main__":
    html_file = "baidu_news.html"
    if os.path.exists(html_file):
        analyze_html_structure(html_file)
    else:
        print(f"错误: 文件 {html_file} 不存在")
