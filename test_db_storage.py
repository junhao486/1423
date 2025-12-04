#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试抓取数据是否能正确存储到数据库
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import db
from app import custom_create_app
from app.models import News
from app.utils import crawl_baidu_news

# 创建应用实例和上下文
app = custom_create_app()
app_context = app.app_context()
app_context.push()

# 测试数据抓取和存储功能
def test_crawl_and_store(keyword="成都"):
    print(f"开始测试抓取并存储{keyword}相关新闻...")
    
    # 1. 调用抓取函数获取新闻数据
    news_data = crawl_baidu_news(keyword)
    print(f"抓取成功，共获取{len(news_data)}条新闻")
    
    # 2. 测试数据存储
    count = 0
    for item in news_data:
        # 检查是否已存在相同URL的新闻
        existing_news = News.query.filter_by(url=item['原始URL']).first()
        if not existing_news:
            # 创建新闻对象
            news = News(
                title=item['标题'],
                content=item['概要'],
                source=item['来源'],
                url=item['原始URL'],
                cover=item['封面'],
                publish_time=item['publish_time'],
                crawl_time=item['crawl_time']
            )
            
            # 添加到数据库
            db.session.add(news)
            count += 1
    
    # 提交事务
    db.session.commit()
    
    print(f"成功存储{count}条新新闻到数据库")
    
    # 3. 验证数据库中的数据
    stored_news = News.query.filter(News.title.like(f"%{keyword}%")).count()
    print(f"数据库中包含关键词'{keyword}'的新闻共有{stored_news}条")
    
    # 显示最近存储的新闻
    recent_news = News.query.order_by(News.crawl_time.desc()).limit(5).all()
    print("\n最近存储的5条新闻：")
    for news in recent_news:
        print(f"- {news.title} ({news.publish_time if news.publish_time else '未知时间'})")
    
    return count

# 主函数
if __name__ == "__main__":
    test_crawl_and_store("成都")
