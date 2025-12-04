#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端页面显示效果
"""

import requests
import time
from app.utils import crawl_baidu_news

# 先爬取一些新闻数据，确保数据库中有数据
def crawl_test_data():
    print("正在爬取测试数据...")
    try:
        keywords = ["成都", "新闻", "科技"]
        for keyword in keywords[:2]:  # 只爬取前两个关键词
            news_list = crawl_baidu_news(keyword, page=1, num_per_page=5)
            print(f"关键词 '{keyword}' 爬取完成，获取到 {len(news_list)} 条新闻")
            time.sleep(1)  # 避免请求过快
        print("测试数据爬取完成！")
    except Exception as e:
        print(f"爬取数据失败: {e}")

# 测试前端页面是否可以正常访问
def test_frontend_access():
    print("\n测试前端页面访问...")
    try:
        url = "http://127.0.0.1:5000"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"前端页面访问成功！状态码: {response.status_code}")
            print("服务器正在运行在: http://127.0.0.1:5000")
            print("请在浏览器中访问该地址查看封面图片显示效果")
        else:
            print(f"前端页面访问失败！状态码: {response.status_code}")
    except requests.ConnectionError:
        print("无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"访问测试失败: {e}")

if __name__ == "__main__":
    crawl_test_data()
    test_frontend_access()
