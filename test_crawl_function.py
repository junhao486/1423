#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据抓取功能测试脚本
"""

import sys
import os
import requests
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils import crawl_baidu_news

def test_data_crawl():
    """测试数据抓取功能"""
    print("开始测试数据抓取功能...")
    
    # 测试关键词
    keyword = "成都"
    
    # 直接调用抓取函数
    print(f"\n使用关键词 '{keyword}' 调用crawl_baidu_news函数...")
    try:
        # 调用抓取函数
        news_list = crawl_baidu_news(keyword, page=1, num_per_page=10)
        
        print(f"共抓取到 {len(news_list)} 条新闻")
        
        if news_list:
            print("\n抓取结果详情：")
            for i, news in enumerate(news_list, 1):
                print(f"\n新闻 {i}:")
                print(f"标题: {news.get('标题', '')}")
                print(f"概要: {news.get('概要', '')}")
                print(f"来源: {news.get('来源', '')}")
                print(f"原始URL: {news.get('原始URL', '')}")
                print(f"封面: {news.get('封面', '')}")
        else:
            print("\n未抓取到任何新闻")
    except Exception as e:
        print(f"调用抓取函数失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n数据抓取功能测试完成！")

if __name__ == "__main__":
    test_data_crawl()
