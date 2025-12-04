#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试HTML内容，查看图片URL的实际来源和格式
"""

import sys
import os
import re
import time
import requests
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath('.'))

def debug_baidu_html(keyword="成都", page=1):
    """调试百度新闻的HTML内容，查看图片URL的实际格式"""
    print(f"=== 调试百度新闻HTML内容 (关键词: {keyword}, 第{page}页) ===")
    
    # 构造百度新闻搜索URL
    url = f"https://www.baidu.com/s?ie=utf-8&medium=0&rtt=1&bsst=1&rsv_dl=news_b_pn&cl=2&wd={keyword}&tn=news&rsv_bp=1&rsv_sug3=2&rsv_sug1=2&rsv_sug7=100&rsv_sug2=0&oq=&rsv_btype=i&f=8&rsv_sug4=9312"
    
    # 构造请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # 发送请求
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        
        print(f"\n请求状态: {response.status_code}")
        print(f"响应URL: {response.url}")
        
        # 保存原始HTML到文件
        with open("baidu_news_debug.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"\nHTML内容已保存到: baidu_news_debug.html")
        
        # 解析HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找新闻容器
        news_containers = soup.find_all("div", class_=re.compile(r'news-list.*|result.*', re.I))
        print(f"\n找到新闻容器: {len(news_containers)}")
        
        # 查找所有新闻项
        news_items = []
        for container in news_containers:
            # 尝试多种新闻项选择器
            items = container.find_all(["div", "li"], class_=re.compile(r'news-item|result-item|c-container', re.I))
            news_items.extend(items)
        
        print(f"找到新闻项: {len(news_items)}")
        
        # 分析前5条新闻的图片URL
        for i, item in enumerate(news_items[:5], 1):
            print(f"\n--- 新闻项 {i} ---")
            
            # 查找图片标签
            imgs = item.find_all("img")
            print(f"图片标签数量: {len(imgs)}")
            
            for j, img in enumerate(imgs, 1):
                img_src = img.get("src", "")
                data_src = img.get("data-src", "")
                data_original = img.get("data-original", "")
                
                print(f"  图片 {j}:")
                print(f"    src: {img_src}")
                print(f"    data-src: {data_src}")
                print(f"    data-original: {data_original}")
                print(f"    所有属性: {list(img.attrs.keys())}")
            
            # 查找所有包含图片的链接
            img_links = item.find_all("a", href=re.compile(r'.*img.*', re.I))
            for j, link in enumerate(img_links, 1):
                href = link.get("href", "")
                print(f"  图片链接 {j}:")
                print(f"    href: {href}")
        
        return True
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_baidu_html()