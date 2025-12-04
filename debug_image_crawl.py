#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试图片爬取功能的脚本
"""

import sys
import os
import re
import time
from bs4 import BeautifulSoup
import requests

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath('.'))

from app.utils import crawl_baidu_news

def test_fix_image_url():
    """模拟测试图片URL修复功能"""
    print("=== 模拟测试图片URL修复功能 ===")
    # 直接在函数内实现修复逻辑，模拟utils.py中的处理
    def fix_url(url):
        if not url or url.startswith('data:') or url.startswith('//www.baidu.com/img/'):
            return url
        
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            return 'https://www.baidu.com' + url
        elif url.startswith('https:') and not url.startswith('https://'):
            return 'https://' + url[6:]
        elif url.startswith('http:') and not url.startswith('http://'):
            return 'http://' + url[5:]
        elif not url.startswith(('http://', 'https://')):
            return 'https://www.baidu.com/' + url
        return url
    
    test_cases = [
        "https:t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF",
        "http:t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF",
        "//t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF",
        "/t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF",
        "t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF",
        "https://t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF",
        "http://t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF",
        "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
        "//www.baidu.com/img/baidu_jgylogo3.gif"
    ]
    
    for test_url in test_cases:
        fixed = fix_url(test_url)
        print(f"原始: {test_url}")
        print(f"修复: {fixed}")
        print("-" * 50)

def test_crawl_with_debug():
    """测试爬取功能并输出详细调试信息"""
    print("\n=== 测试百度新闻爬取功能 ===")
    print("开始爬取...")
    
    # 调用爬取函数 - 使用正确的参数名称
    news_list = crawl_baidu_news("成都", page=1, num_per_page=5)
    
    print(f"\n爬取完成，获取到 {len(news_list)} 条新闻")
    print(f"有效新闻: {len(news_list)}")
    
    # 输出每条新闻的详细信息
    for i, news in enumerate(news_list[:5], 1):  # 只显示前5条
        print(f"\n--- 新闻 {i} ---")
        print(f"标题: {news['title']}")
        print(f"链接: {news['url']}")
        print(f"来源: {news['source']}")
        print(f"时间: {news['publish_time']}")
        print(f"摘要: {news['content'][:50]}...")
        print(f"封面图片: {news['cover_image']}")
        print(f"图片是否为空: {not news['cover_image']}")
        print(f"图片URL格式是否正确: {news['cover_image'].startswith(('http://', 'https://')) if news['cover_image'] else False}")

if __name__ == "__main__":
    # 先测试URL修复功能
    test_fix_image_url()
    
    # 再测试实际爬取功能
    test_crawl_with_debug()