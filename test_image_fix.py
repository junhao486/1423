#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图片URL修复效果
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import re

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 测试clean_text函数对URL的影响
def test_clean_text_effect():
    print("=== 测试clean_text函数对URL的影响 ===")
    from app.utils import clean_text
    
    test_urls = [
        "https://t9.baidu.com/it/u=123456789,123456789&fm=3035&app=3035&size=f242,162&n=0&g=0n&f=JPEG",
        "http://t9.baidu.com/it/u=123456789,123456789&fm=3035&app=3035&size=f242,162",
        "https://t9.baidu.com/it/u=123456789,123456789&fm=3035&app=3035&size=f242,162&n=0&g=0n&f=JPEG?s=A1B2C3D4E5F6G7H8&sec=1764906009&t=abcdef1234567890"
    ]
    
    for url in test_urls:
        cleaned = clean_text(url)
        print(f"原始URL: {url}")
        print(f"clean_text处理后: {cleaned}")
        print(f"是否相同: {url == cleaned}")
        print()

# 测试实际爬取效果
def test_actual_crawl():
    print("\n=== 测试实际爬取效果 ===")
    from app.utils import crawl_baidu_news
    
    try:
        print("正在爬取百度新闻...")
        news_list = crawl_baidu_news("成都", page=1, num_per_page=5)
        
        print(f"爬取到 {len(news_list)} 条新闻")
        
        for i, news in enumerate(news_list[:3], 1):
            print(f"\n新闻 {i}:")
            print(f"标题: {news['title']}")
            print(f"封面图片URL: {news['cover_image']}")
            print(f"URL是否有效: {news['cover_image'].startswith(('http://', 'https://'))}")
            
            # 测试URL是否可访问
            if news['cover_image']:
                try:
                    response = requests.head(news['cover_image'], timeout=5)
                    print(f"URL可访问性: {'成功' if response.status_code == 200 else '失败'}")
                except Exception as e:
                    print(f"URL访问测试失败: {e}")
                    
    except Exception as e:
        print(f"爬取失败: {e}")

if __name__ == "__main__":
    test_clean_text_effect()
    test_actual_crawl()
